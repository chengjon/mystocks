"""TDengineTimeSeriesDataSource 方法级拆分包"""
from src.interfaces.timeseries_data_source import ITimeSeriesDataSource

from .core import TDengineTimeSeriesDataSourceCoreMixin
from .check_data_quality import TDengineTimeSeriesDataSourceCheckDataQualityMixin


class TDengineTimeSeriesDataSource(
    TDengineTimeSeriesDataSourceCoreMixin,
    TDengineTimeSeriesDataSourceCheckDataQualityMixin,
    ITimeSeriesDataSource,
):
    """TDengineTimeSeriesDataSource - 组合所有方法集"""
    pass


__all__ = ["TDengineTimeSeriesDataSource"]
