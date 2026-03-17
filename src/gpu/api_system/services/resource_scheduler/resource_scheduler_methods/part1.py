"""
资源调度器
Resource Scheduler
"""

import logging
import queue
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from src.gpu.api_system.utils.gpu_utils import GPUResourceManager
from src.gpu.api_system.utils.monitoring import MetricsCollector
from src.gpu.api_system.utils.redis_utils import RedisQueue

logger = logging.getLogger(__name__)


class ResourceSchedulerCoreMixin:
    """ResourceScheduler 方法集 Part 1"""

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
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
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
                logger.error("调度器循环错误: %s", e)
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
            logger.error("创建任务对象失败: %s", e)
            return None

    def add_task(self, task: Task):
        """添加任务到调度器"""
        with self.lock:
            self.task_queue.put(task)
            logger.info("任务已添加到调度器: %s (优先级: %s)", task.task_id, task.priority.name)

    def _check_running_tasks(self):
        """检查运行中的任务"""
        with self.lock:
            tasks_to_remove = []

            for task_id, task in self.running_tasks.items():
                # 检查任务是否超时
                if task.started_at and (datetime.now() - task.started_at).total_seconds() > task.timeout:
                    logger.warning("任务 %s 超时，取消执行", task_id)
                    self._cancel_task(task_id)
                    tasks_to_remove.append(task_id)
                    continue

                # 检查任务是否完成
                if task.status == TaskStatus.COMPLETED or task.status == TaskStatus.FAILED:
                    logger.info("任务 %s 完成，状态: %s", task_id, task.status.value)
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
                task for task in self.completed_tasks if task.completed_at and task.completed_at > cutoff_time
            ]

    def _health_check(self):
        """健康检查"""
        try:
            # 检查GPU资源
            gpu_stats = self.gpu_manager.get_gpu_usage_summary()
            if gpu_stats:
                logger.info(
                    "GPU资源状态: 可用={gpu_stats['available_gpus']}, "
                    f"总={gpu_stats['total_gpus']}, 利用率={gpu_stats['average_utilization']:.1f}%"
                )

            # 检查任务队列
            queue_stats = self.redis_queue.get_queue_statistics()
            logger.info("任务队列状态: 待处理=%s", queue_stats.get("total_pending", 0))

            # 检查运行中的任务数量
            running_count = len(self.running_tasks)
            logger.info("运行中任务数量: %s", running_count)

            # 如果运行中任务过多，发出警告
            if running_count > self.config["max_concurrent_tasks"] * 0.9:
                logger.warning("运行中任务数量接近上限: %s/%s", running_count, self.config["max_concurrent_tasks"])

        except Exception as e:
            logger.error("健康检查失败: %s", e)

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

            logger.info("任务调度成功: %s (GPU: %s)", task.task_id, task.gpu_id)
            return task

    def _execute_task(self, task: Task):
        """执行任务"""
        try:
            logger.info("开始执行任务: %s", task.task_id)

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

            logger.info("任务执行完成: %s", task.task_id)

        except Exception as e:
            logger.error("任务执行失败: %s, 错误: %s", task.task_id, e)

            # 重试逻辑
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.RETRYING
                task.error_message = str(e)

                # 延迟重试
                retry_delay = self.config["retry_delay"]
                logger.info("任务 %s 将在 %s 秒后重试 (第 %s 次)", task.task_id, retry_delay, task.retry_count)

                # 重新加入队列
                task.status = TaskStatus.PENDING
                task.started_at = None
                self.task_queue.put(task)
            else:
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.now()
                task.error_message = str(e)
                logger.error("任务 %s 达到最大重试次数，标记为失败", task.task_id)

        finally:
            # 释放GPU资源
            if task.gpu_id is not None:
                self.gpu_manager.release_gpu(task.task_id, task.gpu_id)

    def _execute_backtest_task(self, task: Task) -> Dict[str, Any]:
        """执行回测任务"""
        # 模拟回测执行
        logger.info("执行回测任务: %s", task.task_id)
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
        logger.info("执行实时数据处理任务: %s", task.task_id)
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
        logger.info("执行机器学习训练任务: %s", task.task_id)
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
        logger.info("执行优化任务: %s", task.task_id)
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
        logger.info("执行风险控制任务: %s", task.task_id)
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
        logger.info("执行高频交易任务: %s", task.task_id)
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

                logger.info("任务已取消: %s", task_id)

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
                    task_type.value: len([t for t in self.running_tasks.values() if t.task_type == task_type])
                    for task_type in TaskType
                },
                "priorities": {
                    priority.name: len([t for t in self.running_tasks.values() if t.priority == priority])
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

    def get_queue_visualization(self) -> Dict[str, Any]:
        """获取队列可视化信息"""
        with self.lock:
            queue_viz = {
                "timestamp": datetime.now().isoformat(),
                "total_queue_size": self.task_queue.qsize(),
                "running_tasks_count": len(self.running_tasks),
                "max_concurrent_tasks": self.config["max_concurrent_tasks"],
                "queue_utilization": len(self.running_tasks) / self.config["max_concurrent_tasks"] * 100,
                "task_distribution": {},
                "priority_distribution": {},
                "gpu_utilization": self.gpu_manager.get_gpu_stats().get("utilization", 0),
                "estimated_wait_time": self._calculate_estimated_wait_time(),
                "queue_health": self._assess_queue_health(),
            }

            # 任务类型分布
            for task in self.running_tasks.values():
                task_type = task.task_type.value
                queue_viz["task_distribution"][task_type] = queue_viz["task_distribution"].get(task_type, 0) + 1

            # 优先级分布
            for task in self.running_tasks.values():
                priority = task.priority.name
                queue_viz["priority_distribution"][priority] = queue_viz["priority_distribution"].get(priority, 0) + 1

            return queue_viz

    def get_detailed_task_info(self, task_id: str = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
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
                        "started_at": task.started_at.isoformat() if task.started_at else None,
                        "gpu_id": task.gpu_id,
                        "required_memory": task.required_memory,
                        "required_gpu": task.required_gpu,
                        "retry_count": task.retry_count,
                        "elapsed_time": (datetime.now() - task.created_at).total_seconds() if task.started_at else None,
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
                            "started_at": task.started_at.isoformat() if task.started_at else None,
                            "gpu_id": task.gpu_id,
                            "elapsed_time": (
                                (datetime.now() - task.created_at).total_seconds() if task.started_at else None
                            ),
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
        wait_time = (self.task_queue.qsize() / available_slots) * (avg_task_duration / 60)
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

