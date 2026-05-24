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
from typing import Any, Optional

from fastapi import Request

from .market_data_service import MarketDataService

logger = logging.getLogger(__name__)

_market_data_service: Optional[MarketDataService] = None
MARKET_DATA_SERVICE_STATE_KEY = "market_data_service"


def get_market_data_service() -> MarketDataService:
    """获取市场数据服务单例"""
    global _market_data_service
    if _market_data_service is None:
        _market_data_service = MarketDataService()
    return _market_data_service


def install_market_data_service(app: Any, service: MarketDataService | None = None) -> MarketDataService:
    """Install the market data service instance on FastAPI app.state."""
    selected_service = service if service is not None else get_market_data_service()
    setattr(app.state, MARKET_DATA_SERVICE_STATE_KEY, selected_service)
    return selected_service


def get_market_data_service_dependency(request: Request) -> MarketDataService:
    """FastAPI dependency provider for the market data service."""
    service = getattr(request.app.state, MARKET_DATA_SERVICE_STATE_KEY, None)
    if service is None:
        service = install_market_data_service(request.app)
    return service
