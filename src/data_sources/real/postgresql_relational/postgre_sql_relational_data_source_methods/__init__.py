"""PostgreSQLRelationalDataSource 方法级拆分包"""
from src.interfaces.relational_data_source import IRelationalDataSource

from .core import PostgreSQLRelationalDataSourceCoreMixin
from .get_stock_basic import PostgreSQLRelationalDataSourceGetStockBasicMixin
from .preferences import PostgreSQLRelationalDataSourcePreferencesMixin


class PostgreSQLRelationalDataSource(
    PostgreSQLRelationalDataSourceCoreMixin,
    PostgreSQLRelationalDataSourceGetStockBasicMixin,
    PostgreSQLRelationalDataSourcePreferencesMixin,
    IRelationalDataSource,
):
    """PostgreSQLRelationalDataSource - 组合所有方法集"""
    pass


__all__ = ["PostgreSQLRelationalDataSource"]
