"""EfinanceDataSource 方法级拆分包"""
from .core import EfinanceDataSourceCoreMixin
from .get_bond_basic import EfinanceDataSourceGetBondBasicMixin
from .bond_quote import EfinanceDataSourceBondQuoteMixin


class EfinanceDataSource(
    EfinanceDataSourceCoreMixin,
    EfinanceDataSourceGetBondBasicMixin,
    EfinanceDataSourceBondQuoteMixin,
):
    """EfinanceDataSource - 组合所有方法集"""
    pass


__all__ = ["EfinanceDataSource"]
