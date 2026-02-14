"""PostgreSQLRelationalDataSource 方法级拆分包"""
from .part1 import PostgreSQLRelationalDataSourceCoreMixin
from .part2 import PostgreSQLRelationalDataSourceGetStockBasicMixin


class PostgreSQLRelationalDataSource(
    PostgreSQLRelationalDataSourceCoreMixin,
    PostgreSQLRelationalDataSourceGetStockBasicMixin,
):
    """PostgreSQLRelationalDataSource - 组合所有方法集"""
    pass


__all__ = ["PostgreSQLRelationalDataSource"]
