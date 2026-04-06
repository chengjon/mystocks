"""
市场数据服务 (MarketDataService)

业务逻辑层,负责:
1. 数据获取: 调用adapters获取外部数据
2. 数据存储: 保存到PostgreSQL+TimescaleDB
3. 数据查询: 从数据库读取历史数据
4. 数据刷新: 定时更新最新数据

复用组件:
- akshare_extension: ETF/资金流向/龙虎榜数据
- tqlex_adapter: 竞价抢筹数据
"""

import logging
from typing import Optional


from .market_data_service import MarketDataService

logger = logging.getLogger(__name__)

_market_data_service: Optional[MarketDataService] = None

def get_market_data_service() -> MarketDataService:
    """获取市场数据服务单例"""
    global _market_data_service
    if _market_data_service is None:
        _market_data_service = MarketDataService()
    return _market_data_service


