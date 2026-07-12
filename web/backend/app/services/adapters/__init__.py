"""数据源适配器包 - 从 data_adapter.py 拆分而来

提供统一的数据源适配器接口，集成现有 Data API 到数据源工厂模式。
"""

from .dashboard_adapter import DashboardDataSourceAdapter
from .data_adapter import DataDataSourceAdapter
from .metrics import DataSourceMetrics
from .strategy_adapter import StrategyDataSourceAdapter
from .technical_analysis_adapter import TechnicalAnalysisDataSourceAdapter
from .watchlist_adapter import WatchlistDataSourceAdapter


__all__ = [
    "DashboardDataSourceAdapter",
    "DataDataSourceAdapter",
    "DataSourceMetrics",
    "StrategyDataSourceAdapter",
    "TechnicalAnalysisDataSourceAdapter",
    "WatchlistDataSourceAdapter",
]
