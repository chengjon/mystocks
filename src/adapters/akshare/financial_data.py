"""
AkShare Financial Data Functions — OpenStock 网关外观层.

This is a facade. Internal data fetching is delegated to the OpenStock gateway.
Function names and signatures are retained for backward compatibility.

迁移前: 直接调用 ak.stock_financial_abstract / ak.stock_news_em — 需要 akshare SDK。
迁移后: 通过 OpenStockClient.fetch() 调用 FINANCIAL_DATA / STOCK_NEWS category。
        OpenStock 上游 baostock/akshare failover,不再依赖本地 akshare SDK。

详见: openspec/changes/migrate-data-sources-to-openstock/proposal.md (任务 2.3.1)
      docs/reports/openstock-coverage-gaps.md
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import pandas as pd

from src.services.openstock import (
    DataCategory,
    OpenStockClient,
    OpenStockError,
)

logger = logging.getLogger(__name__)


def _client_or_none():
    """懒初始化 OpenStock 客户端,失败返回 None."""
    try:
        return OpenStockClient()
    except OpenStockError as exc:
        logger.error("financial_data OpenStock 客户端初始化失败: %s", exc)
        return None


def get_financial_data(self, symbol: str, period: str = "annual") -> pd.DataFrame:
    """获取财务数据 — OpenStock FINANCIAL_DATA.

    保留原 (self, symbol, period) 签名,作为 AkshareDataSource 混入方法使用。
    period 参数保留兼容(OpenStock FINANCIAL_DATA 当前返最新快照,不接受 period)。
    """
    try:
        if not symbol:
            return pd.DataFrame()
        client = _client_or_none()
        if client is None:
            return pd.DataFrame()
        try:
            bare = str(symbol).replace(".", "").replace("sh", "").replace("sz", "").lower()
            response = client.fetch(DataCategory.FINANCIAL_DATA, {"symbol": bare})
        finally:
            client.close()

        rows = response.get("data") or []
        if not rows:
            logger.info("[OpenStock] FINANCIAL_DATA 返回空: %s", symbol)
            return pd.DataFrame()

        df = pd.DataFrame(rows)
        # OpenStock 返回字段: code, symbol, time, ipo_date, updated_date,
        # total_shares, float_shares, eps, total_assets, current_assets,
        # net_assets, main_revenue, main_profit, net_profit, bps
        df["query_symbol"] = symbol
        df["query_period"] = period
        df["query_timestamp"] = pd.Timestamp.now()
        return df

    except OpenStockError as exc:
        logger.error("[OpenStock] 获取财务数据失败 %s: %s", symbol, exc)
        return pd.DataFrame()
    except Exception as exc:
        logger.error("获取财务数据失败: %s", exc)
        return pd.DataFrame()


def get_news_data(self, symbol: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
    """获取新闻数据 — OpenStock STOCK_NEWS.

    保留原 (self, symbol, limit) 签名。
    必须提供 symbol(STOCK_NEWS 后端要求);客户端按 symbol 字段二次过滤。
    market-news (symbol=None) OpenStock 暂未覆盖,返空 + warning。
    """
    try:
        if not symbol:
            logger.warning(
                "[OpenStock] STOCK_NEWS 不接受 symbol=None,返空 "
                "(详见 docs/reports/openstock-coverage-gaps.md)",
            )
            return []
        client = _client_or_none()
        if client is None:
            return []
        try:
            params: Dict[str, Any] = {"limit": limit}
            if symbol:
                bare = str(symbol).replace(".", "").replace("sh", "").replace("sz", "").lower()
                params["symbol"] = bare
            response = client.fetch(DataCategory.STOCK_NEWS, params)
        finally:
            client.close()

        rows = response.get("data") or []
        if not rows:
            return []

        # 客户端按 symbol 过滤(STOCK_NEWS 后端可能忽略 symbol 参数)
        if symbol:
            bare = str(symbol).replace(".", "").replace("sh", "").replace("sz", "").lower()
            std_sh = f"sh{bare}"
            std_sz = f"sz{bare}"
            rows = [
                r for r in rows
                if r.get("symbol") in (bare, std_sh, std_sz, symbol)
            ]

        if limit and len(rows) > limit:
            rows = rows[:limit]
        return rows

    except OpenStockError as exc:
        logger.error("[OpenStock] 获取新闻数据失败 %s: %s", symbol, exc)
        return []
    except Exception as exc:
        logger.error("获取新闻数据失败: %s", exc)
        return []


__all__ = ["get_financial_data", "get_news_data"]
