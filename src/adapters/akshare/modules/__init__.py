"""
Market Data Adapter - 模块导出

统一导出市场数据适配器的所有模块
"""

# 导出基础工具（从modules.base目录）
from .base import retry_api_call, ColumnMapper, get_column_mapper

# 导出市场总貌模块
from ..market_overview import MarketOverviewAdapter as SSEMarketOverviewAdapter

# 导出个股信息模块
from ..stock_info import StockInfoAdapter

# 导出资金流向模块
from ..fund_flow import FundFlowAdapter as HSGTFundFlowAdapter

# 保持向后兼容：导出原始类（从原market_data.py）
# from src.adapters.akshare.market_data import AkshareMarketDataAdapter as LegacyAkshareMarketDataAdapter
# from src.adapters.akshare.market_data import get_concept_classify

__all__ = [
    # 基础工具
    "retry_api_call",
    "ColumnMapper",
    "get_column_mapper",
    # 市场总貌
    "SSEMarketOverviewAdapter",
    # 个股信息
    "StockInfoAdapter",
    # 资金流向
    "HSGTFundFlowAdapter",
    # 向后兼容（原始接口）
    # "LegacyAkshareMarketDataAdapter",
    # "get_concept_classify",
]

__version__ = "2.0.0"
