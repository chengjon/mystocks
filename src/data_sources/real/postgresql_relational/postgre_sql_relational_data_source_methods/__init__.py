"""PostgreSQLRelationalDataSource 方法级拆分包"""
from .part1 import PostgreSQLRelationalDataSourceCoreMixin
from .part2 import PostgreSQLRelationalDataSourceGetStockBasicMixin
from .part3 import PostgreSQLRelationalDataSourcePreferencesMixin


class PostgreSQLRelationalDataSource(
    PostgreSQLRelationalDataSourceCoreMixin,
    PostgreSQLRelationalDataSourceGetStockBasicMixin,
    PostgreSQLRelationalDataSourcePreferencesMixin,
):
    """PostgreSQLRelationalDataSource - 组合所有方法集"""
    pass


__all__ = ["PostgreSQLRelationalDataSource"]
