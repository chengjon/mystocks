#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks 高级性能监控器

提供实时性能监控、智能分析和动态优化功能。
"""

import asyncio
import time
import statistics
import psutil
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from queue import Queue
import threading


class AlertLevel(Enum):
    """告警级别"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class PerformanceAlert:
    """性能告警"""

    timestamp: datetime
    level: AlertLevel
    category: str
    message: str
    metric_name: str
    current_value: float
    threshold: float
    severity: str = "medium"
    resolved: bool = False
    resolution_time: Optional[datetime] = None


@dataclass
class OptimizationSuggestion:
    """优化建议"""

    id: str
    priority: int
    category: str
    title: str
    description: str
    impact_score: float
    implementation_difficulty: float
    estimated_improvement: float
    confidence_level: float
    code_snippet: Optional[str] = None
    references: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


class RealTimePerformanceMonitor:
    """实时性能监控器"""

    def __init__(self, check_interval: float = 1.0):
        self.check_interval = check_interval
        self.is_monitoring = False
        self.metrics_history: Dict[str, List[Tuple[float, datetime]]] = {}
        self.alerts: List[PerformanceAlert] = []
        self.alert_queue = Queue()
        self.monitoring_thread: Optional[threading.Thread] = None
        self.callbacks: List[Callable] = []
        self.thresholds: Dict[str, Dict[str, float]] = self._initialize_thresholds()

    def _initialize_thresholds(self) -> Dict[str, Dict[str, float]]:
        """初始化监控阈值"""
        return {
            "cpu": {"warning": 70.0, "error": 85.0, "critical": 95.0},
            "memory": {"warning": 70.0, "error": 85.0, "critical": 95.0},
            "disk_io": {"warning": 80.0, "error": 90.0, "critical": 98.0},
            "network": {"warning": 70.0, "error": 85.0, "critical": 95.0},
            "test_execution": {"warning": 5.0, "error": 10.0, "critical": 30.0},
        }

    def start_monitoring(self):
        """开始监控"""
        if self.is_monitoring:
            return

        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        print("🔴 实时性能监控已启动")

    def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
        print("🟢 实时性能监控已停止")

    def add_callback(self, callback: Callable):
        """添加回调函数"""
        self.callbacks.append(callback)

    def _monitoring_loop(self):
        """监控循环"""
        while self.is_monitoring:
            try:
                self._collect_metrics()
                self._analyze_metrics()
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"❌ 监控错误: {e}")

    def _collect_metrics(self):
        """收集性能指标"""
        process = psutil.Process()

        # CPU指标
        cpu_percent = psutil.cpu_percent(interval=0.1)
        self._record_metric("cpu_usage", cpu_percent)

        # 内存指标
        memory_info = process.memory_info()
        memory_percent = process.memory_percent()
        self._record_metric("memory_usage", memory_percent)
        self._record_metric("memory_rss", memory_info.rss / 1024 / 1024)

        # 磁盘I/O指标
        disk_io = psutil.disk_io_counters()
        if disk_io:
            self._record_metric("disk_read_bytes", disk_io.read_bytes)
            self._record_metric("disk_write_bytes", disk_io.write_bytes)

        # 网络I/O指标
        net_io = psutil.net_io_counters()
        if net_io:
            self._record_metric("network_sent_bytes", net_io.bytes_sent)
            self._record_metric("network_recv_bytes", net_io.bytes_recv)

        # 系统负载
        load_avg = psutil.getloadavg()
        self._record_metric("system_load_1min", load_avg[0])
        self._record_metric("system_load_5min", load_avg[1])
        self._record_metric("system_load_15min", load_avg[2])

    def _record_metric(self, metric_name: str, value: float):
        """记录指标"""
        if metric_name not in self.metrics_history:
            self.metrics_history[metric_name] = []

        self.metrics_history[metric_name].append((value, datetime.now()))

        # 保持历史数据大小
        if len(self.metrics_history[metric_name]) > 1000:
            self.metrics_history[metric_name] = self.metrics_history[metric_name][-1000:]

    def _analyze_metrics(self):
        """分析指标并生成告警"""
        for metric_name, history in self.metrics_history.items():
            if len(history) < 10:
                continue

            latest_value = history[-1][0]
            thresholds = self.thresholds.get(metric_name, {})

            # 检查阈值
            if thresholds:
                if latest_value >= thresholds.get("critical", 100):
                    alert = PerformanceAlert(
                        timestamp=datetime.now(),
                        level=AlertLevel.CRITICAL,
                        category=metric_name,
                        message=f"{metric_name} 达到关键级别: {latest_value:.2f}",
                        metric_name=metric_name,
                        current_value=latest_value,
                        threshold=thresholds["critical"],
                        severity="critical",
                    )
                    self._add_alert(alert)

                elif latest_value >= thresholds.get("error", 90):
                    alert = PerformanceAlert(
                        timestamp=datetime.now(),
                        level=AlertLevel.ERROR,
                        category=metric_name,
                        message=f"{metric_name} 达到错误级别: {latest_value:.2f}",
                        metric_name=metric_name,
                        current_value=latest_value,
                        threshold=thresholds["error"],
                        severity="high",
                    )
                    self._add_alert(alert)

                elif latest_value >= thresholds.get("warning", 70):
                    alert = PerformanceAlert(
                        timestamp=datetime.now(),
                        level=AlertLevel.WARNING,
                        category=metric_name,
                        message=f"{metric_name} 达到警告级别: {latest_value:.2f}",
                        metric_name=metric_name,
                        current_value=latest_value,
                        threshold=thresholds["warning"],
                        severity="medium",
                    )
                    self._add_alert(alert)

        # 通知回调函数
        for callback in self.callbacks:
            try:
                callback(self.alerts)
            except Exception as e:
                print(f"❌ 回调函数执行错误: {e}")

    def _add_alert(self, alert: PerformanceAlert):
        """添加告警"""
        self.alerts.append(alert)
        self.alert_queue.put(alert)
        print(f"⚠️  {alert.level.value.upper()}: {alert.message}")

    def get_current_metrics(self) -> Dict[str, float]:
        """获取当前指标"""
        current_metrics = {}
        for metric_name, history in self.metrics_history.items():
            if history:
                current_metrics[metric_name] = history[-1][0]
        return current_metrics

    def get_metric_trend(self, metric_name: str, window_size: int = 10) -> str:
        """获取指标趋势"""
        if metric_name not in self.metrics_history:
            return "unknown"

        history = self.metrics_history[metric_name]
        if len(history) < window_size:
            window_size = len(history)

        recent_values = [h[0] for h in history[-window_size:]]
        if len(recent_values) < 2:
            return "stable"

        # 计算趋势
        trend = "stable"
        if recent_values[-1] > recent_values[0] * 1.05:
            trend = "increasing"
        elif recent_values[-1] < recent_values[0] * 0.95:
            trend = "decreasing"

        return trend

    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        current_metrics = self.get_current_metrics()
        summary = {
            "timestamp": datetime.now().isoformat(),
            "current_metrics": current_metrics,
            "active_alerts": len([a for a in self.alerts if not a.resolved]),
            "total_alerts": len(self.alerts),
            "system_health": self._calculate_system_health(current_metrics),
        }

        return summary

    def _calculate_system_health(self, metrics: Dict[str, float]) -> str:
        """计算系统健康状态"""
        health_score = 100.0
        critical_thresholds = 0

        for metric_name, value in metrics.items():
            thresholds = self.thresholds.get(metric_name, {})
            if thresholds:
                if value >= thresholds.get("critical", 100):
                    health_score -= 30
                    critical_thresholds += 1
                elif value >= thresholds.get("error", 90):
                    health_score -= 20
                elif value >= thresholds.get("warning", 70):
                    health_score -= 10

        if health_score >= 80:
            return "excellent"
        elif health_score >= 60:
            return "good"
        elif health_score >= 40:
            return "warning"
        else:
            return "critical"


class IntelligentPerformanceAnalyzer:
    """智能性能分析器"""

    def __init__(self):
        self.optimization_suggestions: List[OptimizationSuggestion] = []
        self.patterns: Dict[str, Any] = {}
        self.baseline_metrics: Dict[str, float] = {}

    def analyze_performance_patterns(
        self, metrics_history: Dict[str, List[Tuple[float, datetime]]]
    ) -> List[OptimizationSuggestion]:
        """分析性能模式并生成优化建议"""
        suggestions = []

        # 分析CPU使用模式
        if "cpu_usage" in metrics_history:
            cpu_pattern = self._analyze_cpu_pattern(metrics_history["cpu_usage"])
            if cpu_pattern["has_pattern"]:
                suggestions.append(self._create_cpu_optimization_suggestion(cpu_pattern))

        # 分析内存使用模式
        if "memory_usage" in metrics_history:
            memory_pattern = self._analyze_memory_pattern(metrics_history["memory_usage"])
            if memory_pattern["has_pattern"]:
                suggestions.append(self._create_memory_optimization_suggestion(memory_pattern))

        # 分析测试执行模式
        if "test_execution_time" in metrics_history:
            test_pattern = self._analyze_test_execution_pattern(metrics_history["test_execution_time"])
            if test_pattern["has_pattern"]:
                suggestions.append(self._create_test_optimization_suggestion(test_pattern))

        # 按优先级排序
        suggestions.sort(key=lambda x: x.priority)

        self.optimization_suggestions.extend(suggestions)
        return suggestions

    def _analyze_cpu_pattern(self, history: List[Tuple[float, datetime]]) -> Dict[str, Any]:
        """分析CPU使用模式"""
        if len(history) < 20:
            return {"has_pattern": False}

        values = [h[0] for h in history[-20:]]
        avg_cpu = statistics.mean(values)
        max_cpu = max(values)
        min_cpu = min(values)

        # 识别高峰时段
        peak_threshold = avg_cpu + (max_cpu - avg_cpu) * 0.7
        peak_times = [i for i, v in enumerate(values) if v > peak_threshold]

        pattern = {
            "has_pattern": len(peak_times) > 3,
            "avg_cpu": avg_cpu,
            "max_cpu": max_cpu,
            "min_cpu": min_cpu,
            "peak_times": peak_times,
            "volatility": statistics.stdev(values) if len(values) > 1 else 0,
        }

        return pattern

    def _analyze_memory_pattern(self, history: List[Tuple[float, datetime]]) -> Dict[str, Any]:
        """分析内存使用模式"""
        if len(history) < 20:
            return {"has_pattern": False}

        values = [h[0] for h in history[-20:]]
        avg_memory = statistics.mean(values)
        trend = self._calculate_trend(values)

        pattern = {
            "has_pattern": True,
            "avg_memory": avg_memory,
            "trend": trend,
            "is_increasing": trend == "increasing",
            "memory_leak_suspected": trend == "increasing" and avg_memory > 80,
        }

        return pattern

    def _analyze_test_execution_pattern(self, history: List[Tuple[float, datetime]]) -> Dict[str, Any]:
        """分析测试执行模式"""
        if len(history) < 10:
            return {"has_pattern": False}

        values = [h[0] for h in history[-10:]]
        avg_time = statistics.mean(values)
        trend = self._calculate_trend(values)

        # 检测异常值
        q1, q3 = np.percentile(values, [25, 75])
        iqr = q3 - q1
        outliers = [v for v in values if v < q1 - 1.5 * iqr or v > q3 + 1.5 * iqr]

        pattern = {
            "has_pattern": True,
            "avg_execution_time": avg_time,
            "trend": trend,
            "outlier_count": len(outliers),
            "consistency": 1 - (len(outliers) / len(values)),
        }

        return pattern

    def _calculate_trend(self, values: List[float]) -> str:
        """计算趋势"""
        if len(values) < 2:
            return "stable"

        if values[-1] > values[0] * 1.1:
            return "increasing"
        elif values[-1] < values[0] * 0.9:
            return "decreasing"
        else:
            return "stable"

    def _create_cpu_optimization_suggestion(self, pattern: Dict[str, Any]) -> OptimizationSuggestion:
        """创建CPU优化建议"""
        return OptimizationSuggestion(
            id="cpu_optimization_001",
            priority=1,
            category="CPU",
            title="CPU使用优化",
            description=f"检测到CPU平均使用率 {pattern['avg_cpu']:.1f}%，存在 {len(pattern['peak_times'])} 个高峰时段",
            impact_score=0.8,
            implementation_difficulty=0.4,
            estimated_improvement=0.6,
            confidence_level=0.7,
            references=["https://docs.python.org/3/library/concurrent.html"],
        )

    def _create_memory_optimization_suggestion(self, pattern: Dict[str, Any]) -> OptimizationSuggestion:
        """创建内存优化建议"""
        title = "内存泄漏修复" if pattern["memory_leak_suspected"] else "内存使用优化"
        description = f"检测到内存使用{pattern['trend']}，当前平均使用率 {pattern['avg_memory']:.1f}%"

        return OptimizationSuggestion(
            id="memory_optimization_002",
            priority=2,
            category="Memory",
            title=title,
            description=description,
            impact_score=0.9,
            implementation_difficulty=0.6,
            estimated_improvement=0.5,
            confidence_level=0.8,
            references=["https://docs.python.org/3/library/gc.html"],
        )

    def _create_test_optimization_suggestion(self, pattern: Dict[str, Any]) -> OptimizationSuggestion:
        """创建测试优化建议"""
        return OptimizationSuggestion(
            id="test_optimization_003",
            priority=3,
            category="Test",
            title="测试执行优化",
            description=f"测试平均执行时间 {pattern['avg_execution_time']:.2f}s，趋势: {pattern['trend']}",
            impact_score=0.7,
            implementation_difficulty=0.5,
            estimated_improvement=0.4,
            confidence_level=0.9,
            references=["https://pytest.org/"],
        )

    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """获取优化建议列表"""
        recommendations = []
        for suggestion in self.optimization_suggestions:
            recommendations.append(
                {
                    "id": suggestion.id,
                    "priority": suggestion.priority,
                    "category": suggestion.category,
                    "title": suggestion.title,
                    "description": suggestion.description,
                    "impact_score": suggestion.impact_score,
                    "implementation_difficulty": suggestion.implementation_difficulty,
                    "estimated_improvement": suggestion.estimated_improvement,
                    "confidence_level": suggestion.confidence_level,
                    "created_at": suggestion.created_at.isoformat(),
                }
            )

        return recommendations


class DynamicPerformanceOptimizer:
    """动态性能优化器"""

    def __init__(self):
        self.monitor = RealTimePerformanceMonitor()
        self.analyzer = IntelligentPerformanceAnalyzer()
        self.active_optimizations: Dict[str, Any] = {}
        self.optimization_results: List[Dict[str, Any]] = []

    def start_system_monitoring(self):
        """启动系统监控"""
        self.monitor.start_monitoring()

        # 添加告警回调
        self.monitor.add_callback(self._handle_alerts)

    def stop_system_monitoring(self):
        """停止系统监控"""
        self.monitor.stop_monitoring()

    def _handle_alerts(self, alerts: List[PerformanceAlert]):
        """处理告警"""
        for alert in alerts:
            if not alert.resolved and alert.level in [
                AlertLevel.ERROR,
                AlertLevel.CRITICAL,
            ]:
                print(f"🔧 自动处理告警: {alert.message}")
                self._automatically_optimize(alert)

    async def automatically_optimize(self, alert: PerformanceAlert):
        """自动优化"""
        optimization_id = f"auto_opt_{alert.category}_{int(time.time())}"

        try:
            if alert.category == "cpu":
                await self._optimize_cpu_usage()
            elif alert.category == "memory":
                await self._optimize_memory_usage()
            elif alert.category == "network":
                await self._optimize_network_usage()

            # 记录优化结果
            result = {
                "optimization_id": optimization_id,
                "alert_handled": alert.message,
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
            }
            self.optimization_results.append(result)

        except Exception as e:
            print(f"❌ 自动优化失败: {e}")

    async def _optimize_cpu_usage(self):
        """优化CPU使用"""
        print("🔧 执行CPU使用优化...")
        # 降低线程优先级
        try:
            process = psutil.Process()
            process.nice(10)  # 降低优先级
        except:
            pass

        # 限制CPU核心使用
        cpu_count = psutil.cpu_count()
        if cpu_count > 4:
            print(f"建议限制CPU使用核心数: {cpu_count} -> 4")

    async def _optimize_memory_usage(self):
        """优化内存使用"""
        print("🔧 执行内存使用优化...")
        import gc

        gc.collect()  # 强制垃圾回收

        # 清理缓存
        for optimization in self.active_optimizations.values():
            if "cache" in optimization:
                optimization["cache"].clear()

    async def _optimize_network_usage(self):
        """优化网络使用"""
        print("🔧 执行网络使用优化...")
        # 这里可以添加网络优化逻辑，如连接池管理

    def run_performance_analysis(self, duration: int = 60) -> Dict[str, Any]:
        """运行性能分析"""
        print(f"🔍 开始性能分析，持续 {duration} 秒...")

        analysis_results = {
            "start_time": datetime.now().isoformat(),
            "duration_seconds": duration,
            "metrics_collected": {},
            "alerts_generated": [],
            "optimization_suggestions": [],
            "performance_summary": {},
        }

        start_time = time.time()

        while time.time() - start_time < duration:
            # 收集指标
            current_metrics = self.monitor.get_current_metrics()
            analysis_results["metrics_collected"] = current_metrics

            # 获取系统摘要
            summary = self.monitor.get_performance_summary()
            analysis_results["performance_summary"] = summary

            # 分析模式
            suggestions = self.analyzer.analyze_performance_patterns(self.monitor.metrics_history)
            analysis_results["optimization_suggestions"] = suggestions

            time.sleep(5)

        analysis_results["end_time"] = datetime.now().isoformat()
        return analysis_results

    def generate_performance_report(self) -> str:
        """生成性能报告"""
        report = "# MyStocks 性能分析报告\n\n"
        report += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        # 当前系统状态
        summary = self.monitor.get_performance_summary()
        report += "## 当前系统状态\n\n"
        report += f"- 健康状态: {summary['system_health']}\n"
        report += f"- 活跃告警: {summary['active_alerts']}\n"
        report += f"- 总告警数: {summary['total_alerts']}\n\n"

        # 当前指标
        metrics = self.monitor.get_current_metrics()
        report += "## 当前性能指标\n\n"
        for metric_name, value in metrics.items():
            report += f"- {metric_name}: {value:.2f}\n"
        report += "\n"

        # 优化建议
        suggestions = self.analyzer.get_optimization_recommendations()
        if suggestions:
            report += "## 优化建议\n\n"
            for suggestion in suggestions[:5]:  # 显示前5个建议
                report += f"### {suggestion['title']}\n"
                report += f"**优先级**: {suggestion['priority']}\n"
                report += f"**影响分数**: {suggestion['impact_score']:.2f}\n"
                report += f"**估计改进**: {(suggestion['estimated_improvement'] * 100):.1f}%\n"
                report += f"**描述**: {suggestion['description']}\n\n"

        # 历史优化结果
        if self.optimization_results:
            report += "## 自动优化历史\n\n"
            for result in self.optimization_results[-5:]:  # 显示最近5次
                report += f"- {result['timestamp']}: {result['alert_handled']}\n"
            report += "\n"

        return report


# 使用示例
async def demo_advanced_performance_monitor():
    """演示高级性能监控功能"""
    print("🚀 演示高级性能监控器功能")

    optimizer = DynamicPerformanceOptimizer()

    # 启动监控
    optimizer.start_system_monitoring()

    # 运行性能分析
    analysis_results = optimizer.run_performance_analysis(duration=10)
    print(f"📊 性能分析完成: {analysis_results}")

    # 生成报告
    report = optimizer.generate_performance_report()
    print(f"\n📋 性能报告:\n{report}")

    # 停止监控
    optimizer.stop_system_monitoring()


if __name__ == "__main__":
    # 运行演示
    asyncio.run(demo_advanced_performance_monitor())
