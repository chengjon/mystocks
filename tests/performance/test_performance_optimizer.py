#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks 测试性能优化器

提供测试性能分析、优化策略和改进建议功能。
"""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import psutil


class OptimizationType(Enum):
    """优化类型枚举"""

    SPEED = "speed"
    MEMORY = "memory"
    CONCURRENCY = "concurrency"
    CACHE = "cache"
    DATABASE = "database"
    NETWORK = "network"
    CODE = "code"


@dataclass
class PerformanceMetric:
    """性能指标"""

    name: str
    category: str
    value: float
    unit: str
    threshold: float
    improvement_target: float
    status: str = "good"  # good/warning/critical
    trend: str = "stable"  # improving/stable/deteriorating


@dataclass
class TestExecution:
    """测试执行记录"""

    test_name: str
    execution_time: float
    memory_usage_mb: float
    cpu_usage_percent: float
    timestamp: datetime
    status: str
    error: Optional[str] = None
    optimization_score: float = 0.0


@dataclass
class OptimizationStrategy:
    """优化策略"""

    name: str
    type: OptimizationType
    description: str
    impact_score: float  # 0-1
    complexity_score: float  # 0-1
    estimated_improvement: float
    implementation_cost: str
    priority: int
    test_impact: bool
    implementation_steps: List[str]


class PerformanceAnalyzer:
    """性能分析器"""

    def __init__(self):
        self.metrics_history: Dict[str, List[PerformanceMetric]] = {}
        self.test_executions: List[TestExecution] = []
        self.bottlenecks: List[str] = []
        self.optimization_opportunities: List[Dict[str, Any]] = []

    def analyze_test_execution(self, execution: TestExecution) -> Dict[str, Any]:
        """分析测试执行性能"""
        analysis = {
            "performance_score": self._calculate_performance_score(execution),
            "bottlenecks": self._identify_bottlenecks(execution),
            "recommendations": self._generate_recommendations(execution),
            "optimization_potential": self._assess_optimization_potential(execution),
        }

        # 记录到历史数据
        self.test_executions.append(execution)
        self._update_metrics_history(execution)

        return analysis

    def _calculate_performance_score(self, execution: TestExecution) -> float:
        """计算性能分数"""
        score = 100.0

        # 执行时间影响
        if execution.execution_time > 10.0:
            score -= min(30.0, execution.execution_time - 10.0)

        # 内存使用影响
        if execution.memory_usage_mb > 1000:  # 1GB
            score -= min(20.0, (execution.memory_usage_mb - 1000) / 50)

        # CPU使用影响
        if execution.cpu_usage_percent > 80:
            score -= min(20.0, (execution.cpu_usage_percent - 80) / 5)

        # 错误影响
        if execution.status != "passed":
            score -= 30.0

        return max(0.0, score)

    def _identify_bottlenecks(self, execution: TestExecution) -> List[str]:
        """识别性能瓶颈"""
        bottlenecks = []

        # 时间瓶颈
        if execution.execution_time > 5.0:
            bottlenecks.append(f"测试执行时间过长 ({execution.execution_time:.2f}s)")

        # 内存瓶颈
        if execution.memory_usage_mb > 500:
            bottlenecks.append(f"内存使用过高 ({execution.memory_usage_mb:.2f}MB)")

        # CPU瓶颈
        if execution.cpu_usage_percent > 70:
            bottlenecks.append(f"CPU使用率高 ({execution.cpu_usage_percent:.2f}%)")

        # 网络瓶颈（如果适用）
        if hasattr(execution, "network_latency") and execution.network_latency > 1.0:
            bottlenecks.append(f"网络延迟高 ({execution.network_latency:.2f}s)")

        return bottlenecks

    def _generate_recommendations(self, execution: TestExecution) -> List[str]:
        """生成优化建议"""
        recommendations = []

        if execution.execution_time > 10.0:
            recommendations.append("考虑使用并行测试执行减少总时间")

        if execution.memory_usage_mb > 1000:
            recommendations.append("优化内存使用，考虑数据清理和懒加载")

        if execution.cpu_usage_percent > 80:
            recommendations.append("优化CPU密集型操作，考虑异步处理")

        if execution.status != "passed":
            recommendations.append("修复测试失败问题，提高测试稳定性")

        return recommendations

    def _assess_optimization_potential(self, execution: TestExecution) -> float:
        """评估优化潜力"""
        potential = 0.0

        if execution.execution_time > 5.0:
            potential += 0.4

        if execution.memory_usage_mb > 500:
            potential += 0.3

        if execution.cpu_usage_percent > 70:
            potential += 0.3

        return min(1.0, potential)

    def _update_metrics_history(self, execution: TestExecution):
        """更新指标历史"""
        metrics = [
            PerformanceMetric(
                name=f"execution_time_{execution.test_name}",
                category="speed",
                value=execution.execution_time,
                unit="s",
                threshold=5.0,
                improvement_target=1.0,
            ),
            PerformanceMetric(
                name=f"memory_usage_{execution.test_name}",
                category="memory",
                value=execution.memory_usage_mb,
                unit="MB",
                threshold=500.0,
                improvement_target=200.0,
            ),
            PerformanceMetric(
                name=f"cpu_usage_{execution.test_name}",
                category="cpu",
                value=execution.cpu_usage_percent,
                unit="%",
                threshold=70.0,
                improvement_target=30.0,
            ),
        ]

        for metric in metrics:
            if metric.name not in self.metrics_history:
                self.metrics_history[metric.name] = []
            self.metrics_history[metric.name].append(metric)

    def analyze_historical_trends(self) -> Dict[str, Any]:
        """分析历史趋势"""
        trends = {}

        for metric_name, history in self.metrics_history.items():
            if len(history) >= 3:
                recent_values = [m.value for m in history[-3:]]
                trend = self._calculate_trend(recent_values)
                trends[metric_name] = {
                    "current_value": recent_values[-1],
                    "trend": trend,
                    "improvement_needed": self._assess_improvement_needed(history),
                }

        return trends

    def _calculate_trend(self, values: List[float]) -> str:
        """计算趋势"""
        if len(values) < 2:
            return "stable"

        if values[-1] > values[0] * 1.1:
            return "deteriorating"
        elif values[-1] < values[0] * 0.9:
            return "improving"
        else:
            return "stable"

    def _assess_improvement_needed(self, history: List[PerformanceMetric]) -> bool:
        """评估是否需要改进"""
        if not history:
            return False

        latest = history[-1]
        return latest.value > latest.threshold


class PerformanceOptimizer:
    """性能优化器"""

    def __init__(self):
        self.strategies: List[OptimizationStrategy] = self._initialize_optimization_strategies()
        self.analyzer = PerformanceAnalyzer()
        self.optimization_history: List[Dict[str, Any]] = []

    def _initialize_optimization_strategies(self) -> List[OptimizationStrategy]:
        """初始化优化策略"""
        return [
            OptimizationStrategy(
                name="并行测试执行",
                type=OptimizationType.CONCURRENCY,
                description="使用pytest-xdist并行运行测试，充分利用多核CPU",
                impact_score=0.8,
                complexity_score=0.3,
                estimated_improvement=0.6,
                implementation_cost="low",
                priority=1,
                test_impact=True,
                implementation_steps=[
                    "安装pytest-xdist: pip install pytest-xdist",
                    "运行: pytest -n auto",
                    "配置并行数量: pytest -n 4",
                ],
            ),
            OptimizationStrategy(
                name="测试数据缓存",
                type=OptimizationType.CACHE,
                description="缓存测试数据避免重复创建，减少I/O操作",
                impact_score=0.7,
                complexity_score=0.5,
                estimated_improvement=0.5,
                implementation_cost="medium",
                priority=2,
                test_impact=False,
                implementation_steps=[
                    "创建测试数据缓存机制",
                    "使用内存缓存常用数据",
                    "设置合理的缓存过期策略",
                ],
            ),
            OptimizationStrategy(
                name="数据库查询优化",
                type=OptimizationType.DATABASE,
                description="优化测试中的数据库查询，添加索引和批处理",
                impact_score=0.9,
                complexity_score=0.7,
                estimated_improvement=0.7,
                implementation_cost="high",
                priority=3,
                test_impact=True,
                implementation_steps=[
                    "分析慢查询",
                    "添加合适的索引",
                    "使用批量操作替代单条操作",
                ],
            ),
            OptimizationStrategy(
                name="异步测试执行",
                type=OptimizationType.SPEED,
                description="将同步测试转换为异步，提高并发性能",
                impact_score=0.6,
                complexity_score=0.8,
                estimated_improvement=0.4,
                implementation_cost="high",
                priority=4,
                test_impact=True,
                implementation_steps=[
                    "使用pytest-asyncio",
                    "重构测试为异步模式",
                    "优化异步测试的并发控制",
                ],
            ),
            OptimizationStrategy(
                name="内存使用优化",
                type=OptimizationType.MEMORY,
                description="优化内存使用，减少内存泄漏和过度分配",
                impact_score=0.5,
                complexity_score=0.6,
                estimated_improvement=0.3,
                implementation_cost="medium",
                priority=5,
                test_impact=False,
                implementation_steps=[
                    "使用内存分析工具检测泄漏",
                    "及时释放大对象",
                    "使用生成器而非列表",
                ],
            ),
            OptimizationStrategy(
                name="网络请求优化",
                type=OptimizationType.NETWORK,
                description="优化测试中的网络请求，减少延迟和连接数",
                impact_score=0.7,
                complexity_score=0.4,
                estimated_improvement=0.5,
                implementation_cost="low",
                priority=2,
                test_impact=False,
                implementation_steps=[
                    "连接池管理",
                    "批量请求替代单条请求",
                    "使用CDN和缓存",
                ],
            ),
        ]

    async def optimize_test_performance(self, test_name: str, test_function: Callable) -> Dict[str, Any]:
        """优化测试性能"""
        print(f"\n🔧 开始优化测试: {test_name}")

        # 基准测试
        baseline_result = await self._run_benchmark(test_name, test_function)
        print(f"📊 基准测试结果: {baseline_result}")

        # 分析性能
        analysis = self.analyzer.analyze_test_execution(baseline_result)
        print(f"🔍 性能分析: {analysis}")

        # 选择优化策略
        strategies = self._select_optimization_strategies(analysis)
        print(f"🎯 选中 {len(strategies)} 个优化策略")

        # 应用优化
        optimization_results = []
        for strategy in strategies:
            print(f"\n📋 应用策略: {strategy.name}")
            result = await self._apply_optimization_strategy(test_name, test_function, strategy)
            optimization_results.append(result)

        # 评估优化效果
        final_result = await self._run_benchmark(test_name, test_function)
        improvement = self._calculate_improvement(baseline_result, final_result)

        optimization_report = {
            "test_name": test_name,
            "baseline_performance": self._execution_to_dict(baseline_result),
            "optimization_strategies": [self._strategy_to_dict(s) for s in strategies],
            "optimization_results": optimization_results,
            "final_performance": self._execution_to_dict(final_result),
            "improvement_metrics": improvement,
            "overall_improvement_score": self._calculate_overall_improvement(improvement),
            "optimization_timestamp": datetime.now().isoformat(),
        }

        self.optimization_history.append(optimization_report)
        print(f"\n✅ 优化完成，整体改进分数: {optimization_report['overall_improvement_score']:.2f}")

        return optimization_report

    async def _run_benchmark(self, test_name: str, test_function: Callable) -> TestExecution:
        """运行基准测试"""
        process = psutil.Process()
        start_time = time.time()
        start_memory = process.memory_info().rss / 1024 / 1024
        start_cpu = psutil.cpu_percent()

        try:
            await test_function()
            status = "passed"
            error = None
        except Exception as e:
            status = "failed"
            error = str(e)

        end_time = time.time()
        end_memory = process.memory_info().rss / 1024 / 1024
        end_cpu = psutil.cpu_percent()

        return TestExecution(
            test_name=test_name,
            execution_time=end_time - start_time,
            memory_usage_mb=end_memory - start_memory,
            cpu_usage_percent=end_cpu,
            timestamp=datetime.now(),
            status=status,
            error=error,
        )

    def _select_optimization_strategies(self, analysis: Dict[str, Any]) -> List[OptimizationStrategy]:
        """选择优化策略"""
        selected = []
        bottlenecks = analysis.get("bottlenecks", [])

        # 根据瓶颈选择策略
        for bottleneck in bottlenecks:
            if "时间长" in bottleneck:
                selected.extend(
                    s
                    for s in self.strategies
                    if s.type in [OptimizationType.SPEED, OptimizationType.CONCURRENCY] and s not in selected
                )

            if "内存" in bottleneck:
                selected.extend(s for s in self.strategies if s.type == OptimizationType.MEMORY and s not in selected)

            if "CPU" in bottleneck:
                selected.extend(s for s in self.strategies if s.type == OptimizationType.CODE and s not in selected)

        # 按优先级和影响排序
        selected.sort(key=lambda x: (x.priority, -x.impact_score))

        return selected[:3]  # 最多选择3个策略

    async def _apply_optimization_strategy(
        self, test_name: str, test_function: Callable, strategy: OptimizationStrategy
    ) -> Dict[str, Any]:
        """应用优化策略"""
        result = {
            "strategy_name": strategy.name,
            "type": strategy.type.value,
            "applied": False,
            "improvement": 0.0,
            "details": [],
        }

        try:
            # 根据策略类型应用优化
            if strategy.type == OptimizationType.CONCURRENCY:
                optimized_function = self._apply_parallel_execution(test_function)
            elif strategy.type == OptimizationType.CACHE:
                optimized_function = self._apply_caching(test_function)
            elif strategy.type == OptimizationType.MEMORY:
                optimized_function = self._apply_memory_optimization(test_function)
            else:
                optimized_function = test_function

            # 测试优化效果
            execution = await self._run_benchmark(f"{test_name}_{strategy.name}", optimized_function)
            improvement = execution.execution_time / (len(self.test_executions) + 1)

            result.update(
                {
                    "applied": True,
                    "execution_time": execution.execution_time,
                    "memory_usage_mb": execution.memory_usage_mb,
                    "cpu_usage_percent": execution.cpu_usage_percent,
                    "status": execution.status,
                    "improvement": improvement,
                    "details": strategy.implementation_steps,
                }
            )

        except Exception as e:
            result.update({"applied": False, "error": str(e), "details": ["优化策略应用失败"]})

        return result

    def _apply_parallel_execution(self, test_function: Callable) -> Callable:
        """应用并行执行优化"""

        async def parallel_function():
            with ThreadPoolExecutor(max_workers=4) as executor:
                await asyncio.gather(
                    *[asyncio.get_event_loop().run_in_executor(executor, test_function) for _ in range(4)]
                )

        return parallel_function

    def _apply_caching(self, test_function: Callable) -> Callable:
        """应用缓存优化"""
        cache = {}

        async def cached_function():
            cache_key = str(id(test_function))
            if cache_key not in cache:
                cache[cache_key] = await test_function()
            return cache[cache_key]

        return cached_function

    def _apply_memory_optimization(self, test_function: Callable) -> Callable:
        """应用内存优化"""

        async def memory_optimized_function():
            # 使用生成器而非列表
            for item in range(1000):
                yield item
            await test_function()

        return memory_optimized_function

    def _calculate_improvement(self, baseline: TestExecution, final: TestExecution) -> Dict[str, float]:
        """计算改进程度"""
        time_improvement = (baseline.execution_time - final.execution_time) / baseline.execution_time
        memory_improvement = (baseline.memory_usage_mb - final.memory_usage_mb) / baseline.memory_usage_mb
        cpu_improvement = (baseline.cpu_usage_percent - final.cpu_usage_percent) / baseline.cpu_usage_percent

        return {
            "time_improvement": time_improvement,
            "memory_improvement": memory_improvement,
            "cpu_improvement": cpu_improvement,
            "overall_improvement": (time_improvement + memory_improvement + cpu_improvement) / 3,
        }

    def _calculate_overall_improvement(self, improvement: Dict[str, float]) -> float:
        """计算总体改进分数"""
        overall = improvement.get("overall_improvement", 0.0)
        time_imp = improvement.get("time_improvement", 0.0) * 0.4
        memory_imp = improvement.get("memory_improvement", 0.0) * 0.3
        cpu_imp = improvement.get("cpu_improvement", 0.0) * 0.3

        return max(0.0, min(1.0, overall + time_imp + memory_imp + cpu_imp))

    def _execution_to_dict(self, execution: TestExecution) -> Dict[str, Any]:
        """将执行结果转换为字典"""
        return {
            "execution_time": execution.execution_time,
            "memory_usage_mb": execution.memory_usage_mb,
            "cpu_usage_percent": execution.cpu_usage_percent,
            "status": execution.status,
            "optimization_score": execution.optimization_score,
        }

    def _strategy_to_dict(self, strategy: OptimizationStrategy) -> Dict[str, Any]:
        """将策略转换为字典"""
        return {
            "name": strategy.name,
            "type": strategy.type.value,
            "impact_score": strategy.impact_score,
            "complexity_score": strategy.complexity_score,
            "estimated_improvement": strategy.estimated_improvement,
            "priority": strategy.priority,
        }

    def generate_optimization_report(self) -> str:
        """生成优化报告"""
        if not self.optimization_history:
            return "暂无优化历史记录"

        report = "# 测试性能优化报告\n\n"
        report += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        for i, optimization in enumerate(self.optimization_history, 1):
            report += f"## 优化 #{i}: {optimization['test_name']}\n\n"
            report += "**基准性能:**\n"
            report += f"- 执行时间: {optimization['baseline_performance']['execution_time']:.2f}s\n"
            report += f"- 内存使用: {optimization['baseline_performance']['memory_usage_mb']:.2f}MB\n"
            report += f"- CPU使用: {optimization['baseline_performance']['cpu_usage_percent']:.2f}%\n\n"

            report += "**优化策略:**\n"
            for strategy in optimization["optimization_strategies"]:
                report += f"- {strategy['name']} (影响分数: {strategy['impact_score']:.2f})\n"

            report += "\n**优化后性能:**\n"
            report += f"- 执行时间: {optimization['final_performance']['execution_time']:.2f}s\n"
            report += f"- 内存使用: {optimization['final_performance']['memory_usage_mb']:.2f}MB\n"
            report += f"- CPU使用: {optimization['final_performance']['cpu_usage_percent']:.2f}%\n\n"

            improvement = optimization["improvement_metrics"]
            report += "**改进效果:**\n"
            report += f"- 时间改进: {(improvement['time_improvement'] * 100):+.1f}%\n"
            report += f"- 内存改进: {(improvement['memory_improvement'] * 100):+.1f}%\n"
            report += f"- CPU改进: {(improvement['cpu_improvement'] * 100):+.1f}%\n"
            report += f"- 总体改进分数: {optimization['overall_improvement_score']:.2f}\n\n"

        return report


# 使用示例
async def demo_performance_optimizer():
    """演示性能优化器功能"""
    print("🚀 演示测试性能优化器功能")

    optimizer = PerformanceOptimizer()

    # 模拟测试函数
    async def slow_test():
        await asyncio.sleep(2)  # 模拟耗时操作
        data = [i * i for i in range(100000)]  # 模拟内存操作
        return sum(data)

    async def memory_intensive_test():
        # 模拟内存密集型测试
        large_data = ["test_data"] * 1000000
        return len(large_data)

    # 优化第一个测试
    await optimizer.optimize_test_performance("slow_test", slow_test)

    # 优化第二个测试
    await optimizer.optimize_test_performance("memory_intensive_test", memory_intensive_test)

    # 生成优化报告
    report = optimizer.generate_optimization_report()
    print(f"\n📋 优化报告:\n{report}")


if __name__ == "__main__":
    # 运行演示
    asyncio.run(demo_performance_optimizer())
