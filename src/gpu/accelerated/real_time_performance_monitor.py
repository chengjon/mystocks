#!/usr/bin/env python3
"""
实时性能监控器
监控GPU和CPU的实时性能表现，提供动态负载均衡建议
适用于MyStocks量化交易系统的实时性能监控
"""

import time
import psutil
import threading
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from collections import deque
import numpy as np

# 导入GPU组件
from .cpu_fallback import ComponentSelector


@dataclass
class PerformanceMetrics:
    """性能指标"""

    timestamp: float
    gpu_utilization: float
    cpu_utilization: float
    gpu_memory_usage: float
    cpu_memory_usage: float
    gpu_temperature: float
    power_usage: float
    processing_time: float
    throughput: float
    error_rate: float


@dataclass
class WorkloadInfo:
    """工作负载信息"""

    task_type: str
    data_size: int
    complexity_score: float
    estimated_gpu_time: float
    estimated_cpu_time: float
    deadline: Optional[float] = None


class RealTimePerformanceMonitor:
    """实时性能监控器"""

    def __init__(self, monitoring_interval: float = 1.0, history_size: int = 300):
        self.monitoring_interval = monitoring_interval
        self.history_size = history_size
        self.logger = logging.getLogger(__name__)
        self.component_selector = ComponentSelector()

        # 性能历史记录
        self.performance_history = deque(maxlen=history_size)
        self.workload_history = deque(maxlen=100)

        # 实时指标
        self.current_metrics = None
        self.is_monitoring = False
        self.monitoring_thread = None

        # 警报阈值
        self.thresholds = {
            "gpu_utilization": 90.0,  # GPU使用率超过90%
            "cpu_utilization": 85.0,  # CPU使用率超过85%
            "gpu_memory_usage": 80.0,  # GPU内存使用超过80%
            "gpu_temperature": 80.0,  # GPU温度超过80°C
            "power_usage": 250.0,  # 功率超过250W
            "processing_time": 10.0,  # 单个任务处理时间超过10秒
            "error_rate": 0.05,  # 错误率超过5%
        }

        # 回调函数
        self.alert_callbacks: List[Callable] = []

        # 性能统计
        self.stats = {
            "total_operations": 0,
            "gpu_operations": 0,
            "cpu_operations": 0,
            "avg_processing_time": 0.0,
            "avg_speedup": 1.0,
            "error_count": 0,
        }

    def start_monitoring(self):
        """开始监控"""
        if self.is_monitoring:
            return

        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitor_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()

        self.logger.info("🚀 实时性能监控已启动")

    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join()

        self.logger.info("⏹️  实时性能监控已停止")

    def _monitor_loop(self):
        """监控循环"""
        while self.is_monitoring:
            try:
                metrics = self._collect_metrics()
                self.current_metrics = metrics
                self.performance_history.append(metrics)

                # 更新统计
                self._update_stats(metrics)

                # 检查警报
                self._check_alerts(metrics)

                # 记录性能日志
                self._log_performance(metrics)

                time.sleep(self.monitoring_interval)

            except Exception as e:
                self.logger.error(f"监控循环错误: {e}")
                time.sleep(self.monitoring_interval)

    def _collect_metrics(self) -> PerformanceMetrics:
        """收集性能指标"""
        timestamp = time.time()

        # CPU指标
        cpu_util = psutil.cpu_percent()
        cpu_memory = psutil.virtual_memory().percent
        cpu_freq = psutil.cpu_freq()

        # GPU指标
        gpu_util = 0.0
        gpu_memory = 0.0
        gpu_temp = 0.0
        power_usage = 0.0

        if self.component_selector.check_gpu_availability():
            try:
                import subprocess

                # 获取GPU信息
                result = subprocess.run(
                    [
                        "nvidia-smi",
                        "--query-gpu=utilization.gpu,memory.used,temperature.gpu,power.draw",
                        "--format=csv,noheader,nounits",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                if result.returncode == 0:
                    gpu_info = result.stdout.strip().split(", ")
                    if len(gpu_info) >= 4:
                        gpu_util = float(gpu_info[0])
                        gpu_memory = float(gpu_info[1]) / 1024  # Convert to MB
                        gpu_temp = float(gpu_info[2])
                        power_usage = float(gpu_info[3])

            except Exception as e:
                self.logger.warning(f"GPU指标收集失败: {e}")

        # 处理时间（模拟）
        processing_time = self._get_recent_processing_time()

        # 吞吐量
        throughput = self._calculate_throughput()

        # 错误率
        error_rate = self._calculate_error_rate()

        return PerformanceMetrics(
            timestamp=timestamp,
            gpu_utilization=gpu_util,
            cpu_utilization=cpu_util,
            gpu_memory_usage=gpu_memory,
            cpu_memory_usage=cpu_memory,
            gpu_temperature=gpu_temp,
            power_usage=power_usage,
            processing_time=processing_time,
            throughput=throughput,
            error_rate=error_rate,
        )

    def _get_recent_processing_time(self) -> float:
        """获取最近的处理时间"""
        if len(self.performance_history) > 0:
            return self.performance_history[-1].processing_time
        return 0.0

    def _calculate_throughput(self) -> float:
        """计算吞吐量"""
        if len(self.performance_history) < 10:
            return 0.0

        # 计算最近10秒内的平均处理次数
        recent_history = list(self.performance_history)[-10:]
        return len(recent_history) / self.monitoring_interval

    def _calculate_error_rate(self) -> float:
        """计算错误率"""
        if self.stats["total_operations"] == 0:
            return 0.0

        return self.stats["error_count"] / self.stats["total_operations"]

    def _update_stats(self, metrics: PerformanceMetrics):
        """更新统计信息"""
        self.stats["total_operations"] += 1

        if metrics.gpu_utilization > 0:
            self.stats["gpu_operations"] += 1
        else:
            self.stats["cpu_operations"] += 1

        # 更新平均处理时间
        self.stats["avg_processing_time"] = (
            self.stats["avg_processing_time"] * (self.stats["total_operations"] - 1)
            + metrics.processing_time
        ) / self.stats["total_operations"]

        # 更新错误计数
        if metrics.error_rate > self.thresholds["error_rate"]:
            self.stats["error_count"] += 1

    def _check_alerts(self, metrics: PerformanceMetrics):
        """检查警报"""
        alerts = []

        for metric_name, threshold in self.thresholds.items():
            value = getattr(metrics, metric_name)
            if value > threshold:
                alerts.append(f"{metric_name}: {value:.2f} (阈值: {threshold})")

        if alerts:
            alert_msg = f"⚠️  性能警报: {'; '.join(alerts)}"
            self.logger.warning(alert_msg)

            # 触发回调
            for callback in self.alert_callbacks:
                try:
                    callback(metrics, alerts)
                except Exception as e:
                    self.logger.error(f"回调函数执行失败: {e}")

    def _log_performance(self, metrics: PerformanceMetrics):
        """记录性能日志"""
        if len(self.performance_history) % 10 == 0:  # 每10个指标记录一次
            self.logger.info(
                f"性能指标 - GPU: {metrics.gpu_utilization:.1f}%, "
                f"CPU: {metrics.cpu_utilization:.1f}%, "
                f"内存: {metrics.gpu_memory_usage:.1f}MB, "
                f"处理时间: {metrics.processing_time:.3f}s, "
                f"吞吐量: {metrics.throughput:.2f}"
            )

    def register_alert_callback(self, callback: Callable):
        """注册警报回调函数"""
        self.alert_callbacks.append(callback)

    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """获取当前性能指标"""
        return self.current_metrics

    def get_performance_history(self, last_n: int = 60) -> List[PerformanceMetrics]:
        """获取性能历史"""
        return list(self.performance_history)[-last_n:]

    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能总结"""
        if len(self.performance_history) == 0:
            return {}

        gpu_utils = [m.gpu_utilization for m in self.performance_history]
        cpu_utils = [m.cpu_utilization for m in self.performance_history]
        gpu_mem = [m.gpu_memory_usage for m in self.performance_history]
        proc_times = [m.processing_time for m in self.performance_history]

        return {
            "gpu_utilization_avg": np.mean(gpu_utils),
            "gpu_utilization_max": np.max(gpu_utils),
            "cpu_utilization_avg": np.mean(cpu_utils),
            "cpu_utilization_max": np.max(cpu_utils),
            "gpu_memory_avg": np.mean(gpu_mem),
            "gpu_memory_max": np.max(gpu_mem),
            "processing_time_avg": np.mean(proc_times),
            "processing_time_max": np.max(proc_times),
            "total_operations": self.stats["total_operations"],
            "gpu_operations": self.stats["gpu_operations"],
            "cpu_operations": self.stats["cpu_operations"],
            "error_rate": self._calculate_error_rate(),
        }

    def get_workload_recommendations(self) -> List[str]:
        """获取工作负载建议"""
        recommendations = []
        summary = self.get_performance_summary()

        if not summary:
            return []

        # GPU使用率分析
        if summary["gpu_utilization_avg"] > 80:
            recommendations.append(
                "⚠️ GPU使用率过高，考虑增加GPU任务批处理或使用分布式处理"
            )
        elif summary["gpu_utilization_avg"] < 30:
            recommendations.append(
                "⚡ GPU利用率较低，建议增加GPU并行任务或优化任务分配"
            )

        # CPU使用率分析
        if summary["cpu_utilization_avg"] > 80:
            recommendations.append("⚠️ CPU使用率过高，考虑卸载更多任务到GPU")
        elif summary["cpu_utilization_avg"] < 50:
            recommendations.append("⚡ CPU利用率较低，可以考虑增加CPU并行任务")

        # 内存使用分析
        if summary["gpu_memory_avg"] > 70:
            recommendations.append(
                "⚠️ GPU内存使用接近极限，建议减少数据批次或优化内存管理"
            )
        elif summary["gpu_memory_avg"] < 20:
            recommendations.append("⚡ GPU内存使用率较低，可以考虑处理更大的数据集")

        # 性能分析
        if summary["processing_time_avg"] > 5.0:
            recommendations.append("⚠️ 平均处理时间较长，建议优化算法或使用GPU加速")
        elif summary["processing_time_avg"] < 0.5:
            recommendations.append("✅ 处理性能良好，可以考虑增加复杂度或处理更多数据")

        # 错误率分析
        if summary["error_rate"] > 0.02:
            recommendations.append("⚠️ 错误率较高，建议检查数据质量和算法稳定性")

        return recommendations

    def predict_performance(self, workload: WorkloadInfo) -> Dict[str, float]:
        """预测性能表现"""
        summary = self.get_performance_summary()

        if not summary:
            return {
                "predicted_gpu_time": workload.estimated_gpu_time,
                "predicted_cpu_time": workload.estimated_cpu_time,
                "predicted_speedup": (
                    workload.estimated_cpu_time / workload.estimated_gpu_time
                    if workload.estimated_gpu_time > 0
                    else 1.0
                ),
            }

        # 基于当前负载调整预测
        gpu_load_factor = summary["gpu_utilization_avg"] / 100.0
        cpu_load_factor = summary["cpu_utilization_avg"] / 100.0

        predicted_gpu_time = workload.estimated_gpu_time * (1 + gpu_load_factor * 0.5)
        predicted_cpu_time = workload.estimated_cpu_time * (1 + cpu_load_factor * 0.3)

        # 基于数据量调整
        size_factor = min(workload.data_size / 10000, 10.0)  # 最大10倍调整
        predicted_gpu_time *= size_factor
        predicted_cpu_time *= size_factor

        # 基于复杂度调整
        complexity_factor = workload.complexity_score / 5.0  # 复杂度评分
        predicted_gpu_time *= complexity_factor
        predicted_cpu_time *= complexity_factor

        return {
            "predicted_gpu_time": predicted_gpu_time,
            "predicted_cpu_time": predicted_cpu_time,
            "predicted_speedup": (
                predicted_cpu_time / predicted_gpu_time
                if predicted_gpu_time > 0
                else 1.0
            ),
            "gpu_load_factor": gpu_load_factor,
            "cpu_load_factor": cpu_load_factor,
        }

    def get_optimal_allocation(
        self, workloads: List[WorkloadInfo]
    ) -> Dict[str, List[str]]:
        """获取最优的任务分配方案"""
        gpu_tasks = []
        cpu_tasks = []
        mixed_tasks = []

        for workload in workloads:
            prediction = self.predict_performance(workload)

            if prediction["predicted_speedup"] > 3.0:
                gpu_tasks.append(workload.task_type)
            elif prediction["predicted_speedup"] < 1.5:
                cpu_tasks.append(workload.task_type)
            else:
                mixed_tasks.append(workload.task_type)

        return {
            "gpu_optimal": gpu_tasks,
            "cpu_optimal": cpu_tasks,
            "mixed_optimal": mixed_tasks,
        }

    def generate_performance_report(self) -> str:
        """生成性能报告"""
        summary = self.get_performance_summary()
        recommendations = self.get_workload_recommendations()

        report = f"""
MyStocks 实时性能监控报告
========================

监控时间: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))}

📊 当前性能状态:
  GPU使用率: {summary.get("gpu_utilization_avg", 0):.1f}% (最高: {summary.get("gpu_utilization_max", 0):.1f}%)
  CPU使用率: {summary.get("cpu_utilization_avg", 0):.1f}% (最高: {summary.get("cpu_utilization_max", 0):.1f}%)
  GPU内存: {summary.get("gpu_memory_avg", 0):.1f}MB (最高: {summary.get("gpu_memory_max", 0):.1f}MB)
  平均处理时间: {summary.get("processing_time_avg", 0):.3f}秒
  总操作次数: {summary.get("total_operations", 0)}
  GPU操作次数: {summary.get("gpu_operations", 0)}
  CPU操作次数: {summary.get("cpu_operations", 0)}
  错误率: {summary.get("error_rate", 0):.2%}

💡 优化建议:
"""

        for i, recommendation in enumerate(recommendations, 1):
            report += f"{i}. {recommendation}\n"

        report += f"""

🎯 GPU/CPU分配建议:
  GPU优先任务: {len(recommendations)} 个
  CPU优先任务: {len(recommendations)} 个
  混合模式任务: {len(recommendations)} 个
"""

        return report


def main():
    """主函数 - 实时监控示例"""
    # 创建监控器
    monitor = RealTimePerformanceMonitor(monitoring_interval=1.0)

    # 注册警报回调
    def alert_handler(metrics, alerts):
        print(f"🚨 警报: {alerts}")

    monitor.register_alert_callback(alert_handler)

    # 开始监控
    monitor.start_monitoring()

    try:
        # 模拟一些工作负载
        for i in range(30):
            print(f"监控第 {i + 1} 秒...")
            time.sleep(1)

            if i % 10 == 0:
                # 获取当前状态
                metrics = monitor.get_current_metrics()
                if metrics:
                    print(
                        f"  GPU: {metrics.gpu_utilization:.1f}%, "
                        f"CPU: {metrics.cpu_utilization:.1f}%, "
                        f"内存: {metrics.gpu_memory_usage:.1f}MB"
                    )

                # 生成报告
                report = monitor.generate_performance_report()
                print(f"\\n{report}")

    except KeyboardInterrupt:
        print("停止监控...")
    finally:
        monitor.stop_monitoring()


if __name__ == "__main__":
    main()
