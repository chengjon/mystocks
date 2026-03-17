"""
GPU 性能优化器报告与状态管理方法集。
"""

import asyncio
import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from src.monitoring.gpu_performance_optimizer.gpu_optimization_config import (
    GPUOptimizationConfig,
    GPUMetrics,
    OptimizationResult,
)


class GPUPerformanceOptimizerReportingMixin:
    """GPUPerformanceOptimizer 报告与状态方法集"""

    async def _send_performance_alert(self, before: GPUMetrics, after: GPUMetrics, improvement: float):
        """发送性能告警"""
        try:
            if not self.config.enable_performance_alerts:
                return

            {
                "optimization_type": "gpu_performance_degradation",
                "improvement_score": improvement,
                "before_metrics": asdict(before),
                "after_metrics": asdict(after),
                "recommendation": self._generate_optimization_recommendation(before, after, []),
            }

            self.logger.warning("GPU性能下降告警: %s", improvement)
        except Exception as error:
            self.logger.error("性能告警发送失败: %s", error)

    async def get_performance_report(self) -> Dict[str, Any]:
        """生成性能报告"""
        try:
            current_metrics = await self._collect_gpu_metrics()

            if self.metrics_history:
                utilization_trend = self._calculate_utilization_trend()
                memory_trend = self._calculate_memory_trend()
            else:
                utilization_trend = 0.0
                memory_trend = 0.0

            avg_efficiency = (
                np.mean([metric.efficiency_score for metric in self.metrics_history[-10:]]) if self.metrics_history else 0.0
            )
            avg_throughput = (
                np.mean([metric.throughput for metric in self.metrics_history[-10:]]) if self.metrics_history else 0.0
            )

            return {
                "timestamp": datetime.now().isoformat(),
                "gpu_available": self.gpu_available,
                "gpu_initialized": self.gpu_initialized,
                "current_metrics": asdict(current_metrics),
                "performance_baseline": asdict(self.performance_baseline) if self.performance_baseline else None,
                "optimization_stats": self.optimization_stats,
                "adaptive_params": self.adaptive_params,
                "performance_trends": {
                    "utilization_trend": utilization_trend,
                    "memory_trend": memory_trend,
                    "avg_efficiency_10": avg_efficiency,
                    "avg_throughput_10": avg_throughput,
                },
                "recommendations": await self._generate_performance_recommendations(current_metrics),
            }
        except Exception as error:
            self.logger.error("性能报告生成失败: %s", error)
            return {"error": str(error)}

    def _calculate_utilization_trend(self) -> float:
        """计算利用率趋势"""
        if len(self.metrics_history) < 2:
            return 0.0
        recent_utilizations = [metric.gpu_utilization for metric in self.metrics_history[-10:]]
        if len(recent_utilizations) < 2:
            return 0.0
        x = np.arange(len(recent_utilizations))
        y = np.array(recent_utilizations)
        return np.polyfit(x, y, 1)[0] if len(x) > 1 else 0.0

    def _calculate_memory_trend(self) -> float:
        """计算内存使用趋势"""
        if len(self.metrics_history) < 2:
            return 0.0
        recent_memory = [metric.gpu_memory_utilization for metric in self.metrics_history[-10:]]
        if len(recent_memory) < 2:
            return 0.0
        x = np.arange(len(recent_memory))
        y = np.array(recent_memory)
        return np.polyfit(x, y, 1)[0] if len(x) > 1 else 0.0

    async def _generate_performance_recommendations(self, metrics: GPUMetrics) -> List[str]:
        """生成性能建议"""
        recommendations = []
        try:
            if metrics.gpu_utilization < 30:
                recommendations.append("💡 GPU利用率较低，建议增加并发任务或扩大批次大小")
            elif metrics.gpu_utilization > 95:
                recommendations.append("⚠️ GPU接近满载，建议减少批次大小或优化算法")

            if metrics.gpu_memory_utilization > 90:
                recommendations.append("🧠 GPU内存使用过高，建议触发内存清理或减少数据集大小")
            elif metrics.gpu_memory_utilization < 20:
                recommendations.append("💾 GPU内存利用率较低，可以考虑处理更大的数据集")

            if metrics.efficiency_score < 0.5:
                recommendations.append("📊 GPU效率评分较低，建议检查算法优化和内存管理")
            elif metrics.efficiency_score > 0.9:
                recommendations.append("🚀 GPU性能表现优秀，当前配置最优")

            if metrics.gpu_temperature > 85:
                recommendations.append("🌡️ GPU温度较高，建议检查散热或降低工作负载")

            if metrics.gpu_power_usage > 200:
                recommendations.append("⚡ GPU功耗较高，注意电源供应和散热需求")
        except Exception as error:
            self.logger.error("性能建议生成失败: %s", error)
            recommendations.append("建议生成失败，请检查系统状态")

        return recommendations

    async def start_continuous_optimization(self, duration_minutes: int = 60):
        """启动连续优化监控"""
        self.logger.info("启动连续GPU性能优化 - 持续时间: %s分钟", duration_minutes)
        end_time = asyncio.get_event_loop().time() + (duration_minutes * 60)

        try:
            while asyncio.get_event_loop().time() < end_time:
                current_metrics = await self._collect_gpu_metrics()
                self.metrics_history.append(current_metrics)

                if len(self.metrics_history) > 1000:
                    self.metrics_history = self.metrics_history[-500:]

                should_optimize = False
                last_optimization = self.adaptive_params.get("last_optimization_time")
                if last_optimization is None:
                    should_optimize = True
                else:
                    time_since_last = (datetime.now() - last_optimization).total_seconds()
                    if time_since_last > self.config.optimization_interval:
                        should_optimize = True

                if should_optimize and self.config.auto_optimize:
                    result = await self.optimize_performance()
                    if result.success:
                        self.logger.info("自动优化完成: %s", result.recommendation)

                await asyncio.sleep(30)
        except asyncio.CancelledError:
            self.logger.info("连续优化监控已取消")
        except Exception as error:
            self.logger.error("连续优化监控出错: %s", error)

        self.logger.info("连续GPU性能优化结束")

    def save_optimization_state(self, filepath: str):
        """保存优化状态"""
        try:
            state = {
                "config": asdict(self.config),
                "optimization_stats": self.optimization_stats,
                "adaptive_params": self.adaptive_params,
                "metrics_history": [asdict(metric) for metric in self.metrics_history[-100:]],
                "optimization_history": [asdict(item) for item in self.optimization_history[-50:]],
                "performance_baseline": asdict(self.performance_baseline) if self.performance_baseline else None,
            }

            with open(filepath, "w", encoding="utf-8") as file_obj:
                json.dump(state, file_obj, indent=2, ensure_ascii=False, default=str)

            self.logger.info("优化状态已保存到: %s", filepath)
        except Exception as error:
            self.logger.error("保存优化状态失败: %s", error)

    def load_optimization_state(self, filepath: str):
        """加载优化状态"""
        try:
            if not Path(filepath).exists():
                self.logger.warning("优化状态文件不存在: %s", filepath)
                return

            with open(filepath, "r", encoding="utf-8") as file_obj:
                state = json.load(file_obj)

            if "config" in state:
                self.config = GPUOptimizationConfig(**state["config"])
            if "optimization_stats" in state:
                self.optimization_stats.update(state["optimization_stats"])
            if "adaptive_params" in state:
                self.adaptive_params.update(state["adaptive_params"])
            if "metrics_history" in state:
                self.metrics_history = [GPUMetrics(**item) for item in state["metrics_history"]]
            if "optimization_history" in state:
                self.optimization_history = [OptimizationResult(**item) for item in state["optimization_history"]]
            if "performance_baseline" in state and state["performance_baseline"]:
                self.performance_baseline = GPUMetrics(**state["performance_baseline"])

            self.logger.info("优化状态已从 %s 加载", filepath)
        except Exception as error:
            self.logger.error("加载优化状态失败: %s", error)
