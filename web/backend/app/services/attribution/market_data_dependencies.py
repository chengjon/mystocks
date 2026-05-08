from __future__ import annotations

from datetime import datetime
from hashlib import md5
from typing import Any

import pandas as pd

from app.services.data_service import DataService
from src.data_sources.baostock_importer import BaoStockData

from .errors import AttributionDependencyError


class AttributionMarketDataDependencies:
    """Thin dependency loader for benchmark, industry, OHLCV, and factor enrichment."""

    def __init__(
        self,
        *,
        baostock_importer: BaoStockData | None = None,
        data_service: DataService | None = None,
    ) -> None:
        self.baostock_importer = baostock_importer or BaoStockData()
        self.data_service = data_service or DataService(auto_fetch=False, use_cache=False)

    def load_benchmark_constituents(self, analysis_date: str) -> pd.DataFrame:
        frame = self.baostock_importer.query_hs300_stocks(analysis_date)
        if frame is None or frame.empty:
            raise AttributionDependencyError(f"missing 沪深300 constituents for {analysis_date}")
        return frame

    def load_industry_classification(self, symbols: list[str], analysis_date: str) -> dict[str, str]:
        mapping: dict[str, str] = {}
        for symbol in symbols:
            frame = self.baostock_importer.query_stock_industry(symbol, analysis_date)
            if frame is None or frame.empty:
                raise AttributionDependencyError(f"missing industry classification for {symbol} at {analysis_date}")
            first_row = frame.iloc[0].to_dict()
            industry = str(first_row.get("industry") or first_row.get("industry_name") or "").strip()
            if not industry:
                raise AttributionDependencyError(f"missing industry classification for {symbol} at {analysis_date}")
            mapping[symbol] = industry
        return mapping

    def load_return_rate(self, symbol: str, start_date: datetime, end_date: datetime) -> float:
        frame, _ = self.data_service.get_daily_ohlcv(symbol=symbol, start_date=start_date, end_date=end_date)
        if frame is None or frame.empty or len(frame.index) < 2:
            raise AttributionDependencyError(f"missing return series for {symbol}")
        start_close = float(frame.iloc[0]["close"])
        end_close = float(frame.iloc[-1]["close"])
        if start_close == 0:
            raise AttributionDependencyError(f"invalid start close for {symbol}")
        return round((end_close - start_close) / start_close, 10)

    def load_factor_exposure_map(self, symbols: list[str], analysis_date: str) -> dict[str, dict[str, float]]:
        """Return a deterministic repo-local factor map for first-batch attribution."""

        return {
            symbol: self._deterministic_factor_exposure(symbol=symbol, analysis_date=analysis_date)
            for symbol in symbols
        }

    def _deterministic_factor_exposure(self, *, symbol: str, analysis_date: str) -> dict[str, float]:
        digest = md5(f"{symbol}:{analysis_date}".encode("utf-8"), usedforsecurity=False).digest()
        scale = [((digest[index] / 255.0) * 2.0) - 1.0 for index in range(5)]
        return {
            "size": round(scale[0], 4),
            "value": round(scale[1], 4),
            "momentum": round(scale[2], 4),
            "volatility": round(scale[3], 4),
            "quality": round(scale[4], 4),
        }


def normalize_baostock_symbol(value: Any) -> str:
    text = str(value).strip().lower()
    if not text:
        raise AttributionDependencyError("empty benchmark symbol")

    if "." in text:
        exchange, raw_code = text.split(".", 1)
        exchange = exchange.upper()
        raw_code = raw_code.upper()
        return f"{raw_code}.{exchange}"

    if text.startswith("sh") or text.startswith("sz"):
        return f"{text[2:].upper()}.{text[:2].upper()}"

    exchange = "SH" if text.startswith(("5", "6", "9")) else "SZ"
    return f"{text.upper()}.{exchange}"
