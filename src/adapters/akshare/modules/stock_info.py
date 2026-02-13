"""
Stock Info Module

提供个股信息查询功能
"""

import logging
import akshare as ak
from typing import Dict

from ..base import retry_api_call

logger = logging.getLogger(__name__)


class StockInfoAdapter:
    """
    个股信息查询适配器

    提供股票基本信息、财务信息、评级信息等查询功能
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @staticmethod
    @retry_api_call(max_retries=3, delay=1)
    async def get_stock_industry_concept(symbol: str) -> Dict[str, list]:
        """
        获取个股行业和概念信息

        Args:
            symbol: 股票代码

        Returns:
            Dict: 包含industries和concepts列表的字典
        """
        try:
            logger.info("[Akshare] 开始获取个股行业和概念信息，股票: %(symbol)s")

            df = ak.stock_individual_info_em(symbol=symbol)

            if df is None or df.empty:
                logger.warning("[Akshare] 未能获取到个股信息，股票: %(symbol)s")
                return {"symbol": symbol, "industries": [], "concepts": []}

            logger.info("[Akshare] 成功获取个股信息，股票: %(symbol)s")

            # 提取行业和概念信息
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

        except Exception:
            logger.error("[Akshare] 获取个股信息失败，股票: %(symbol)s: %s")
            return {"symbol": symbol, "industries": [], "concepts": []}


__all__ = ["StockInfoAdapter"]
