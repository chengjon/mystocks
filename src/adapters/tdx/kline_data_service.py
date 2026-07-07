"""
TDX K线数据服务 — OpenStock 网关外观层.

This is a facade. Internal data fetching is delegated to the OpenStock gateway.
Class name (KlineDataService), constructor signature, and all public method
signatures are retained for backward compatibility.

迁移前: 通过 BaseTdxAdapter._get_tdx_connection() 拿到 tdx_api,调用
        tdx_api.get_k_data / get_history_minute_time_data — 依赖原生 TDX 协议。
迁移后: 通过 OpenStockClient.fetch() 调用 KLINES / ADJUSTED_KLINES / INDEX_QUOTES。
        OpenStock 后端用 eltdx/baostock failover,不再依赖本地 TDX 协议栈。

详见: openspec/changes/migrate-data-sources-to-openstock/proposal.md (任务 2.2.3)
      docs/reports/openstock-coverage-gaps.md
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, Optional

import pandas as pd
from loguru import logger

from .base_tdx_adapter import BaseTdxAdapter
from src.services.openstock import (
    DataCategory,
    OpenStockClient,
    OpenStockError,
)


def _normalize_symbol_to_bare(symbol: str) -> str:
    """归一化到纯数字(eltdx 后端要求)."""
    return str(symbol).replace(".", "").replace("sh", "").replace("sz", "").lower()


def _normalize_symbol_to_baostock(symbol: str) -> str:
    """归一化到 baostock 风格 sh.600000 / sz.000001."""
    s = _normalize_symbol_to_bare(symbol)
    if s.startswith("6"):
        return f"sh.{s}"
    if s.startswith(("0", "3")):
        return f"sz.{s}"
    return symbol


# OpenStock period 映射
_PERIOD_OSTOCK = {"d1": "day", "w1": "week", "m1": "month"}
_PERIOD_NAME = {"d1": "日线", "w1": "周线", "m1": "月线"}


class KlineDataService(BaseTdxAdapter):
    """TDX K线数据服务 — OpenStock 网关外观.

    保留类名、构造签名、所有公开方法签名。内部实现切换为 OpenStockClient,
    不再走 pytdx 原生协议。
    """

    def __init__(self):
        super().__init__()
        try:
            self._client = OpenStockClient()
            self._available = True
        except OpenStockError as exc:
            logger.error("KlineDataService OpenStock 初始化失败: %s", exc)
            self._client = None  # type: ignore[assignment]
            self._available = False
        logger.info("KlineDataService(OpenStock facade)初始化完成")

    # ---- 内部辅助 ----------------------------------------------------

    def _normalize_symbol(self, symbol: str) -> str:
        """保留 BaseTdxAdapter 兼容签名,实际归一化到 baostock 风格."""
        return _normalize_symbol_to_baostock(symbol)

    def _get_market_code(self, symbol: str) -> int:
        """保留 BaseTdxAdapter 兼容签名,OpenStock 不需要 market_code."""
        std = _normalize_symbol_to_baostock(symbol)
        return 1 if std.startswith("sh.") else 0

    def _get_tdx_connection(self):  # type: ignore[no-untyped-def]
        """保留 BaseTdxAdapter 兼容签名,facade 模式下不再使用 TDX 连接."""
        return None

    def _validate_kline_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """保留兼容签名,facade 模式下直接返回输入."""
        return df

    def _standardize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """保留兼容签名,facade 模式下直接返回输入."""
        return df

    # ---- K线数据 ----------------------------------------------------

    def get_stock_daily(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        adjust: str = "qfq",
    ) -> pd.DataFrame:
        """获取股票日线数据 — OpenStock KLINES / ADJUSTED_KLINES."""
        try:
            if not symbol:
                raise ValueError("股票代码不能为空")
            if not self._available:
                return pd.DataFrame()

            bare = _normalize_symbol_to_bare(symbol)
            std = _normalize_symbol_to_baostock(symbol)

            if end_date is None:
                end_date = datetime.now().strftime("%Y-%m-%d")
            if start_date is None:
                start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

            logger.info("OpenStock 获取股票日线: %s %s~%s adjust=%s", bare, start_date, end_date, adjust)
            category = (
                DataCategory.ADJUSTED_KLINES if adjust in ("qfq", "hfq")
                else DataCategory.KLINES
            )
            params = {
                "symbol": bare,
                "period": "day",
                "start_date": start_date.replace("-", ""),
                "end_date": end_date.replace("-", ""),
            }
            if category is DataCategory.ADJUSTED_KLINES:
                params["adjust"] = adjust

            response = self._client.fetch(category, params)
            rows = response.get("data") or []
            if not rows:
                return pd.DataFrame()

            df = pd.DataFrame(rows)
            # OpenStock 返回字段: symbol, time, open, high, low, close, volume, amount, period
            # 兼容 date/time 两种命名
            column_map = {
                "time": "datetime",
                "date": "datetime",
            }
            df = df.rename(columns={k: v for k, v in column_map.items() if k in df.columns})
            if "datetime" in df.columns:
                df["datetime"] = pd.to_datetime(df["datetime"]).dt.strftime("%Y-%m-%d")

            df["symbol"] = std
            df["market"] = "上交所" if std.startswith("sh.") else "深交所"
            df["adjust"] = adjust

            logger.info("OpenStock 股票日线 %s: %d 条", std, len(df))
            return df

        except OpenStockError as exc:
            logger.error("OpenStock 获取股票日线失败 %s: %s", symbol, exc)
            return pd.DataFrame()
        except Exception as exc:
            logger.error("获取股票日线数据失败: %s", exc)
            return pd.DataFrame()

    def get_index_daily(
        self,
        index_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """获取指数日线数据 — OpenStock INDEX_QUOTES."""
        try:
            if not index_code:
                raise ValueError("指数代码不能为空")
            if not self._available:
                return pd.DataFrame()

            std = _normalize_symbol_to_baostock(index_code)

            if end_date is None:
                end_date = datetime.now().strftime("%Y-%m-%d")
            if start_date is None:
                start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

            logger.info("OpenStock 获取指数日线: %s %s~%s", std, start_date, end_date)
            response = self._client.fetch(
                DataCategory.INDEX_QUOTES,
                {
                    "symbol": std,
                    "period": "day",
                    "start_date": start_date.replace("-", ""),
                    "end_date": end_date.replace("-", ""),
                },
            )
            rows = response.get("data") or []
            if not rows:
                return pd.DataFrame()

            df = pd.DataFrame(rows)
            column_map = {
                "time": "datetime",
                "date": "datetime",
            }
            df = df.rename(columns={k: v for k, v in column_map.items() if k in df.columns})
            if "datetime" in df.columns:
                df["datetime"] = pd.to_datetime(df["datetime"]).dt.strftime("%Y-%m-%d")

            df["symbol"] = std
            df["security_type"] = "index"

            logger.info("OpenStock 指数日线 %s: %d 条", std, len(df))
            return df

        except OpenStockError as exc:
            logger.error("OpenStock 获取指数日线失败 %s: %s", index_code, exc)
            return pd.DataFrame()
        except Exception as exc:
            logger.error("获取指数日线数据失败: %s", exc)
            return pd.DataFrame()

    def get_stock_kline(
        self,
        symbol: str,
        period: str = "d1",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        adjust: str = "qfq",
    ) -> Dict:
        """获取股票K线数据(多种周期)— OpenStock KLINES / ADJUSTED_KLINES + 客户端重采样."""
        try:
            if period not in _PERIOD_OSTOCK:
                raise ValueError(f"不支持的周期类型: {period}")

            os_period = _PERIOD_OSTOCK[period]
            period_name = _PERIOD_NAME[period]

            if period == "d1":
                df = self.get_stock_daily(symbol, start_date, end_date, adjust)
            else:
                # 周/月线: 拉日线后客户端重采样
                df = self.get_stock_daily(symbol, start_date, end_date, adjust)
                df = self._resample_kline_data(df, period)

            return {
                "symbol": symbol,
                "period": period,
                "period_name": period_name,
                "data": df.to_dict("records") if not df.empty else [],
                "count": len(df) if not df.empty else 0,
                "start_date": (
                    df["datetime"].min() if not df.empty and "datetime" in df.columns else start_date
                ),
                "end_date": (
                    df["datetime"].max() if not df.empty and "datetime" in df.columns else end_date
                ),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as exc:
            logger.error("获取股票K线数据失败: %s", exc)
            return {
                "symbol": symbol,
                "period": period,
                "error": str(exc),
                "success": False,
            }

    def get_index_kline(
        self,
        index_code: str,
        period: str = "d1",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict:
        """获取指数K线数据(多种周期)— OpenStock INDEX_QUOTES + 客户端重采样."""
        try:
            if period not in _PERIOD_OSTOCK:
                raise ValueError(f"不支持的周期类型: {period}")

            period_name = _PERIOD_NAME[period]

            if period == "d1":
                df = self.get_index_daily(index_code, start_date, end_date)
            else:
                df = self.get_index_daily(index_code, start_date, end_date)
                df = self._resample_kline_data(df, period)

            return {
                "index_code": index_code,
                "period": period,
                "period_name": period_name,
                "data": df.to_dict("records") if not df.empty else [],
                "count": len(df) if not df.empty else 0,
                "start_date": (
                    df["datetime"].min() if not df.empty and "datetime" in df.columns else start_date
                ),
                "end_date": (
                    df["datetime"].max() if not df.empty and "datetime" in df.columns else end_date
                ),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as exc:
            logger.error("获取指数K线数据失败: %s", exc)
            return {
                "index_code": index_code,
                "period": period,
                "error": str(exc),
                "success": False,
            }

    def _resample_kline_data(self, df: pd.DataFrame, period: str) -> pd.DataFrame:
        """重新采样K线数据到指定周期."""
        try:
            if df.empty or "datetime" not in df.columns:
                return df

            df = df.copy()
            df["datetime"] = pd.to_datetime(df["datetime"])
            df.set_index("datetime", inplace=True)

            if period == "w1":
                resampled = df.resample("W").agg(
                    {
                        "open": "first",
                        "high": "max",
                        "low": "min",
                        "close": "last",
                        "volume": "sum",
                    }
                )
            elif period == "m1":
                resampled = df.resample("M").agg(
                    {
                        "open": "first",
                        "high": "max",
                        "low": "min",
                        "close": "last",
                        "volume": "sum",
                    }
                )
            else:
                return df.reset_index() if "datetime" not in df.columns else df

            return resampled.reset_index()

        except Exception as exc:
            logger.error("重新采样K线数据失败: %s", exc)
            return pd.DataFrame()

    def get_minute_kline(
        self, symbol: str, period: str = "1min", count: int = 240, adjust: str = "qfq"
    ) -> pd.DataFrame:
        """获取分钟K线数据 — OpenStock 暂未覆盖,返回空 DataFrame + warning.

        详见 docs/reports/openstock-coverage-gaps.md。
        """
        logger.warning(
            "OpenStock 分钟线 OpenStock 暂未覆盖,返回空 DataFrame "
            "(symbol=%s, period=%s, 详见 docs/reports/openstock-coverage-gaps.md)",
            symbol, period,
        )
        return pd.DataFrame()

    # ==================== IDataSource接口补全(保留 no-op 占位) ====================

    def get_stock_basic(self, symbol: str) -> Dict:
        """KlineDataService 专注 K 线数据,不支持股票基本信息."""
        logger.warning("KlineDataService 不支持获取股票基本信息: %s", symbol)
        return {}

    def get_index_components(self, symbol: str) -> list:
        """KlineDataService 专注 K 线数据,不支持指数成分股."""
        logger.warning("KlineDataService 不支持获取指数成分股: %s", symbol)
        return []

    def get_real_time_data(self, symbol: str) -> Optional[Dict]:
        """KlineDataService 专注历史 K 线,不支持实时数据."""
        logger.warning("KlineDataService 不支持获取实时数据: %s", symbol)
        return None

    def get_market_calendar(self, start_date: str, end_date: str) -> pd.DataFrame:
        """KlineDataService 专注 K 线数据,不支持交易日历."""
        logger.warning("KlineDataService 不支持获取交易日历")
        return pd.DataFrame()

    def get_financial_data(self, symbol: str, period: str = "annual") -> pd.DataFrame:
        """KlineDataService 专注 K 线数据,不支持财务数据."""
        logger.warning("KlineDataService 不支持获取财务数据: %s", symbol)
        return pd.DataFrame()

    def get_news_data(self, symbol: Optional[str] = None, limit: int = 10) -> list:
        """KlineDataService 专注 K 线数据,不支持新闻数据."""
        logger.warning("KlineDataService 不支持获取新闻数据")
        return []
