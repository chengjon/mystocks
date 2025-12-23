"""
资源调度器
Resource Scheduler
"""

import logging
import time
import threading
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import queue
from enum import Enum

from src.utils.gpu_utils import GPUResourceManager
from src.utils.redis_utils import RedisQueue
from src.utils.monitoring import MetricsCollector

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
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "gpu_id": self.gpu_id,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
            "result": self.result,
            "error_message": self.error_message,
        }


class ResourceScheduler:
    """资源调度器"""

    def __init__(
        self,
        gpu_manager: GPUResourceManager,
        redis_queue: RedisQueue,
        metrics_collector: MetricsCollector,
    ):
        self.gpu_manager = gpu_manager
        self.redis_queue = redis_queue
        self.metrics_collector = metrics_collector
        self.task_queue = queue.PriorityQueue()
        self.running_tasks: Dict[str, Task] = {}
        self.completed_tasks: List[Task] = []
        self.scheduler_thread = None
        self.running = False
        self.lock = threading.Lock()
        self.config = {
            "max_concurrent_tasks": 10,
            "max_gpu_tasks": 8,
            "task_timeout": 3600,
            "retry_delay": 300,  # 5分钟重试延迟
            "cleanup_interval": 300,  # 5分钟清理间隔
            "health_check_interval": 60,  # 1分钟健康检查间隔
        }

    def initialize(self):
        """初始化调度器"""
        logger.info("正在初始化资源调度器...")

        # 初始化GPU资源管理器
        if not self.gpu_manager.gpu_states:
            self.gpu_manager.initialize()

        # 启动调度器线程
        self.running = True
        self.scheduler_thread = threading.Thread(
            target=self._scheduler_loop, daemon=True
        )
        self.scheduler_thread.start()

        logger.info("资源调度器初始化完成")

    def _scheduler_loop(self):
        """调度器主循环"""
        logger.info("资源调度器主循环启动")

        while self.running:
            try:
                # 从Redis队列获取任务
                task_data = self.redis_queue.dequeue_task("gpu", timeout=10)
                if task_data:
                    task = self._create_task_from_data(task_data)
                    if task:
                        self.add_task(task)

                # 检查运行中的任务
                self._check_running_tasks()

                # 清理完成的任务
                self._cleanup_completed_tasks()

                # 健康检查
                self._health_check()

            except Exception as e:
                logger.error(f"调度器循环错误: {e}")
                time.sleep(5)

    def _create_task_from_data(self, task_data: Dict[str, Any]) -> Optional[Task]:
        """从任务数据创建Task对象"""
        try:
            task_id = task_data.get("task_id")
            if not task_id:
                return None

            # 解析任务类型
            task_type_str = task_data.get("task_type", "backtest")
            task_type = TaskType(task_type_str)

            # 解析优先级
            priority_str = task_data.get("priority", "medium")
            priority = TaskPriority[priority_str.upper()]

            # 解析资源需求
            required_memory = task_data.get("required_memory", 0)
            required_gpu = task_data.get("required_gpu", True)

            # 创建任务对象
            task = Task(
                task_id=task_id,
                task_type=task_type,
                priority=priority,
                required_memory=required_memory,
                required_gpu=required_gpu,
                task_data=task_data,
            )

            return task

        except Exception as e:
            logger.error(f"创建任务对象失败: {e}")
            return None

    def add_task(self, task: Task):
        """添加任务到调度器"""
        with self.lock:
            self.task_queue.put(task)
            logger.info(
                f"任务已添加到调度器: {task.task_id} (优先级: {task.priority.name})"
            )

    def _check_running_tasks(self):
        """检查运行中的任务"""
        with self.lock:
            tasks_to_remove = []

            for task_id, task in self.running_tasks.items():
                # 检查任务是否超时
                if (
                    task.started_at
                    and (datetime.now() - task.started_at).total_seconds()
                    > task.timeout
                ):
                    logger.warning(f"任务 {task_id} 超时，取消执行")
                    self._cancel_task(task_id)
                    tasks_to_remove.append(task_id)
                    continue

                # 检查任务是否完成
                if (
                    task.status == TaskStatus.COMPLETED
                    or task.status == TaskStatus.FAILED
                ):
                    logger.info(f"任务 {task_id} 完成，状态: {task.status.value}")
                    self.completed_tasks.append(task)
                    tasks_to_remove.append(task_id)

            # 清理已完成的任务
            for task_id in tasks_to_remove:
                del self.running_tasks[task_id]

    def _cleanup_completed_tasks(self):
        """清理完成的任务"""
        with self.lock:
            # 保持最近1000个完成的任务
            if len(self.completed_tasks) > 1000:
                self.completed_tasks = self.completed_tasks[-1000:]

            # 清理超过1天的已完成任务
            cutoff_time = datetime.now() - timedelta(days=1)
            self.completed_tasks = [
                task
                for task in self.completed_tasks
                if task.completed_at and task.completed_at > cutoff_time
            ]

    def _health_check(self):
        """健康检查"""
        try:
            # 检查GPU资源
            gpu_stats = self.gpu_manager.get_gpu_usage_summary()
            if gpu_stats:
                logger.info(
                    f"GPU资源状态: 可用={gpu_stats['available_gpus']}, "
                    f"总={gpu_stats['total_gpus']}, 利用率={gpu_stats['average_utilization']:.1f}%"
                )

            # 检查任务队列
            queue_stats = self.redis_queue.get_queue_statistics()
            logger.info(f"任务队列状态: 待处理={queue_stats.get('total_pending', 0)}")

            # 检查运行中的任务数量
            running_count = len(self.running_tasks)
            logger.info(f"运行中任务数量: {running_count}")

            # 如果运行中任务过多，发出警告
            if running_count > self.config["max_concurrent_tasks"] * 0.9:
                logger.warning(
                    f"运行中任务数量接近上限: {running_count}/{self.config['max_concurrent_tasks']}"
                )

        except Exception as e:
            logger.error(f"健康检查失败: {e}")

    def _schedule_task(self) -> Optional[Task]:
        """调度任务执行"""
        with self.lock:
            # 检查是否可以添加更多任务
            if len(self.running_tasks) >= self.config["max_concurrent_tasks"]:
                return None

            # 获取下一个最高优先级的任务
            try:
                task = self.task_queue.get_nowait()
            except queue.Empty:
                return None

            # 分配GPU资源
            if task.required_gpu:
                gpu_id = self.gpu_manager.allocate_gpu(
                    task.task_id,
                    priority=task.priority.name.lower(),
                    memory_required=task.required_memory,
                )

                if gpu_id is None:
                    # GPU资源不足，重新加入队列
                    self.task_queue.put(task)
                    return None

                task.gpu_id = gpu_id
            else:
                task.gpu_id = None

            # 更新任务状态
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            self.running_tasks[task.task_id] = task

            logger.info(f"任务调度成功: {task.task_id} (GPU: {task.gpu_id})")
            return task

    def _execute_task(self, task: Task):
        """执行任务"""
        try:
            logger.info(f"开始执行任务: {task.task_id}")

            # 根据任务类型执行相应的处理逻辑
            if task.task_type == TaskType.BACKTEST:
                result = self._execute_backtest_task(task)
            elif task.task_type == TaskType.REALTIME:
                result = self._execute_realtime_task(task)
            elif task.task_type == TaskType.ML_TRAINING:
                result = self._execute_ml_task(task)
            elif task.task_type == TaskType.OPTIMIZATION:
                result = self._execute_optimization_task(task)
            elif task.task_type == TaskType.RISK_CONTROL:
                result = self._execute_risk_control_task(task)
            elif task.task_type == TaskType.HIGH_FREQUENCY:
                result = self._execute_high_freq_task(task)
            else:
                raise ValueError(f"不支持的任务类型: {task.task_type}")

            # 任务完成
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = result

            logger.info(f"任务执行完成: {task.task_id}")

        except Exception as e:
            logger.error(f"任务执行失败: {task.task_id}, 错误: {e}")

            # 重试逻辑
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.RETRYING
                task.error_message = str(e)

                # 延迟重试
                retry_delay = self.config["retry_delay"]
                logger.info(
                    f"任务 {task.task_id} 将在 {retry_delay} 秒后重试 (第 {task.retry_count} 次)"
                )

                # 重新加入队列
                task.status = TaskStatus.PENDING
                task.started_at = None
                self.task_queue.put(task)
            else:
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.now()
                task.error_message = str(e)
                logger.error(f"任务 {task.task_id} 达到最大重试次数，标记为失败")

        finally:
            # 释放GPU资源
            if task.gpu_id is not None:
                self.gpu_manager.release_gpu(task.task_id, task.gpu_id)

    def _execute_backtest_task(self, task: Task) -> Dict[str, Any]:
        """执行回测任务"""
        # 模拟回测执行
        logger.info(f"执行回测任务: {task.task_id}")
        time.sleep(5)  # 模拟处理时间

        return {
            "status": "success",
            "backtest_id": task.task_id,
            "total_return": 0.125,
            "sharpe_ratio": 1.85,
            "max_drawdown": 0.08,
            "win_rate": 0.65,
            "duration": 60,
            "execution_time": time.time() - task.started_at.timestamp(),
        }

    def _execute_realtime_task(self, task: Task) -> Dict[str, Any]:
        """执行实时数据处理任务"""
        logger.info(f"执行实时数据处理任务: {task.task_id}")
        time.sleep(2)  # 模拟处理时间

        return {
            "status": "success",
            "processed_records": 10000,
            "feature_count": 50,
            "processing_time": 2.5,
            "timestamp": datetime.now().isoformat(),
        }

    def _execute_ml_task(self, task: Task) -> Dict[str, Any]:
        """执行机器学习训练任务"""
        logger.info(f"执行机器学习训练任务: {task.task_id}")
        time.sleep(30)  # 模拟训练时间

        return {
            "status": "success",
            "model_type": "random_forest",
            "accuracy": 0.92,
            "feature_importance": [0.25, 0.18, 0.15, 0.12, 0.10],
            "training_time": 30,
            "model_size": 12500000,
        }

    def _execute_optimization_task(self, task: Task) -> Dict[str, Any]:
        """执行优化任务"""
        logger.info(f"执行优化任务: {task.task_id}")
        time.sleep(15)  # 模拟处理时间

        return {
            "status": "success",
            "optimized_parameters": [0.75, 0.25, 1.5, 0.5],
            "improvement": 0.15,
            "iterations": 1000,
            "convergence_time": 15,
        }

    def _execute_risk_control_task(self, task: Task) -> Dict[str, Any]:
        """执行风险控制任务"""
        logger.info(f"执行风险控制任务: {task.task_id}")
        time.sleep(8)  # 模拟处理时间

        return {
            "status": "success",
            "risk_score": 0.65,
            "portfolio_var": 0.12,
            "max_position_size": 1000000,
            "risk_checks_passed": 15,
            "total_risk_checks": 20,
        }

    def _execute_high_freq_task(self, task: Task) -> Dict[str, Any]:
        """执行高频交易任务"""
        logger.info(f"执行高频交易任务: {task.task_id}")
        time.sleep(3)  # 模拟处理时间

        return {
            "status": "success",
            "orders_executed": 5000,
            "execution_rate": 0.98,
            "latency": 0.001,
            "fill_rate": 0.95,
            "total_volume": 50000000,
        }

    def _cancel_task(self, task_id: str):
        """取消任务"""
        with self.lock:
            if task_id in self.running_tasks:
                task = self.running_tasks[task_id]
                task.status = TaskStatus.CANCELLED
                task.completed_at = datetime.now()

                # 释放GPU资源
                if task.gpu_id is not None:
                    self.gpu_manager.release_gpu(task.task_id, task.gpu_id)

                logger.info(f"任务已取消: {task_id}")

    def get_task_status(self, task_id: str) -> Optional[Task]:
        """获取任务状态"""
        # 检查运行中的任务
        if task_id in self.running_tasks:
            return self.running_tasks[task_id]

        # 检查已完成的任务
        for task in self.completed_tasks:
            if task.task_id == task_id:
                return task

        # 检查待处理任务
        # 这里可以添加对任务队列的检查

        return None

    def get_scheduler_statistics(self) -> Dict[str, Any]:
        """获取调度器统计信息"""
        with self.lock:
            return {
                "timestamp": datetime.now().isoformat(),
                "running_tasks": len(self.running_tasks),
                "pending_tasks": self.task_queue.qsize(),
                "completed_tasks": len(self.completed_tasks),
                "gpu_available": self.gpu_manager.get_available_gpu_count(),
                "gpu_total": len(self.gpu_manager.gpu_ids),
                "task_types": {
                    task_type.value: len(
                        [
                            t
                            for t in self.running_tasks.values()
                            if t.task_type == task_type
                        ]
                    )
                    for task_type in TaskType
                },
                "priorities": {
                    priority.name: len(
                        [
                            t
                            for t in self.running_tasks.values()
                            if t.priority == priority
                        ]
                    )
                    for priority in TaskPriority
                },
            }

    def stop(self):
        """停止调度器"""
        logger.info("正在停止资源调度器...")
        self.running = False

        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=10)

        # 释放所有GPU资源
        self.gpu_manager.cleanup()

        logger.info("资源调度器已停止")

    # 高级功能方法
    def get_queue_visualization(self) -> Dict[str, Any]:
        """获取队列可视化信息"""
        with self.lock:
            queue_viz = {
                "timestamp": datetime.now().isoformat(),
                "total_queue_size": self.task_queue.qsize(),
                "running_tasks_count": len(self.running_tasks),
                "max_concurrent_tasks": self.config["max_concurrent_tasks"],
                "queue_utilization": len(self.running_tasks)
                / self.config["max_concurrent_tasks"]
                * 100,
                "task_distribution": {},
                "priority_distribution": {},
                "gpu_utilization": self.gpu_manager.get_gpu_stats().get(
                    "utilization", 0
                ),
                "estimated_wait_time": self._calculate_estimated_wait_time(),
                "queue_health": self._assess_queue_health(),
            }

            # 任务类型分布
            for task in self.running_tasks.values():
                task_type = task.task_type.value
                queue_viz["task_distribution"][task_type] = (
                    queue_viz["task_distribution"].get(task_type, 0) + 1
                )

            # 优先级分布
            for task in self.running_tasks.values():
                priority = task.priority.name
                queue_viz["priority_distribution"][priority] = (
                    queue_viz["priority_distribution"].get(priority, 0) + 1
                )

            return queue_viz

    def get_detailed_task_info(
        self, task_id: str = None
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """获取详细任务信息"""
        with self.lock:
            if task_id:
                # 返回特定任务的详细信息
                if task_id in self.running_tasks:
                    task = self.running_tasks[task_id]
                    return {
                        "task_id": task.task_id,
                        "task_type": task.task_type.value,
                        "priority": task.priority.name,
                        "status": task.status.value,
                        "created_at": task.created_at.isoformat(),
                        "started_at": task.started_at.isoformat()
                        if task.started_at
                        else None,
                        "gpu_id": task.gpu_id,
                        "required_memory": task.required_memory,
                        "required_gpu": task.required_gpu,
                        "retry_count": task.retry_count,
                        "elapsed_time": (
                            datetime.now() - task.created_at
                        ).total_seconds()
                        if task.started_at
                        else None,
                        "estimated_remaining_time": self._estimate_remaining_time(task),
                    }
                else:
                    return {"error": f"Task {task_id} not found"}
            else:
                # 返回所有任务的详细信息
                all_tasks = []

                # 运行中的任务
                for task in self.running_tasks.values():
                    all_tasks.append(
                        {
                            "task_id": task.task_id,
                            "task_type": task.task_type.value,
                            "priority": task.priority.name,
                            "status": task.status.value,
                            "created_at": task.created_at.isoformat(),
                            "started_at": task.started_at.isoformat()
                            if task.started_at
                            else None,
                            "gpu_id": task.gpu_id,
                            "elapsed_time": (
                                datetime.now() - task.created_at
                            ).total_seconds()
                            if task.started_at
                            else None,
                        }
                    )

                # 待处理任务（队列中的前10个）
                try:
                    queue_tasks = []
                    temp_queue = list(self.task_queue.queue)
                    for task in temp_queue[:10]:  # 只显示前10个
                        queue_tasks.append(
                            {
                                "task_id": task.task_id,
                                "task_type": task.task_type.value,
                                "priority": task.priority.name,
                                "status": "pending",
                                "created_at": task.created_at.isoformat(),
                                "estimated_start_time": self._estimate_start_time(task),
                            }
                        )
                    all_tasks.extend(queue_tasks)
                except Exception:
                    pass

                return all_tasks

    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        with self.lock:
            gpu_stats = self.gpu_manager.get_gpu_stats()
            queue_stats = self.redis_queue.get_queue_statistics()

            # 计算系统效率指标
            system_efficiency = self._calculate_system_efficiency()
            task_throughput = self._calculate_task_throughput()
            gpu_efficiency = self._calculate_gpu_efficiency()

            performance_metrics = {
                "timestamp": datetime.now().isoformat(),
                "system_efficiency": system_efficiency,
                "task_throughput": task_throughput,
                "gpu_efficiency": gpu_efficiency,
                "gpu_utilization": gpu_stats.get("utilization", 0),
                "gpu_memory_usage": gpu_stats.get("memory_usage", 0),
                "active_tasks": len(self.running_tasks),
                "pending_tasks": self.task_queue.qsize(),
                "completed_tasks": len(self.completed_tasks),
                "average_task_duration": self._calculate_average_task_duration(),
                "success_rate": self._calculate_success_rate(),
                "bottleneck_analysis": self._identify_bottlenecks(),
                "resource_utilization": {
                    "cpu_efficiency": system_efficiency["cpu_efficiency"],
                    "memory_efficiency": system_efficiency["memory_efficiency"],
                    "gpu_efficiency": gpu_efficiency,
                    "queue_efficiency": task_throughput["queue_efficiency"],
                },
            }

            return performance_metrics

    def get_efficiency_analysis(self) -> Dict[str, Any]:
        """获取效率分析报告"""
        with self.lock:
            current_time = datetime.now()

            # 计算各项效率指标
            gpu_utilization = self.gpu_manager.get_gpu_stats().get("utilization", 0)
            queue_efficiency = self._calculate_queue_efficiency()
            task_efficiency = self._calculate_task_efficiency()
            resource_efficiency = self._calculate_resource_efficiency()

            efficiency_report = {
                "timestamp": current_time.isoformat(),
                "overall_efficiency_score": self._calculate_overall_efficiency(),
                "gpu_utilization_efficiency": gpu_utilization,
                "queue_processing_efficiency": queue_efficiency,
                "task_execution_efficiency": task_efficiency,
                "resource_allocation_efficiency": resource_efficiency,
                "efficiency_trends": self._calculate_efficiency_trends(),
                "optimization_recommendations": self._generate_optimization_recommendations(),
                "capacity_analysis": self._analyze_capacity_utilization(),
                "performance_benchmarks": self._get_performance_benchmarks(),
            }

            return efficiency_report

    def _calculate_estimated_wait_time(self) -> float:
        """计算预估等待时间"""
        if self.task_queue.qsize() == 0:
            return 0.0

        # 基于当前运行任务数和队列长度估算
        avg_task_duration = 300  # 默认5分钟
        running_tasks = len(self.running_tasks)
        max_concurrent = self.config["max_concurrent_tasks"]

        # 计算可用的并发槽位
        available_slots = max_concurrent - running_tasks
        if available_slots <= 0:
            return float("inf")  # 队列已满

        # 估算等待时间
        wait_time = (self.task_queue.qsize() / available_slots) * (
            avg_task_duration / 60
        )
        return round(wait_time, 2)

    def _assess_queue_health(self) -> str:
        """评估队列健康状态"""
        queue_size = self.task_queue.qsize()
        running_tasks = len(self.running_tasks)
        max_concurrent = self.config["max_concurrent_tasks"]

        utilization = (running_tasks / max_concurrent) * 100

        if queue_size == 0 and utilization < 50:
            return "healthy"
        elif queue_size < 100 and utilization < 80:
            return "normal"
        elif queue_size < 500 and utilization < 90:
            return "warning"
        else:
            return "critical"

    def _estimate_remaining_time(self, task: Task) -> Optional[float]:
        """估算任务剩余时间"""
        if not task.started_at:
            return None

        elapsed = (datetime.now() - task.started_at).total_seconds()
        timeout = task.timeout

        # 基于已用时间和超时时间估算
        if elapsed < timeout * 0.1:  # 不足10%时间，难以估算
            return None

        # 简单线性估算
        estimated_remaining = timeout - elapsed
        return max(0, estimated_remaining)

    def _estimate_start_time(self, task: Task) -> Optional[str]:
        """估算任务开始时间"""
        current_time = datetime.now()
        wait_time = self._calculate_estimated_wait_time()

        if wait_time == float("inf"):
            return None

        start_time = current_time + timedelta(minutes=wait_time)
        return start_time.isoformat()

    def _calculate_system_efficiency(self) -> Dict[str, float]:
        """计算系统效率"""
        gpu_utilization = self.gpu_manager.get_gpu_stats().get("utilization", 0)
        running_tasks = len(self.running_tasks)
        max_concurrent = self.config["max_concurrent_tasks"]

        # CPU效率（基于任务运行情况估算）
        cpu_efficiency = min(running_tasks / max_concurrent * 100, 100)

        # 内存效率（基于GPU内存使用估算）
        memory_efficiency = gpu_utilization  # 假设GPU利用率反映内存使用效率

        # 综合系统效率
        overall_efficiency = (cpu_efficiency + memory_efficiency) / 2

        return {
            "cpu_efficiency": round(cpu_efficiency, 2),
            "memory_efficiency": round(memory_efficiency, 2),
            "overall_efficiency": round(overall_efficiency, 2),
        }

    def _calculate_task_throughput(self) -> Dict[str, Any]:
        """计算任务吞吐量"""
        completed_count = len(
            [t for t in self.completed_tasks if t.status == TaskStatus.COMPLETED]
        )
        total_count = len(self.completed_tasks)

        # 计算最近1小时的吞吐量
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_completed = len(
            [
                t
                for t in self.completed_tasks
                if t.status == TaskStatus.COMPLETED
                and t.completed_at
                and t.completed_at > one_hour_ago
            ]
        )

        throughput = {
            "total_completed": completed_count,
            "recent_hourly_throughput": recent_completed,
            "success_rate": round(completed_count / total_count * 100, 2)
            if total_count > 0
            else 0,
            "queue_efficiency": round(
                self.task_queue.qsize() / self.config["max_concurrent_tasks"] * 100, 2
            ),
        }

        return throughput

    def _calculate_gpu_efficiency(self) -> float:
        """计算GPU效率"""
        gpu_stats = self.gpu_manager.get_gpu_stats()
        utilization = gpu_stats.get("utilization", 0)
        memory_usage = gpu_stats.get("memory_usage", 0)

        # 综合GPU效率 = 利用率权重0.7 + 内存使用率权重0.3
        gpu_efficiency = utilization * 0.7 + memory_usage * 0.3
        return round(gpu_efficiency, 2)

    def _calculate_average_task_duration(self) -> float:
        """计算平均任务执行时间"""
        completed_tasks = [
            t
            for t in self.completed_tasks
            if t.status == TaskStatus.COMPLETED and t.started_at and t.completed_at
        ]

        if not completed_tasks:
            return 0.0

        durations = []
        for task in completed_tasks[-100:]:  # 最近100个任务
            duration = (task.completed_at - task.started_at).total_seconds()
            durations.append(duration)

        return round(sum(durations) / len(durations), 2) if durations else 0.0

    def _calculate_success_rate(self) -> float:
        """计算任务成功率"""
        if not self.completed_tasks:
            return 0.0

        successful_tasks = len(
            [t for t in self.completed_tasks if t.status == TaskStatus.COMPLETED]
        )
        total_tasks = len(self.completed_tasks)

        return round(successful_tasks / total_tasks * 100, 2)

    def _identify_bottlenecks(self) -> List[str]:
        """识别系统瓶颈"""
        bottlenecks = []

        # 检查GPU利用率瓶颈
        gpu_utilization = self.gpu_manager.get_gpu_stats().get("utilization", 0)
        if gpu_utilization > 90:
            bottlenecks.append("GPU资源饱和")

        # 检查队列长度瓶颈
        if self.task_queue.qsize() > 1000:
            bottlenecks.append("任务队列积压")

        # 检查并发任务数瓶颈
        if len(self.running_tasks) >= self.config["max_concurrent_tasks"]:
            bottlenecks.append("并发任务数已达上限")

        # 检查任务执行时间瓶颈
        avg_duration = self._calculate_average_task_duration()
        if avg_duration > 3600:  # 超过1小时
            bottlenecks.append("任务执行时间过长")

        return bottlenecks

    def _calculate_queue_efficiency(self) -> float:
        """计算队列处理效率"""
        queue_size = self.task_queue.qsize()
        max_concurrent = self.config["max_concurrent_tasks"]

        # 队列效率 = 理想队列长度 / 实际队列长度
        ideal_queue_size = max_concurrent * 2  # 理想队列大小为并发数的2倍
        efficiency = min(ideal_queue_size / max(queue_size, 1) * 100, 100)

        return round(efficiency, 2)

    def _calculate_task_efficiency(self) -> float:
        """计算任务执行效率"""
        completed_tasks = [
            t for t in self.completed_tasks if t.status == TaskStatus.COMPLETED
        ]

        if not completed_tasks:
            return 0.0

        # 计算任务按时完成率
        on_time_tasks = 0
        for task in completed_tasks[-100:]:  # 最近100个任务
            if task.started_at and task.completed_at:
                duration = (task.completed_at - task.started_at).total_seconds()
                if duration <= task.timeout:
                    on_time_tasks += 1

        return round(on_time_tasks / min(len(completed_tasks), 100) * 100, 2)

    def _calculate_resource_efficiency(self) -> float:
        """计算资源分配效率"""
        gpu_utilization = self.gpu_manager.get_gpu_stats().get("utilization", 0)
        running_tasks = len(self.running_tasks)
        max_concurrent = self.config["max_concurrent_tasks"]

        # 资源效率 = GPU利用率 * 任务执行效率
        task_efficiency = self._calculate_task_efficiency()
        resource_efficiency = gpu_utilization * task_efficiency / 100

        return round(resource_efficiency, 2)

    def _calculate_overall_efficiency(self) -> float:
        """计算整体效率得分"""
        gpu_efficiency = self._calculate_gpu_efficiency()
        queue_efficiency = self._calculate_queue_efficiency()
        task_efficiency = self._calculate_task_efficiency()
        resource_efficiency = self._calculate_resource_efficiency()

        # 加权平均效率
        overall_efficiency = (
            gpu_efficiency * 0.3
            + queue_efficiency * 0.2
            + task_efficiency * 0.3
            + resource_efficiency * 0.2
        )

        return round(overall_efficiency, 2)

    def _calculate_efficiency_trends(self) -> Dict[str, float]:
        """计算效率趋势"""
        # 这里可以基于历史数据计算效率趋势
        # 当前简化实现，返回固定值
        return {
            "trend_1h": 0.0,
            "trend_24h": 0.0,
            "trend_7d": 0.0,
            "stability_score": 85.0,
        }

    def _generate_optimization_recommendations(self) -> List[str]:
        """生成优化建议"""
        recommendations = []

        # 基于当前状态生成建议
        gpu_utilization = self.gpu_manager.get_gpu_stats().get("utilization", 0)
        queue_size = self.task_queue.qsize()

        if gpu_utilization < 30:
            recommendations.append("考虑减少GPU实例数量以节省成本")
        elif gpu_utilization > 90:
            recommendations.append("考虑增加GPU实例数量或优化任务调度")

        if queue_size > 1000:
            recommendations.append("任务队列积压严重，建议增加并发处理能力")

        if len(self.running_tasks) < self.config["max_concurrent_tasks"] * 0.5:
            recommendations.append("当前并发任务数较低，可以考虑提高并发上限")

        return recommendations

    def _analyze_capacity_utilization(self) -> Dict[str, Any]:
        """分析容量利用率"""
        gpu_stats = self.gpu_manager.get_gpu_stats()
        running_tasks = len(self.running_tasks)
        max_concurrent = self.config["max_concurrent_tasks"]

        capacity_analysis = {
            "gpu_capacity": {
                "total": len(self.gpu_manager.gpu_ids),
                "available": self.gpu_manager.get_available_gpu_count(),
                "utilization": gpu_stats.get("utilization", 0),
                "memory_usage": gpu_stats.get("memory_usage", 0),
            },
            "task_capacity": {
                "max_concurrent": max_concurrent,
                "current_running": running_tasks,
                "queue_size": self.task_queue.qsize(),
                "utilization": running_tasks / max_concurrent * 100,
            },
            "overall_capacity_utilization": round(
                (gpu_stats.get("utilization", 0) + running_tasks / max_concurrent * 100)
                / 2,
                2,
            ),
        }

        return capacity_analysis

    def _get_performance_benchmarks(self) -> Dict[str, Any]:
        """获取性能基准"""
        return {
            "gpu_utilization_benchmark": {
                "excellent": ">80%",
                "good": "60-80%",
                "fair": "40-60%",
                "poor": "<40%",
            },
            "task_duration_benchmark": {
                "fast": "<60s",
                "normal": "60-300s",
                "slow": "300s-3600s",
                "very_slow": ">3600s",
            },
            "queue_length_benchmark": {
                "optimal": "0-100",
                "acceptable": "100-500",
                "warning": "500-1000",
                "critical": ">1000",
            },
            "success_rate_benchmark": {
                "excellent": ">95%",
                "good": "90-95%",
                "fair": "80-90%",
                "poor": "<80%",
            },
        }
