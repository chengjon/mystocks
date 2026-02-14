"""EfinanceDataSource 方法级拆分包"""
from .part1 import EfinanceDataSourceCoreMixin
from .part2 import EfinanceDataSourceGetBondBasicMixin


class EfinanceDataSource(
    EfinanceDataSourceCoreMixin,
    EfinanceDataSourceGetBondBasicMixin,
):
    """EfinanceDataSource - 组合所有方法集"""
    pass


__all__ = ["EfinanceDataSource"]
