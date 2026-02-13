"""
Fund Flow Module

提供沪深港通资金流向数据获取功能
"""

import logging
import akshare as ak
from typing import Dict

from ..base import retry_api_call

logger = logging.getLogger(__name__)


class HSGTFundFlowAdapter:
    """
    沪深港通资金流向适配器

    提供港通资金汇总、明细和个股统计功能
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @retry_api_call(max_retries=3, delay=1)
    async def get_hsgt_fund_flow_summary(self, start_date: str, end_date: str) -> Dict:
        """
        获取沪深港通资金流向汇总

        Args:
            start_date: 开始日期，格式YYYY-MM-DD
            end_date: 结束日期，格式YYYY-MM-DD

        Returns:
            Dict: 港通资金汇总数据
        """
        try:
            self.logger.info("[Akshare] 开始获取沪深港通资金流向汇总，日期范围: %s 到 %s", start_date, end_date)

            df = ak.stock_hsgt_fund_flow_summary_em()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到沪深港通资金流向汇总")
                return {}

            self.logger.info("[Akshare] 成功获取沪深港通资金流向汇总，共 %s 行", len(df))

            return {"start_date": start_date, "end_date": end_date, "records": len(df)}

        except Exception as e:
            self.logger.error("[Akshare] 获取沪深港通资金流向汇总失败: %s", e)
            return {}


__all__ = ["HSGTFundFlowAdapter"]
