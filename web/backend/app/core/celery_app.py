"""
Celery Application Configuration

配置 Celery 异步任务系统
"""

from celery import Celery

from app.core.config import settings

# 创建 Celery 应用
celery_app = Celery(
    "mystocks",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.backtest_tasks"],  # 导入任务模块
)

# Celery 配置
celery_app.conf.update(
    task_track_started=settings.celery_task_track_started,
    task_time_limit=settings.celery_task_time_limit,
    enable_utc=settings.celery_enable_utc,
    timezone=settings.celery_timezone,
    # 任务结果配置
    result_expires=3600,  # 结果保留1小时
    result_persistent=True,
    # 序列化配置
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    # 任务路由配置
    task_routes={
        "app.tasks.backtest_tasks.*": {"queue": "backtest"},
    },
    # Worker 配置
    worker_prefetch_multiplier=1,  # 每次只取一个任务（适合长时间任务）
    worker_max_tasks_per_child=10,  # 每个worker执行10个任务后重启（防止内存泄漏）
)


# 任务进度回调（用于 WebSocket 推送）
task_progress_callbacks = {}


def register_progress_callback(task_id: str, callback):
    """注册任务进度回调"""
    task_progress_callbacks[task_id] = callback


def unregister_progress_callback(task_id: str):
    """注销任务进度回调"""
    if task_id in task_progress_callbacks:
        del task_progress_callbacks[task_id]


def get_progress_callback(task_id: str):
    """获取任务进度回调"""
    return task_progress_callbacks.get(task_id)
