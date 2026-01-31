# pylint: disable=all
"""
AkShare适配器模块包

备用实现模块，包含完整的数据适配器类
"""

from .base import (
    _retry_api_call as retry_api_call,
    ColumnMapper,
    get_column_mapper,
)

from .stock_info import StockInfoAdapter
from .fund_flow import FundFlowAdapter
from .market_overview import MarketOverviewAdapter

__all__ = [
    # 基础工具
    "retry_api_call",
    "ColumnMapper",
    "get_column_mapper",
    # 适配器类
    "StockInfoAdapter",
    "FundFlowAdapter",
    "MarketOverviewAdapter",
]

__version__ = "1.0.0"
