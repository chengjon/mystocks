"""
BaoStock 数据源适配器 — OpenStock 网关外观层.

This is a facade. Internal data fetching is delegated to the OpenStock gateway.
Class name and public method signatures retained for backward compatibility.

迁移前: import baostock as bs; bs.login(); bs.query_history_k_data_plus(...) — 受
        baostock SDK 网络稳定性限制,登录态管理复杂,长期挂在 FUNCTION_TREE.md。
迁移后: 通过 OpenStockClient.fetch() 调用 OpenStock 的 HISTORICAL_KLINES /
        INDEX_KLINES / STOCK_BASIC / INDEX_CONSTITUENTS / TRADE_DATES /
        FINANCIAL_STATEMENTS / REALTIME_QUOTES / STOCK_NEWS 等 category。
        OpenStock 后端用 baostock/eltdx 自动 failover,无需 SDK login/logout。

详见: openspec/changes/migrate-data-sources-to-openstock/proposal.md (决策 1: Adapter 外观层)
      docs/reports/openstock-coverage-gaps.md
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Union

import pandas as pd

from src.interfaces.refactored_interfaces import IDataSource
from src.services.openstock import (
    DataCategory,
    OpenStockClient,
    OpenStockError,
)

logger = logging.getLogger(__name__)


class BaostockDataSource(IDataSource):
    """BaoStock 数据源实现 — OpenStock 网关外观.

    保留原 BaostockDataSource 类名与方法签名。内部实现切换为 OpenStockClient 调用,
    不再 import baostock SDK,不再需要 bs.login()/bs.logout() 配对。
    """

    def __init__(self) -> None:
        # OpenStock 网关已封装 baostock/eltdx/akshare 多 provider failover,
        # 本类只需读取 OPENSTOCK_BASE_URL + OPENSTOCK_API_KEY。
        try:
            self._client = OpenStockClient()
            self.available = True
            logger.info("BaostockDataSource 已切换到 OpenStock 网关")
        except OpenStockError as exc:
            logger.error("BaostockDataSource 初始化失败: %s", exc)
            self._client = None  # type: ignore[assignment]
            self.available = False

    def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取股票日线数据 — 通过 OpenStock HISTORICAL_KLINES."""
        if not self.available:
            return pd.DataFrame()
        try:
            response = self._client.fetch(
                DataCategory.HISTORICAL_KLINES,
                {
                    "symbol": self._format_symbol(symbol),
                    "start_date": start_date,
                    "end_date": end_date,
                    "period": "daily",
                },
            )
            return self._to_dataframe(response)
        except OpenStockError as exc:
            logger.error("BaostockDataSource.get_stock_daily 失败: %s", exc)
            return pd.DataFrame()

    def get_index_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取指数日线数据 — 通过 OpenStock INDEX_KLINES."""
        if not self.available:
            return pd.DataFrame()
        try:
            response = self._client.fetch(
                DataCategory.INDEX_KLINES,
                {
                    "symbol": self._format_index(symbol),
                    "start_date": start_date,
                    "end_date": end_date,
                    "period": "daily",
                },
            )
            return self._to_dataframe(response)
        except OpenStockError as exc:
            logger.error("BaostockDataSource.get_index_daily 失败: %s", exc)
            return pd.DataFrame()

    def get_stock_basic(self, symbol: str) -> Dict[str, Any]:
        """获取股票基本信息 — 通过 OpenStock STOCK_BASIC."""
        if not self.available:
            return {}
        try:
            response = self._client.fetch(
                DataCategory.STOCK_BASIC,
                {"symbol": self._format_symbol(symbol)},
            )
            rows = response.get("data") or []
            if not rows:
                return {}
            return dict(rows[0])
        except OpenStockError as exc:
            logger.error("BaostockDataSource.get_stock_basic 失败: %s", exc)
            return {}

    def get_index_components(self, symbol: str) -> List[str]:
        """获取指数成分股 — 通过 OpenStock INDEX_CONSTITUENTS."""
        if not self.available:
            return []
        try:
            response = self._client.fetch(
                DataCategory.INDEX_CONSTITUENTS,
                {"index_code": self._format_index(symbol)},
            )
            rows = response.get("data") or []
            return [str(row.get("symbol") or row.get("code") or "") for row in rows if row]
        except OpenStockError as exc:
            logger.error("BaostockDataSource.get_index_components 失败: %s", exc)
            return []

    def get_real_time_data(self, symbol: str) -> Union[Dict[str, Any], str]:
        """获取实时数据 — 通过 OpenStock REALTIME_QUOTES."""
        if not self.available:
            return {"error": "OpenStock client not available"}
        try:
            response = self._client.fetch(
                DataCategory.REALTIME_QUOTES,
                {"symbol": symbol},
            )
            rows = response.get("data") or []
            if not rows:
                return {"error": "no realtime data"}
            return dict(rows[0])
        except OpenStockError as exc:
            return {"error": str(exc)}

    def get_market_calendar(self, start_date: str, end_date: str) -> Union[pd.DataFrame, str]:
        """获取交易日历 — 通过 OpenStock TRADE_DATES."""
        if not self.available:
            return pd.DataFrame()
        try:
            response = self._client.fetch(
                DataCategory.TRADE_DATES,
                {
                    "start_date": start_date,
                    "end_date": end_date,
                },
            )
            return self._to_dataframe(response)
        except OpenStockError as exc:
            logger.error("BaostockDataSource.get_market_calendar 失败: %s", exc)
            return pd.DataFrame()

    def get_financial_data(self, symbol: str, period: str = "annual") -> Union[pd.DataFrame, str]:
        """获取财务数据 — 通过 OpenStock FINANCIAL_STATEMENTS."""
        if not self.available:
            return pd.DataFrame()
        try:
            response = self._client.fetch(
                DataCategory.FINANCIAL_STATEMENTS,
                {
                    "symbol": self._format_symbol(symbol),
                    "statement_type": "profit",
                    "report_type": "express" if period != "annual" else "",
                },
            )
            return self._to_dataframe(response)
        except OpenStockError as exc:
            logger.error("BaostockDataSource.get_financial_data 失败: %s", exc)
            return pd.DataFrame()

    def get_news_data(self, symbol: str = None, limit: int = 10) -> Union[List[Dict[str, Any]], str]:
        """获取新闻数据 — 通过 OpenStock STOCK_NEWS."""
        if not self.available:
            return []
        try:
            params: Dict[str, Any] = {"limit": limit}
            if symbol:
                params["symbol"] = symbol
            response = self._client.fetch(DataCategory.STOCK_NEWS, params)
            return list(response.get("data") or [])
        except OpenStockError as exc:
            logger.error("BaostockDataSource.get_news_data 失败: %s", exc)
            return []

    @staticmethod
    def _format_symbol(symbol: str) -> str:
        """格式化股票代码 — baostock 风格 sh.600000 / sz.000001.

        OpenStock 接受 sz000001 / sh600000 / 000001 等多种格式,本方法保留原 baostock
        约定,OpenStock 后端兼容。
        """
        symbol = symbol.replace(".", "").replace("sh", "").replace("sz", "")
        if symbol.startswith("6"):
            return f"sh.{symbol}"
        if symbol.startswith("0") or symbol.startswith("3"):
            return f"sz.{symbol}"
        return symbol

    @staticmethod
    def _format_index(symbol: str) -> str:
        """格式化指数代码 — baostock 风格 sh.000001 / sz.399001."""
        symbol = symbol.replace(".", "").replace("sh", "").replace("sz", "")
        if symbol.startswith("000"):
            return f"sh.{symbol}"
        if symbol.startswith("399"):
            return f"sz.{symbol}"
        return symbol

    @staticmethod
    def _to_dataframe(response: Dict[str, Any]) -> pd.DataFrame:
        """OpenStock 响应统一转 DataFrame."""
        rows = response.get("data") or []
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame(rows)
