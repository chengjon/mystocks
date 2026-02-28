"""
资源调度器
Resource Scheduler
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict


logger = logging.getLogger(__name__)

class TaskPriority(Enum):
    """任务优先级"""

    CRITICAL = 1  # 紧急任务
    HIGH = 2  # 高优先级任务
    MEDIUM = 3  # 中等优先级任务
    LOW = 4  # 低优先级任务
    BATCH = 5  # 批处理任务


class TaskStatus(Enum):
    """任务状态"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class TaskType(Enum):
    """任务类型"""

    BACKTEST = "backtest"
    REALTIME = "realtime"
    ML_TRAINING = "ml_training"
    OPTIMIZATION = "optimization"
    RISK_CONTROL = "risk_control"
    HIGH_FREQUENCY = "high_frequency"


class Task:
    """任务类"""

    def __init__(
        self,
        task_id: str,
        task_type: TaskType,
        priority: TaskPriority,
        required_memory: int = 0,
        required_gpu: bool = True,
        task_data: Dict[str, Any] = None,
    ):
        self.task_id = task_id
        self.task_type = task_type
        self.priority = priority
        self.required_memory = required_memory
        self.required_gpu = required_gpu
        self.task_data = task_data or {}
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.gpu_id = None
        self.retry_count = 0
        self.max_retries = 3
        self.timeout = 3600  # 默认1小时超时
        self.result = None
        self.error_message = None

    def __lt__(self, other):
        """用于优先级队列排序"""
        return self.priority.value < other.priority.value

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type.value,
            "priority": self.priority.name,
            "required_memory": self.required_memory,
            "required_gpu": self.required_gpu,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "gpu_id": self.gpu_id,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
            "result": self.result,
            "error_message": self.error_message,
        }


