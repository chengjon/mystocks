from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


@dataclass
class OperationMetrics:
    """操作指标数据类"""

    operation_id: str
    table_name: str
    database_type: str
    database_name: str
    operation_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    status: str = "processing"
    data_count: int = 0
    error_message: Optional[str] = None

    def mark_completed(self, data_count: int = 0) -> None:
        """标记操作完成"""
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()
        self.status = "success"
        self.data_count = data_count

    def mark_failed(self, error_message: str) -> None:
        """标记操作失败"""
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()
        self.status = "failed"
        self.error_message = error_message


class AlertLevel(Enum):
    """告警级别"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Alert:
    """告警数据类"""

    alert_id: str
    level: AlertLevel
    title: str
    message: str
    source: str
    timestamp: datetime
    resolved: bool = False
    resolve_time: Optional[datetime] = None


__all__ = ["OperationMetrics", "AlertLevel", "Alert"]
