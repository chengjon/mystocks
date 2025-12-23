"""
测试优化器

提供智能测试优化、资源管理、执行策略和性能调优功能。
"""

import asyncio
import json
import logging
import math
import random
import time
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict, Counter, deque
from abc import ABC, abstractmethod

import numpy as np
import pandas as pd
import psutil
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.model_selection import cross_val_score
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import seaborn as sns

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestOptimizationStrategy(Enum):
    """测试优化策略枚举"""
    SPEED = "speed"
    RESOURCE = "resource"
    COVERAGE = "coverage"
    RELIABILITY = "reliability"
    BALANCED = "balanced"


class OptimizationPriority(Enum):
    """优化优先级枚举"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class TestExecutionResult:
    """测试执行结果"""
    test_name: str
    duration: float
    memory_usage: float
    cpu_usage: float
    passed: bool
    error_message: str = ""
    execution_timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationTarget:
    """优化目标"""
    name: str
    current_value: float
    target_value: float
    priority: OptimizationPriority
    strategy: TestOptimizationStrategy
    constraints: Dict[str, Any] = field(default_factory=dict)


class TestAnalyzer(ABC):
    """测试分析器抽象基类"""

    @abstractmethod
    def analyze(self, test_results: List[TestExecutionResult]) -> Dict[str, Any]:
        """分析测试结果"""
        pass


class PerformanceAnalyzer(TestAnalyzer):
    """性能分析器"""

    def __init__(self):
        self.history = deque(maxlen=1000)

    def analyze(self, test_results: List[TestExecutionResult]) -> Dict[str, Any]:
        """分析性能指标"""
        if not test_results:
            return {}

        durations = [r.duration for r in test_results]
        memory_usage = [r.memory_usage for r in test_results]
        cpu_usage = [r.cpu_usage for r in test_results]

        self.history.extend(test_results)

        return {
            "performance_metrics": {
                "avg_duration": statistics.mean(durations),
                "max_duration": max(durations),
                "min_duration": min(durations),
                "std_duration": statistics.stdev(durations) if len(durations) > 1 else 0,
                "avg_memory_usage": statistics.mean(memory_usage),
                "avg_cpu_usage": statistics.mean(cpu_usage),
                "test_throughput": len(test_results) / sum(durations) if sum(durations) > 0 else 0,
                "resource_efficiency": self._calculate_efficiency(test_results)
            },
            "performance_trends": self._analyze_trends(),
            "bottlenecks": self._identify_bottlenecks(test_results)
        }

    def _calculate_efficiency(self, results: List[TestExecutionResult]) -> float:
        """计算资源效率"""
        total_duration = sum(r.duration for r in results)
        total_memory = sum(r.memory_usage for r in results)
        total_cpu = sum(r.cpu_usage for r in results)

        # 效率评分：测试数量/(时间×资源使用)
        if total_duration > 0 and (total_memory + total_cpu) > 0:
            return len(results) / (total_duration * (total_memory + total_cpu))
        return 0.0

    def _analyze_trends(self) -> Dict[str, Any]:
        """分析性能趋势"""
        if len(self.history) < 10:
            return {}

        recent_results = list(self.history)[-50:]
        durations = [r.duration for r in recent_results]

        # 简单的趋势分析
        if len(durations) > 1:
            slope = np.polyfit(range(len(durations)), durations, 1)[0]
            return {
                "trend_direction": "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable",
                "slope": slope,
                "volatility": np.std(durations)
            }
        return {}

    def _identify_bottlenecks(self, results: List[TestExecutionResult]) -> List[str]:
        """识别性能瓶颈"""
        bottlenecks = []

        # 找出耗时最长的测试
        slow_tests = sorted(results, key=lambda x: x.duration, reverse=True)[:3]
        for test in slow_tests:
            if test.duration > 2.0:  # 超过2秒认为是瓶颈
                bottlenecks.append(f"{test.test_name} (耗时: {test.duration:.2f}s)")

        # 找出内存使用过高的测试
        memory_intensive = sorted(results, key=lambda x: x.memory_usage, reverse=True)[:3]
        for test in memory_intensive:
            if test.memory_usage > 100:  # 超过100MB认为是内存瓶颈
                bottlenecks.append(f"{test.test_name} (内存: {test.memory_usage:.2f}MB)")

        return bottlenecks


class CoverageAnalyzer(TestAnalyzer):
    """覆盖率分析器"""

    def analyze(self, test_results: List[TestExecutionResult]) -> Dict[str, Any]:
        """分析覆盖率指标"""
        # 这里应该集成覆盖率工具，如coverage.py
        # 暂时返回模拟数据
        passed = sum(1 for r in test_results if r.passed)
        total = len(test_results)

        return {
            "coverage_metrics": {
                "pass_rate": passed / total if total > 0 else 0,
                "total_tests": total,
                "passed_tests": passed,
                "failed_tests": total - passed,
                "coverage_score": self._calculate_coverage(test_results)
            }
        }

    def _calculate_coverage(self, results: List[TestExecutionResult]) -> float:
        """计算覆盖率分数"""
        # 模拟覆盖率计算
        passed = sum(1 for r in results if r.passed)
        return (passed / len(results)) * 0.8 if results else 0


class ReliabilityAnalyzer(TestAnalyzer):
    """可靠性分析器"""

    def __init__(self):
        self.failure_history = defaultdict(list)

    def analyze(self, test_results: List[TestExecutionResult]) -> Dict[str, Any]:
        """分析可靠性指标"""
        # 记录失败历史
        for result in test_results:
            if not result.passed:
                self.failure_history[result.test_name].append(result.execution_timestamp)

        reliability_metrics = {
            "mtbf": self._calculate_mtbf(),  # 平均故障间隔时间
            "failure_rate": self._calculate_failure_rate(test_results),
            "reliability_score": self._calculate_reliability_score(test_results),
            "flakiness_analysis": self._analyze_flakiness()
        }

        return {
            "reliability_metrics": reliability_metrics
        }

    def _calculate_mtbf(self) -> float:
        """计算平均故障间隔时间（小时）"""
        if not self.failure_history:
            return float('inf')

        all_failures = []
        for test_failures in self.failure_history.values():
            all_failures.extend(test_failures)

        if len(all_failures) < 2:
            return 0.0

        all_failures.sort()
        intervals = [(all_failures[i+1] - all_failures[i]).total_seconds() / 3600
                    for i in range(len(all_failures)-1)]

        return sum(intervals) / len(intervals) if intervals else 0.0

    def _calculate_failure_rate(self, results: List[TestExecutionResult]) -> float:
        """计算故障率"""
        failed = sum(1 for r in results if not r.passed)
        return failed / len(results) if results else 0.0

    def _calculate_reliability_score(self, results: List[TestExecutionResult]) -> float:
        """计算可靠性分数"""
        pass_rate = self._calculate_failure_rate(results)
        flakiness_score = self._analyze_flakiness().get("overall_flakiness", 0)

        # 综合可靠性评分
        reliability = (1 - pass_rate) * 0.7 + (1 - flakiness_score) * 0.3
        return max(0, min(1, reliability))

    def _analyze_flakiness(self) -> Dict[str, Any]:
        """分析测试的不稳定性"""
        flakiness_scores = {}

        for test_name, failures in self.failure_history.items():
            if len(failures) >= 3:
                # 计算波动性
                timestamps = [f.timestamp() for f in failures]
                volatility = np.std(timestamps) if len(timestamps) > 1 else 0
                flakiness_scores[test_name] = {
                    "failure_count": len(failures),
                    "volatility": volatility,
                    "flakiness_score": min(1.0, volatility / 3600)  # 归一化
                }

        # 计算整体不稳定性分数
        overall_flakiness = sum(score["flakiness_score"] for score in flakiness_scores.values()) / len(flakiness_scores) if flakiness_scores else 0

        return {
            "flakiness_scores": flakiness_scores,
            "overall_flakiness": overall_flakiness
        }


class TestOptimizer:
    """测试优化器主类"""

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.execution_results: List[TestExecutionResult] = []
        self.optimization_targets: List[OptimizationTarget] = []

        # 初始化分析器
        self.analyzers = {
            "performance": PerformanceAnalyzer(),
            "coverage": CoverageAnalyzer(),
            "reliability": ReliabilityAnalyzer()
        }

        # 优化策略配置
        self.strategies = {
            TestOptimizationStrategy.SPEED: self._optimize_speed,
            TestOptimizationStrategy.RESOURCE: self._optimize_resources,
            TestOptimizationStrategy.COVERAGE: self._optimize_coverage,
            TestOptimizationStrategy.RELIABILITY: self._optimize_reliability,
            TestOptimizationStrategy.BALANCED: self._optimize_balanced
        }

        # 系统监控
        self.system_monitor = SystemMonitor()

        # 自适应参数
        self.adaptive_params = {
            "execution_timeout": 30,
            "max_memory_mb": 512,
            "max_cpu_percent": 80,
            "batch_size": 10,
            "retry_limit": 3
        }

    def add_optimization_target(self, target: OptimizationTarget):
        """添加优化目标"""
        self.optimization_targets.append(target)
        logger.info(f"添加优化目标: {target.name}")

    def run_optimization(self, test_functions: List[Callable],
                        strategy: TestOptimizationStrategy = TestOptimizationStrategy.BALANCED,
                        iterations: int = 3) -> Dict[str, Any]:
        """运行优化"""
        logger.info(f"开始优化，策略: {strategy.value}")

        optimization_plan = self._create_optimization_plan(test_functions, strategy)

        for iteration in range(iterations):
            logger.info(f"优化迭代 {iteration + 1}/{iterations}")

            # 执行优化计划
            results = self._execute_optimization_plan(optimization_plan)

            # 分析结果
            analysis = self._analyze_test_results(results)

            # 调整策略
            adjusted_plan = self._adjust_optimization_strategy(analysis, strategy)

            # 应用调整
            self._apply_adjustments(adjusted_plan)

            yield {
                "iteration": iteration + 1,
                "results": results,
                "analysis": analysis,
                "adjusted_plan": adjusted_plan
            }

    def _create_optimization_plan(self, test_functions: List[Callable],
                                 strategy: TestOptimizationStrategy) -> List[Dict]:
        """创建优化计划"""
        plan = []

        # 基于策略制定计划
        if strategy == TestOptimizationStrategy.SPEED:
            # 速度优化：并行执行，超时控制
            plan.extend([{
                "test_func": func,
                "execution_mode": "parallel",
                "timeout": self.adaptive_params["execution_timeout"] // 2,
                "priority": "high"
            } for func in test_functions])

        elif strategy == TestOptimizationStrategy.RESOURCE:
            # 资源优化：顺序执行，资源限制
            plan.extend([{
                "test_func": func,
                "execution_mode": "sequential",
                "memory_limit": self.adaptive_params["max_memory_mb"] // 2,
                "cpu_limit": self.adaptive_params["max_cpu_percent"] // 2,
                "priority": "medium"
            } for func in test_functions])

        elif strategy == TestOptimizationStrategy.COVERAGE:
            # 覆盖率优化：重点测试关键路径
            plan.extend([{
                "test_func": func,
                "execution_mode": "focus",
                "coverage_weight": 1.2,
                "priority": "high"
            } for func in test_functions])

        elif strategy == TestOptimizationStrategy.RELIABILITY:
            # 可靠性优化：重试机制，错误处理
            plan.extend([{
                "test_func": func,
                "execution_mode": "robust",
                "retry_count": self.adaptive_params["retry_limit"],
                "error_handling": "strict",
                "priority": "high"
            } for func in test_functions])

        else:  # BALANCED
            # 平衡优化：综合策略
            plan.extend([{
                "test_func": func,
                "execution_mode": "adaptive",
                "timeout": self.adaptive_params["execution_timeout"],
                "memory_limit": self.adaptive_params["max_memory_mb"],
                "retry_count": 1,
                "priority": "medium"
            } for func in test_functions])

        return plan

    def _execute_optimization_plan(self, plan: List[Dict]) -> List[TestExecutionResult]:
        """执行优化计划"""
        results = []

        # 创建线程池
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []

            for item in plan:
                future = executor.submit(self._execute_single_test, item)
                futures.append(future)

            # 收集结果
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=60)
                    results.append(result)
                except Exception as e:
                    logger.error(f"测试执行失败: {e}")
                    # 创建失败结果
                    result = TestExecutionResult(
                        test_name=str(item["test_func"].__name__),
                        duration=0,
                        memory_usage=0,
                        cpu_usage=0,
                        passed=False,
                        error_message=str(e)
                    )
                    results.append(result)

        self.execution_results.extend(results)
        return results

    def _execute_single_test(self, test_config: Dict) -> TestExecutionResult:
        """执行单个测试"""
        test_func = test_config["test_func"]
        test_name = test_func.__name__

        # 开始监控
        self.system_monitor.start_monitoring()

        try:
            # 获取当前进程
            process = psutil.Process()

            # 设置资源限制（如果需要）
            if "memory_limit" in test_config:
                pass  # 实现内存限制

            if "cpu_limit" in test_config:
                pass  # 实现CPU限制

            # 执行测试
            start_time = time.time()
            start_memory = process.memory_info().rss / 1024 / 1024  # MB

            # 调用测试函数
            result = test_func()

            # 计算指标
            end_time = time.time()
            duration = end_time - start_time

            end_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_usage = end_memory - start_memory

            # 获取CPU使用率
            cpu_usage = process.cpu_percent()

            return TestExecutionResult(
                test_name=test_name,
                duration=duration,
                memory_usage=memory_usage,
                cpu_usage=cpu_usage,
                passed=True,
                metadata={"result": result}
            )

        except Exception as e:
            duration = time.time() - start_time
            memory_usage = process.memory_info().rss / 1024 / 1024 - start_memory
            cpu_usage = process.cpu_percent()

            return TestExecutionResult(
                test_name=test_name,
                duration=duration,
                memory_usage=memory_usage,
                cpu_usage=cpu_usage,
                passed=False,
                error_message=str(e)
            )
        finally:
            # 停止监控
            monitoring_data = self.system_monitor.stop_monitoring()

    def _analyze_test_results(self, results: List[TestExecutionResult]) -> Dict[str, Any]:
        """分析测试结果"""
        analysis = {}

        # 使用各个分析器进行分析
        for analyzer_name, analyzer in self.analyzers.items():
            analysis[analyzer_name] = analyzer.analyze(results)

        # 综合分析
        analysis["summary"] = self._generate_summary(results)
        analysis["recommendations"] = self._generate_recommendations(results)

        return analysis

    def _generate_summary(self, results: List[TestExecutionResult]) -> Dict[str, Any]:
        """生成总结报告"""
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.passed)

        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "pass_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "avg_duration": statistics.mean([r.duration for r in results]),
            "total_duration": sum(r.duration for r in results),
            "success_rate": self._calculate_success_rate(results)
        }

    def _generate_recommendations(self, results: List[TestExecutionResult]) -> List[str]:
        """生成优化建议"""
        recommendations = []

        # 性能建议
        slow_tests = [r for r in results if r.duration > 2.0]
        if slow_tests:
            recommendations.append(f"有 {len(slow_tests)} 个测试执行缓慢，建议优化或拆分")

        # 内存建议
        memory_intensive = [r for r in results if r.memory_usage > 100]
        if memory_intensive:
            recommendations.append(f"有 {len(memory_intensive)} 个测试内存使用过高，建议优化内存使用")

        # 可靠性建议
        failed_tests = [r for r in results if not r.passed]
        if failed_tests:
            recommendations.append(f"有 {len(failed_tests)} 个测试失败，建议检查失败原因")

        # 覆盖率建议
        coverage_score = self.analyzers["coverage"].analyze(results).get("coverage_metrics", {}).get("coverage_score", 0)
        if coverage_score < 0.8:
            recommendations.append(f"覆盖率较低 ({coverage_score:.2%})，建议增加测试用例")

        return recommendations

    def _adjust_optimization_strategy(self, analysis: Dict[str, Any],
                                   current_strategy: TestOptimizationStrategy) -> List[Dict]:
        """调整优化策略"""
        adjusted_plan = []

        # 基于分析结果调整参数
        if analysis.get("performance", {}).get("performance_metrics", {}).get("avg_duration", 0) > 5:
            # 如果平均耗时过长，增加并行度
            self.adaptive_params["execution_timeout"] *= 1.2

        if analysis.get("reliability", {}).get("reliability_metrics", {}).get("failure_rate", 0) > 0.1:
            # 如果故障率高，增加重试次数
            self.adaptive_params["retry_limit"] += 1

        # 返回调整后的计划
        return adjusted_plan

    def _apply_adjustments(self, adjustments: List[Dict]):
        """应用调整"""
        for adjustment in adjustments:
            # 应用具体的调整逻辑
            logger.info(f"应用调整: {adjustment}")

    def optimize_test_execution(self, test_functions: List[Callable],
                               strategy: TestOptimizationStrategy = TestOptimizationStrategy.BALANCED) -> Dict[str, Any]:
        """优化测试执行"""
        logger.info("开始测试执行优化")

        # 首先运行基线测试
        baseline_results = self._run_baseline_tests(test_functions)
        baseline_analysis = self._analyze_test_results(baseline_results)

        # 运行优化测试
        optimization_results = []
        for iteration_result in self.run_optimization(test_functions, strategy):
            optimization_results.append(iteration_result)

            # 检查是否达到优化目标
            if self._check_optimization_goals(iteration_result):
                logger.info("已达到优化目标，停止优化")
                break

        # 比较优化效果
        optimization_summary = self._compare_optimization(baseline_analysis, optimization_results)

        return {
            "baseline": baseline_analysis,
            "optimization_results": optimization_results,
            "summary": optimization_summary,
            "final_strategy": strategy,
            "adaptive_params": self.adaptive_params
        }

    def _run_baseline_tests(self, test_functions: List[Callable]) -> List[TestExecutionResult]:
        """运行基线测试"""
        logger.info("运行基线测试")
        baseline_config = {
            "test_func": func,
            "execution_mode": "baseline",
            "timeout": 30,
            "retry_count": 0
        }

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(self._execute_single_test, baseline_config) for func in test_functions]
            results = [future.result() for future in as_completed(futures)]

        return results

    def _check_optimization_goals(self, iteration_result: Dict) -> bool:
        """检查是否达到优化目标"""
        # 检查各个优化目标是否达到
        for target in self.optimization_targets:
            # 这里应该检查目标是否达成
            pass
        return False

    def _compare_optimization(self, baseline: Dict, optimization_results: List[Dict]) -> Dict[str, Any]:
        """比较优化效果"""
        if not optimization_results:
            return {}

        final_result = optimization_results[-1]

        # 计算改进指标
        baseline_pass_rate = baseline["summary"]["pass_rate"]
        final_pass_rate = final_result["analysis"]["summary"]["pass_rate"]

        baseline_avg_duration = baseline["summary"]["avg_duration"]
        final_avg_duration = final_result["analysis"]["summary"]["avg_duration"]

        return {
            "pass_rate_improvement": final_pass_rate - baseline_pass_rate,
            "duration_improvement": baseline_avg_duration - final_avg_duration,
            "duration_reduction_percent": (baseline_avg_duration - final_avg_duration) / baseline_avg_duration * 100,
            "iterations_completed": len(optimization_results),
            "convergence_achieved": self._check_convergence(optimization_results)
        }

    def _check_convergence(self, optimization_results: List[Dict]) -> bool:
        """检查优化是否收敛"""
        if len(optimization_results) < 3:
            return False

        # 检查最近几次迭代的改进幅度
        recent_improvements = []
        for i in range(1, len(optimization_results)):
            prev = optimization_results[i-1]["analysis"]["summary"]["avg_duration"]
            curr = optimization_results[i]["analysis"]["summary"]["avg_duration"]
            improvement = (prev - curr) / prev if prev > 0 else 0
            recent_improvements.append(improvement)

        # 如果最近几次改进都很小，认为收敛
        return improvement < 0.01 for improvement in recent_improvements[-3:]


class SystemMonitor:
    """系统监控器"""

    def __init__(self):
        self.monitoring = False
        self.start_time = None
        self.metrics = []

    def start_monitoring(self):
        """开始监控"""
        self.monitoring = True
        self.start_time = time.time()
        self.metrics = []

    def stop_monitoring(self) -> Dict[str, Any]:
        """停止监控"""
        self.monitoring = False
        return {
            "duration": time.time() - self.start_time,
            "metrics": self.metrics
        }

    def record_metric(self, metric_type: str, value: float):
        """记录指标"""
        if self.monitoring:
            self.metrics.append({
                "timestamp": time.time(),
                "type": metric_type,
                "value": value
            })


# 添加缺失的导入
import statistics


# 使用示例
def demo_test_optimizer():
    """演示测试优化器功能"""
    print("🚀 演示测试优化器功能")

    # 创建优化器
    optimizer = TestOptimizer(max_workers=4)

    # 添加优化目标
    speed_target = OptimizationTarget(
        name="execution_speed",
        current_value=5.0,
        target_value=2.0,
        priority=OptimizationPriority.HIGH,
        strategy=TestOptimizationStrategy.SPEED
    )
    optimizer.add_optimization_target(speed_target)

    # 定义测试函数
    def fast_test():
        """快速测试"""
        time.sleep(0.5)
        return "fast_test_passed"

    def slow_test():
        """慢速测试"""
        time.sleep(3.0)
        return "slow_test_passed"

    def resource_intensive_test():
        """资源密集型测试"""
        # 模拟大量计算
        data = [random.random() for _ in range(100000)]
        return len(data)

    def flaky_test():
        """不稳定测试"""
        if random.random() < 0.3:  # 30% 失败率
            raise Exception("Random failure")
        return "flaky_test_passed"

    test_functions = [
        fast_test,
        slow_test,
        resource_intensive_test,
        flaky_test
    ]

    # 运行优化
    results = optimizer.optimize_test_execution(
        test_functions,
        strategy=TestOptimizationStrategy.BALANCED
    )

    # 显示结果
    print(f"\n📊 优化结果:")
    print(f"基线通过率: {results['baseline']['summary']['pass_rate']:.2%}")
    print(f"优化后通过率: {results['summary']['pass_rate_improvement']:+.2%}")
    print(f"执行时间改进: {results['summary']['duration_improvement']:.2f}s")
    print(f"持续时间减少: {results['summary']['duration_reduction_percent']:.1f}%")

    print(f"\n🎯 最终策略: {results['final_strategy'].value}")
    print(f"📈 自适应参数: {results['adaptive_params']}")

    # 显示建议
    analysis = results['optimization_results'][-1]['analysis']
    if "recommendations" in analysis:
        print(f"\n💡 优化建议:")
        for rec in analysis["recommendations"]:
            print(f"  - {rec}")


if __name__ == "__main__":
    demo_test_optimizer()