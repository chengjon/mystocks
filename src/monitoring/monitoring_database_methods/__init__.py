"""MonitoringDatabase 方法级拆分包"""
from .part1 import MonitoringDatabaseCoreMixin
from .part2 import MonitoringDatabaseCleanupOldRecordsMixin
from .part3 import MonitoringDatabaseHistoryMixin


class MonitoringDatabase(
    MonitoringDatabaseCoreMixin,
    MonitoringDatabaseCleanupOldRecordsMixin,
    MonitoringDatabaseHistoryMixin,
):
    """MonitoringDatabase - 组合所有方法集"""
    pass


__all__ = ["MonitoringDatabase"]
