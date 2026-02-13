"""
SSE Market Overview Module

提供上海证券交易所市场总貌数据获取功能
"""

import logging
import akshare as ak
from typing import Dict

from ..base import retry_api_call

logger = logging.getLogger(__name__)


class SSEMarketOverviewAdapter:
    """
    上海证券交易所市场总貌数据适配器

    提供SSE市场总貌数据查询功能
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @retry_api_call(max_retries=3, delay=1)
    async def get_sse_summary(self) -> Dict:
        """
        获取上海证券交易所市场总貌数据

        Returns:
            Dict: SSE市场总貌数据
        """
        try:
            self.logger.info("[Akshare] 开始获取上海证券交易所市场总貌数据...")

            # 调用akshare接口
            df = ak.stock_sse_summary()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到上海证券交易所市场总貌数据")
                return {}

            self.logger.info("[Akshare] 成功获取上海证券交易所市场总貌数据，共 %s 条记录", len(df))

            # 返回标准化的数据
            return {
                "index_code": list(df.get("指数代码", [])),
                "index_name": list(df.get("指数名称", [])),
                "yesterday_close": list(df.get("昨收", [])),
                "today_open": list(df.get("今开", [])),
                "latest_price": list(df.get("最新价", [])),
                "change_percent": list(df.get("涨跌幅", [])),
                "volume": list(df.get("成交量", [])),
                "amount": list(df.get("成交额", [])),
            }

        except Exception:
            self.logger.error("[Akshare] 获取SSE市场总貌数据失败: {str(e)}", exc_info=True)
            return {}


# 导出
__all__ = ["SSEMarketOverviewAdapter"]
