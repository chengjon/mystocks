"""
策略管理监控数据库适配器。
"""

from __future__ import annotations

import structlog

logger = structlog.get_logger(__name__)


class MonitoringAdapter:
    """适配 Week1 API 参数到 `MonitoringDatabase` 接口。"""

    def __init__(self, real_db):
        self.real_db = real_db

    def log_operation(
        self,
        operation_type="UNKNOWN",
        table_name=None,
        operation_name=None,
        rows_affected=0,
        operation_time_ms=0,
        success=True,
        details="",
        **kwargs,
    ):
        try:
            return self.real_db.log_operation(
                operation_type=operation_type,
                classification="DERIVED_DATA",
                target_database="PostgreSQL",
                table_name=table_name,
                record_count=rows_affected,
                operation_status="SUCCESS" if success else "FAILED",
                error_message=None if success else details,
                execution_time_ms=int(operation_time_ms),
                additional_info=(
                    {"operation_name": operation_name, "details": details} if operation_name or details else None
                ),
            )
        except Exception:
            logger.debug("Monitoring log failed (non-critical): %(e)s")
            return False


class MonitoringFallback:
    """监控数据库不可用时的兜底实现。"""

    def log_operation(self, *args, **kwargs):
        logger.debug("Monitoring fallback: operation logged")
        return True
