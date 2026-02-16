"""MonitoringDatabase - 向后兼容入口"""
from .monitoring_database_methods import MonitoringDatabase  # noqa: F401

# Global singleton instance
_monitoring_database_instance = None


def get_monitoring_database() -> MonitoringDatabase:
    """获取监控数据库实例（单例模式）"""
    global _monitoring_database_instance
    if _monitoring_database_instance is None:
        _monitoring_database_instance = MonitoringDatabase()
    return _monitoring_database_instance
