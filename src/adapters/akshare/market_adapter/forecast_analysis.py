"""
AkShare Forecast & Analysis Mixin — OpenStock 网关外观层.

This is a facade. Internal data fetching is delegated to the OpenStock gateway.
Class name (ForecastAnalysisMixin) and all async method signatures are retained
for backward compatibility.

迁移前: 直接调用 ak.stock_profit_forecast_em / stock_profit_forecast_ths /
        stock_technical_indicator_em / stock_account_statistics_em — 需要 akshare SDK。
迁移后: 通过 OpenStockClient.fetch() 调用 FORECAST_DATA / STOCK_TECHNICAL_INDICATOR
        / STOCK_ACCOUNT_STATISTICS category。OpenStock 上游 akshare/baostock failover,
        不再依赖本地 akshare SDK。

详见: openspec/changes/migrate-data-sources-to-openstock/proposal.md (任务 2.3.3)
      docs/reports/openstock-coverage-gaps.md
"""

from __future__ import annotations

import asyncio
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
        logger.error("ForecastAnalysisMixin OpenStock 客户端初始化失败: %s", exc)
        return None


def _bare(symbol: str) -> str:
    return str(symbol).replace(".", "").replace("sh", "").replace("sz", "").lower()


class ForecastAnalysisMixin:
    """预测与技术分析方法集合 — OpenStock 网关外观."""

    async def get_stock_profit_forecast_em(self, symbol: str) -> pd.DataFrame:
        """获取盈利预测(东方财富) — OpenStock FORECAST_DATA(source=em).

        上游 OpenStock FORECAST_DATA 当前返空,返回空 DataFrame + warning。
        """
        try:
            logger.info("[OpenStock] 开始获取盈利预测(em),股票: %s", symbol)
            client = _client_or_none()
            if client is None:
                return pd.DataFrame()
            try:
                response = await asyncio.to_thread(
                    client.fetch,
                    DataCategory.FORECAST_DATA,
                    {"symbol": _bare(symbol), "source": "em"},
                )
            finally:
                client.close()

            rows = response.get("data") or []
            if not rows:
                logger.warning(
                    "[OpenStock] FORECAST_DATA(em) 上游返回空: %s "
                    "(详见 docs/reports/openstock-coverage-gaps.md)", symbol,
                )
                return pd.DataFrame()

            df = pd.DataFrame(rows)
            df = df.rename(
                columns={
                    "股票代码": "symbol",
                    "年度": "year",
                    "季度": "quarter",
                    "预测每股收益": "eps_forecast",
                    "预测净利润": "net_profit_forecast",
                    "预测增长率": "growth_rate_forecast",
                    "分析师数量": "analyst_count",
                    "机构名称": "institution",
                }
            )
            df["forecast_source"] = "em"
            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except OpenStockError as exc:
            logger.error("[OpenStock] 获取盈利预测(em)失败 %s: %s", symbol, exc)
            return pd.DataFrame()
        except Exception as exc:
            logger.error("[OpenStock] 获取盈利预测(em)失败 %s: %s", symbol, exc, exc_info=True)
            return pd.DataFrame()

    async def get_stock_profit_forecast_ths(self, symbol: str) -> pd.DataFrame:
        """获取盈利预测(同花顺) — OpenStock FORECAST_DATA(source=ths).

        上游 OpenStock FORECAST_DATA 当前返空,返回空 DataFrame + warning。
        """
        try:
            logger.info("[OpenStock] 开始获取盈利预测(ths),股票: %s", symbol)
            client = _client_or_none()
            if client is None:
                return pd.DataFrame()
            try:
                response = await asyncio.to_thread(
                    client.fetch,
                    DataCategory.FORECAST_DATA,
                    {"symbol": _bare(symbol), "source": "ths"},
                )
            finally:
                client.close()

            rows = response.get("data") or []
            if not rows:
                logger.warning(
                    "[OpenStock] FORECAST_DATA(ths) 上游返回空: %s "
                    "(详见 docs/reports/openstock-coverage-gaps.md)", symbol,
                )
                return pd.DataFrame()

            df = pd.DataFrame(rows)
            df = df.rename(
                columns={
                    "股票代码": "symbol",
                    "报告日期": "report_date",
                    "预测类型": "forecast_type",
                    "每股收益预测": "eps_forecast",
                    "营收预测": "revenue_forecast",
                    "净利润预测": "net_profit_forecast",
                    "市盈率预测": "pe_forecast",
                    "分析师评级": "analyst_rating",
                }
            )
            df["forecast_source"] = "ths"
            df["query_timestamp"] = pd.Timestamp.now()
            return df

        except OpenStockError as exc:
            logger.error("[OpenStock] 获取盈利预测(ths)失败 %s: %s", symbol, exc)
            return pd.DataFrame()
        except Exception as exc:
            logger.error("[OpenStock] 获取盈利预测(ths)失败 %s: %s", symbol, exc, exc_info=True)
            return pd.DataFrame()

    async def get_stock_technical_indicator_em(self, symbol: str) -> pd.DataFrame:
        """获取技术指标数据 — OpenStock 暂未覆盖,返回空 DataFrame + warning.

        详见 docs/reports/openstock-coverage-gaps.md。
        """
        logger.warning(
            "[OpenStock] stock_technical_indicator OpenStock 暂未覆盖,返回空 DataFrame "
            "(symbol=%s, 详见 docs/reports/openstock-coverage-gaps.md)", symbol,
        )
        return pd.DataFrame()

    async def get_stock_account_statistics_em(self, date: str) -> pd.DataFrame:
        """获取股票账户统计月度 — OpenStock 暂未覆盖,返回空 DataFrame + warning.

        详见 docs/reports/openstock-coverage-gaps.md。
        """
        logger.warning(
            "[OpenStock] stock_account_statistics OpenStock 暂未覆盖,返回空 DataFrame "
            "(date=%s, 详见 docs/reports/openstock-coverage-gaps.md)", date,
        )
        return pd.DataFrame()


__all__ = ["ForecastAnalysisMixin"]
