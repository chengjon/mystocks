#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试自动化编排

提供智能化的测试执行编排、依赖管理、执行策略和资源调度功能。
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from tests.orchestration._orchestration_tail import (
    OrchestrationManager as OrchestrationManagerHelper,
    demo_orchestration as demo_orchestration_helper,
)

logger = logging.getLogger(__name__)


class ExecutionStrategy(Enum):
    """执行策略枚举"""

    SEQUENTIAL = "sequential"  # 顺序执行
    PARALLEL = "parallel"  # 并行执行
    ADAPTIVE = "adaptive"  # 自适应执行
    PIPELINE = "pipeline"  # 管道执行
    DISTRIBUTED = "distributed"  # 分布式执行


class TaskPriority(Enum):
    """任务优先级枚举"""

    CRITICAL = 1  # 关键任务
    HIGH = 2  # 高优先级
    NORMAL = 3  # 普通优先级
    LOW = 4  # 低优先级
    BACKGROUND = 5  # 后台任务


@dataclass
class TestTask:
    """测试任务定义"""

    id: str
    name: str
    description: str
    test_type: str  # unit, integration, e2e, performance, ai, security, chaos
    priority: TaskPriority
    dependencies: List[str] = field(default_factory=list)
    timeout: int = 300  # 秒
    retry_count: int = 3
    retry_delay: float = 1.0
    tags: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    execution_mode: ExecutionStrategy = ExecutionStrategy.SEQUENTIAL

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "test_type": self.test_type,
            "priority": self.priority.value,
            "dependencies": self.dependencies,
            "timeout": self.timeout,
            "retry_count": self.retry_count,
            "retry_delay": self.retry_delay,
            "tags": self.tags,
            "config": self.config,
            "execution_mode": self.execution_mode.value,
        }


@dataclass
class TestExecution:
    """测试执行记录"""

    task_id: str
    task_name: str
    status: str  # pending, running, completed, failed, skipped
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: float = 0.0
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    resources_used: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "task_name": self.task_name,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "result": self.result,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "resources_used": self.resources_used,
            "metrics": self.metrics,
        }


@dataclass
class OrchestrationConfig:
    """编排配置"""

    max_concurrent_tasks: int = 5
    task_timeout: int = 600
    enable_retry: bool = True
    enable_parallel: bool = True
    enable_monitoring: bool = True
    enable_metrics: bool = True
    enable_resource_scaling: bool = False
    checkpoint_enabled: bool = True
    checkpoint_interval: int = 300  # 5分钟
    log_level: str = "INFO"


class DependencyResolver:
    """依赖关系解析器"""

    def __init__(self):
        self.tasks: Dict[str, TestTask] = {}
        self.execution_order: List[List[str]] = []

    def add_task(self, task: TestTask):
        """添加任务"""
        self.tasks[task.id] = task

    def resolve_dependencies(self) -> List[List[str]]:
        """解析依赖关系并返回执行顺序"""
        self.execution_order = []

        # 构建依赖图
        dependency_graph = {}
        all_tasks = set(self.tasks.keys())

        for task_id, task in self.tasks.items():
            dependencies = set(task.dependencies)
            dependent_tasks = set()

            # 查找依赖此任务的其他任务
            for other_id, other_task in self.tasks.items():
                if task_id in other_task.dependencies:
                    dependent_tasks.add(other_id)

            dependency_graph[task_id] = {
                "dependencies": dependencies,
                "dependents": dependent_tasks,
            }

        # 拓扑排序
        in_degree = {
            task_id: len(dep_graph[task_id]["dependencies"]) for task_id, dep_graph in dependency_graph.items()
        }

        # 找出所有没有依赖的任务
        queue = [task_id for task_id, degree in in_degree.items() if degree == 0]
        execution_levels = []

        while queue:
            # 当前层的任务
            current_level = []
            for _ in range(len(queue)):
                task_id = queue.pop(0)
                current_level.append(task_id)

                # 更新依赖此任务的任务的入度
                for dependent in dependency_graph[task_id]["dependents"]:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)

            if current_level:
                execution_levels.append(current_level)

        self.execution_order = execution_levels
        return execution_levels

    def get_execution_plan(self) -> Dict[str, Any]:
        """获取执行计划"""
        return {
            "total_tasks": len(self.tasks),
            "execution_levels": self.execution_order,
            "task_count_by_level": [len(level) for level in self.execution_order],
            "critical_path": self._find_critical_path(),
            "parallel_groups": len(self.execution_order),
            "estimated_duration": self._estimate_total_duration(),
        }

    def _find_critical_path(self) -> List[str]:
        """查找关键路径"""
        critical_path = []
        max_duration = 0

        for task in self.tasks.values():
            path_duration = 0
            current_task = task

            # 向上遍历依赖链
            while current_task:
                path_duration += current_task.timeout
                if current_task.dependencies:
                    # 选择执行时间最长的依赖
                    dependency_durations = []
                    for dep_id in current_task.dependencies:
                        if dep_id in self.tasks:
                            dep_task = self.tasks[dep_id]
                            dependency_durations.append(dep_task.timeout + self._get_dependency_duration(dep_task))
                    if dependency_durations:
                        path_duration += max(dependency_durations)
                    break
                else:
                    break

                # 更新当前任务
                if current_task.dependencies:
                    # 选择执行时间最长的依赖
                    max_dep_duration = 0
                    max_dep_task = None
                    for dep_id in current_task.dependencies:
                        if dep_id in self.tasks:
                            dep_task = self.tasks[dep_id]
                            if dep_task.timeout > max_dep_duration:
                                max_dep_duration = dep_task.timeout
                                max_dep_task = dep_task
                    current_task = max_dep_task if max_dep_task else None
                else:
                    current_task = None

            if path_duration > max_duration:
                max_duration = path_duration
                critical_path = [task.id]

        return critical_path

    def _get_dependency_duration(self, task: TestTask) -> int:
        """获取任务依赖的执行时间"""
        if not task.dependencies:
            return 0

        max_dep_duration = 0
        for dep_id in task.dependencies:
            if dep_id in self.tasks:
                dep_task = self.tasks[dep_id]
                dep_duration = dep_task.timeout + self._get_dependency_duration(dep_task)
                if dep_duration > max_dep_duration:
                    max_dep_duration = dep_duration

        return max_dep_duration

    def _estimate_total_duration(self) -> int:
        """估计总执行时间"""
        total_duration = 0

        for level in self.execution_order:
            # 同一层的任务并行执行，取最长时间
            level_max_duration = 0
            for task_id in level:
                if task_id in self.tasks:
                    task = self.tasks[task_id]
                    level_max_duration = max(level_max_duration, task.timeout)
            total_duration += level_max_duration

        return total_duration


class TaskExecutor:
    """任务执行器"""

    def __init__(self, config: OrchestrationConfig):
        self.config = config
        self.active_executions: Dict[str, TestExecution] = {}
        self.completed_executions: Dict[str, TestExecution] = {}
        self.resource_monitor = ResourceMonitor()

    async def execute_task(self, task: TestTask) -> TestExecution:
        """执行单个任务"""
        execution = TestExecution(task_id=task.id, task_name=task.name, status="running")

        self.active_executions[task.id] = execution

        try:
            # 开始执行
            execution.start_time = datetime.now()
            logger.info("开始执行任务: {task.name} ({task.id})")

            # 监控资源使用
            resource_task = asyncio.create_task(self.resource_monitor.monitor_resources(task.id, task.timeout))

            # 执行任务
            if task.execution_mode == ExecutionStrategy.SEQUENTIAL:
                result = await self._execute_sequential(task)
            elif task.execution_mode == ExecutionStrategy.PARALLEL:
                result = await self._execute_parallel(task)
            elif task.execution_mode == ExecutionStrategy.ADAPTIVE:
                result = await self._execute_adaptive(task)
            else:
                # 默认执行
                result = await self._execute_default(task)

            # 停止资源监控
            resource_task.cancel()
            try:
                await resource_task
            except asyncio.CancelledError:
                pass

            # 设置执行结果
            execution.end_time = datetime.now()
            execution.duration = (execution.end_time - execution.start_time).total_seconds()
            execution.status = "completed"
            execution.result = result
            execution.metrics = {
                "execution_time": execution.duration,
                "memory_usage": self.resource_monitor.get_memory_usage(task.id),
                "cpu_usage": self.resource_monitor.get_cpu_usage(task.id),
            }

            logger.info("任务执行完成: {task.name} ({execution.duration:.2f}秒)")

        except Exception as e:
            # 处理异常
            execution.end_time = datetime.now()
            execution.duration = (execution.end_time - execution.start_time).total_seconds()
            execution.status = "failed"
            execution.error_message = str(e)

            logger.error("任务执行失败: {task.name} - {str(e)}")

        finally:
            # 从活动执行中移除
            self.active_executions.pop(task.id, None)
            self.completed_executions[task.id] = execution

        return execution

    async def _execute_sequential(self, task: TestTask) -> Dict[str, Any]:
        """顺序执行任务"""
        # 模拟任务执行
        await asyncio.sleep(min(task.timeout, 10))  # 最多等待10秒

        return {
            "status": "success",
            "task_id": task.id,
            "executed_at": datetime.now().isoformat(),
            "data": {"message": f"Sequential task {task.name} completed"},
        }

    async def _execute_parallel(self, task: TestTask) -> Dict[str, Any]:
        """并行执行任务"""
        # 创建子任务
        subtasks = []
        for i in range(min(3, task.config.get("subtask_count", 3))):
            subtask = asyncio.create_task(self._execute_subtask(f"{task.id}_{i}"))
            subtasks.append(subtask)

        # 等待所有子任务完成
        results = await asyncio.gather(*subtasks, return_exceptions=True)

        return {
            "status": "success",
            "task_id": task.id,
            "subtasks": len(subtasks),
            "results": results,
        }

    async def _execute_adaptive(self, task: TestTask) -> Dict[str, Any]:
        """自适应执行任务"""
        # 根据系统负载动态调整执行策略
        system_load = self.resource_monitor.get_system_load()

        if system_load < 0.5:
            # 负载低，使用并行策略
            return await self._execute_parallel(task)
        else:
            # 负载高，使用顺序策略
            return await self._execute_sequential(task)

    async def _execute_default(self, task: TestTask) -> Dict[str, Any]:
        """默认执行策略"""
        await asyncio.sleep(min(task.timeout, 5))
        return {
            "status": "success",
            "task_id": task.id,
            "message": f"Task {task.name} completed",
        }

    async def _execute_subtask(self, subtask_id: str) -> Dict[str, Any]:
        """执行子任务"""
        await asyncio.sleep(random.uniform(1, 3))
        return {
            "subtask_id": subtask_id,
            "status": "completed",
            "result": f"Subtask {subtask_id} done",
        }

    async def execute_with_retry(self, task: TestTask) -> TestExecution:
        """带重试的任务执行"""
        last_error = None

        for attempt in range(task.retry_count + 1):
            if attempt > 0:
                await asyncio.sleep(task.retry_delay * attempt)

            try:
                execution = await self.execute_task(task)
                if execution.status == "completed":
                    return execution
                else:
                    last_error = execution.error_message
                    logger.warning("任务 {task.name} 第%(attempt)s次执行失败")

            except Exception as e:
                last_error = str(e)
                logger.warning("任务 {task.name} 第%(attempt)s次执行异常: {str(e)}")

        # 所有重试都失败
        execution = TestExecution(
            task_id=task.id,
            task_name=task.name,
            status="failed",
            error_message=f"所有重试都失败: {last_error}",
        )
        return execution


class ResourceMonitor:
    """资源监控器"""

    def __init__(self):
        self.task_resources: Dict[str, Dict[str, List[float]]] = {}
        self.system_resources = {"cpu": [], "memory": [], "disk": []}

    async def monitor_resources(self, task_id: str, duration: int):
        """监控任务资源使用"""
        start_time = time.time()
        interval = 1.0  # 1秒间隔

        while time.time() - start_time < duration:
            # 收集系统资源
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            disk_percent = psutil.disk_usage("/").percent

            # 记录系统资源
            self.system_resources["cpu"].append(cpu_percent)
            self.system_resources["memory"].append(memory_percent)
            self.system_resources["disk"].append(disk_percent)

            # 如果任务有资源记录，记录任务资源
            if task_id in self.task_resources:
                self.task_resources[task_id]["cpu"].append(cpu_percent)
                self.task_resources[task_id]["memory"].append(memory_percent)

            await asyncio.sleep(interval)

    def get_memory_usage(self, task_id: str) -> float:
        """获取任务内存使用情况"""
        if task_id in self.task_resources and "memory" in self.task_resources[task_id]:
            return max(self.task_resources[task_id]["memory"])
        return 0.0

    def get_cpu_usage(self, task_id: str) -> float:
        """获取任务CPU使用情况"""
        if task_id in self.task_resources and "cpu" in self.task_resources[task_id]:
            return max(self.task_resources[task_id]["cpu"])
        return 0.0

    def get_system_load(self) -> float:
        """获取系统负载"""
        if self.system_resources["cpu"]:
            return max(self.system_resources["cpu"][-10:])  # 最近10个采样
        return 0.0


class TestOrchestrator:
    """测试编排器主类"""

    def __init__(self, config: OrchestrationConfig):
        self.config = config
        self.dependency_resolver = DependencyResolver()
        self.task_executor = TaskExecutor(config)
        self.task_queue = asyncio.Queue()
        self.execution_history: List[TestExecution] = []
        self.checkpoint_manager = CheckpointManager()

    def add_task(self, task: TestTask):
        """添加任务"""
        self.dependency_resolver.add_task(task)

    async def execute_all_tasks(self) -> Dict[str, Any]:
        """执行所有任务"""
        logger.info("开始执行所有任务")

        # 解析依赖关系
        execution_levels = self.dependency_resolver.resolve_dependencies()
        plan = self.dependency_resolver.get_execution_plan()

        logger.info("执行计划: %(plan)s")

        # 启动监控任务
        monitor_task = asyncio.create_task(self._monitor_execution())

        # 按层级执行
        all_executions = []
        for level_idx, level in enumerate(execution_levels):
            logger.info("执行第 {level_idx + 1} 层任务: {len(level)} 个任务")

            if level and self.config.enable_parallel:
                # 并行执行同一层级的任务
                level_executions = await self._execute_level_parallel(level)
            else:
                # 顺序执行
                level_executions = await self._execute_level_sequential(level)

            all_executions.extend(level_executions)

            # 保存检查点
            if self.config.checkpoint_enabled and level_idx % 2 == 0:
                await self.checkpoint_manager.save_checkpoint(all_executions)

        # 停止监控
        monitor_task.cancel()

        # 生成执行报告
        report = self._generate_execution_report(all_executions)

        # 保存执行历史
        self.execution_history.extend(all_executions)

        logger.info("所有任务执行完成，共执行 {len(all_executions)} 个任务")
        return report

    async def _execute_level_parallel(self, task_ids: List[str]) -> List[TestExecution]:
        """并行执行层级的任务"""
        semaphore = asyncio.Semaphore(self.config.max_concurrent_tasks)

        async def execute_with_semaphore(task_id: str) -> TestExecution:
            async with semaphore:
                if task_id in self.dependency_resolver.tasks:
                    task = self.dependency_resolver.tasks[task_id]
                    return await self.task_executor.execute_with_retry(task)
                else:
                    return TestExecution(
                        task_id=task_id,
                        task_name="Unknown Task",
                        status="failed",
                        error_message="Task not found",
                    )

        # 创建并发任务
        tasks = [execute_with_semaphore(task_id) for task_id in task_ids]
        executions = await asyncio.gather(*tasks, return_exceptions=True)

        # 过滤异常结果
        valid_executions = []
        for execution in executions:
            if isinstance(execution, TestExecution):
                valid_executions.append(execution)
            else:
                logger.error("任务执行异常: %(execution)s")

        return valid_executions

    async def _execute_level_sequential(self, task_ids: List[str]) -> List[TestExecution]:
        """顺序执行层级的任务"""
        executions = []

        for task_id in task_ids:
            if task_id in self.dependency_resolver.tasks:
                task = self.dependency_resolver.tasks[task_id]
                execution = await self.task_executor.execute_with_retry(task)
                executions.append(execution)
            else:
                logger.error("任务不存在: %(task_id)s")

        return executions

    async def _monitor_execution(self):
        """监控执行过程"""
        while True:
            # 获取执行统计
            active_count = len(self.task_executor.active_executions)
            completed_count = len(self.task_executor.completed_executions)

            logger.info("执行统计 - 活跃任务: %(active_count)s, 已完成: %(completed_count)s")

            # 检查是否有长时间运行的任务
            current_time = datetime.now()
            for execution in self.task_executor.active_executions.values():
                if execution.start_time:
                    duration = (current_time - execution.start_time).total_seconds()
                    if duration > execution.task.timeout * 1.5:
                        logger.warning("任务 {execution.task_name} 执行超时")

            await asyncio.sleep(self.config.task_timeout // 10)

    def _generate_execution_report(self, executions: List[TestExecution]) -> Dict[str, Any]:
        """生成执行报告"""
        total_tasks = len(executions)
        completed_tasks = len([e for e in executions if e.status == "completed"])
        failed_tasks = len([e for e in executions if e.status == "failed"])

        # 计算平均执行时间
        avg_duration = sum(e.duration for e in executions) / total_tasks if total_tasks > 0 else 0

        # 按任务类型统计
        by_type = {}
        for execution in executions:
            test_type = execution.config.get("test_type", "unknown")
            if test_type not in by_type:
                by_type[test_type] = {"total": 0, "completed": 0, "failed": 0}
            by_type[test_type]["total"] += 1
            if execution.status == "completed":
                by_type[test_type]["completed"] += 1
            elif execution.status == "failed":
                by_type[test_type]["failed"] += 1

        return {
            "execution_summary": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "failed_tasks": failed_tasks,
                "success_rate": completed_tasks / total_tasks if total_tasks > 0 else 0,
                "average_duration": avg_duration,
            },
            "task_type_statistics": by_type,
            "execution_details": [e.to_dict() for e in executions],
            "execution_plan": self.dependency_resolver.get_execution_plan(),
        }

    async def restore_from_checkpoint(self) -> Dict[str, Any]:
        """从检查点恢复执行"""
        try:
            checkpoint = await self.checkpoint_manager.load_latest_checkpoint()
            if checkpoint:
                logger.info("从检查点恢复: {checkpoint['timestamp']}")
                self.execution_history.extend(checkpoint["executions"])
                return checkpoint
            else:
                logger.warning("未找到检查点")
                return {"executions": [], "timestamp": None}
        except Exception:
            logger.error("检查点恢复失败: {str(e)}")
            return {"executions": [], "timestamp": None}


class CheckpointManager:
    """检查点管理器"""

    def __init__(self, checkpoint_dir: str = "checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)

    async def save_checkpoint(self, executions: List[TestExecution]):
        """保存检查点"""
        timestamp = datetime.now().isoformat()
        checkpoint = {
            "timestamp": timestamp,
            "executions": [e.to_dict() for e in executions],
        }

        filename = f"checkpoint_{timestamp.replace(':', '-')}.json"
        filepath = self.checkpoint_dir / filename

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(checkpoint, f, indent=2, ensure_ascii=False)
            logger.info("检查点已保存: %(filepath)s")
        except Exception:
            logger.error("检查点保存失败: {str(e)}")

    async def load_latest_checkpoint(self) -> Optional[Dict[str, Any]]:
        """加载最新的检查点"""
        checkpoint_files = list(self.checkpoint_dir.glob("checkpoint_*.json"))
        if not checkpoint_files:
            return None

        # 找到最新的文件
        latest_file = max(checkpoint_files, key=lambda f: f.stat().st_mtime)

        try:
            with open(latest_file, "r", encoding="utf-8") as f:
                checkpoint = json.load(f)
            logger.info("加载检查点: %(latest_file)s")
            return checkpoint
        except Exception:
            logger.error("检查点加载失败: {str(e)}")
            return None

    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """列出所有检查点"""
        checkpoints = []
        for checkpoint_file in self.checkpoint_dir.glob("checkpoint_*.json"):
            try:
                with open(checkpoint_file, "r", encoding="utf-8") as f:
                    checkpoint = json.load(f)
                checkpoints.append(
                    {
                        "filename": checkpoint_file.name,
                        "timestamp": checkpoint["timestamp"],
                        "execution_count": len(checkpoint.get("executions", [])),
                    }
                )
            except Exception:
                logger.error("读取检查点失败 %(checkpoint_file)s: {str(e)}")

        return sorted(checkpoints, key=lambda x: x["timestamp"], reverse=True)


# 管理器工厂
class OrchestrationManager:
    """编排管理器工厂"""

    @staticmethod
    def create_default_orchestrator() -> TestOrchestrator:
        """创建默认编排器"""
        return OrchestrationManagerHelper.create_default_orchestrator(TestOrchestrator, OrchestrationConfig)

    @staticmethod
    def create_performance_orchestrator() -> TestOrchestrator:
        """创建性能测试编排器"""
        return OrchestrationManagerHelper.create_performance_orchestrator(TestOrchestrator, OrchestrationConfig)

    @staticmethod
    def create_chaos_orchestrator() -> TestOrchestrator:
        """创建混沌工程编排器"""
        return OrchestrationManagerHelper.create_chaos_orchestrator(TestOrchestrator, OrchestrationConfig)


# 使用示例
async def demo_orchestration():
    """演示编排功能"""
    await demo_orchestration_helper(
        OrchestrationManager,
        TestOrchestrator,
        OrchestrationConfig,
        TestTask,
        TaskPriority,
        CheckpointManager,
    )


if __name__ == "__main__":
    # 运行演示
    import random

    import psutil

    asyncio.run(demo_orchestration())
