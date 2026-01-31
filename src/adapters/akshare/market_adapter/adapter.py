"""
AkShare Market Data Adapter (Facade)

聚合拆分后的市场数据方法实现。
"""

import logging

from .board_sector import BoardSectorMixin
from .forecast_analysis import ForecastAnalysisMixin
from .fund_flow import FundFlowMixin
from .market_overview import MarketOverviewMixin
from .stock_profile import StockProfileMixin
from .stock_sentiment import StockSentimentMixin


class AkshareMarketDataAdapter(
    MarketOverviewMixin,
    StockProfileMixin,
    StockSentimentMixin,
    FundFlowMixin,
    ForecastAnalysisMixin,
    BoardSectorMixin,
):
    """AkShare市场数据适配器（拆分后的聚合入口）"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def _retry_api_call(func, max_retries: int = 3, delay: int = 1):
        """API调用重试装饰器（异步）"""
        import asyncio
        from functools import wraps

        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay * (2**attempt))
                        continue
            raise last_exception

        return wrapper


__all__ = ["AkshareMarketDataAdapter"]
