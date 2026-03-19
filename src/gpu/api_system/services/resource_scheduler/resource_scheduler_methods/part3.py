"""
资源调度器性能分析方法集。
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

from src.gpu.api_system.services.resource_scheduler.helpers import TaskStatus

logger = logging.getLogger(__name__)


class ResourceSchedulerPerformanceMixin:
    """ResourceScheduler 方法集 Part 3"""

    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        with self.lock:
            gpu_stats = self.gpu_manager.get_gpu_stats()
            self.redis_queue.get_queue_statistics()
            system_efficiency = self._calculate_system_efficiency()
            task_throughput = self._calculate_task_throughput()
            gpu_efficiency = self._calculate_gpu_efficiency()
            return {
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

    def get_efficiency_analysis(self) -> Dict[str, Any]:
        """获取效率分析报告"""
        with self.lock:
            current_time = datetime.now()
            gpu_utilization = self.gpu_manager.get_gpu_stats().get("utilization", 0)
            queue_efficiency = self._calculate_queue_efficiency()
            task_efficiency = self._calculate_task_efficiency()
            resource_efficiency = self._calculate_resource_efficiency()
            return {
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

    def _identify_bottlenecks(self) -> List[str]:
        """识别系统瓶颈"""
        bottlenecks = []
        gpu_utilization = self.gpu_manager.get_gpu_stats().get("utilization", 0)
        if gpu_utilization > 90:
            bottlenecks.append("GPU资源饱和")
        if self.task_queue.qsize() > 1000:
            bottlenecks.append("任务队列积压")
        if len(self.running_tasks) >= self.config["max_concurrent_tasks"]:
            bottlenecks.append("并发任务数已达上限")
        avg_duration = self._calculate_average_task_duration()
        if avg_duration > 3600:
            bottlenecks.append("任务执行时间过长")
        return bottlenecks

    def _calculate_average_task_duration(self) -> float:
        """计算平均任务执行时间"""
        completed_tasks = [
            task
            for task in self.completed_tasks
            if task.status == TaskStatus.COMPLETED and task.started_at and task.completed_at
        ]
        if not completed_tasks:
            return 0.0
        durations = []
        for task in completed_tasks[-100:]:
            durations.append((task.completed_at - task.started_at).total_seconds())
        return round(sum(durations) / len(durations), 2) if durations else 0.0

    def _calculate_success_rate(self) -> float:
        """计算任务成功率"""
        if not self.completed_tasks:
            return 0.0
        successful_tasks = len([task for task in self.completed_tasks if task.status == TaskStatus.COMPLETED])
        total_tasks = len(self.completed_tasks)
        return round(successful_tasks / total_tasks * 100, 2)

    def _calculate_task_throughput(self) -> Dict[str, Any]:
        """计算任务吞吐量"""
        completed_count = len([task for task in self.completed_tasks if task.status == TaskStatus.COMPLETED])
        total_count = len(self.completed_tasks)
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_completed = len(
            [
                task
                for task in self.completed_tasks
                if task.status == TaskStatus.COMPLETED and task.completed_at and task.completed_at > one_hour_ago
            ]
        )
        return {
            "total_completed": completed_count,
            "recent_hourly_throughput": recent_completed,
            "success_rate": round(completed_count / total_count * 100, 2) if total_count > 0 else 0,
            "queue_efficiency": round(self.task_queue.qsize() / self.config["max_concurrent_tasks"] * 100, 2),
        }

    def _calculate_gpu_efficiency(self) -> float:
        """计算GPU效率"""
        gpu_stats = self.gpu_manager.get_gpu_stats()
        utilization = gpu_stats.get("utilization", 0)
        memory_usage = gpu_stats.get("memory_usage", 0)
        return round(utilization * 0.7 + memory_usage * 0.3, 2)
