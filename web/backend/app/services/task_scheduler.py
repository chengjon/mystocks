"""
任务调度器
基于APScheduler实现定时任务调度
"""

import logging
from typing import Dict, List

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.models.task import TaskConfig, TaskSchedule
from app.services.task_manager import task_manager

logger = logging.getLogger(__name__)


class TaskScheduler:
    """任务调度器"""

    def __init__(self):
        # 配置APScheduler
        jobstores = {"default": MemoryJobStore()}
        executors = {"default": ThreadPoolExecutor(20)}
        job_defaults = {
            "coalesce": True,  # 合并错过的任务
            "max_instances": 3,  # 同一任务最多同时运行3个实例
            "misfire_grace_time": 300,  # 任务错过执行时间后的宽限时间(秒)
        }

        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone="Asia/Shanghai",
        )

        self.scheduled_tasks: Dict[str, str] = {}  # task_id -> job_id mapping
        logger.info("TaskScheduler initialized")

    def start(self):
        """启动调度器"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("TaskScheduler started")

    def shutdown(self, wait: bool = True):
        """关闭调度器"""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=wait)
            logger.info("TaskScheduler shutdown")

    def schedule_task(self, task_config: TaskConfig) -> bool:
        """调度任务"""
        if not task_config.schedule or not task_config.schedule.enabled:
            logger.warning("Task {task_config.task_id} has no schedule or is disabled")
            return False

        try:
            # 移除已存在的调度
            if task_config.task_id in self.scheduled_tasks:
                self.unschedule_task(task_config.task_id)

            # 创建触发器
            trigger = self._create_trigger(task_config.schedule)
            if not trigger:
                logger.error("Failed to create trigger for task {task_config.task_id}")
                return False

            # 添加任务到调度器
            job = self.scheduler.add_job(
                func=self._execute_scheduled_task,
                trigger=trigger,
                args=[task_config.task_id],
                id=task_config.task_id,
                name=task_config.task_name,
                replace_existing=True,
            )

            self.scheduled_tasks[task_config.task_id] = job.id
            logger.info("Task {task_config.task_id} scheduled successfully")
            return True

        except Exception as e:
            logger.error("Failed to schedule task {task_config.task_id}: %(e)s")
            return False

    def unschedule_task(self, task_id: str) -> bool:
        """取消任务调度"""
        try:
            if task_id in self.scheduled_tasks:
                self.scheduler.remove_job(self.scheduled_tasks[task_id])
                del self.scheduled_tasks[task_id]
                logger.info("Task %(task_id)s unscheduled")
                return True
            return False
        except Exception as e:
            logger.error("Failed to unschedule task %(task_id)s: %(e)s")
            return False

    def pause_task(self, task_id: str) -> bool:
        """暂停任务调度"""
        try:
            if task_id in self.scheduled_tasks:
                self.scheduler.pause_job(self.scheduled_tasks[task_id])
                logger.info("Task %(task_id)s paused")
                return True
            return False
        except Exception as e:
            logger.error("Failed to pause task %(task_id)s: %(e)s")
            return False

    def resume_task(self, task_id: str) -> bool:
        """恢复任务调度"""
        try:
            if task_id in self.scheduled_tasks:
                self.scheduler.resume_job(self.scheduled_tasks[task_id])
                logger.info("Task %(task_id)s resumed")
                return True
            return False
        except Exception as e:
            logger.error("Failed to resume task %(task_id)s: %(e)s")
            return False

    def get_scheduled_jobs(self) -> List[Dict]:
        """获取所有已调度的任务"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append(
                {
                    "job_id": job.id,
                    "name": job.name,
                    "next_run_time": (job.next_run_time.isoformat() if job.next_run_time else None),
                    "trigger": str(job.trigger),
                }
            )
        return jobs

    def _create_trigger(self, schedule: TaskSchedule):
        """创建APScheduler触发器"""
        try:
            if schedule.schedule_type == "cron":
                if not schedule.cron_expression:
                    return None
                # 解析cron表达式
                parts = schedule.cron_expression.split()
                if len(parts) != 5:
                    logger.error("Invalid cron expression: {schedule.cron_expression}")
                    return None

                return CronTrigger(
                    minute=parts[0],
                    hour=parts[1],
                    day=parts[2],
                    month=parts[3],
                    day_of_week=parts[4],
                    start_date=schedule.start_time,
                    end_date=schedule.end_time,
                    timezone="Asia/Shanghai",
                )

            elif schedule.schedule_type == "interval":
                if not schedule.interval_seconds:
                    return None
                return IntervalTrigger(
                    seconds=schedule.interval_seconds,
                    start_date=schedule.start_time,
                    end_date=schedule.end_time,
                    timezone="Asia/Shanghai",
                )

            elif schedule.schedule_type == "once":
                if not schedule.start_time:
                    return None
                return DateTrigger(run_date=schedule.start_time, timezone="Asia/Shanghai")

            else:
                logger.error("Unknown schedule type: {schedule.schedule_type}")
                return None

        except Exception as e:
            logger.error("Failed to create trigger: %(e)s")
            return None

    async def _execute_scheduled_task(self, task_id: str):
        """执行调度的任务"""
        logger.info("Executing scheduled task: %(task_id)s")
        try:
            await task_manager.start_task(task_id)
        except Exception as e:
            logger.error("Failed to execute scheduled task %(task_id)s: %(e)s")


# 全局调度器实例
task_scheduler = TaskScheduler()
