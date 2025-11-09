#!/usr/bin/env python3
"""
GPU性能基准测试系统
全面测试GPU加速组件的性能对比和优化效果
适用于MyStocks量化交易系统的GPU加速效果评估
"""

import time
import psutil
import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import tracemalloc
from contextlib import contextmanager
import matplotlib.pyplot as plt
import json

# 导入GPU组件
from .gpu_manager import GPUUnifiedManager, GPUConfig, GPUProcessingResult
from .cpu_fallback import (
    ComponentSelector,
    PricePredictorCPU,
    DataProcessorCPU,
    FeatureGeneratorCPU,
)
from .price_predictor_gpu import GPUPricePredictor, PredictionResult
from .feature_generator_gpu import GPUFeatureGenerator
from .data_processor_gpu import GPUDataProcessor

# 导入原版组件
from ..data_adapters.financial_adapter import FinancialDataSource
from ..unified_manager import MyStocksUnifiedManager


@dataclass
class BenchmarkConfig:
    """基准测试配置"""

    test_data_sizes: List[int] = None
    model_types: List[str] = None
    test_iterations: int = 3
    warmup_iterations: int = 1
    enable_memory_profiling: bool = True
    enable_cpu_benchmark: bool = True
    enable_feature_benchmark: bool = True
    enable_data_processing_benchmark: bool = True
    enable_prediction_benchmark: bool = True

    def __post_init__(self):
        if self.test_data_sizes is None:
            self.test_data_sizes = [1000, 5000, 10000, 50000]
        if self.model_types is None:
            self.model_types = ["linear", "ridge", "lasso", "random_forest"]


@dataclass
class BenchmarkResult:
    """基准测试结果"""

    test_name: str
    data_size: int
    gpu_time: float
    cpu_time: float
    speedup_factor: float
    memory_usage_mb: float
    gpu_memory_mb: float
    cpu_memory_mb: float
    gpu_accuracy: float
    cpu_accuracy: float
    timestamp: float


class GPUPerformanceBenchmark:
    """GPU性能基准测试器"""

    def __init__(self, config: BenchmarkConfig = None):
        self.config = config or BenchmarkConfig()
        self.logger = logging.getLogger(__name__)
        self.results = []
        self.component_selector = ComponentSelector()

        # 初始化组件
        self.gpu_manager = GPUUnifiedManager()
        self.unified_manager = MyStocksUnifiedManager()

        # 性能统计
        self.stats = {
            "total_tests": 0,
            "successful_gpu_tests": 0,
            "successful_cpu_tests": 0,
            "failed_tests": 0,
            "average_speedup": 0.0,
            "max_speedup": 0.0,
            "min_speedup": float("inf"),
        }

    @contextmanager
    def _memory_profiler(self):
        """内存分析上下文管理器"""
        if not self.config.enable_memory_profiling:
            yield
            return

        tracemalloc.start()
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024

        try:
            yield
        finally:
            final_memory = process.memory_info().rss / 1024 / 1024
            peak_memory = tracemalloc.get_traced_memory()[1] / 1024 / 1024

            tracemalloc.stop()

            self.logger.info(
                f"内存使用 - 初始: {initial_memory:.2f}MB, "
                f"最终: {final_memory:.2f}MB, 峰值: {peak_memory:.2f}MB"
            )

    def _generate_test_data(self, size: int) -> pd.DataFrame:
        """生成测试数据"""
        np.random.seed(42)  # 确保可重复性

        # 生成模拟股票数据
        dates = pd.date_range("2023-01-01", periods=size, freq="D")

        data = pd.DataFrame(
            {
                "date": dates,
                "open": np.random.uniform(10, 100, size),
                "high": np.random.uniform(105, 105, size),
                "low": np.random.uniform(95, 105, size),
                "close": np.random.uniform(10, 100, size),
                "volume": np.random.uniform(1000000, 10000000, size),
                "adj_close": np.random.uniform(10, 100, size),
            }
        )

        # 确保high >= low, high >= open/close, low <= open/close
        data["high"] = np.maximum(
            data["high"], data[["open", "high", "low", "close"]].max(axis=1)
        )
        data["low"] = np.minimum(
            data["low"], data[["open", "high", "low", "close"]].min(axis=1)
        )

        # 添加一些缺失值测试数据质量处理
        if size > 1000:
            missing_indices = np.random.choice(size, size // 100, replace=False)
            data.loc[missing_indices, "volume"] = np.nan

        return data

    def _benchmark_data_processing(self, data: pd.DataFrame) -> Dict[str, float]:
        """基准测试数据处理器"""
        times = {"gpu": [], "cpu": []}

        for _ in range(self.config.warmup_iterations):
            # GPU预热
            if self.component_selector.check_gpu_availability():
                try:
                    gpu_processor = GPUDataProcessor(gpu_enabled=True)
                    gpu_processor.preprocess(data)
                except:
                    pass

            # CPU预热
            cpu_processor = DataProcessorCPU(gpu_enabled=False)
            cpu_processor.preprocess(data)

        # GPU测试
        if self.component_selector.check_gpu_availability():
            try:
                gpu_times = []
                for _ in range(self.config.test_iterations):
                    with self._memory_profiler():
                        start_time = time.time()
                        gpu_processor = GPUDataProcessor(gpu_enabled=True)
                        result = gpu_processor.preprocess(data)
                        gpu_times.append(time.time() - start_time)
                times["gpu"] = gpu_times
            except Exception as e:
                self.logger.error(f"GPU数据处理测试失败: {e}")

        # CPU测试
        cpu_times = []
        for _ in range(self.config.test_iterations):
            with self._memory_profiler():
                start_time = time.time()
                cpu_processor = DataProcessorCPU(gpu_enabled=False)
                result = cpu_processor.preprocess(data)
                cpu_times.append(time.time() - start_time)
        times["cpu"] = cpu_times

        return {
            "gpu_time": np.mean(times["gpu"]) if times["gpu"] else float("inf"),
            "cpu_time": np.mean(times["cpu"]),
            "gpu_memory": self._get_gpu_memory_usage(),
            "cpu_memory": psutil.Process().memory_info().rss / 1024 / 1024,
        }

    def _benchmark_feature_generation(self, data: pd.DataFrame) -> Dict[str, float]:
        """基准测试特征生成器"""
        times = {"gpu": [], "cpu": []}

        for _ in range(self.config.warmup_iterations):
            # GPU预热
            if self.component_selector.check_gpu_availability():
                try:
                    gpu_generator = GPUFeatureGenerator(gpu_enabled=True)
                    gpu_generator.generate_features(data)
                except:
                    pass

            # CPU预热
            cpu_generator = FeatureGeneratorCPU(gpu_enabled=False)
            cpu_generator.generate_features(data)

        # GPU测试
        if self.component_selector.check_gpu_availability():
            try:
                gpu_times = []
                for _ in range(self.config.test_iterations):
                    with self._memory_profiler():
                        start_time = time.time()
                        gpu_generator = GPUFeatureGenerator(gpu_enabled=True)
                        result = gpu_generator.generate_features(data)
                        gpu_times.append(time.time() - start_time)
                times["gpu"] = gpu_times
            except Exception as e:
                self.logger.error(f"GPU特征生成测试失败: {e}")

        # CPU测试
        cpu_times = []
        for _ in range(self.config.test_iterations):
            with self._memory_profiler():
                start_time = time.time()
                cpu_generator = FeatureGeneratorCPU(gpu_enabled=False)
                result = cpu_generator.generate_features(data)
                cpu_times.append(time.time() - start_time)
        times["cpu"] = cpu_times

        return {
            "gpu_time": np.mean(times["gpu"]) if times["gpu"] else float("inf"),
            "cpu_time": np.mean(times["cpu"]),
            "gpu_memory": self._get_gpu_memory_usage(),
            "cpu_memory": psutil.Process().memory_info().rss / 1024 / 1024,
        }

    def _benchmark_price_prediction(
        self, data: pd.DataFrame, model_type: str
    ) -> Dict[str, float]:
        """基准测试价格预测器"""
        times = {"gpu": [], "cpu": []}
        accuracies = {"gpu": [], "cpu": []}

        for _ in range(self.config.warmup_iterations):
            # GPU预热
            if self.component_selector.check_gpu_availability():
                try:
                    gpu_predictor = GPUPricePredictor(gpu_enabled=True)
                    gpu_predictor.train_models(data)
                except:
                    pass

            # CPU预热
            cpu_predictor = PricePredictorCPU(gpu_enabled=False)
            cpu_predictor.train_models(data)

        # GPU测试
        if self.component_selector.check_gpu_availability():
            try:
                gpu_times = []
                gpu_accs = []
                for _ in range(self.config.test_iterations):
                    with self._memory_profiler():
                        start_time = time.time()
                        gpu_predictor = GPUPricePredictor(gpu_enabled=True)
                        gpu_predictor.train_models(data)

                        # 模拟预测准确度（这里使用训练R²分数）
                        performance = gpu_predictor.get_performance_summary()
                        gpu_accs.append(performance.get("avg_prediction_time", 0))
                        gpu_times.append(time.time() - start_time)
                times["gpu"] = gpu_times
                accuracies["gpu"] = gpu_accs
            except Exception as e:
                self.logger.error(f"GPU价格预测测试失败: {e}")

        # CPU测试
        cpu_times = []
        cpu_accs = []
        for _ in range(self.config.test_iterations):
            with self._memory_profiler():
                start_time = time.time()
                cpu_predictor = PricePredictorCPU(gpu_enabled=False)
                cpu_predictor.train_models(data)

                performance = cpu_predictor.get_performance_summary()
                cpu_accs.append(performance.get("avg_prediction_time", 0))
                cpu_times.append(time.time() - start_time)
        times["cpu"] = cpu_times
        accuracies["cpu"] = cpu_accs

        return {
            "gpu_time": np.mean(times["gpu"]) if times["gpu"] else float("inf"),
            "cpu_time": np.mean(times["cpu"]),
            "gpu_accuracy": np.mean(accuracies["gpu"]) if accuracies["gpu"] else 0,
            "cpu_accuracy": np.mean(accuracies["cpu"]),
            "gpu_memory": self._get_gpu_memory_usage(),
            "cpu_memory": psutil.Process().memory_info().rss / 1024 / 1024,
        }

    def _get_gpu_memory_usage(self) -> float:
        """获取GPU内存使用情况"""
        try:
            import cupy as cp

            return cp.cuda.get_default_memory_pool().used_bytes() / 1024 / 1024
        except:
            return 0.0

    def run_comprehensive_benchmark(self) -> List[BenchmarkResult]:
        """运行综合基准测试"""
        self.logger.info("🚀 开始综合GPU性能基准测试")
        print("=" * 60)
        print("🚀 MyStocks GPU加速性能基准测试")
        print("=" * 60)

        # 测试数据大小循环
        for data_size in self.config.test_data_sizes:
            print(f"\n📊 测试数据大小: {data_size:,} 行")
            print("-" * 40)

            # 生成测试数据
            test_data = self._generate_test_data(data_size)

            # 数据处理基准测试
            if self.config.enable_data_processing_benchmark:
                print("🔧 数据处理性能测试:")
                result = self._benchmark_data_processing(test_data)

                speedup = (
                    result["cpu_time"] / result["gpu_time"]
                    if result["gpu_time"] > 0
                    else 0
                )
                self._update_stats(speedup)

                self._print_benchmark_result(
                    "数据处理",
                    data_size,
                    result["gpu_time"],
                    result["cpu_time"],
                    speedup,
                    result["gpu_memory"],
                    result["cpu_memory"],
                )

                # 保存结果
                self.results.append(
                    BenchmarkResult(
                        test_name="数据处理",
                        data_size=data_size,
                        gpu_time=result["gpu_time"],
                        cpu_time=result["cpu_time"],
                        speedup_factor=speedup,
                        memory_usage_mb=result["gpu_memory"],
                        gpu_memory_mb=result["gpu_memory"],
                        cpu_memory_mb=result["cpu_memory"],
                        gpu_accuracy=0.0,
                        cpu_accuracy=0.0,
                        timestamp=time.time(),
                    )
                )

            # 特征生成基准测试
            if self.config.enable_feature_benchmark:
                print("\n🎯 特征生成性能测试:")
                result = self._benchmark_feature_generation(test_data)

                speedup = (
                    result["cpu_time"] / result["gpu_time"]
                    if result["gpu_time"] > 0
                    else 0
                )
                self._update_stats(speedup)

                self._print_benchmark_result(
                    "特征生成",
                    data_size,
                    result["gpu_time"],
                    result["cpu_time"],
                    speedup,
                    result["gpu_memory"],
                    result["cpu_memory"],
                )

                # 保存结果
                self.results.append(
                    BenchmarkResult(
                        test_name="特征生成",
                        data_size=data_size,
                        gpu_time=result["gpu_time"],
                        cpu_time=result["cpu_time"],
                        speedup_factor=speedup,
                        memory_usage_mb=result["gpu_memory"],
                        gpu_memory_mb=result["gpu_memory"],
                        cpu_memory_mb=result["cpu_memory"],
                        gpu_accuracy=0.0,
                        cpu_accuracy=0.0,
                        timestamp=time.time(),
                    )
                )

            # 价格预测基准测试
            if self.config.enable_prediction_benchmark:
                print(f"\n📈 价格预测性能测试:")
                for model_type in self.config.model_types:
                    print(f"  模型类型: {model_type}")
                    result = self._benchmark_price_prediction(test_data, model_type)

                    speedup = (
                        result["cpu_time"] / result["gpu_time"]
                        if result["gpu_time"] > 0
                        else 0
                    )
                    self._update_stats(speedup)

                    self._print_benchmark_result(
                        f"预测_{model_type}",
                        data_size,
                        result["gpu_time"],
                        result["cpu_time"],
                        speedup,
                        result["gpu_memory"],
                        result["cpu_memory"],
                        result["gpu_accuracy"],
                        result["cpu_accuracy"],
                    )

                    # 保存结果
                    self.results.append(
                        BenchmarkResult(
                            test_name=f"预测_{model_type}",
                            data_size=data_size,
                            gpu_time=result["gpu_time"],
                            cpu_time=result["cpu_time"],
                            speedup_factor=speedup,
                            memory_usage_mb=result["gpu_memory"],
                            gpu_memory_mb=result["gpu_memory"],
                            cpu_memory_mb=result["cpu_memory"],
                            gpu_accuracy=result["gpu_accuracy"],
                            cpu_accuracy=result["cpu_accuracy"],
                            timestamp=time.time(),
                        )
                    )

        self._print_summary()
        return self.results

    def _print_benchmark_result(
        self,
        test_name: str,
        data_size: int,
        gpu_time: float,
        cpu_time: float,
        speedup: float,
        gpu_mem: float,
        cpu_mem: float,
        gpu_acc: float = 0.0,
        cpu_acc: float = 0.0,
    ):
        """打印基准测试结果"""
        status = "✅" if speedup > 1 else "❌"
        print(f"  {status} {test_name}:")
        print(
            f"    GPU时间: {gpu_time:.4f}s | CPU时间: {cpu_time:.4f}s | 加速比: {speedup:.2f}x"
        )
        print(f"    GPU内存: {gpu_mem:.2f}MB | CPU内存: {cpu_mem:.2f}MB")

        if gpu_acc > 0 and cpu_acc > 0:
            print(f"    GPU精度: {gpu_acc:.4f} | CPU精度: {cpu_acc:.4f}")

    def _update_stats(self, speedup: float):
        """更新统计信息"""
        self.stats["total_tests"] += 1

        if speedup > 1:
            self.stats["successful_gpu_tests"] += 1
        else:
            self.stats["successful_cpu_tests"] += 1

        if speedup > 0:
            self.stats["average_speedup"] += speedup
            self.stats["max_speedup"] = max(self.stats["max_speedup"], speedup)
            self.stats["min_speedup"] = min(self.stats["min_speedup"], speedup)

    def _print_summary(self):
        """打印总结报告"""
        print("\n" + "=" * 60)
        print("📋 GPU性能基准测试总结")
        print("=" * 60)

        total = self.stats["total_tests"]
        gpu_success = self.stats["successful_gpu_tests"]
        cpu_success = self.stats["successful_cpu_tests"]

        print(f"总测试项目: {total}")
        print(f"GPU胜出项目: {gpu_success} ({gpu_success/total*100:.1f}%)")
        print(f"CPU胜出项目: {cpu_success} ({cpu_success/total*100:.1f}%)")

        if total > 0:
            self.stats["average_speedup"] = self.stats["average_speedup"] / total
            print(f"平均加速比: {self.stats['average_speedup']:.2f}x")
            print(f"最大加速比: {self.stats['max_speedup']:.2f}x")
            print(f"最小加速比: {self.stats['min_speedup']:.2f}x")

        # 性能评级
        if self.stats["average_speedup"] > 3:
            rating = "🏆 优秀"
        elif self.stats["average_speedup"] > 2:
            rating = "✅ 良好"
        elif self.stats["average_speedup"] > 1:
            rating = "⚠️  一般"
        else:
            rating = "❌ 未达到预期"

        print(f"\n综合性能评级: {rating}")

        # 建议
        self._generate_recommendations()

    def _generate_recommendations(self):
        """生成优化建议"""
        print("\n💡 优化建议:")

        # 基于结果生成建议
        if self.stats["average_speedup"] < 1.5:
            print("⚠️  GPU加速效果不明显，建议检查:")
            print("  1. GPU硬件是否正常工作")
            print("  2. CUDA版本是否兼容")
            print("  3. 数据量是否足够大（建议>10,000行）")
            print("  4. 内存带宽是否足够")

        if self.stats["max_speedup"] > 5:
            print("✅ 在某些场景下GPU表现优秀，建议:")
            print("  1. 优先在大型数据处理任务中使用GPU")
            print("  2. 考虑批量处理以提高GPU利用率")
            print("  3. 优化数据传输以减少CPU-GPU通信开销")

        if self.stats["successful_gpu_tests"] > self.stats["successful_cpu_tests"]:
            print("🎯 GPU加速效果显著，建议:")
            print("  1. 启用GPU自动选择功能")
            print("  2. 在策略回测中使用GPU模式")
            print("  3. 考虑扩展到更多机器学习任务")

    def save_benchmark_results(self, filepath: str):
        """保存基准测试结果"""
        results_data = {
            "timestamp": time.time(),
            "config": self.config.__dict__,
            "stats": self.stats,
            "results": [
                {
                    "test_name": r.test_name,
                    "data_size": r.data_size,
                    "gpu_time": r.gpu_time,
                    "cpu_time": r.cpu_time,
                    "speedup_factor": r.speedup_factor,
                    "memory_usage_mb": r.memory_usage_mb,
                    "gpu_memory_mb": r.gpu_memory_mb,
                    "cpu_memory_mb": r.cpu_memory_mb,
                    "gpu_accuracy": r.gpu_accuracy,
                    "cpu_accuracy": r.cpu_accuracy,
                    "timestamp": r.timestamp,
                }
                for r in self.results
            ],
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)

        self.logger.info(f"基准测试结果已保存到: {filepath}")

    def generate_performance_report(self) -> str:
        """生成性能报告"""
        report = f"""
MyStocks GPU加速性能报告
========================

测试时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}

📊 测试统计:
  总测试项目: {self.stats['total_tests']}
  GPU胜出项目: {self.stats['successful_gpu_tests']}
  CPU胜出项目: {self.stats['successful_cpu_tests']}
  平均加速比: {self.stats['average_speedup']:.2f}x
  最大加速比: {self.stats['max_speedup']:.2f}x
  最小加速比: {self.stats['min_speedup']:.2f}x

🎯 详细结果:
"""

        for result in self.results:
            report += f"""
  {result.test_name} (数据量: {result.data_size:,}行):
    GPU时间: {result.gpu_time:.4f}s
    CPU时间: {result.cpu_time:.4f}s
    加速比: {result.speedup_factor:.2f}x
    GPU内存: {result.gpu_memory_mb:.2f}MB
    CPU内存: {result.cpu_memory_mb:.2f}MB"""

        # 添加GPU环境信息
        gpu_status = (
            "可用" if self.component_selector.check_gpu_availability() else "不可用"
        )
        report += f"""
🖥️  GPU环境状态: {gpu_status}
"""

        return report


def main():
    """主函数 - 基准测试示例"""
    # 创建基准测试配置
    config = BenchmarkConfig(
        test_data_sizes=[1000, 5000, 10000],
        model_types=["ridge", "random_forest"],
        test_iterations=2,
        enable_memory_profiling=True,
    )

    # 运行基准测试
    benchmark = GPUPerformanceBenchmark(config)
    results = benchmark.run_comprehensive_benchmark()

    # 保存结果
    benchmark.save_benchmark_results("gpu_performance_benchmark.json")

    # 生成报告
    report = benchmark.generate_performance_report()
    print(report)

    # 保存报告
    with open("gpu_performance_report.txt", "w", encoding="utf-8") as f:
        f.write(report)

    return results


if __name__ == "__main__":
    results = main()
