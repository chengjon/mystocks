"""
AkShare Market Overview Mixin — OpenStock 网关外观层.

This is a facade. Internal data fetching is delegated to the OpenStock gateway.
Class name, mixin structure, and async method signatures are retained for
backward compatibility.

迁移前: 直接调用 ak.stock_sse_summary / stock_szse_summary / stock_szse_area_summary /
        stock_szse_sector_summary / stock_sse_deal_daily — 需要 akshare SDK。
迁移后: 通过 OpenStockClient.fetch() 调用 INDEX_QUOTES / SECTOR_QUOTES category。
        OpenStock 上游 akshare provider 当前 RemoteDisconnected,SSE/SZSE 详细汇总
        是已登记的上游盲区(详见 docs/reports/openstock-coverage-gaps.md)。Facade
        捕获 OpenStockError 返回空 DataFrame + warning,等上游修复后无感切换。

详见: openspec/changes/migrate-data-sources-to-openstock/proposal.md (任务 2.2.1)
      docs/reports/openstock-coverage-gaps.md
"""

from __future__ import annotations

import logging

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
        logger.error("MarketOverviewMixin OpenStock 客户端初始化失败: %s", exc)
        return None


class MarketOverviewMixin:
    """市场总貌数据方法集合 — OpenStock 网关外观."""

    async def get_market_overview_sse(self) -> pd.DataFrame:
        """获取上海证券交易所市场总貌数据 — OpenStock INDEX_QUOTES + SSE 指数.

        上游 akshare provider 当前 RemoteDisconnected,返回空 DataFrame + warning。
        """
        try:
            logger.info("[OpenStock] 开始获取上证市场总貌...")
            client = _client_or_none()
            if client is None:
                return pd.DataFrame()
            try:
                response = client.fetch(
                    DataCategory.INDEX_QUOTES,
                    {"symbol": "sh.000001"},
                )
            finally:
                client.close()

            rows = response.get("data") or []
            if not rows:
                logger.warning(
                    "[OpenStock] INDEX_QUOTES(sh.000001) 返回空,上游 akshare provider 不稳定"
                )
                return pd.DataFrame()

            df = pd.DataFrame(rows)
            df = df.rename(
                columns={
                    "指数代码": "index_code",
                    "指数名称": "index_name",
                    "昨收": "yesterday_close",
                    "今开": "today_open",
                    "最新价": "latest_price",
                    "涨跌幅": "change_percent",
                    "成交量": "volume",
                    "成交额": "amount",
                }
            )
            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except OpenStockError as exc:
            logger.warning(
                "[OpenStock] SSE 市场总貌上游不可用,返回空 DataFrame: %s "
                "(详见 docs/reports/openstock-coverage-gaps.md)", exc,
            )
            return pd.DataFrame()
        except Exception as exc:
            logger.error(
                "[OpenStock] 获取上证市场总貌失败: %s", exc, exc_info=True
            )
            return pd.DataFrame()

    async def get_market_overview_szse(self, date: str) -> pd.DataFrame:
        """获取深圳证券交易所市场总貌数据 — OpenStock INDEX_QUOTES + 深证成指.

        上游 akshare provider 当前不稳定。date 参数保留(OpenStock 暂未对 INDEX_QUOTES
        强制要求 date),返回最新快照。
        """
        try:
            logger.info("[OpenStock] 开始获取深证市场总貌,日期: %s", date)
            client = _client_or_none()
            if client is None:
                return pd.DataFrame()
            try:
                response = client.fetch(
                    DataCategory.INDEX_QUOTES,
                    {"symbol": "sz.399001"},
                )
            finally:
                client.close()

            rows = response.get("data") or []
            if not rows:
                logger.warning(
                    "[OpenStock] INDEX_QUOTES(sz.399001) 返回空,上游 akshare provider 不稳定"
                )
                return pd.DataFrame()

            df = pd.DataFrame(rows)
            df = df.rename(
                columns={
                    "板块": "sector",
                    "涨跌幅": "change_percent",
                    "总市值": "total_market_value",
                    "平均市盈率": "avg_pe_ratio",
                    "换手率": "turnover_rate",
                    "上涨家数": "up_count",
                    "下跌家数": "down_count",
                }
            )
            df["query_date"] = date
            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except OpenStockError as exc:
            logger.warning(
                "[OpenStock] SZSE 市场总貌上游不可用,返回空 DataFrame: %s "
                "(详见 docs/reports/openstock-coverage-gaps.md)", exc,
            )
            return pd.DataFrame()
        except Exception as exc:
            logger.error(
                "[OpenStock] 获取深证市场总貌失败: %s", exc, exc_info=True
            )
            return pd.DataFrame()

    async def get_szse_area_trading_summary(self, date: str) -> pd.DataFrame:
        """获取深圳地区交易排序数据 — OpenStock 暂未覆盖,返回空 DataFrame + warning.

        详见 docs/reports/openstock-coverage-gaps.md。
        """
        logger.warning(
            "[OpenStock] szse_area_trading OpenStock 暂未覆盖,返回空 DataFrame "
            "(date=%s, 详见 docs/reports/openstock-coverage-gaps.md)", date,
        )
        return pd.DataFrame()

    async def get_szse_sector_trading_summary(self, symbol: str, date: str) -> pd.DataFrame:
        """获取深圳行业成交数据 — OpenStock 暂未覆盖,返回空 DataFrame + warning.

        详见 docs/reports/openstock-coverage-gaps.md。
        """
        logger.warning(
            "[OpenStock] szse_sector_trading OpenStock 暂未覆盖,返回空 DataFrame "
            "(symbol=%s, date=%s, 详见 docs/reports/openstock-coverage-gaps.md)", symbol, date,
        )
        return pd.DataFrame()

    async def get_sse_daily_deal_summary(self, date: str) -> pd.DataFrame:
        """获取上海交易所每日概况数据 — OpenStock 暂未覆盖,返回空 DataFrame + warning.

        详见 docs/reports/openstock-coverage-gaps.md。
        """
        logger.warning(
            "[OpenStock] sse_daily_deal OpenStock 暂未覆盖,返回空 DataFrame "
            "(date=%s, 详见 docs/reports/openstock-coverage-gaps.md)", date,
        )
        return pd.DataFrame()


__all__ = ["MarketOverviewMixin"]
