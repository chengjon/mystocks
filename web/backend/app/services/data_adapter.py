"""数据源适配器 - 向后兼容入口

实际实现已拆分至 app.services.adapters 包。
"""

from app.services.adapters import (  # noqa: F401
    DashboardDataSourceAdapter,
    DataDataSourceAdapter,
    DataSourceMetrics,
    StrategyDataSourceAdapter,
    TechnicalAnalysisDataSourceAdapter,
    WatchlistDataSourceAdapter,
)
