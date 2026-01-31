"""
AkShare Market Data Compatibility Layer

保持旧导入路径，同时保留 AkshareDataSource 的混入函数。
"""

import logging
from typing import Any, Dict

import akshare as ak
import pandas as pd

from src.adapters.akshare.market_adapter import AkshareMarketDataAdapter

logger = logging.getLogger(__name__)


def get_concept_classify(self=None) -> pd.DataFrame:
    """
    获取概念分类数据

    Returns:
        pd.DataFrame: 概念分类数据
    """
    try:
        logger.info("[Akshare] 开始获取概念分类数据...")

        df = ak.stock_board_concept_name_em()

        if df is None or df.empty:
            logger.info("[Akshare] 未能获取到概念分类数据")
            return pd.DataFrame()

        logger.info("[Akshare] 成功获取概念分类数据，共 %s 条记录", len(df))

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

        return df

    except Exception as e:
        logger.error("[Akshare] 获取概念分类数据失败: %s", e, exc_info=True)
        return pd.DataFrame()


def get_stock_industry_concept(self, symbol: str) -> Dict[str, Any]:
    """
    获取个股的行业和概念分类信息

    Args:
        symbol: 股票代码

    Returns:
        Dict: 个股行业和概念信息
    """
    try:
        logger.info("[Akshare] 开始获取个股 %s 的行业和概念信息...", symbol)

        if self is not None and hasattr(self, "_retry_api_call"):

            @self._retry_api_call
            def _get_stock_industry():
                return ak.stock_individual_info_em(symbol=symbol)

            df = _get_stock_industry()
        else:
            df = ak.stock_individual_info_em(symbol=symbol)

        if df is None or df.empty:
            logger.info("[Akshare] 未能获取到个股 %s 的信息", symbol)
            return {"symbol": symbol, "industries": [], "concepts": []}

        logger.info("[Akshare] 成功获取个股 %s 的信息", symbol)

        industries = []
        concepts = []

        for _, row in df.iterrows():
            item = str(row.get("item", ""))
            if "行业" in item or "所属行业" in item:
                industry = str(row.get("value", ""))
                if industry and industry != "--":
                    industries.append(industry)
            elif "概念" in item:
                concept = str(row.get("value", ""))
                if concept:
                    concept_list = [c.strip() for c in str(concept).split(",") if c.strip()]
                    concepts.extend(concept_list)

        return {
            "symbol": symbol,
            "industries": list(set(industries)),
            "concepts": list(set(concepts)),
        }

    except Exception as e:
        logger.error("[Akshare] 获取个股 %s 的行业和概念信息失败: %s", symbol, e, exc_info=True)
        return {"symbol": symbol, "industries": [], "concepts": []}


__all__ = [
    "AkshareMarketDataAdapter",
    "get_concept_classify",
    "get_stock_industry_concept",
]
