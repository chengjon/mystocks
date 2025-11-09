"""
任务管理数据模型
定义任务的数据结构和状态
"""

from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class TaskType(str, Enum):
    """任务类型枚举"""

    CRON = "cron"  # 定时任务
    SUPERVISOR = "supervisor"  # 进程管理任务
    MANUAL = "manual"  # 手动任务
    DATA_SYNC = "data_sync"  # 数据同步任务
    INDICATOR_CALC = "indicator_calc"  # 指标计算任务
    MARKET_FETCH = "market_fetch"  # 市场数据获取任务


class TaskStatus(str, Enum):
    """任务状态枚举"""

    PENDING = "pending"  # 待执行
    RUNNING = "running"  # 运行中
    SUCCESS = "success"  # 成功完成
    FAILED = "failed"  # 执行失败
    PAUSED = "paused"  # 已暂停
    CANCELLED = "cancelled"  # 已取消


class TaskPriority(int, Enum):
    """任务优先级"""

    CRITICAL = 100  # 关键任务
    HIGH = 200  # 高优先级
    NORMAL = 500  # 普通优先级
    LOW = 800  # 低优先级
    BATCH = 900  # 批处理任务


class TaskSchedule(BaseModel):
    """任务调度配置"""

    schedule_type: str = Field(..., description="调度类型: cron, interval, once")
    cron_expression: Optional[str] = Field(None, description="Cron表达式")
    interval_seconds: Optional[int] = Field(None, description="执行间隔(秒)")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    enabled: bool = Field(True, description="是否启用")


class TaskConfig(BaseModel):
    """任务配置"""

    task_id: str = Field(..., description="任务ID")
    task_name: str = Field(..., description="任务名称")
    task_type: TaskType = Field(..., description="任务类型")
    task_module: str = Field(..., description="任务模块路径")
    task_function: str = Field(..., description="任务函数名称")
    description: Optional[str] = Field(None, description="任务描述")
    priority: TaskPriority = Field(TaskPriority.NORMAL, description="任务优先级")
    schedule: Optional[TaskSchedule] = Field(None, description="调度配置")
    params: Dict[str, Any] = Field(default_factory=dict, description="任务参数")
    timeout: int = Field(3600, description="超时时间(秒)")
    retry_count: int = Field(0, description="重试次数")
    retry_delay: int = Field(60, description="重试延迟(秒)")
    dependencies: List[str] = Field(default_factory=list, description="依赖任务ID列表")
    tags: List[str] = Field(default_factory=list, description="任务标签")
    auto_restart: bool = Field(False, description="是否自动重启")
    stop_on_error: bool = Field(True, description="错误时停止")


class TaskExecution(BaseModel):
    """任务执行记录"""

    execution_id: str = Field(..., description="执行ID")
    task_id: str = Field(..., description="任务ID")
    status: TaskStatus = Field(TaskStatus.PENDING, description="执行状态")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    duration: Optional[float] = Field(None, description="执行时长(秒)")
    result: Optional[Dict[str, Any]] = Field(None, description="执行结果")
    error_message: Optional[str] = Field(None, description="错误信息")
    log_path: Optional[str] = Field(None, description="日志文件路径")
    retry_count: int = Field(0, description="已重试次数")


class TaskStatistics(BaseModel):
    """任务统计信息"""

    task_id: str
    task_name: str
    total_executions: int = 0
    success_count: int = 0
    failed_count: int = 0
    avg_duration: float = 0.0
    last_execution_time: Optional[datetime] = None
    last_status: Optional[TaskStatus] = None
    success_rate: float = 0.0


class TaskResponse(BaseModel):
    """任务响应模型"""

    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    task_id: Optional[str] = None
    execution_id: Optional[str] = None
