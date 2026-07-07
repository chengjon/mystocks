"""
AkShare Market Data Compatibility Layer — OpenStock 网关外观层.

This is a facade. Internal data fetching is delegated to the OpenStock gateway.
Function signatures and module-level exports are retained for backward compatibility.

迁移前: 直接调用 ak.stock_board_concept_name_em() / ak.stock_individual_info_em(symbol)
        — 需要 akshare SDK 与网络代理,长期稳定性差,挂在 FUNCTION_TREE.md ⚠️ 列表。
迁移后: 通过 OpenStockClient.fetch() 调用 OpenStock 的 STOCK_INDUSTRY / TOPICS_CONCEPTS
        category。OpenStock 后端用 baostock/eltdx 自动 failover,不再依赖 akshare SDK。
        SECTOR_QUOTES(concept/industry)目前 OpenStock 上游 akshare provider 不稳定,
        get_concept_classify 暂返回空 DataFrame + warning,等上游修复后切换。

详见: openspec/changes/migrate-data-sources-to-openstock/proposal.md (任务 2.1.1 / 2.1.2)
      docs/reports/openstock-coverage-gaps.md
"""

from __future__ import annotations

import logging
from typing import Any, Dict

import pandas as pd

from src.adapters.akshare.market_adapter import AkshareMarketDataAdapter
from src.services.openstock import (
    DataCategory,
    OpenStockClient,
    OpenStockError,
)

logger = logging.getLogger(__name__)


def _normalize_symbol_to_baostock(symbol: str) -> str:
    """归一化股票代码到 baostock 风格 sh.600000 / sz.000001.

    OpenStock 后端 (baostock/eltdx) 接受 sh.600000 / 600000 / sh600000 等,
    但不接受 <CODE>.SH/.SZ (byapi/Tushare 风格)。
    """
    s = str(symbol).replace(".", "").replace("sh", "").replace("sz", "").lower()
    if s.startswith("6"):
        return f"sh.{s}"
    if s.startswith(("0", "3")):
        return f"sz.{s}"
    return symbol


def _normalize_symbol_to_bare(symbol: str) -> str:
    """归一化股票代码到纯数字 600000 / 000001.

    OpenStock TOPICS_CONCEPTS 后端 (eltdx) 只接受纯数字代码。
    """
    return str(symbol).replace(".", "").replace("sh", "").replace("sz", "").lstrip("0").zfill(6) if str(symbol).replace(".", "").replace("sh", "").replace("sz", "").isdigit() else str(symbol).replace(".", "").replace("sh", "").replace("sz", "").lower()


def get_concept_classify(self=None) -> pd.DataFrame:  # noqa: ARG001
    """获取概念分类数据 — OpenStock SECTOR_QUOTES(concept).

    OpenStock 上游 akshare provider 当前 RemoteDisconnected,返回空 DataFrame + warning。
    待 OpenStock 修复 SECTOR_QUOTES 上游后切换。

    Returns:
        pd.DataFrame: 概念分类数据(空 DataFrame 表示上游不可用)
    """
    try:
        logger.info("[OpenStock] 开始获取概念分类数据...")
        client = OpenStockClient()
        try:
            response = client.fetch(
                DataCategory.SECTOR_QUOTES,
                {"sector_type": "concept"},
            )
        finally:
            client.close()

        rows = response.get("data") or []
        if not rows:
            logger.warning("[OpenStock] SECTOR_QUOTES(concept) 返回空,上游 akshare provider 不稳定")
            return pd.DataFrame()

        df = pd.DataFrame(rows)
        # 字段映射:OpenStock 上游 akshare 板块字段 -> 项目标准字段
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

        logger.info("[OpenStock] 成功获取概念分类数据,共 %s 条记录", len(df))
        return df

    except OpenStockError as exc:
        logger.warning(
            "[OpenStock] SECTOR_QUOTES(concept) 上游不可用,返回空 DataFrame: %s "
            "(详见 docs/reports/openstock-coverage-gaps.md)", exc
        )
        return pd.DataFrame()
    except Exception as exc:
        logger.error("[OpenStock] 获取概念分类数据失败: %s", exc, exc_info=True)
        return pd.DataFrame()


def get_stock_industry_concept(self, symbol: str) -> Dict[str, Any]:  # noqa: ARG001
    """获取个股的行业和概念分类信息 — OpenStock STOCK_INDUSTRY + TOPICS_CONCEPTS.

    Args:
        symbol: 股票代码(支持 600000 / sh.600000 / sh600000 等格式)

    Returns:
        Dict: {symbol, industries: list[str], concepts: list[str]}
    """
    industries: list[str] = []
    concepts: list[str] = []

    try:
        logger.info("[OpenStock] 开始获取个股 %s 的行业和概念信息...", symbol)
        client = OpenStockClient()
        try:
            # STOCK_INDUSTRY 返回全部 A 股列表,客户端按 symbol 过滤
            industry_resp = client.fetch(DataCategory.STOCK_INDUSTRY, {})
            std_symbol = _normalize_symbol_to_baostock(symbol)
            industry_rows = [
                r for r in (industry_resp.get("data") or [])
                if r.get("symbol") == std_symbol or r.get("code") == std_symbol
            ]
            for row in industry_rows:
                industry = str(row.get("industry") or "").strip()
                if industry and industry != "--":
                    # 行业字段形如 "J66货币金融服务" — 保留原文
                    industries.append(industry)

            # TOPICS_CONCEPTS 接受纯数字代码(eltdx 后端要求)
            bare_symbol = _normalize_symbol_to_bare(symbol)
            topics_resp = client.fetch(
                DataCategory.TOPICS_CONCEPTS,
                {"symbol": bare_symbol},
            )
            for row in (topics_resp.get("data") or []):
                topic = str(row.get("topic_name") or "").strip()
                if topic:
                    concepts.append(topic)
        finally:
            client.close()

        logger.info(
            "[OpenStock] 成功获取个股 %s 的信息: industries=%d concepts=%d",
            symbol, len(industries), len(concepts),
        )
        return {
            "symbol": symbol,
            "industries": list(dict.fromkeys(industries)),  # 去重保序
            "concepts": list(dict.fromkeys(concepts)),
        }

    except OpenStockError as exc:
        logger.error(
            "[OpenStock] 获取个股 %s 的行业和概念信息失败: %s", symbol, exc, exc_info=True
        )
        return {"symbol": symbol, "industries": [], "concepts": []}
    except Exception as exc:
        logger.error(
            "[OpenStock] 获取个股 %s 的行业和概念信息失败: %s", symbol, exc, exc_info=True
        )
        return {"symbol": symbol, "industries": [], "concepts": []}


__all__ = [
    "AkshareMarketDataAdapter",
    "get_concept_classify",
    "get_stock_industry_concept",
]
