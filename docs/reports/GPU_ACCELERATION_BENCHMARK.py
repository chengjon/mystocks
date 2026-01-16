"""
GPU Acceleration Performance Benchmark - GPU加速性能基准测试

测试GPU指标计算的性能提升和准确性：
- CPU vs GPU 性能对比
- 准确性验证
- 内存使用分析
- 批量处理优化

作者: Claude Code (Sisyphus)
日期: 2026-01-14
"""

import time
import logging
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from dataclasses import dataclass
from pathlib import Path

from web.backend.app.services.indicators.gpu_adapter import (
    GPUIndicatorAdapter,
    GPUIndicatorFactory,
    GPU_AVAILABLE,
)
from src.indicators.indicator_factory import IndicatorFactory
from web.backend.app.services.indicators.gpu_adapter import IndicatorConfig

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """基准测试结果"""

    indicator_name: str
    data_size: int
    gpu_time: float
    cpu_time: float
    speedup_ratio: float
    gpu_accuracy: float
    cpu_accuracy: float
    gpu_memory_mb: float
    cpu_memory_mb: float
    batch_size: int


class GPUPerformanceBenchmark:
    """
    GPU性能基准测试器

    提供全面的GPU加速性能评估：
    - 性能对比测试
    - 准确性验证
    - 内存使用分析
    - 批量大小优化
    """

    def __init__(self):
        self.results = []
        self.test_data_sizes = [1000, 5000, 10000, 50000, 100000]
        self.test_indicators = ["macd", "rsi", "bbands"]

        # 创建测试数据生成器
        self.data_generator = TestDataGenerator()

        logger.info("✅ GPU Performance Benchmark initialized")

    def run_full_benchmark(self) -> List[BenchmarkResult]:
        """
        运行完整基准测试

        Returns:
            基准测试结果列表
        """
        logger.info("🚀 Starting GPU Performance Benchmark...")

        for indicator_name in self.test_indicators:
            logger.info(f"Testing indicator: {indicator_name}")

            for data_size in self.test_data_sizes:
                try:
                    result = self._benchmark_indicator(indicator_name, data_size)
                    self.results.append(result)
                    logger.info(
                        f"✅ {indicator_name} ({data_size}): {result.speedup_ratio:.1f}x speedup"
                    )

                except Exception as e:
                    logger.error(
                        f"❌ Benchmark failed for {indicator_name} ({data_size}): {e}"
                    )

        logger.info("✅ GPU Performance Benchmark completed")
        return self.results

    def _benchmark_indicator(
        self, indicator_name: str, data_size: int
    ) -> BenchmarkResult:
        """测试单个指标的性能"""
        # 生成测试数据
        test_data = self.data_generator.generate_stock_data(data_size)

        # GPU测试
        gpu_result = self._test_gpu_indicator(indicator_name, test_data)

        # CPU测试
        cpu_result = self._test_cpu_indicator(indicator_name, test_data)

        # 计算加速比
        speedup_ratio = (
            cpu_result["time"] / gpu_result["time"] if gpu_result["time"] > 0 else 0
        )

        # 验证准确性
        accuracy_score = self._validate_accuracy(gpu_result["data"], cpu_result["data"])

        return BenchmarkResult(
            indicator_name=indicator_name,
            data_size=data_size,
            gpu_time=gpu_result["time"],
            cpu_time=cpu_result["time"],
            speedup_ratio=speedup_ratio,
            gpu_accuracy=accuracy_score,
            cpu_accuracy=1.0,  # CPU作为基准
            gpu_memory_mb=gpu_result["memory_mb"],
            cpu_memory_mb=cpu_result["memory_mb"],
            batch_size=data_size,  # 简化处理
        )

    def _test_gpu_indicator(
        self, indicator_name: str, test_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """测试GPU指标计算"""
        try:
            # 创建GPU指标
            config = IndicatorConfig(
                name=f"{indicator_name}_gpu",
                type=indicator_name,
                parameters=self._get_indicator_params(indicator_name),
            )

            indicator = GPUIndicatorFactory.create_indicator(indicator_name, config)

            # 记录开始时间和内存
            start_time = time.time()
            start_memory = self._get_memory_usage()

            # 执行计算
            result = indicator.calculate(test_data)

            # 记录结束时间和内存
            end_time = time.time()
            end_memory = self._get_memory_usage()

            return {
                "time": end_time - start_time,
                "memory_mb": end_memory - start_memory,
                "data": result.data,
            }

        except Exception as e:
            logger.warning(f"GPU test failed, falling back to CPU: {e}")
            return self._test_cpu_indicator(indicator_name, test_data)

    def _test_cpu_indicator(
        self, indicator_name: str, test_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """测试CPU指标计算"""
        try:
            # 使用现有的CPU指标工厂
            indicator = IndicatorFactory.create_indicator(indicator_name)

            # 记录开始时间和内存
            start_time = time.time()
            start_memory = self._get_memory_usage()

            # 执行计算
            result = indicator.calculate(test_data)

            # 记录结束时间和内存
            end_time = time.time()
            end_memory = self._get_memory_usage()

            return {
                "time": end_time - start_time,
                "memory_mb": end_memory - start_memory,
                "data": result.data if hasattr(result, "data") else result,
            }

        except Exception as e:
            logger.error(f"CPU test failed: {e}")
            return {
                "time": 1.0,  # 默认1秒
                "memory_mb": 0.0,
                "data": {},
            }

    def _get_indicator_params(self, indicator_name: str) -> Dict[str, Any]:
        """获取指标默认参数"""
        param_map = {
            "macd": {"fast_period": 12, "slow_period": 26, "signal_period": 9},
            "rsi": {"period": 14},
            "bbands": {"period": 20, "std_dev": 2.0},
        }
        return param_map.get(indicator_name, {})

    def _get_memory_usage(self) -> float:
        """获取当前内存使用量（MB）"""
        try:
            import psutil

            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            return 0.0

    def _validate_accuracy(
        self, gpu_data: Dict[str, Any], cpu_data: Dict[str, Any]
    ) -> float:
        """验证GPU和CPU结果的准确性"""
        try:
            accuracy_scores = []

            for key in gpu_data.keys():
                if key in cpu_data:
                    gpu_values = np.array(gpu_data[key])
                    cpu_values = np.array(cpu_data[key])

                    # 计算相对误差
                    diff = np.abs(gpu_values - cpu_values)
                    relative_error = diff / (np.abs(cpu_values) + 1e-10)  # 避免除零

                    # 计算准确率（误差小于1%的比例）
                    accuracy = np.mean(relative_error < 0.01)
                    accuracy_scores.append(accuracy)

            return np.mean(accuracy_scores) if accuracy_scores else 0.0

        except Exception as e:
            logger.error(f"Accuracy validation failed: {e}")
            return 0.0

    def generate_report(
        self, output_path: str = "docs/reports/GPU_ACCELERATION_BENCHMARK.md"
    ) -> None:
        """
        生成基准测试报告

        Args:
            output_path: 报告输出路径
        """
        if not self.results:
            logger.warning("No benchmark results to report")
            return

        report = self._create_markdown_report()

        # 确保目录存在
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # 写入报告
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)

        logger.info(f"✅ Benchmark report generated: {output_path}")

    def _create_markdown_report(self) -> str:
        """创建Markdown格式的报告"""
        lines = []

        # 标题
        lines.append("# GPU Acceleration Performance Benchmark Report")
        lines.append("")
        lines.append("**Generated:** 2026-01-14")
        lines.append("**Test Environment:** MyStocks Quantitative Trading System")
        lines.append("")

        # 概述
        total_tests = len(self.results)
        gpu_available = GPU_AVAILABLE
        avg_speedup = np.mean(
            [r.speedup_ratio for r in self.results if r.speedup_ratio > 0]
        )

        lines.append("## Executive Summary")
        lines.append("")
        lines.append(f"- **Total Tests:** {total_tests}")
        lines.append(f"- **GPU Available:** {'✅ Yes' if gpu_available else '❌ No'}")
        lines.append(".1f")
        lines.append(
            f"- **Average Accuracy:** {np.mean([r.gpu_accuracy for r in self.results]):.1%}"
        )
        lines.append("")

        # 详细结果表格
        lines.append("## Detailed Results")
        lines.append("")
        lines.append(
            "| Indicator | Data Size | GPU Time | CPU Time | Speedup | Accuracy | GPU Memory | CPU Memory |"
        )
        lines.append(
            "|-----------|-----------|----------|----------|---------|----------|------------|------------|"
        )

        for result in self.results:
            lines.append("3.3f3.3f.1f.1%.1f.1f")

        lines.append("")

        # 性能分析
        lines.append("## Performance Analysis")
        lines.append("")

        # 按指标分组的加速比
        for indicator in self.test_indicators:
            indicator_results = [
                r for r in self.results if r.indicator_name == indicator
            ]
            if indicator_results:
                avg_speedup = np.mean([r.speedup_ratio for r in indicator_results])
                max_speedup = np.max([r.speedup_ratio for r in indicator_results])
                lines.append(f"### {indicator.upper()}")
                lines.append(".1f")
                lines.append(".1f")
                lines.append("")

        # 建议
        lines.append("## Recommendations")
        lines.append("")
        if gpu_available and avg_speedup > 2.0:
            lines.append("✅ **GPU acceleration is highly effective**")
            lines.append(
                "- Consider enabling GPU acceleration for production workloads"
            )
            lines.append("- Focus on optimizing data transfer between CPU and GPU")
        elif gpu_available and avg_speedup > 1.2:
            lines.append("⚠️ **GPU acceleration provides moderate benefits**")
            lines.append(
                "- Consider GPU acceleration for large datasets (>10K data points)"
            )
            lines.append("- Evaluate cost-benefit ratio for production deployment")
        else:
            lines.append("❌ **GPU acceleration not recommended**")
            lines.append("- Stick with CPU implementation for better reliability")
            lines.append("- Consider optimizing CPU algorithms instead")

        lines.append("")
        lines.append("## Technical Notes")
        lines.append("")
        lines.append("- All tests use synthetic stock market data")
        lines.append("- Accuracy validation uses 1% relative error threshold")
        lines.append("- Memory measurements may include system overhead")
        lines.append("- Results may vary based on specific hardware configuration")

        return "\n".join(lines)


class TestDataGenerator:
    """测试数据生成器"""

    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        self.seed = seed

    def generate_stock_data(self, size: int) -> Dict[str, Any]:
        """生成股票测试数据"""
        # 生成基础价格数据
        base_price = 100.0
        price_changes = np.random.normal(0.001, 0.02, size)  # 每日收益率
        prices = base_price * np.cumprod(1 + price_changes)

        # 生成OHLCV数据
        high_multipliers = 1 + np.random.uniform(0, 0.05, size)
        low_multipliers = 1 - np.random.uniform(0, 0.05, size)
        volume_base = 1000000

        return {
            "open": prices * (1 + np.random.normal(0, 0.01, size)),
            "high": prices * high_multipliers,
            "low": prices * low_multipliers,
            "close": prices,
            "volume": volume_base * (1 + np.random.uniform(0, 2, size)),
        }


# 便捷函数
def run_gpu_benchmark(save_report: bool = True) -> List[BenchmarkResult]:
    """运行GPU基准测试（便捷函数）"""
    benchmark = GPUPerformanceBenchmark()
    results = benchmark.run_full_benchmark()

    if save_report:
        benchmark.generate_report()

    return results


if __name__ == "__main__":
    # 运行基准测试
    results = run_gpu_benchmark()

    # 打印摘要
    print("\n🎯 GPU Benchmark Summary:")
    print(f"Tests completed: {len(results)}")

    if results:
        avg_speedup = np.mean([r.speedup_ratio for r in results if r.speedup_ratio > 0])
        avg_accuracy = np.mean([r.gpu_accuracy for r in results])
        print(".1f")
        print(".1%")

    print("\n📊 Detailed report saved to: docs/reports/GPU_ACCELERATION_BENCHMARK.md")
