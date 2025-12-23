"""
数据源接口定义
避免循环依赖
"""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict


class HealthStatusEnum(str, Enum):
    """健康状态枚举"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"


class DataSourceStatus(str, Enum):
    """数据源状态枚举"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    DISABLED = "disabled"


class HealthStatus:
    """健康状态数据类"""

    def __init__(
        self,
        status: HealthStatusEnum,
        response_time: float,
        message: str,
        timestamp: datetime,
    ):
        self.status = status
        self.response_time = response_time
        self.message = message
        self.timestamp = timestamp


class IDataSource(ABC):
    """数据源接口"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.type = config.get("type", "unknown")

    @abstractmethod
    async def get_data(
        self, endpoint: str, params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """获取数据"""
        pass

    @abstractmethod
    async def health_check(self) -> HealthStatus:
        """健康检查"""
        pass

    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        pass
