"""
自动化调度系统 (Automated Scheduling System)

功能说明:
- 定时数据更新和策略执行
- 多任务调度管理
- 任务监控和日志
- 故障重试和通知

使用APScheduler实现灵活的任务调度，支持:
- Cron表达式定时
- 间隔时间调度
- 一次性任务
- 任务链和依赖

作者: MyStocks量化交易团队
创建时间: 2025-10-18
版本: 1.0.0
"""

import sys
import os
import logging
import time
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

    APSCHEDULER_AVAILABLE = True
except ImportError:
    APSCHEDULER_AVAILABLE = False
    print("警告: APScheduler未安装，使用简化版调度器")
    print("安装: pip install apscheduler")


class TaskStatus(Enum):
    """任务状态"""

    PENDING = "pending"  # 等待执行
    RUNNING = "running"  # 执行中
    SUCCESS = "success"  # 成功
    FAILED = "failed"  # 失败
    RETRYING = "retrying"  # 重试中
    CANCELLED = "cancelled"  # 已取消


class TaskPriority(Enum):
    """任务优先级"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class TaskConfig:
    """任务配置"""

    name: str  # 任务名称
    func: Callable  # 任务函数
    trigger_type: str  # 触发器类型 (cron/interval/date)
    trigger_args: Dict[str, Any]  # 触发器参数

    # 可选配置
    priority: TaskPriority = TaskPriority.NORMAL
    max_retries: int = 3  # 最大重试次数
    retry_delay: int = 60  # 重试延迟（秒）
    timeout: int = 3600  # 超时时间（秒）
    enabled: bool = True  # 是否启用

    # 依赖和链式
    depends_on: List[str] = field(default_factory=list)  # 依赖任务
    next_tasks: List[str] = field(default_factory=list)  # 后续任务

    # 通知配置
    notify_on_success: bool = False  # 成功通知
    notify_on_failure: bool = True  # 失败通知

    # 任务参数
    kwargs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskExecution:
    """任务执行记录"""

    task_name: str
    execution_id: str
    status: TaskStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: float = 0.0  # 执行时长（秒）
    retry_count: int = 0
    error_message: Optional[str] = None
    result: Any = None


class JobLock:
    """任务锁 - 防止重叠执行"""

    def __init__(self):
        self._locks: Dict[str, bool] = {}
        self._lock_times: Dict[str, datetime] = {}

    def acquire(self, job_id: str, timeout: int = 3600) -> bool:
        """
        获取任务锁

        参数:
            job_id: 任务ID
            timeout: 锁超时时间（秒）

        返回:
            bool: 是否成功获取锁
        """
        now = datetime.now()

        # 检查是否已锁定
        if job_id in self._locks and self._locks[job_id]:
            # 检查锁是否超时
            lock_time = self._lock_times.get(job_id)
            if lock_time and (now - lock_time).total_seconds() > timeout:
                # 锁超时，强制释放
                self.release(job_id)
                logging.warning(f"任务锁超时，强制释放: {job_id}")
            else:
                return False

        # 获取锁
        self._locks[job_id] = True
        self._lock_times[job_id] = now
        return True

    def release(self, job_id: str):
        """释放任务锁"""
        if job_id in self._locks:
            self._locks[job_id] = False
            self._lock_times.pop(job_id, None)

    def is_locked(self, job_id: str) -> bool:
        """检查任务是否已锁定"""
        return self._locks.get(job_id, False)


class TaskScheduler:
    """
    自动化任务调度器

    功能:
    - 定时任务调度
    - 任务重试逻辑
    - 执行监控和日志
    - 防止重叠执行
    """

    def __init__(self, notification_manager=None, monitoring_db=None):
        """
        初始化调度器

        参数:
            notification_manager: 通知管理器
            monitoring_db: 监控数据库
        """
        self.logger = logging.getLogger(f"{__name__}.TaskScheduler")
        self.logger.setLevel(logging.INFO)

        # 初始化调度器
        if APSCHEDULER_AVAILABLE:
            self.scheduler = BackgroundScheduler()
            self.scheduler.add_listener(self._job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        else:
            self.scheduler = None
            self.logger.warning("APScheduler不可用，使用简化模式")

        # 任务配置和状态
        self.tasks: Dict[str, TaskConfig] = {}
        self.executions: List[TaskExecution] = []
        self.job_lock = JobLock()

        # 外部服务
        self.notification_manager = notification_manager
        self.monitoring_db = monitoring_db

        # 统计信息
        self.stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "total_retries": 0,
        }

    def add_task(self, task_config: TaskConfig) -> str:
        """
        添加定时任务

        参数:
            task_config: 任务配置

        返回:
            str: 任务ID
        """
        if not task_config.enabled:
            self.logger.self.logger.info("info")
            return ""

        # 保存配置
        self.tasks[task_config.name] = task_config

        if not APSCHEDULER_AVAILABLE:
            self.logger.self.logger.warning("warning")
            return task_config.name

        # 创建触发器
        trigger = self._create_trigger(task_config.trigger_type, task_config.trigger_args)

        # 包装任务函数（添加锁和重试逻辑）
        wrapped_func = self._wrap_task_function(task_config)

        # 添加到调度器
        job = self.scheduler.add_job(
            wrapped_func,
            trigger=trigger,
            id=task_config.name,
            name=task_config.name,
            kwargs=task_config.kwargs,
            max_instances=1,  # 防止重叠
        )

        self.logger.self.logger.info("info")
        self.logger.self.logger.info("info")
        self.logger.self.logger.info("info")

        return job.id

    def _create_trigger(self, trigger_type: str, trigger_args: Dict):
        """创建触发器"""
        if trigger_type == "cron":
            return CronTrigger(**trigger_args)
        elif trigger_type == "interval":
            return IntervalTrigger(**trigger_args)
        else:
            raise ValueError(f"不支持的触发器类型: {trigger_type}")

    def _wrap_task_function(self, task_config: TaskConfig) -> Callable:
        """
        包装任务函数，添加锁、重试、监控逻辑
        """

        def wrapped_func(**kwargs):
            execution_id = f"{task_config.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # 尝试获取锁
            if not self.job_lock.acquire(task_config.name, timeout=task_config.timeout):
                self.logger.self.logger.warning("warning")
                return

            # 创建执行记录
            execution = TaskExecution(
                task_name=task_config.name,
                execution_id=execution_id,
                status=TaskStatus.RUNNING,
                start_time=datetime.now(),
            )

            self.logger.self.logger.info("info")

            try:
                # 执行任务（带重试）
                result = self._execute_with_retry(
                    task_config.func,
                    kwargs,
                    max_retries=task_config.max_retries,
                    retry_delay=task_config.retry_delay,
                    execution=execution,
                )

                # 任务成功
                execution.status = TaskStatus.SUCCESS
                execution.result = result
                execution.end_time = datetime.now()
                execution.duration = (execution.end_time - execution.start_time).total_seconds()

                self.stats["successful_executions"] += 1
                self.logger.self.logger.info("info")

                # 成功通知
                if task_config.notify_on_success and self.notification_manager:
                    self.notification_manager.send_success_notification(
                        task_name=task_config.name,
                        execution_time=execution.duration,
                        result=result,
                    )

                # 执行后续任务
                self._trigger_next_tasks(task_config.next_tasks)

            except Exception as e:
                self.logger.error("任务执行异常，已记录")
                execution.status = TaskStatus.FAILED
                execution.error_message = str(e)
                execution.end_time = datetime.now()
                execution.duration = (execution.end_time - execution.start_time).total_seconds()

                self.stats["failed_executions"] += 1
                self.logger.error("error")

                # 失败通知
                if task_config.notify_on_failure and self.notification_manager:
                    self.notification_manager.send_failure_notification(
                        task_name=task_config.name,
                        error_message=str(e),
                        retry_count=execution.retry_count,
                    )

            finally:
                # 释放锁
                self.job_lock.release(task_config.name)

                # 保存执行记录
                self.executions.append(execution)
                self.stats["total_executions"] += 1

                # 记录到监控数据库
                if self.monitoring_db:
                    self._log_to_monitoring(execution)

        return wrapped_func

    def _execute_with_retry(
        self,
        func: Callable,
        kwargs: Dict,
        max_retries: int,
        retry_delay: int,
        execution: TaskExecution,
    ) -> Any:
        """
        执行任务，失败时重试（指数退避）
        """
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                result = func(**kwargs)

                if attempt > 0:
                    self.logger.self.logger.info("info")

                return result

            except Exception as e:
                last_error = e
                execution.retry_count = attempt

                if attempt < max_retries:
                    # 指数退避
                    delay = retry_delay * (2**attempt)
                    execution.status = TaskStatus.RETRYING

                    self.logger.self.logger.warning("warning")
                    self.stats["total_retries"] += 1

                    time.sleep(delay)
                else:
                    # 所有重试都失败
                    self.logger.self.logger.error("error")
                    raise

        raise last_error

    def _trigger_next_tasks(self, next_task_names: List[str]):
        """触发后续任务"""
        for task_name in next_task_names:
            if task_name in self.tasks:
                self.logger.self.logger.info("info")
                task_config = self.tasks[task_name]
                # 立即执行一次
                if self.scheduler:
                    self.scheduler.add_job(
                        task_config.func,
                        "date",
                        run_date=datetime.now() + timedelta(seconds=5),
                        kwargs=task_config.kwargs,
                    )

    def _job_listener(self, event):
        """APScheduler事件监听器"""
        if event.exception:
            self.logger.self.logger.error("error")
        else:
            self.logger.self.logger.debug("debug")

    def _log_to_monitoring(self, execution: TaskExecution):
        """记录到监控数据库"""
        try:
            if self.monitoring_db:
                self.monitoring_db.log_task_execution(
                    task_name=execution.task_name,
                    execution_id=execution.execution_id,
                    status=execution.status.value,
                    start_time=execution.start_time,
                    end_time=execution.end_time,
                    duration=execution.duration,
                    retry_count=execution.retry_count,
                    error_message=execution.error_message,
                )
        except Exception:
            self.logger.self.logger.error("error")

    def start(self):
        """启动调度器"""
        if APSCHEDULER_AVAILABLE and self.scheduler:
            self.scheduler.start()
            self.logger.info("=" * 70)
            self.logger.info("调度器已启动")
            self.logger.self.logger.info("info")
            self.logger.info("=" * 70)
        else:
            self.logger.warning("调度器未启动（APScheduler不可用）")

    def stop(self):
        """停止调度器"""
        if APSCHEDULER_AVAILABLE and self.scheduler:
            self.scheduler.shutdown()
            self.logger.info("调度器已停止")

    def get_task_status(self, task_name: str) -> Optional[TaskStatus]:
        """获取任务状态"""
        # 查找最近一次执行
        for execution in reversed(self.executions):
            if execution.task_name == task_name:
                return execution.status
        return None

    def get_execution_history(self, task_name: Optional[str] = None, limit: int = 100) -> List[TaskExecution]:
        """
        获取执行历史

        参数:
            task_name: 任务名称（可选）
            limit: 返回记录数

        返回:
            List[TaskExecution]: 执行记录列表
        """
        if task_name:
            history = [e for e in self.executions if e.task_name == task_name]
        else:
            history = self.executions

        return sorted(history, key=lambda x: x.start_time, reverse=True)[:limit]

    def get_statistics(self) -> Dict:
        """获取调度器统计信息"""
        return {
            **self.stats,
            "total_tasks": len(self.tasks),
            "active_tasks": sum(1 for t in self.tasks.values() if t.enabled),
            "locked_tasks": sum(1 for locked in self.job_lock._locks.values() if locked),
        }

    def pause_task(self, task_name: str):
        """暂停任务"""
        if APSCHEDULER_AVAILABLE and self.scheduler:
            self.scheduler.pause_job(task_name)
            self.logger.self.logger.info("info")

    def resume_task(self, task_name: str):
        """恢复任务"""
        if APSCHEDULER_AVAILABLE and self.scheduler:
            self.scheduler.resume_job(task_name)
            self.logger.self.logger.info("info")

    def remove_task(self, task_name: str):
        """移除任务"""
        if task_name in self.tasks:
            self.tasks.pop(task_name)

        if APSCHEDULER_AVAILABLE and self.scheduler:
            self.scheduler.remove_job(task_name)
            self.logger.self.logger.info("info")

    def list_tasks(self) -> List[Dict]:
        """列出所有任务"""
        result = []
        for name, config in self.tasks.items():
            status = self.get_task_status(name)

            next_run = None
            if APSCHEDULER_AVAILABLE and self.scheduler:
                job = self.scheduler.get_job(name)
                next_run = job.next_run_time if job else None

            result.append(
                {
                    "name": name,
                    "enabled": config.enabled,
                    "priority": config.priority.name,
                    "trigger_type": config.trigger_type,
                    "status": status.value if status else "unknown",
                    "next_run": next_run,
                }
            )

        return result


if __name__ == "__main__":
    # 测试代码
    print("自动化调度器测试")
    print("=" * 70)

    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # 创建调度器
    scheduler = TaskScheduler()

    # 测试任务函数
    def test_task(task_id: str = "test"):
        print(f"  执行测试任务: {task_id}")
        time.sleep(1)
        return {"task_id": task_id, "result": "success"}

    # 添加任务
    print("\n测试1: 添加间隔任务")
    task_config = TaskConfig(
        name="test_interval_task",
        func=test_task,
        trigger_type="interval",
        trigger_args={"seconds": 10},
        kwargs={"task_id": "interval_test"},
    )

    scheduler.add_task(task_config)

    # 获取任务列表
    print("\n测试2: 查看任务列表")
    tasks = scheduler.list_tasks()
    for task in tasks:
        print(f"  - {task['name']}: {task['status']} (下次: {task['next_run']})")

    # 获取统计
    print("\n测试3: 调度器统计")
    stats = scheduler.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 70)
    print("测试完成")
    print("\n提示: 要启动调度器，调用 scheduler.start()")
    print("      要停止调度器，调用 scheduler.stop()")
