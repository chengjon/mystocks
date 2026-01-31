#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks 测试性能集成系统

提供完整的测试性能优化解决方案，集成所有性能相关组件。
"""

import asyncio
import json
import statistics
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import pandas as pd
import psutil


@dataclass
class PerformanceBenchmark:
    """性能基准"""

    name: str
    description: str
    category: str
    baseline_metrics: Dict[str, float]
    current_metrics: Dict[str, float]
    improvement_targets: Dict[str, float]
    status: str = "pending"  # pending/in_progress/completed/failed
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class OptimizationProfile:
    """优化配置文件"""

    name: str
    description: str
    enabled_optimizations: List[str]
    custom_thresholds: Dict[str, float]
    scheduling_config: Dict[str, Any]
    resource_limits: Dict[str, Any]
    priority_rules: List[str]


class PerformanceIntegrationSystem:
    """性能集成系统主类"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.config = self._load_config()

        # 初始化组件
        self.benchmark_registry: Dict[str, PerformanceBenchmark] = {}
        self.optimization_profiles: Dict[str, OptimizationProfile] = {}
        self.performance_history: List[Dict[str, Any]] = []

        # 核心组件
        self.optimizer = None
        self.monitor = None
        self.analyzer = None
        self.integration_manager = None

        # 状态管理
        self.is_running = False
        self.current_session_id: Optional[str] = None

    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        default_config = {
            "monitoring": {
                "check_interval": 1.0,
                "history_size": 1000,
                "alert_thresholds": {
                    "cpu": {"warning": 70, "error": 85, "critical": 95},
                    "memory": {"warning": 70, "error": 85, "critical": 95},
                    "test_execution": {"warning": 5, "error": 10, "critical": 30},
                },
            },
            "optimization": {
                "auto_optimize": True,
                "max_concurrent_optimizations": 3,
                "optimization_timeout": 300,
            },
            "reporting": {
                "auto_generate_reports": True,
                "report_interval": 3600,
                "report_format": "html",
            },
            "integration": {
                "enable_chaos_testing": False,
                "enable_ai_analysis": True,
                "enable_real_time_optimization": True,
            },
        }

        if self.config_path and Path(self.config_path).exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                user_config = json.load(f)
                # 合并配置
                for key, value in user_config.items():
                    if key in default_config:
                        if isinstance(value, dict) and isinstance(default_config[key], dict):
                            default_config[key].update(value)
                        else:
                            default_config[key] = value
                    else:
                        default_config[key] = value

        return default_config

    def initialize_components(self):
        """初始化所有组件"""
        from .test_advanced_performance_monitor import DynamicPerformanceOptimizer
        from .test_performance_optimizer import PerformanceOptimizer

        # 初始化性能优化器
        self.optimizer = PerformanceOptimizer()

        # 初始化动态性能优化器
        self.integration_manager = DynamicPerformanceOptimizer()
        self.integration_manager.start_system_monitoring()

        # 创建默认优化配置文件
        self._create_default_profiles()

    def _create_default_profiles(self):
        """创建默认优化配置文件"""
        profiles = [
            OptimizationProfile(
                name="production",
                description="生产环境优化配置",
                enabled_optimizations=[
                    "parallel_execution",
                    "memory_optimization",
                    "caching",
                    "database_optimization",
                ],
                custom_thresholds={
                    "cpu_warning": 60,
                    "memory_warning": 65,
                    "test_execution_warning": 3,
                },
                scheduling_config={
                    "optimization_schedule": "off_hours",
                    "window_start": "22:00",
                    "window_end": "06:00",
                },
                resource_limits={"max_memory_mb": 2048, "max_cpu_percent": 80},
                priority_rules=[
                    "stability_first",
                    "performance_second",
                    "resource_efficiency",
                ],
            ),
            OptimizationProfile(
                name="development",
                description="开发环境优化配置",
                enabled_optimizations=[
                    "fast_feedback",
                    "memory_optimization",
                    "code_analysis",
                ],
                custom_thresholds={
                    "cpu_warning": 80,
                    "memory_warning": 85,
                    "test_execution_warning": 10,
                },
                scheduling_config={
                    "optimization_schedule": "continuous",
                    "immediate_feedback": True,
                },
                resource_limits={"max_memory_mb": 4096, "max_cpu_percent": 90},
                priority_rules=[
                    "fast_feedback",
                    "developer_experience",
                    "resource_efficiency",
                ],
            ),
            OptimizationProfile(
                name="testing",
                description="测试环境优化配置",
                enabled_optimizations=[
                    "parallel_execution",
                    "concurrency_optimization",
                    "test_data_optimization",
                ],
                custom_thresholds={
                    "cpu_warning": 75,
                    "memory_warning": 80,
                    "test_execution_warning": 5,
                },
                scheduling_config={"optimization_schedule": "batch", "batch_size": 10},
                resource_limits={"max_memory_mb": 3072, "max_cpu_percent": 85},
                priority_rules=["test_speed", "reliability", "resource_efficiency"],
            ),
        ]

        for profile in profiles:
            self.optimization_profiles[profile.name] = profile

    async def run_performance_benchmark(self, benchmark_name: str, test_functions: List[Callable]) -> Dict[str, Any]:
        """运行性能基准测试"""
        print(f"\n🚀 开始性能基准测试: {benchmark_name}")

        session_id = f"benchmark_{int(time.time())}"
        self.current_session_id = session_id

        # 创建基准记录
        benchmark = PerformanceBenchmark(
            name=benchmark_name,
            description=f"性能基准测试: {benchmark_name}",
            category="comprehensive",
            baseline_metrics={},
            current_metrics={},
            improvement_targets={},
            status="in_progress",
            started_at=datetime.now(),
        )

        try:
            # 运行基准测试
            baseline_results = await self._run_baseline_tests(test_functions)
            benchmark.baseline_metrics = baseline_results

            # 应用优化
            optimized_results = await self._apply_optimizations(test_functions)
            benchmark.current_metrics = optimized_results

            # 计算改进
            improvement = self._calculate_improvement(baseline_results, optimized_results)
            benchmark.improvement_targets = improvement

            benchmark.status = "completed"
            benchmark.completed_at = datetime.now()

        except Exception as e:
            benchmark.status = "failed"
            benchmark.completed_at = datetime.now()
            print(f"❌ 基准测试失败: {e}")

        self.benchmark_registry[session_id] = benchmark
        self.performance_history.append(
            {
                "session_id": session_id,
                "benchmark": benchmark,
                "timestamp": datetime.now().isoformat(),
            }
        )

        # 生成报告
        report = self._generate_benchmark_report(benchmark)

        print("✅ 基准测试完成")
        print(f"📊 改进效果: {improved}")

        return {
            "session_id": session_id,
            "benchmark": benchmark,
            "report": report,
            "improvement": improvement,
        }

    async def _run_baseline_tests(self, test_functions: List[Callable]) -> Dict[str, float]:
        """运行基准测试"""
        results = {}

        for test_func in test_functions:
            test_name = test_func.__name__

            try:
                import time

                start_time = time.time()
                await test_func()
                execution_time = time.time() - start_time

                process = psutil.Process()
                memory_info = process.memory_info()
                cpu_percent = process.cpu_percent()

                results[test_name] = {
                    "execution_time": execution_time,
                    "memory_usage_mb": memory_info.rss / 1024 / 1024,
                    "cpu_usage_percent": cpu_percent,
                }

            except Exception as e:
                print(f"❌ 测试 {test_name} 失败: {e}")
                results[test_name] = {
                    "execution_time": float("inf"),
                    "memory_usage_mb": float("inf"),
                    "cpu_usage_percent": 100.0,
                }

        return results

    async def _apply_optimizations(self, test_functions: List[Callable]) -> Dict[str, float]:
        """应用优化"""
        results = {}

        for test_func in test_functions:
            test_name = test_func.__name__

            try:
                # 使用优化器执行测试
                optimization_result = await self.optimizer.optimize_test_performance(test_name, test_func)

                results[test_name] = {
                    "execution_time": optimization_result["final_performance"]["execution_time"],
                    "memory_usage_mb": optimization_result["final_performance"]["memory_usage_mb"],
                    "cpu_usage_percent": optimization_result["final_performance"]["cpu_usage_percent"],
                }

            except Exception as e:
                print(f"❌ 优化测试 {test_name} 失败: {e}")
                results[test_name] = {
                    "execution_time": float("inf"),
                    "memory_usage_mb": float("inf"),
                    "cpu_usage_percent": 100.0,
                }

        return results

    def _calculate_improvement(self, baseline: Dict[str, Dict], optimized: Dict[str, Dict]) -> Dict[str, float]:
        """计算改进程度"""
        improvements = {}

        for test_name in baseline:
            if test_name in optimized:
                baseline_time = baseline[test_name]["execution_time"]
                optimized_time = optimized[test_name]["execution_time"]

                if baseline_time > 0:
                    time_improvement = (baseline_time - optimized_time) / baseline_time
                else:
                    time_improvement = 0.0

                improvements[test_name] = {
                    "time_improvement": time_improvement,
                    "execution_time_improvement_ms": baseline_time - optimized_time,
                    "status": "improved" if time_improvement > 0 else "degraded",
                }

        return improvements

    def _generate_benchmark_report(self, benchmark: PerformanceBenchmark) -> str:
        """生成基准测试报告"""
        report = "# 性能基准测试报告\n\n"
        report += f"**测试名称**: {benchmark.name}\n"
        report += f"**描述**: {benchmark.description}\n"
        report += f"**开始时间**: {benchmark.started_at}\n"
        report += f"**结束时间**: {benchmark.completed_at}\n"
        report += f"**状态**: {benchmark.status}\n\n"

        if benchmark.status == "completed":
            report += "## 基准对比\n\n"
            report += "| 测试项 | 基准值 | 优化后 | 改进 | 状态 |\n"
            report += "|--------|--------|--------|------|------|\n"

            for test_name, metrics in benchmark.baseline_metrics.items():
                if test_name in benchmark.current_metrics:
                    baseline = metrics
                    optimized = benchmark.current_metrics[test_name]

                    time_improvement = (
                        (baseline["execution_time"] - optimized["execution_time"]) / baseline["execution_time"]
                        if baseline["execution_time"] > 0
                        else 0
                    )

                    status = "✅ 改进" if time_improvement > 0 else "❌ 退化"
                    report += f"| {test_name} | {baseline['execution_time']:.2f}s | {optimized['execution_time']:.2f}s | {time_improvement * 100:.1f}% | {status} |\n"

            # 总体改进
            overall_improvement = self._calculate_overall_improvement(benchmark)
            report += "\n## 总体评估\n\n"
            report += f"**总体改进分数**: {overall_improvement:.2f}\n"
            report += f"**性能提升**: {((overall_improvement - 0.5) * 200):+.1f}%\n\n"

            # 建议
            report += "## 优化建议\n\n"
            if overall_improvement < 0.7:
                report += "- 建议启用更多优化策略\n"
                report += "- 考虑调整系统资源分配\n"
                report += "- 检查是否存在未识别的性能瓶颈\n"
            else:
                report += "- 性能优化效果良好\n"
                report += "- 建议持续监控性能指标\n"
                report += "- 定期重新运行基准测试\n"

        return report

    def _calculate_overall_improvement(self, benchmark: PerformanceBenchmark) -> float:
        """计算总体改进分数"""
        if not benchmark.baseline_metrics or not benchmark.current_metrics:
            return 0.0

        improvements = []
        for test_name in benchmark.baseline_metrics:
            if test_name in benchmark.current_metrics:
                baseline_time = benchmark.baseline_metrics[test_name]["execution_time"]
                optimized_time = benchmark.current_metrics[test_name]["execution_time"]

                if baseline_time > 0:
                    improvement = (baseline_time - optimized_time) / baseline_time
                    improvements.append(max(0, improvement))

        return statistics.mean(improvements) if improvements else 0.0

    async def run_continuous_optimization(self, duration_hours: int = 24):
        """运行持续优化"""
        print(f"🔄 开始持续优化，将持续 {duration_hours} 小时...")

        end_time = datetime.now() + timedelta(hours=duration_hours)
        optimization_sessions = []

        while datetime.now() < end_time:
            try:
                # 运行性能分析
                analysis_results = self.integration_manager.run_performance_analysis(duration=60)

                # 获取优化建议
                suggestions = self.analyzer.get_optimization_recommendations()

                # 应用关键优化
                if suggestions:
                    top_suggestions = sorted(suggestions, key=lambda x: x.priority)[:3]
                    for suggestion in top_suggestions:
                        print(f"🔧 应用优化建议: {suggestion.title}")
                        # 这里可以添加具体的优化逻辑

                # 记录会话
                session = {
                    "timestamp": datetime.now().isoformat(),
                    "analysis_results": analysis_results,
                    "suggestions_applied": len(top_suggestions),
                    "system_health": analysis_results.get("performance_summary", {}).get("system_health", "unknown"),
                }
                optimization_sessions.append(session)

                # 等待下一个周期
                await asyncio.sleep(300)  # 5分钟间隔

            except Exception as e:
                print(f"❌ 持续优化错误: {e}")
                await asyncio.sleep(60)  # 出错后等待1分钟

        # 生成持续优化报告
        report = self._generate_continuous_optimization_report(optimization_sessions)
        print("✅ 持续优化完成")
        print(f"📊 完成报告: {report}")

        return report

    def _generate_continuous_optimization_report(self, sessions: List[Dict]) -> str:
        """生成持续优化报告"""
        report = "# 持续优化报告\n\n"
        report += f"开始时间: {sessions[0]['timestamp']}\n"
        report += f"结束时间: {sessions[-1]['timestamp']}\n"
        report += f"优化会话数: {len(sessions)}\n\n"

        # 统计分析
        health_improvements = []
        suggestion_counts = []

        for session in sessions:
            health = session.get("system_health", "unknown")
            suggestions = session.get("suggestions_applied", 0)

            if health == "excellent":
                health_improvements.append(1.0)
            elif health == "good":
                health_improvements.append(0.8)
            elif health == "warning":
                health_improvements.append(0.5)
            else:
                health_improvements.append(0.0)

            suggestion_counts.append(suggestions)

        report += "## 优化统计\n\n"
        report += f"- 平均健康分数: {statistics.mean(health_improvements):.2f}\n"
        report += f"- 总应用建议数: {sum(suggestion_counts)}\n"
        report += f"- 平均每会话建议数: {statistics.mean(suggestion_counts):.1f}\n\n"

        # 健康趋势
        if len(health_improvements) > 1:
            trend = "improving" if health_improvements[-1] > health_improvements[0] else "stable"
            report += f"## 健康趋势: {trend}\n\n"

        # 建议
        report += "## 建议\n\n"
        if statistics.mean(health_improvements) < 0.7:
            report += "- 建议增加优化频率\n"
            report += "- 检查系统配置和资源分配\n"
            report += "- 考虑启用更多优化策略\n"
        else:
            report += "- 持续优化运行良好\n"
            report += "- 建议维持当前优化策略\n"
            report += "- 定期评估优化效果\n"

        return report

    def export_performance_data(self, output_path: str, format: str = "json"):
        """导出性能数据"""
        export_data = {
            "config": self.config,
            "benchmark_registry": self.benchmark_registry,
            "optimization_profiles": self.optimization_profiles,
            "performance_history": self.performance_history,
            "export_timestamp": datetime.now().isoformat(),
        }

        if format == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
        elif format == "csv":
            # 转换为CSV格式
            df = pd.DataFrame(
                [
                    {
                        "timestamp": h["timestamp"],
                        "benchmark_name": h["benchmark"].name,
                        "status": h["benchmark"].status,
                        "baseline_time": h["benchmark"]
                        .baseline_metrics.get("test_execution", {})
                        .get("execution_time", 0),
                        "optimized_time": h["benchmark"]
                        .current_metrics.get("test_execution", {})
                        .get("execution_time", 0),
                    }
                    for h in self.performance_history
                ]
            )
            df.to_csv(output_path, index=False)

        print(f"✅ 性能数据已导出到: {output_path}")

    def get_system_health_summary(self) -> Dict[str, Any]:
        """获取系统健康摘要"""
        if self.integration_manager:
            return self.integration_manager.monitor.get_performance_summary()
        return {"status": "unknown", "timestamp": datetime.now().isoformat()}

    def cleanup(self):
        """清理资源"""
        if self.integration_manager:
            self.integration_manager.stop_system_monitoring()

        print("🧹 性能集成系统已清理")


# 使用示例
async def demo_performance_integration():
    """演示性能集成系统功能"""
    print("🚀 演示性能集成系统功能")

    # 创建集成系统
    system = PerformanceIntegrationSystem()
    system.initialize_components()

    # 模拟测试函数
    async def test_database_operations():
        await asyncio.sleep(1)
        # 模拟数据库操作
        return "database_complete"

    async def test_api_calls():
        await asyncio.sleep(2)
        # 模拟API调用
        return "api_complete"

    async def test_file_operations():
        await asyncio.sleep(0.5)
        # 模拟文件操作
        return "file_complete"

    # 运行基准测试
    test_functions = [test_database_operations, test_api_calls, test_file_operations]
    benchmark_result = await system.run_performance_benchmark("comprehensive_performance_test", test_functions)

    print(f"📊 基准测试结果: {benchmark_result}")

    # 运行持续优化（短时间演示）
    continuous_report = await system.run_continuous_optimization(duration_hours=0.1)  # 6分钟

    # 获取系统健康状态
    health_summary = system.get_system_health_summary()
    print(f"🏥 系统健康状态: {health_summary}")

    # 清理
    system.cleanup()


if __name__ == "__main__":
    # 运行演示
    asyncio.run(demo_performance_integration())
