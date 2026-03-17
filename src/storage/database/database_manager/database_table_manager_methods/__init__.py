"""DatabaseTableManager 方法级拆分包"""
from .part1 import DatabaseTableManagerCoreMixin
from .part2 import DatabaseTableManagerCloseAllConnectionsMixin
from .part3 import DatabaseTableManagerDDLInfoMixin


class DatabaseTableManager(
    DatabaseTableManagerCoreMixin,
    DatabaseTableManagerCloseAllConnectionsMixin,
    DatabaseTableManagerDDLInfoMixin,
):
    """DatabaseTableManager - 组合所有方法集"""
    pass


__all__ = ["DatabaseTableManager"]
