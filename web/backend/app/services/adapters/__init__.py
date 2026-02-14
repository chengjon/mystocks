"""
数据源适配器包 - 从 data_adapter.py 拆分而来

提供统一的数据源适配器接口，集成现有 Data API 到数据源工厂模式。
"""

from .metrics import DataSourceMetrics
from .data_adapter import DataDataSourceAdapter
from .dashboard_adapter import DashboardDataSourceAdapter
from .technical_analysis_adapter import TechnicalAnalysisDataSourceAdapter
from .strategy_adapter import StrategyDataSourceAdapter
from .watchlist_adapter import WatchlistDataSourceAdapter

__all__ = [
    "DataSourceMetrics",
    "DataDataSourceAdapter",
    "DashboardDataSourceAdapter",
    "TechnicalAnalysisDataSourceAdapter",
    "StrategyDataSourceAdapter",
    "WatchlistDataSourceAdapter",
]
