"""
数据源适配器 - 集成现有 Data API 到数据源工厂模式

Refactored to split logic into multiple modules.
"""

from .data_adapters.base import DataSourceMetrics
from .data_adapters.data_source import DataDataSourceAdapter
from .data_adapters.dashboard import DashboardDataSourceAdapter
from .data_adapters.technical_analysis import TechnicalAnalysisDataSourceAdapter
from .data_adapters.strategy import StrategyDataSourceAdapter
from .data_adapters.watchlist import WatchlistDataSourceAdapter

__all__ = [
    "DataSourceMetrics",
    "DataDataSourceAdapter",
    "DashboardDataSourceAdapter",
    "TechnicalAnalysisDataSourceAdapter",
    "StrategyDataSourceAdapter",
    "WatchlistDataSourceAdapter"
]