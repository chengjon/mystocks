"""
技术指标API

提供各种技术指标的计算功能
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

import math
import pandas as pd
from fastapi import APIRouter, Depends, Query
from app.core.exceptions import BusinessException
from pydantic import BaseModel, Field

from app.core.responses import UnifiedResponse
from app.services.data_service import DataService, StockDataNotFoundError, get_data_service
from src.indicators.implementations.momentum.rsi import RSIIndicator
from src.indicators.implementations.trend.ema import EMAIndicator
from src.indicators.implementations.trend.macd import MACDIndicator
from src.indicators.implementations.trend.sma import SMAIndicator

router = APIRouter(
    prefix="/technical-indicators",
    tags=["Technical Indicators"],
)


def get_strategy_indicator_data_service() -> DataService:
    return get_data_service()


TECHNICAL_INDICATORS_SUCCESS_EXAMPLE = {
    "success": True,
    "code": 200,
    "message": "Technical indicators calculated successfully",
    "data": {
        "symbol": "IF9999.CCFX",
        "indicators": {
            "rsi": {"value": 54.21, "signal": "neutral", "period": 14},
            "macd": {"macd": 1.25, "signal_line": 0.88, "histogram": 0.37, "signal": "bullish"},
        },
        "calculated_at": "2026-04-13T08:00:00+00:00",
        "data_points": 180,
        "window_start": "2025-10-16",
        "window_end": "2026-04-13",
    },
}

TECHNICAL_INDICATORS_RESPONSES = {
    200: {
        "description": "技术指标计算结果",
        "content": {
            "application/json": {
                "example": TECHNICAL_INDICATORS_SUCCESS_EXAMPLE,
            }
        },
    }
}

_SUPPORTED_INDICATORS = {"sma", "ema", "rsi", "macd"}


class TechnicalIndicatorResponse(BaseModel):
    """Technical indicator response"""

    symbol: str = Field(..., description="请求指标计算的股票代码。")
    indicators: Dict[str, Any] = Field(..., description="按指标名称组织的计算结果映射。")
    calculated_at: str = Field(..., description="本次指标计算完成时间。")
    data_points: int = Field(..., description="用于本次计算的 OHLCV 数据点数量。")
    window_start: str = Field(..., description="本次计算使用的数据窗口开始日期。")
    window_end: str = Field(..., description="本次计算使用的数据窗口结束日期。")


def _normalize_indicator_names(indicators: List[str]) -> List[str]:
    normalized: List[str] = []
    unsupported: List[str] = []
    for indicator in indicators:
        name = indicator.strip().lower()
        if not name:
            continue
        if name not in _SUPPORTED_INDICATORS:
            unsupported.append(indicator)
            continue
        if name not in normalized:
            normalized.append(name)

    if unsupported:
        supported = ", ".join(sorted(_SUPPORTED_INDICATORS))
        raise BusinessException(
            status_code=400,
            detail=f"Unsupported indicators: {', '.join(unsupported)}. Supported indicators: {supported}",
        )
    if not normalized:
        raise BusinessException(status_code=400, detail="At least one supported indicator is required")
    return normalized


def _coerce_latest(value: Any) -> float | None:
    if isinstance(value, pd.Series):
        value = value.iloc[-1]
    if value is None:
        return None
    numeric = float(value)
    if math.isnan(numeric):
        return None
    return round(numeric, 4)


def _build_signal(indicator: str, latest_close: float, payload: Dict[str, float | None]) -> str:
    if indicator == "rsi":
        value = payload.get("value")
        if value is None:
            return "unknown"
        if value >= 70:
            return "overbought"
        if value <= 30:
            return "oversold"
        return "neutral"

    if indicator in {"sma", "ema"}:
        value = payload.get("value")
        if value is None:
            return "unknown"
        if latest_close > value:
            return "bullish"
        if latest_close < value:
            return "bearish"
        return "neutral"

    if indicator == "macd":
        macd_value = payload.get("macd")
        signal_value = payload.get("signal_line")
        if macd_value is None or signal_value is None:
            return "unknown"
        if macd_value > signal_value:
            return "bullish"
        if macd_value < signal_value:
            return "bearish"
        return "neutral"

    return "unknown"


def _calculate_indicator_payloads(frame: pd.DataFrame, indicators: List[str], period: int) -> Dict[str, Any]:
    latest_close = float(frame["close"].iloc[-1])
    payloads: Dict[str, Any] = {}

    for indicator in indicators:
        if indicator == "sma":
            series = SMAIndicator({"required_columns": ["close"], "parameters": {"period": {"default": period}}}).calculate(
                frame, period=period
            )
            payload = {"value": _coerce_latest(series), "period": period}
        elif indicator == "ema":
            series = EMAIndicator({"required_columns": ["close"], "parameters": {"period": {"default": period}}}).calculate(
                frame, period=period
            )
            payload = {"value": _coerce_latest(series), "period": period}
        elif indicator == "rsi":
            series = RSIIndicator({"required_columns": ["close"], "parameters": {"period": {"default": period}}}).calculate(
                frame, period=period
            )
            payload = {"value": _coerce_latest(series), "period": period}
        elif indicator == "macd":
            result = MACDIndicator({"required_columns": ["close"]}).calculate(frame)
            payload = {
                "macd": _coerce_latest(result["macd"]),
                "signal_line": _coerce_latest(result["signal"]),
                "histogram": _coerce_latest(result["hist"]),
            }
        else:
            continue

        payload["signal"] = _build_signal(indicator, latest_close, payload)
        payloads[indicator] = payload

    return payloads


@router.get(
    "",
    response_model=UnifiedResponse[Dict[str, Any]],
    summary="Get Technical Indicators",
    description="按标的、指标集合和周期参数计算技术指标，当前实现复用后端行情加载与原生指标实现，返回真实计算结果。",
    responses=TECHNICAL_INDICATORS_RESPONSES,
)
async def get_technical_indicators(
    symbol: str = Query(..., description="Stock symbol"),
    indicators: List[str] = Query(..., description="Indicator names (sma,ema,rsi,macd)"),
    period: int = Query(14, ge=2, le=250, description="Calculation period"),
    data_service: DataService = Depends(get_strategy_indicator_data_service),
):
    """
    计算技术指标。

    Loads trailing daily OHLCV data through the runtime DataService and calculates
    supported indicators using the repository's native indicator implementations.
    """
    normalized_indicators = _normalize_indicator_names(indicators)
    lookback_days = max(period * 6, 90)
    end_dt = datetime.now(timezone.utc).replace(tzinfo=None)
    start_dt = end_dt - timedelta(days=lookback_days)

    try:
        frame, _ = data_service.get_daily_ohlcv(symbol=symbol, start_date=start_dt, end_date=end_dt)
    except StockDataNotFoundError as exc:
        raise BusinessException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise BusinessException(status_code=503, detail=f"Unable to load price data for {symbol}: {exc}") from exc

    if frame.empty or "close" not in frame.columns:
        raise BusinessException(status_code=503, detail=f"No OHLCV data available for {symbol}")

    indicator_payloads = _calculate_indicator_payloads(frame, normalized_indicators, period)
    response = TechnicalIndicatorResponse(
        symbol=symbol,
        indicators=indicator_payloads,
        calculated_at=datetime.now(timezone.utc).isoformat(),
        data_points=len(frame),
        window_start=str(frame["trade_date"].min().date()),
        window_end=str(frame["trade_date"].max().date()),
    )
    return UnifiedResponse(
        success=True,
        code=200,
        message="Technical indicators calculated successfully",
        data=response.model_dump(),
    )
