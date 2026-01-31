"""
# 功能：财务适配器主文件（向后兼容）
# 作者：MyStocks Project
# 创建日期：2025-12-20
# 版本：2.0.0（重构版本）
# 说明：本文件提供向后兼容的导入接口，所有实现已拆分到financial/子模块
#
# 重构说明：
#   - 原文件1,148行已拆分为9个子模块
#   - 最大子模块：169行
#   - 主文件：本文件（向后兼容层）
#
# 子模块：
#   - base.py: FinancialDataSource基类、缓存逻辑
#   - stock_daily.py: get_stock_daily()
#   - index_daily.py: get_index_daily()
#   - stock_basic.py: get_stock_basic()
#   - realtime_data.py: get_real_time_data()
#   - index_components.py: get_index_components()
#   - financial_data.py: get_financial_data()
#   - market_calendar.py: get_market_calendar()
#   - news_data.py: get_news_data()
#
# 向后兼容：
#   本文件从financial/__init__.py导入并重新导出FinancialDataSource
#   确保旧代码可以继续使用：from src.adapters.financial_adapter import FinancialDataSource
"""

from __future__ import annotations

import importlib.util
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd

from src.interfaces.data_source import IDataSource
from src.utils import date_utils, symbol_utils

logger = logging.getLogger(__name__)


def _inject_financial_module(module) -> None:
    module.__dict__.setdefault("pd", pd)
    module.__dict__.setdefault("logger", logger)
    module.__dict__.setdefault("symbol_utils", symbol_utils)
    module.__dict__.setdefault("date_utils", date_utils)
    module.__dict__.setdefault("datetime", datetime)
    module.__dict__.setdefault("Any", Any)
    module.__dict__.setdefault("Dict", Dict)
    module.__dict__.setdefault("List", List)
    module.__dict__.setdefault("Optional", Optional)


_FINANCIAL_DIR = os.path.join(os.path.dirname(__file__), "financial")


def _load_financial_module(name: str):
    module_name = f"src.adapters.financial.{name}"
    module_path = os.path.join(_FINANCIAL_DIR, f"{name}.py")
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load financial module: {name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(module_name, module)
    _inject_financial_module(module)
    spec.loader.exec_module(module)
    return module


stock_daily = _load_financial_module("stock_daily")
index_daily = _load_financial_module("index_daily")
stock_basic = _load_financial_module("stock_basic")
index_components = _load_financial_module("index_components")
realtime_data = _load_financial_module("realtime_data")
financial_data = _load_financial_module("financial_data")
market_calendar = _load_financial_module("market_calendar")
news_data = _load_financial_module("news_data")


class FinancialDataSource(IDataSource):
    """
    Legacy FinancialDataSource compatibility layer.

    Keeps the pre-split behavior used by tests and older code paths while the
    modular implementation lives under src.adapters.financial.
    """

    def __init__(self) -> None:
        self.ef = None
        self.eq = None
        self.efinance_available = False
        self.easyquotation_available = False
        self.data_cache: Dict[str, Dict[str, Any]] = {}
        self.logger = logger

        # Best-effort dependency detection; callers/tests may override.
        try:
            import efinance  # noqa: WPS433

            self.ef = efinance
            self.efinance_available = True
        except Exception:
            self.efinance_available = False

        try:
            import easyquotation  # noqa: WPS433

            self.eq = easyquotation
            self.easyquotation_available = True
        except Exception:
            self.easyquotation_available = False

    def _get_cache_key(self, symbol: str, data_type: str, **kwargs: Any) -> str:
        key_parts = [symbol, data_type]
        for key, value in sorted(kwargs.items()):
            key_parts.append(f"{key}={value}")
        return "|".join(key_parts)

    def _save_to_cache(self, cache_key: str, data: Any) -> None:
        self.data_cache[cache_key] = {"data": data, "timestamp": datetime.now()}

    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        cached = self.data_cache.get(cache_key)
        if not cached:
            return None

        timestamp = cached.get("timestamp")
        try:
            if timestamp and datetime.now() - timestamp > timedelta(minutes=5):
                self.data_cache.pop(cache_key, None)
                return None
        except Exception:
            # If timestamp is not comparable, treat as non-expired.
            pass

        return cached.get("data")

    def _validate_and_clean_data(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        if df is None or df.empty:
            return pd.DataFrame()

        cleaned = df.copy()
        cleaned = cleaned.drop_duplicates()

        price_columns = [col for col in ["开盘", "收盘", "最高", "最低", "最新价"] if col in cleaned.columns]
        if price_columns:
            numeric_prices = cleaned[price_columns].apply(pd.to_numeric, errors="coerce")
            mask = (numeric_prices >= 0).all(axis=1)
            cleaned = cleaned[mask]

        if not cleaned.empty:
            numeric_cols = cleaned.select_dtypes(include="number").columns
            if len(numeric_cols) > 0:
                cleaned[numeric_cols] = cleaned[numeric_cols].ffill().bfill().fillna(0)
            text_cols = [col for col in cleaned.columns if col not in numeric_cols]
            if text_cols:
                cleaned[text_cols] = cleaned[text_cols].ffill().bfill().fillna("")

        if "日期" in cleaned.columns:
            try:
                cleaned["日期"] = pd.to_datetime(cleaned["日期"])
                cleaned = cleaned.sort_values("日期")
                cleaned["日期"] = cleaned["日期"].dt.strftime("%Y-%m-%d")
            except Exception:
                cleaned = cleaned.sort_values("日期")

        return cleaned.reset_index(drop=True)

    def _rename_columns(self, data: pd.DataFrame) -> pd.DataFrame:
        column_map = {
            "date": "日期",
            "open": "开盘",
            "close": "收盘",
            "high": "最高",
            "low": "最低",
            "volume": "成交量",
            "amount": "成交额",
        }
        return data.rename(columns=column_map)

    # Bind legacy mixin methods
    get_stock_daily = stock_daily.get_stock_daily
    get_index_daily = index_daily.get_index_daily
    get_stock_basic = stock_basic.get_stock_basic
    get_index_components = index_components.get_index_components
    get_real_time_data = realtime_data.get_real_time_data
    get_financial_data = financial_data.get_financial_data
    get_market_calendar = market_calendar.get_market_calendar
    get_news_data = news_data.get_news_data


__all__ = ["FinancialDataSource"]
