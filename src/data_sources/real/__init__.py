"""
真实数据源实现模块

提供所有数据源接口的生产级真实实现。

核心组件:
- TDengineTimeSeriesDataSource: TDengine时序数据源
- PostgreSQLRelationalDataSource: PostgreSQL关系数据源
- CompositeBusinessDataSource: 复合业务数据源（整合TDengine + PostgreSQL）

使用示例:
    from src.data_sources.real import (
        TDengineTimeSeriesDataSource,
        PostgreSQLRelationalDataSource,
        CompositeBusinessDataSource
    )

    # 创建TDengine数据源
    td_source = TDengineTimeSeriesDataSource()

    # 获取实时行情
    quotes = td_source.get_realtime_quotes(symbols=["600000", "000001"])

    # 创建PostgreSQL数据源
    pg_source = PostgreSQLRelationalDataSource()

    # 获取自选股
    watchlist = pg_source.get_watchlist(user_id=1001)

    # 创建复合业务数据源
    biz_source = CompositeBusinessDataSource()

    # 获取仪表盘汇总
    dashboard = biz_source.get_dashboard_summary(user_id=1001)

版本: 2.0.0
"""

from src.data_sources.real.tdengine_timeseries import TDengineTimeSeriesDataSource
from src.data_sources.real.postgresql_relational import PostgreSQLRelationalDataSource
from src.data_sources.real.composite_business import CompositeBusinessDataSource

__all__ = [
    "TDengineTimeSeriesDataSource",
    "PostgreSQLRelationalDataSource",
    "CompositeBusinessDataSource",
]

__version__ = "2.0.0"
