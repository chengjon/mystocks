"""TDengineTimeSeriesDataSource 方法级拆分包"""
from .part1 import TDengineTimeSeriesDataSourceCoreMixin
from .part2 import TDengineTimeSeriesDataSourceCheckDataQualityMixin


class TDengineTimeSeriesDataSource(
    TDengineTimeSeriesDataSourceCoreMixin,
    TDengineTimeSeriesDataSourceCheckDataQualityMixin,
):
    """TDengineTimeSeriesDataSource - 组合所有方法集"""
    pass


__all__ = ["TDengineTimeSeriesDataSource"]
