"""
Byapi (biyingapi.com) 数据源适配器 — OpenStock 网关外观层.

This is a facade. Internal data fetching is delegated to the OpenStock gateway.
Class name and public method signatures retained for backward compatibility.

迁移前: 直接调用 https://api.biyingapi.com 各端点 (hslt/list, hsstock/history,
        hsrl/ssjy, hsstock/financial 等) — 需要 BYAPI_KEY/LICENCE,403 配额超限,
        长期挂在 FUNCTION_TREE.md 的 ⚠️ 列表。
迁移后: 通过 OpenStockClient.fetch() 调用 OpenStock 的 REALTIME_QUOTES /
        HISTORICAL_KLINES / FINANCIAL_STATEMENTS / ALL_STOCKS 等 category。
        OpenStock 后端用 eltdx/baostock 自动 failover,不再依赖 byapi licence。

详见: openspec/changes/migrate-data-sources-to-openstock/proposal.md (决策 1: Adapter 外观层)
      docs/reports/openstock-coverage-gaps.md
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List

import pandas as pd

from src.services.openstock import (
    DataCategory,
    OpenStockClient,
    OpenStockError,
)

logger = logging.getLogger(__name__)


DEFAULT_BYAPI_LICENCE = "04C01BF1-7F2F-41A3-B470-1F81F14B1FC8"
DEFAULT_BYAPI_BASE_URL = "https://api.biyingapi.com"


class DataSourceError(Exception):
    """数据源异常"""


class IDataSource(ABC):
    """数据源统一接口"""

    @property
    @abstractmethod
    def source_name(self) -> str:
        """数据源名称"""

    @property
    @abstractmethod
    def supported_markets(self) -> List[str]:
        """支持的市场列表"""

    @abstractmethod
    def get_kline_data(self, symbol: str, start_date: str, end_date: str, frequency: str = "daily") -> pd.DataFrame:
        """获取K线数据"""

    @abstractmethod
    def get_realtime_quotes(self, symbols: List[str]) -> pd.DataFrame:
        """获取实时行情"""

    @abstractmethod
    def get_fundamental_data(self, symbol: str, report_period: str, data_type: str = "income") -> pd.DataFrame:
        """获取财务数据"""

    @abstractmethod
    def get_stock_list(self) -> pd.DataFrame:
        """获取股票列表"""


class ByapiAdapter(IDataSource):
    """
    Byapi (biyingapi.com) 数据源适配器 — OpenStock 网关外观.

    保留原 ByapiAdapter 类名、构造签名、所有公开方法签名。内部实现切换为
    OpenStockClient 调用,不再需要 BYAPI_KEY/LICENCE 环境变量。

    Args:
        licence: 保留参数(向后兼容),OpenStock 网关不使用,可忽略
        base_url: 保留参数(向后兼容),OpenStock 网关不使用,可忽略
        min_interval: 保留参数(向后兼容),OpenStock 内部已有 provider failover
    """

    def __init__(
        self,
        licence: str | None = None,
        base_url: str | None = None,
        min_interval: float = 0.2,
    ):
        # 保留向后兼容字段(消费端可能引用)
        self.licence = licence or DEFAULT_BYAPI_LICENCE
        self.base_url = (base_url or DEFAULT_BYAPI_BASE_URL).rstrip("/") if base_url else DEFAULT_BYAPI_BASE_URL
        self.min_interval = min_interval
        self.last_request_time = 0.0

        # 频率映射: IDataSource 标准 -> OpenStock period
        self.frequency_map = {
            "1min": "1",
            "5min": "5",
            "15min": "15",
            "30min": "30",
            "60min": "60",
            "daily": "daily",
            "weekly": "weekly",
            "monthly": "monthly",
            "yearly": "yearly",
        }

        # 财务数据类型映射
        self.fundamental_type_map = {
            "income": "profit",
            "balance": "balance",
            "cashflow": "cashflow",
            "metrics": "metrics",
        }

        # 初始化 OpenStock 客户端
        try:
            self._client = OpenStockClient()
            self.available = True
            logger.info("ByapiAdapter 已切换到 OpenStock 网关")
        except OpenStockError as exc:
            logger.error("ByapiAdapter 初始化失败: %s", exc)
            self._client = None  # type: ignore[assignment]
            self.available = False

    @property
    def source_name(self) -> str:
        return "Byapi"

    @property
    def supported_markets(self) -> List[str]:
        return ["CN_A"]

    def _standardize_symbol(self, symbol: str) -> str:
        """标准化股票代码 — baostock 风格 sh.600000 / sz.000001.

        OpenStock 后端 (baostock/eltdx) 接受 sh.600000 / 600000 / sh600000 等,
        但不接受 <CODE>.SH/.SZ (byapi/Tushare 风格)。本方法归一化为 baostock 风格。
        """
        s = symbol.replace(".", "").replace("sh", "").replace("sz", "").lower()
        if s.startswith("6"):
            return f"sh.{s}"
        if s.startswith(("0", "3")):
            return f"sz.{s}"
        return symbol
        return symbol

    def get_stock_list(self) -> pd.DataFrame:
        """获取股票列表 — 通过 OpenStock ALL_STOCKS."""
        if not self.available:
            return pd.DataFrame()
        try:
            response = self._client.fetch(DataCategory.ALL_STOCKS, {})
            rows = response.get("data") or []
            if not rows:
                return pd.DataFrame()
            df = pd.DataFrame(rows)
            if "symbol" not in df.columns:
                df["symbol"] = df.get("code", "")
            if "name" not in df.columns:
                df["name"] = df.get("stock_name", "")
            if "exchange" not in df.columns:
                df["exchange"] = "UNKNOWN"
            df["list_date"] = pd.NaT
            df["status"] = "ACTIVE"
            return df
        except OpenStockError as exc:
            logger.error("ByapiAdapter.get_stock_list 失败: %s", exc)
            return pd.DataFrame()

    def get_kline_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        frequency: str = "daily",
    ) -> pd.DataFrame:
        """获取K线数据 — 通过 OpenStock HISTORICAL_KLINES."""
        if not self.available:
            return pd.DataFrame()
        try:
            std_symbol = self._standardize_symbol(symbol)
            period = self.frequency_map.get(frequency, "daily")
            category = DataCategory.HISTORICAL_KLINES
            response = self._client.fetch(
                category,
                {
                    "symbol": std_symbol,
                    "start_date": start_date,
                    "end_date": end_date,
                    "period": period,
                },
            )
            rows = response.get("data") or []
            if not rows:
                return pd.DataFrame()
            df = pd.DataFrame(rows)
            df["symbol"] = std_symbol
            return df
        except OpenStockError as exc:
            logger.error("ByapiAdapter.get_kline_data 失败: %s", exc)
            return pd.DataFrame()

    def get_realtime_quotes(self, symbols: List[str]) -> pd.DataFrame:
        """获取实时行情 — 通过 OpenStock REALTIME_QUOTES."""
        if not self.available:
            return pd.DataFrame()
        try:
            std_symbols = [self._standardize_symbol(s) for s in symbols]
            response = self._client.fetch(
                DataCategory.REALTIME_QUOTES,
                {"symbols": ",".join(std_symbols)},
            )
            rows = response.get("data") or []
            if not rows:
                return pd.DataFrame()
            return pd.DataFrame(rows)
        except OpenStockError as exc:
            logger.error("ByapiAdapter.get_realtime_quotes 失败: %s", exc)
            return pd.DataFrame()

    def get_fundamental_data(
        self,
        symbol: str,
        report_period: str,
        data_type: str = "income",
    ) -> pd.DataFrame:
        """获取财务数据 — 通过 OpenStock FINANCIAL_STATEMENTS."""
        if not self.available:
            return pd.DataFrame()
        try:
            std_symbol = self._standardize_symbol(symbol)
            statement_type = self.fundamental_type_map.get(data_type, "profit")
            response = self._client.fetch(
                DataCategory.FINANCIAL_STATEMENTS,
                {
                    "symbol": std_symbol,
                    "statement_type": statement_type,
                    "report_type": "express" if report_period == "latest" else "",
                },
            )
            rows = response.get("data") or []
            if not rows:
                return pd.DataFrame()
            df = pd.DataFrame(rows)
            df["symbol"] = std_symbol
            return df
        except OpenStockError as exc:
            logger.error("ByapiAdapter.get_fundamental_data 失败: %s", exc)
            return pd.DataFrame()

    def get_technical_indicator(
        self,
        symbol: str,
        indicator: str,
        frequency: str = "daily",
        limit: int | None = None,
    ) -> pd.DataFrame:
        """获取技术指标 — OpenStock 暂未覆盖,返回空 DataFrame.

        OpenStock 已覆盖 K 线与实时行情;技术指标(MACD/MA)可由客户端基于 K 线计算,
        或等待 OpenStock 补 TECH_INDICATORS category。详见 docs/reports/openstock-coverage-gaps.md。
        """
        logger.warning("ByapiAdapter.get_technical_indicator: OpenStock 暂未覆盖,返回空 DataFrame")
        return pd.DataFrame()

    def get_limit_up_stocks(self, trade_date: str) -> pd.DataFrame:
        """获取涨停股池 — 通过 OpenStock LIMIT_UP_POOL."""
        if not self.available:
            return pd.DataFrame()
        try:
            response = self._client.fetch(
                DataCategory.LIMIT_UP_POOL,
                {"trade_date": trade_date.replace("-", "")},
            )
            rows = response.get("data") or []
            if not rows:
                return pd.DataFrame()
            df = pd.DataFrame(rows)
            df["trade_date"] = trade_date
            return df
        except OpenStockError as exc:
            logger.error("ByapiAdapter.get_limit_up_stocks 失败: %s", exc)
            return pd.DataFrame()

    def get_limit_down_stocks(self, trade_date: str) -> pd.DataFrame:
        """获取跌停股池 — OpenStock 暂未提供独立 LIMIT_DOWN_POOL category.

        详见 docs/reports/openstock-coverage-gaps.md。当前返回空 DataFrame,
        待 OpenStock 补齐跌停股池 category 后再切换。
        """
        logger.warning(
            "ByapiAdapter.get_limit_down_stocks: OpenStock 暂未提供独立 LIMIT_DOWN_POOL,返回空 DataFrame"
        )
        return pd.DataFrame()

    def close(self):
        """关闭 session(OpenStock httpx.Client 在析构时自动关闭,本方法保留为 no-op)."""
        if self._client is not None:
            try:
                self._client.close()
            except Exception:  # noqa: BLE001
                pass

    def __del__(self):
        try:
            self.close()
        except Exception:  # noqa: BLE001
            pass


# 向后兼容: 别名
ByapiDataSource = ByapiAdapter
