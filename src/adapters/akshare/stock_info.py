# pylint: disable=no-member
"""
AkShare 股票信息模块 — OpenStock 网关外观层.

This is a facade. Internal data fetching is delegated to the OpenStock gateway.
Class name, async method signatures, and column renaming are retained for backward
compatibility.

迁移前: 直接 ak.stock_concept_classify() / ak.stock_board_industry_name_em() /
        ak.stock_info_a_code_name() / ak.stock_sse_index_spot() — 需要 akshare SDK。
迁移后: 通过 OpenStockClient.fetch() 调用 OpenStock 的 STOCK_INDUSTRY / TOPICS_CONCEPTS /
        ALL_STOCKS / INDEX_QUOTES category。OpenStock 后端用 baostock/eltdx failover,
        不再依赖 akshare SDK。SECTOR_QUOTES 上游 akshare 当前不稳定,get_concept_classify
        和 get_industry_classify 暂返回空 DataFrame + warning。

详见: openspec/changes/migrate-data-sources-to-openstock/proposal.md (任务 2.1.1 / 2.1.2)
      docs/reports/openstock-coverage-gaps.md
"""

from __future__ import annotations

import asyncio
import logging
from typing import Optional

import pandas as pd

from .base import BaseAkshareAdapter, retry_api_call
from src.services.openstock import (
    DataCategory,
    OpenStockClient,
    OpenStockError,
)

logger = logging.getLogger(__name__)


def _normalize_symbol_to_baostock(symbol: str) -> str:
    """归一化股票代码到 baostock 风格 sh.600000 / sz.000001."""
    s = str(symbol).replace(".", "").replace("sh", "").replace("sz", "").lower()
    if s.startswith("6"):
        return f"sh.{s}"
    if s.startswith(("0", "3")):
        return f"sz.{s}"
    return symbol


def _normalize_symbol_to_bare(symbol: str) -> str:
    """归一化股票代码到纯数字(eltdx TOPICS_CONCEPTS 要求)."""
    s = str(symbol).replace(".", "").replace("sh", "").replace("sz", "").lower()
    return s


class StockInfoAdapter(BaseAkshareAdapter):
    """股票信息适配器 — OpenStock 网关外观层.

    保留原 StockInfoAdapter 类名、构造签名、所有 async 方法签名。
    内部实现切换为 OpenStockClient + asyncio.to_thread。
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self._client = OpenStockClient()
            self._available = True
        except OpenStockError as exc:
            logger.error("StockInfoAdapter 初始化 OpenStock 客户端失败: %s", exc)
            self._client = None  # type: ignore[assignment]
            self._available = False

    def _close(self) -> None:
        if self._client is not None:
            try:
                self._client.close()
            except Exception:  # noqa: BLE001
                pass

    @retry_api_call(max_retries=3, delay=1)
    async def get_concept_classify(self) -> pd.DataFrame:
        """获取概念分类数据 — OpenStock SECTOR_QUOTES(concept).

        OpenStock 上游 akshare provider 当前不稳定,返回空 DataFrame + warning。
        """
        try:
            logger.info("[OpenStock] 开始获取概念分类数据...")
            if not self._available:
                return pd.DataFrame()

            response = await asyncio.to_thread(
                self._client.fetch,
                DataCategory.SECTOR_QUOTES,
                {"sector_type": "concept"},
            )
            rows = response.get("data") or []
            if not rows:
                logger.warning(
                    "[OpenStock] SECTOR_QUOTES(concept) 返回空,上游 akshare provider 不稳定"
                )
                return pd.DataFrame()

            df = pd.DataFrame(rows)
            df = df.rename(
                columns={
                    "板块代码": "index",
                    "板块名称": "name",
                    "最新价": "latest_price",
                    "涨跌幅": "change_percent",
                    "涨跌额": "change_amount",
                    "成交量": "volume",
                    "成交额": "amount",
                    "总市值": "total_market_value",
                    "换手率": "turnover_rate",
                    "上涨家数": "up_count",
                    "下跌家数": "down_count",
                    "领涨股": "leader_stock",
                }
            )

            if "up_count" in df.columns and "down_count" in df.columns:
                df["stock_count"] = df["up_count"] + df["down_count"]

            self._add_timestamp(df)
            logger.info("[OpenStock] 成功获取概念分类数据,共 %s 条记录", len(df))
            return df

        except OpenStockError as exc:
            logger.warning(
                "[OpenStock] SECTOR_QUOTES(concept) 上游不可用,返回空 DataFrame: %s "
                "(详见 docs/reports/openstock-coverage-gaps.md)", exc,
            )
            return pd.DataFrame()
        except Exception as exc:
            logger.error("[OpenStock] 获取概念分类数据失败: %s", exc, exc_info=True)
            return pd.DataFrame()

    @retry_api_call(max_retries=3, delay=1)
    async def get_industry_classify(self) -> pd.DataFrame:
        """获取行业分类数据 — OpenStock SECTOR_QUOTES(industry).

        OpenStock 上游 akshare provider 当前不稳定,返回空 DataFrame + warning。
        """
        try:
            logger.info("[OpenStock] 开始获取行业分类数据...")
            if not self._available:
                return pd.DataFrame()

            response = await asyncio.to_thread(
                self._client.fetch,
                DataCategory.SECTOR_QUOTES,
                {"sector_type": "industry"},
            )
            rows = response.get("data") or []
            if not rows:
                logger.warning(
                    "[OpenStock] SECTOR_QUOTES(industry) 返回空,上游 akshare provider 不稳定"
                )
                return pd.DataFrame()

            df = pd.DataFrame(rows)
            df = df.rename(
                columns={
                    "板块代码": "index",
                    "板块名称": "name",
                    "最新价": "latest_price",
                    "涨跌幅": "change_percent",
                    "成交量": "volume",
                    "成交额": "amount",
                    "总市值": "total_market_value",
                    "换手率": "turnover_rate",
                    "上涨家数": "up_count",
                    "下跌家数": "down_count",
                }
            )

            if "up_count" in df.columns and "down_count" in df.columns:
                df["stock_count"] = df["up_count"] + df["down_count"]

            self._add_timestamp(df)
            logger.info("[OpenStock] 成功获取行业分类数据,共 %s 条记录", len(df))
            return df

        except OpenStockError as exc:
            logger.warning(
                "[OpenStock] SECTOR_QUOTES(industry) 上游不可用,返回空 DataFrame: %s "
                "(详见 docs/reports/openstock-coverage-gaps.md)", exc,
            )
            return pd.DataFrame()
        except Exception as exc:
            logger.error("[OpenStock] 获取行业分类数据失败: %s", exc, exc_info=True)
            return pd.DataFrame()

    @retry_api_call(max_retries=3, delay=1)
    async def get_stock_info(self, symbol: str) -> Optional[pd.DataFrame]:
        """获取单个股票的基本信息 — OpenStock ALL_STOCKS(客户端过滤)."""
        try:
            logger.info("[OpenStock] 开始获取股票 %s 的信息...", symbol)
            if not self._available:
                return None

            response = await asyncio.to_thread(
                self._client.fetch,
                DataCategory.ALL_STOCKS,
                {},
            )
            rows = response.get("data") or []
            if not rows:
                logger.warning("[OpenStock] ALL_STOCKS 返回空")
                return None

            df = pd.DataFrame(rows)
            # 客户端按 symbol 过滤(支持多种代码格式)
            bare = _normalize_symbol_to_bare(symbol)
            bao = _normalize_symbol_to_baostock(symbol)
            mask = df.apply(
                lambda row: str(row.get("code", "")) == bao
                or str(row.get("symbol", "")) == bao
                or str(row.get("code", "")).replace(".", "").lower().endswith(bare),
                axis=1,
            )
            df = df[mask]

            if df.empty:
                logger.warning("[OpenStock] ALL_STOCKS 未找到股票 %s", symbol)
                return None

            # 标准化列名
            df = df.rename(
                columns={
                    "code": "symbol",
                    "code_name": "stock_name",
                    "name": "stock_name",
                    "list_date": "list_date",
                }
            )

            # industry 字段若 ALL_STOCKS 没有提供,留空
            if "industry" not in df.columns:
                df["industry"] = ""
            if "area" not in df.columns:
                df["area"] = ""

            self._add_timestamp(df)
            logger.info("[OpenStock] 成功获取股票 %s 的信息", symbol)
            return df

        except OpenStockError as exc:
            logger.error(
                "[OpenStock] 获取股票 %s 信息失败: %s", symbol, exc, exc_info=True
            )
            return None
        except Exception as exc:
            logger.error(
                "[OpenStock] 获取股票 %s 信息失败: %s", symbol, exc, exc_info=True
            )
            return None

    @retry_api_call(max_retries=3, delay=1)
    async def get_sse_daily(self, date: str = "") -> pd.DataFrame:
        """获取上海交易所每日概况数据 — OpenStock 暂未提供独立 SSE_DAILY category.

        详见 docs/reports/openstock-coverage-gaps.md。当前返回空 DataFrame + warning,
        待 OpenStock 补齐后切换。
        """
        logger.warning(
            "[OpenStock] SSE_DAILY category 暂未覆盖,返回空 DataFrame "
            "(详见 docs/reports/openstock-coverage-gaps.md)"
        )
        return pd.DataFrame()
