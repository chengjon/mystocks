from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class AlertType(Enum):
    """告警类型。"""

    PERFORMANCE_DEGRADATION = "performance_degradation"
    GPU_MEMORY_HIGH = "gpu_memory_high"
    AI_MODEL_ERROR = "ai_model_error"
    DATA_QUALITY_ISSUE = "data_quality_issue"
    SYSTEM_RESOURCE_HIGH = "system_resource_high"
    STRATEGY_ANOMALY = "strategy_anomaly"
    TRADING_SIGNAL_ABNORMAL = "trading_signal_abnormal"
    SLOW_QUERY = "slow_query"
    CONNECTION_FAILURE = "connection_failure"


class AlertSeverity(Enum):
    """告警严重性。"""

    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


@dataclass
class AlertRule:
    """告警规则。"""

    name: str
    alert_type: AlertType
    severity: AlertSeverity
    threshold: float
    duration_seconds: int
    enabled: bool
    description: str
    custom_conditions: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["alert_type"] = self.alert_type.value
        data["severity"] = self.severity.value
        return data


@dataclass
class Alert:
    """告警实例。"""

    id: str
    rule_name: str
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    timestamp: datetime
    metrics: Dict[str, Any]
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["alert_type"] = self.alert_type.value
        data["severity"] = self.severity.value
        return data


class IAlertHandler(ABC):
    """告警处理器接口。"""

    @abstractmethod
    async def handle_alert(self, alert: Alert) -> bool:
        """处理告警。"""

    @abstractmethod
    async def test_connection(self) -> bool:
        """测试连接。"""


@dataclass
class SystemMetrics:
    """系统指标。"""

    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    gpu_memory_used: float
    gpu_memory_total: float
    gpu_utilization: float
    disk_usage: float
    network_io: Dict[str, float]
    ai_strategy_metrics: Dict[str, Any]
    trading_metrics: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data
