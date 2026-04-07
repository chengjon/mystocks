"""DatabaseTableManager 方法级拆分包"""
from .core import DatabaseTableManagerCoreMixin
from .close_all_connections import DatabaseTableManagerCloseAllConnectionsMixin
from .ddl_info import DatabaseTableManagerDDLInfoMixin


class DatabaseTableManager(
    DatabaseTableManagerCoreMixin,
    DatabaseTableManagerCloseAllConnectionsMixin,
    DatabaseTableManagerDDLInfoMixin,
):
    """DatabaseTableManager - 组合所有方法集"""
    pass


__all__ = ["DatabaseTableManager"]
