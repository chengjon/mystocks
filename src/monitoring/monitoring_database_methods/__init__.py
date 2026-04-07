"""MonitoringDatabase 方法级拆分包"""
from .core import MonitoringDatabaseCoreMixin
from .cleanup_old_records import MonitoringDatabaseCleanupOldRecordsMixin
from .history import MonitoringDatabaseHistoryMixin


class MonitoringDatabase(
    MonitoringDatabaseCoreMixin,
    MonitoringDatabaseCleanupOldRecordsMixin,
    MonitoringDatabaseHistoryMixin,
):
    """MonitoringDatabase - 组合所有方法集"""
    pass


__all__ = ["MonitoringDatabase"]
