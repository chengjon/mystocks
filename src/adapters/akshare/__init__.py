"""
Market Data Adapter Modules

统一的Akshare市场数据适配器模块
拆分自原market_data.py，按功能组织为多个子模块
"""

# 导出基础工具（从modules目录）
from .modules.base import retry_api_call, ColumnMapper, get_column_mapper

# 导出市场总貌模块
from .market_overview import MarketOverviewAdapter as SSEMarketOverviewAdapter

# 导出个股信息模块
from .stock_info import StockInfoAdapter

# 导出资金流向模块
from .fund_flow import FundFlowAdapter as HSGTFundFlowAdapter

# 导出主数据源类
from .base import AkshareDataSource
from .market_adapter import AkshareMarketDataAdapter

# 导出旧版市场数据函数（如果存在）
try:
    from .legacy_market_data import (
        get_market_overview_sse,
        get_market_overview_szse,
    )
    LEGACY_AVAILABLE = True
except ImportError:
    LEGACY_AVAILABLE = False
    get_market_overview_sse = None
    get_market_overview_szse = None

__all__ = [
    # 基础工具
    "retry_api_call",
    "ColumnMapper",
    "get_column_mapper",
    # 主数据源
    "AkshareDataSource",
    "AkshareMarketDataAdapter",
    # 市场总貌
    "SSEMarketOverviewAdapter",
    # 个股信息
    "StockInfoAdapter",
    # 资金流向
    "HSGTFundFlowAdapter",
    # 旧版函数
    "get_market_overview_sse",
    "get_market_overview_szse",
]

__version__ = "2.0.0"
