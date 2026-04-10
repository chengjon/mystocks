"""
资源调度器
Resource Scheduler
"""

import logging
from typing import Any, Dict, List

from src.gpu.api_system.services.resource_scheduler.helpers import TaskStatus


logger = logging.getLogger(__name__)


class ResourceSchedulerCalculateQueueEfficiencyMixin:
    """ResourceScheduler 方法集 Part 2"""

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
        completed_tasks = [t for t in self.completed_tasks if t.status == TaskStatus.COMPLETED]

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
        len(self.running_tasks)
        self.config["max_concurrent_tasks"]

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
            gpu_efficiency * 0.3 + queue_efficiency * 0.2 + task_efficiency * 0.3 + resource_efficiency * 0.2
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
                (gpu_stats.get("utilization", 0) + running_tasks / max_concurrent * 100) / 2,
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

