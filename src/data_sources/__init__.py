"""
Data Sources Module

数据源模块，提供统一的数据源管理和访问接口。

核心组件:
- DataSourceFactory: 数据源工厂，负责创建和管理数据源实例
- TdxBinaryParser: 通达信二进制数据解析器
- Mock数据源: 开发和测试使用的模拟数据源
- 真实数据源: TDengine、PostgreSQL等生产数据源

使用示例:
    from src.data_sources import get_timeseries_source, get_relational_source

    # 获取时序数据源（根据环境变量自动选择）
    ts_source = get_timeseries_source()
    quotes = ts_source.get_realtime_quotes(symbols=["600000"])

    # 获取关系数据源
    rel_source = get_relational_source()
    watchlist = rel_source.get_watchlist(user_id=1)

版本: 1.0.0
"""

# 数据源工厂
from src.data_sources.factory import (
    DataSourceFactory,
    get_timeseries_source,
    get_relational_source,
    get_business_source,
    DataSourceFactoryException,
    UnsupportedDataSourceType,
    DataSourceNotRegistered
)

# 数据解析器
from .tdx_binary_parser import TdxBinaryParser

__all__ = [
    # 工厂类和便捷函数
    "DataSourceFactory",
    "get_timeseries_source",
    "get_relational_source",
    "get_business_source",

    # 异常类
    "DataSourceFactoryException",
    "UnsupportedDataSourceType",
    "DataSourceNotRegistered",

    # 数据解析器
    "TdxBinaryParser"
]

__version__ = "1.0.0"
