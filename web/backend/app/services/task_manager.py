"""
任务管理服务
提供任务调度、执行和监控功能
"""

import asyncio
import concurrent.futures
import json
import logging
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from app.models.task import (
    TaskConfig,
    TaskExecution,
    TaskResponse,
    TaskStatistics,
    TaskStatus,
    TaskType,
)

logger = logging.getLogger(__name__)


class TaskManager:
    """任务管理器核心类"""

    def __init__(self, log_dir: str = "/tmp/mystocks_tasks"):
        self.tasks: Dict[str, TaskConfig] = {}
        self.executions: Dict[str, TaskExecution] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.task_functions: Dict[str, Callable] = {}
        self.statistics: Dict[str, TaskStatistics] = {}
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

        logger.info("TaskManager initialized with log directory: {self.log_dir}")

    def register_task(self, task_config: TaskConfig) -> TaskResponse:
        """注册新任务"""
        try:
            if task_config.task_id in self.tasks:
                return TaskResponse(
                    success=False,
                    message=f"Task {task_config.task_id} already exists",
                    task_id=task_config.task_id,
                )

            self.tasks[task_config.task_id] = task_config

            # 初始化统计信息
            self.statistics[task_config.task_id] = TaskStatistics(
                task_id=task_config.task_id, task_name=task_config.task_name
            )

            logger.info("Task registered: {task_config.task_id} - {task_config.task_name}")

            return TaskResponse(
                success=True,
                message="Task registered successfully",
                task_id=task_config.task_id,
                data=task_config.dict(),
            )
        except Exception as e:
            logger.error("Failed to register task: %(e)s")
            return TaskResponse(success=False, message=f"Failed to register task: {str(e)}")

    def unregister_task(self, task_id: str) -> TaskResponse:
        """注销任务"""
        try:
            if task_id not in self.tasks:
                return TaskResponse(success=False, message=f"Task {task_id} not found")

            # 如果任务正在运行,先停止
            if task_id in self.running_tasks:
                self.stop_task(task_id)

            del self.tasks[task_id]
            if task_id in self.statistics:
                del self.statistics[task_id]

            logger.info("Task unregistered: %(task_id)s")

            return TaskResponse(success=True, message="Task unregistered successfully", task_id=task_id)
        except Exception as e:
            logger.error("Failed to unregister task: %(e)s")
            return TaskResponse(success=False, message=f"Failed to unregister task: {str(e)}")

    def register_function(self, function_name: str, function: Callable):
        """注册任务函数"""
        self.task_functions[function_name] = function
        logger.info("Function registered: %(function_name)s")

    async def execute_task(self, task_id: str, params: Optional[Dict[str, Any]] = None) -> TaskExecution:
        """执行任务"""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")

        task_config = self.tasks[task_id]
        execution_id = str(uuid.uuid4())

        # 创建执行记录
        execution = TaskExecution(
            execution_id=execution_id,
            task_id=task_id,
            status=TaskStatus.RUNNING,
            start_time=datetime.now(),
            log_path=str(self.log_dir / f"{task_id}_{execution_id}.log"),
        )

        self.executions[execution_id] = execution

        logger.info("Starting task execution: %(task_id)s [%(execution_id)s]")

        try:
            # 合并参数
            exec_params = {**task_config.params, **(params or {})}

            # 获取任务函数
            if task_config.task_function in self.task_functions:
                task_func = self.task_functions[task_config.task_function]
            else:
                raise ValueError(f"Task function {task_config.task_function} not registered")

            # 执行任务(在线程池中执行,避免阻塞)
            loop = asyncio.get_event_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(self.executor, task_func, exec_params),
                timeout=task_config.timeout,
            )

            # 更新执行记录
            execution.status = TaskStatus.SUCCESS
            execution.end_time = datetime.now()
            execution.duration = (execution.end_time - execution.start_time).total_seconds()
            execution.result = result if isinstance(result, dict) else {"data": result}

            # 更新统计信息
            self._update_statistics(task_id, execution)

            logger.info("Task completed successfully: %(task_id)s [%(execution_id)s] in {execution.duration}s")

        except asyncio.TimeoutError:
            execution.status = TaskStatus.FAILED
            execution.end_time = datetime.now()
            execution.error_message = f"Task execution timeout after {task_config.timeout}s"
            logger.error("Task timeout: %(task_id)s [%(execution_id)s]")

        except Exception as e:
            execution.status = TaskStatus.FAILED
            execution.end_time = datetime.now()
            execution.error_message = str(e)
            logger.error("Task failed: %(task_id)s [%(execution_id)s] - %(e)s")

            # 检查是否需要重试
            if execution.retry_count < task_config.retry_count:
                execution.retry_count += 1
                logger.info("Retrying task: %(task_id)s (attempt {execution.retry_count}/{task_config.retry_count})")
                await asyncio.sleep(task_config.retry_delay)
                return await self.execute_task(task_id, params)

        finally:
            execution.end_time = execution.end_time or datetime.now()
            self.executions[execution_id] = execution

        return execution

    async def start_task(self, task_id: str, params: Optional[Dict[str, Any]] = None) -> TaskResponse:
        """启动任务(异步)"""
        try:
            if task_id not in self.tasks:
                return TaskResponse(success=False, message=f"Task {task_id} not found")

            if task_id in self.running_tasks:
                return TaskResponse(success=False, message=f"Task {task_id} is already running")

            # 创建异步任务
            task = asyncio.create_task(self.execute_task(task_id, params))
            self.running_tasks[task_id] = task

            return TaskResponse(success=True, message="Task started successfully", task_id=task_id)
        except Exception as e:
            logger.error("Failed to start task: %(e)s")
            return TaskResponse(success=False, message=f"Failed to start task: {str(e)}")

    def stop_task(self, task_id: str) -> TaskResponse:
        """停止任务"""
        try:
            if task_id not in self.running_tasks:
                return TaskResponse(success=False, message=f"Task {task_id} is not running")

            task = self.running_tasks[task_id]
            task.cancel()
            del self.running_tasks[task_id]

            logger.info("Task stopped: %(task_id)s")

            return TaskResponse(success=True, message="Task stopped successfully", task_id=task_id)
        except Exception as e:
            logger.error("Failed to stop task: %(e)s")
            return TaskResponse(success=False, message=f"Failed to stop task: {str(e)}")

    def get_task(self, task_id: str) -> Optional[TaskConfig]:
        """获取任务配置"""
        return self.tasks.get(task_id)

    def list_tasks(self, task_type: Optional[TaskType] = None, tags: Optional[List[str]] = None) -> List[TaskConfig]:
        """列出所有任务"""
        tasks = list(self.tasks.values())

        if task_type:
            tasks = [t for t in tasks if t.task_type == task_type]

        if tags:
            tasks = [t for t in tasks if any(tag in t.tags for tag in tags)]

        return tasks

    def get_execution(self, execution_id: str) -> Optional[TaskExecution]:
        """获取执行记录"""
        return self.executions.get(execution_id)

    def list_executions(self, task_id: Optional[str] = None, limit: int = 100) -> List[TaskExecution]:
        """列出执行记录"""
        executions = list(self.executions.values())

        if task_id:
            executions = [e for e in executions if e.task_id == task_id]

        # 按开始时间倒序排序
        executions.sort(key=lambda x: x.start_time or datetime.min, reverse=True)

        return executions[:limit]

    def get_statistics(self, task_id: Optional[str] = None) -> Dict[str, TaskStatistics]:
        """获取统计信息"""
        if task_id:
            return {task_id: self.statistics.get(task_id)} if task_id in self.statistics else {}
        return self.statistics

    def _update_statistics(self, task_id: str, execution: TaskExecution):
        """更新统计信息"""
        if task_id not in self.statistics:
            self.statistics[task_id] = TaskStatistics(task_id=task_id, task_name=self.tasks[task_id].task_name)

        stats = self.statistics[task_id]
        stats.total_executions += 1

        if execution.status == TaskStatus.SUCCESS:
            stats.success_count += 1
        elif execution.status == TaskStatus.FAILED:
            stats.failed_count += 1

        if execution.duration:
            # 计算平均执行时长
            total_duration = stats.avg_duration * (stats.total_executions - 1) + execution.duration
            stats.avg_duration = total_duration / stats.total_executions

        stats.last_execution_time = execution.end_time
        stats.last_status = execution.status

        if stats.total_executions > 0:
            stats.success_rate = (stats.success_count / stats.total_executions) * 100

    def export_config(self, output_path: str):
        """导出任务配置"""
        config_data = {
            "tasks": [task.dict() for task in self.tasks.values()],
            "export_time": datetime.now().isoformat(),
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False, default=str)

        logger.info("Task configuration exported to %(output_path)s")

    def import_config(self, config_path: str) -> TaskResponse:
        """导入任务配置"""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            imported_count = 0
            for task_data in config_data.get("tasks", []):
                task_config = TaskConfig(**task_data)
                response = self.register_task(task_config)
                if response.success:
                    imported_count += 1

            return TaskResponse(
                success=True,
                message=f"Successfully imported {imported_count} tasks",
                data={"imported_count": imported_count},
            )
        except Exception as e:
            logger.error("Failed to import config: %(e)s")
            return TaskResponse(success=False, message=f"Failed to import config: {str(e)}")

    def cleanup_old_executions(self, days: int = 7):
        """清理旧的执行记录"""
        cutoff_time = datetime.now() - timedelta(days=days)
        old_executions = [
            exec_id
            for exec_id, execution in self.executions.items()
            if execution.end_time and execution.end_time < cutoff_time
        ]

        for exec_id in old_executions:
            del self.executions[exec_id]

        logger.info("Cleaned up {len(old_executions)} old execution records")
        return len(old_executions)


# 全局任务管理器实例
task_manager = TaskManager()
