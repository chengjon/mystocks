"""
自动化调度系统 (Automation and Scheduling System)

提供量化交易系统的自动化任务调度功能:
- 定时数据更新
- 策略自动执行
- 交易信号通知
- 任务监控和日志

主要组件:
- TaskScheduler: 任务调度器
- NotificationManager: 通知管理器
- PredefinedTasks: 预定义任务

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0
"""

from .scheduler import (
    TaskScheduler,
    TaskConfig,
    TaskStatus,
    TaskPriority,
    TaskExecution,
    JobLock,
)

from .notification_manager import (
    NotificationManager,
    NotificationConfig,
    NotificationChannel,
    NotificationLevel,
    Notification,
)

__all__ = [
    # Scheduler
    "TaskScheduler",
    "TaskConfig",
    "TaskStatus",
    "TaskPriority",
    "TaskExecution",
    "JobLock",
    # Notification
    "NotificationManager",
    "NotificationConfig",
    "NotificationChannel",
    "NotificationLevel",
    "Notification",
]

__version__ = "1.0.0"
