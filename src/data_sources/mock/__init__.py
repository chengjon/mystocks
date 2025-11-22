"""
Mock数据源模块

提供所有数据源接口的Mock实现，用于开发和测试。

核心组件:
- MockTimeSeriesDataSource: 时序数据Mock
- MockRelationalDataSource: 关系数据Mock (待实现)
- MockBusinessDataSource: 业务数据Mock (待实现)

使用示例:
    from src.data_sources.mock import MockTimeSeriesDataSource

    # 创建Mock数据源
    mock_source = MockTimeSeriesDataSource(seed=42)  # 固定种子便于测试

    # 获取实时行情
    quotes = mock_source.get_realtime_quotes(symbols=["600000", "000001"])

版本: 1.0.0
"""

from src.data_sources.mock.timeseries_mock import MockTimeSeriesDataSource
from src.data_sources.mock.relational_mock import MockRelationalDataSource
from src.data_sources.mock.business_mock import MockBusinessDataSource

__all__ = [
    "MockTimeSeriesDataSource",
    "MockRelationalDataSource",
    "MockBusinessDataSource"
]

__version__ = "1.0.0"
