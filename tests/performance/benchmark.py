#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能基准测试工具

提供基准测试框架，支持：
- 函数/方法性能基准
- 内存使用基准
- 响应时间基准
- 吞吐量基准
"""

import time
import gc
import functools
import statistics
from typing import Callable, Any, Dict, List, Optional
from dataclasses import dataclass, field
from contextlib import contextmanager
import psutil
import os


@dataclass
class BenchmarkResult:
    """基准测试结果"""

    name: str
    iterations: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    std_dev: float
    throughput: float
    memory_used: float
    memory_delta: float
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "iterations": self.iterations,
            "total_time": self.total_time,
            "avg_time": self.avg_time,
            "min_time": self.min_time,
            "max_time": self.max_time,
            "std_dev": self.std_dev,
            "throughput": self.throughput,
            "memory_used": self.memory_used,
            "memory_delta": self.memory_delta,
            "timestamp": self.timestamp,
        }


class MemoryTracker:
    """内存跟踪器"""

    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.start_memory = 0
        self.peak_memory = 0

    def start(self):
        gc.collect()
        self.start_memory = self.process.memory_info().rss / 1024 / 1024
        self.peak_memory = self.start_memory

    def stop(self) -> float:
        current_memory = self.process.memory_info().rss / 1024 / 1024
        self.peak_memory = max(self.peak_memory, current_memory)
        return current_memory - self.start_memory

    def get_peak_memory(self) -> float:
        return self.peak_memory - self.start_memory


class PerformanceBenchmark:
    """性能基准测试类"""

    def __init__(
        self,
        warmup_iterations: int = 3,
        min_iterations: int = 10,
        max_iterations: int = 1000,
        max_time_seconds: float = 60.0,
    ):
        """
        初始化基准测试

        Args:
            warmup_iterations: 预热迭代次数
            min_iterations: 最小迭代次数
            max_iterations: 最大迭代次数
            max_time_seconds: 最大测试时间（秒）
        """
        self.warmup_iterations = warmup_iterations
        self.min_iterations = min_iterations
        self.max_iterations = max_iterations
        self.max_time_seconds = max_time_seconds

    def benchmark(
        self,
        name: str,
        func: Callable,
        *args,
        iterations: Optional[int] = None,
        **kwargs,
    ) -> BenchmarkResult:
        """
        运行基准测试

        Args:
            name: 测试名称
            func: 被测试的函数
            *args: 传递给函数的位置参数
            iterations: 迭代次数（可选，自动确定）
            **kwargs: 传递给函数的关键字参数

        Returns:
            BenchmarkResult: 基准测试结果
        """
        if iterations is None:
            iterations = self._auto_detect_iterations(func, *args, **kwargs)

        times = []
        memory_tracker = MemoryTracker()

        for i in range(iterations + self.warmup_iterations):
            memory_tracker.start()
            start_time = time.perf_counter()

            try:
                result = func(*args, **kwargs)
            except Exception as e:
                memory_delta = memory_tracker.stop()
                raise BenchmarkError(f"基准测试失败: {e}") from e

            end_time = time.perf_counter()
            memory_delta = memory_tracker.stop()

            if i >= self.warmup_iterations:
                times.append(end_time - start_time)

        if not times:
            raise BenchmarkError("没有收集到有效的测试时间数据")

        return self._calculate_results(name, times, iterations, memory_tracker)

    def _auto_detect_iterations(self, func: Callable, *args, **kwargs) -> int:
        """自动检测最佳迭代次数"""
        start_time = time.perf_counter()
        try:
            func(*args, **kwargs)
        except Exception:
            pass
        elapsed = time.perf_counter() - start_time

        if elapsed > 1.0:
            return min(self.max_iterations, 10)
        elif elapsed > 0.1:
            return min(self.max_iterations, 100)
        else:
            return self.min_iterations

    def _calculate_results(
        self, name: str, times: List[float], iterations: int, memory_tracker: MemoryTracker
    ) -> BenchmarkResult:
        """计算基准测试结果"""
        total_time = sum(times)
        avg_time = total_time / len(times)

        return BenchmarkResult(
            name=name,
            iterations=iterations,
            total_time=total_time,
            avg_time=avg_time,
            min_time=min(times),
            max_time=max(times),
            std_dev=statistics.stdev(times) if len(times) > 1 else 0,
            throughput=iterations / total_time if total_time > 0 else 0,
            memory_used=memory_tracker.peak_memory,
            memory_delta=memory_tracker.get_peak_memory(),
        )

    def compare(self, name: str, *functions: tuple[str, Callable]) -> Dict[str, BenchmarkResult]:
        """
        比较多个函数的性能

        Args:
            name: 比较测试名称
            *functions: (名称, 函数) 元组列表

        Returns:
            Dict[str, BenchmarkResult]: 各函数的测试结果
        """
        results = {}
        for func_name, func in functions:
            results[func_name] = self.benchmark(f"{name}_{func_name}", func)
        return results


class BenchmarkError(Exception):
    """基准测试错误"""

    pass


def benchmark(
    iterations: int = 100,
    warmup: int = 3,
    name: Optional[str] = None,
):
    """
    基准测试装饰器

    Args:
        iterations: 迭代次数
        warmup: 预热迭代次数
        name: 测试名称（可选，默认使用函数名）

    Usage:
        @benchmark(iterations=1000)
        def my_function():
            ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            bench = PerformanceBenchmark(
                warmup_iterations=warmup,
                min_iterations=iterations,
                max_iterations=iterations,
            )
            result = bench.benchmark(name=name or func.__name__, func=func, *args, **kwargs)
            print(
                f"\n[benchmark] {result.name}: "
                f"avg={result.avg_time * 1000:.4f}ms, "
                f"throughput={result.throughput:.2f} ops/s, "
                f"memory={result.memory_delta:.2f}MB"
            )
            return func(*args, **kwargs)

        return wrapper

    return decorator


@contextmanager
def timed_operation(operation_name: str):
    """上下文管理器：计时操作"""
    start_time = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start_time
    print(f"[timed] {operation_name}: {elapsed * 1000:.4f}ms")


if __name__ == "__main__":

    @benchmark(iterations=10000, name="list_comprehension")
    def test_list_comprehension():
        return [i * 2 for i in range(1000)]

    @benchmark(iterations=10000, name="for_loop")
    def test_for_loop():
        result = []
        for i in range(1000):
            result.append(i * 2)
        return result

    print("Running benchmark comparison...")
    bench = PerformanceBenchmark()
    results = bench.compare(
        "list_vs_for",
        ("list_comprehension", test_list_comprehension),
        ("for_loop", test_for_loop),
    )

    print("\n=== Benchmark Results ===")
    for name, result in results.items():
        print(f"\n{name}:")
        print(f"  Avg Time: {result.avg_time * 1000:.4f}ms")
        print(f"  Throughput: {result.throughput:.2f} ops/s")
        print(f"  Memory Delta: {result.memory_delta:.2f}MB")
