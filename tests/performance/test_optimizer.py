#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试性能优化模块

提供测试执行性能优化功能：
1. 测试执行优化
2. 并发执行控制
3. 资源管理
4. 缓存策略
5. 内存优化
"""

import gc
import time
import threading
import functools
from typing import Callable, Any, Dict, List, Optional, TypeVar
from dataclasses import dataclass
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor, as_completed
import psutil
import os


T = TypeVar("T")


@dataclass
class PerformanceMetrics:
    """性能指标"""

    total_time: float = 0.0
    avg_time: float = 0.0
    min_time: float = float("inf")
    max_time: float = 0.0
    throughput: float = 0.0
    memory_peak_mb: float = 0.0
    gc_count: int = 0
    cache_hits: int = 0
    cache_misses: int = 0


class TestCache:
    """测试结果缓存"""

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl = ttl_seconds
        self._cache: Dict[str, Dict] = {}
        self._lock = threading.Lock()
        self._access_order: List[str] = []

    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if not self._is_expired(entry):
                    self._update_access(key)
                    return entry["value"]
                else:
                    del self._cache[key]
            return None

    def set(self, key: str, value: Any):
        """设置缓存"""
        with self._lock:
            if len(self._cache) >= self.max_size:
                self._evict_oldest()
            self._cache[key] = {
                "value": value,
                "created_at": time.time(),
                "access_count": 0,
            }
            self._access_order.append(key)

    def _is_expired(self, entry: Dict) -> bool:
        """检查是否过期"""
        return time.time() - entry["created_at"] > self.ttl

    def _update_access(self, key: str):
        """更新访问顺序"""
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)
        self._cache[key]["access_count"] += 1

    def _evict_oldest(self):
        """淘汰最旧的条目"""
        if self._access_order:
            oldest_key = self._access_order.pop(0)
            if oldest_key in self._cache:
                del self._cache[oldest_key]

    @property
    def hit_rate(self) -> float:
        """获取命中率"""
        total = len(self._cache)
        return 0.0 if total == 0 else sum(e["access_count"] for e in self._cache.values()) / total

    def clear(self):
        """清空缓存"""
        with self._lock:
            self._cache.clear()
            self._access_order.clear()


class ResourceManager:
    """测试资源管理器"""

    def __init__(self, max_memory_mb: float = 2048, max_workers: int = 4):
        self.max_memory_mb = max_memory_mb
        self.max_workers = max_workers
        self._process = psutil.Process(os.getpid())
        self._lock = threading.Lock()
        self._peak_memory = 0.0

    def check_memory(self) -> float:
        """检查当前内存使用"""
        return self._process.memory_info().rss / 1024 / 1024

    def is_memory_safe(self) -> bool:
        """检查内存是否安全"""
        return self.check_memory() < self.max_memory_mb

    def get_peak_memory(self) -> float:
        """获取峰值内存"""
        return self._peak_memory

    def update_peak_memory(self):
        """更新峰值内存"""
        current = self.check_memory()
        with self._lock:
            if current > self._peak_memory:
                self._peak_memory = current

    def get_optimal_workers(self) -> int:
        """获取最优工作线程数"""
        cpu_count = psutil.cpu_count()
        memory_mb = self.check_memory()

        # 基于 CPU 和内存计算最优线程数
        cpu_based = max(1, cpu_count - 1)
        memory_based = max(1, int(memory_mb / 512))

        return min(self.max_workers, cpu_based, memory_based)

    def force_gc_if_needed(self, threshold_mb: float = 1000):
        """必要时强制垃圾回收"""
        current = self.check_memory()
        if current > threshold_mb:
            gc.collect()
            return True
        return False


class TestOptimizer:
    """测试优化器"""

    def __init__(self):
        self.cache = TestCache()
        self.resource_manager = ResourceManager()
        self._metrics = PerformanceMetrics()

    @contextmanager
    def measure_time(self):
        """计时上下文"""
        start = time.perf_counter()
        yield
        elapsed = time.perf_counter() - start
        self._metrics.total_time += elapsed
        if elapsed < self._metrics.min_time:
            self._metrics.min_time = elapsed
        if elapsed > self._metrics.max_time:
            self._metrics.max_time = elapsed

    def cached_test(self, key: str, test_func: Callable[[], T]) -> T:
        """运行缓存的测试"""
        cached_result = self.cache.get(key)
        if cached_result is not None:
            self._metrics.cache_hits += 1
            return cached_result

        self._metrics.cache_misses += 1
        result = test_func()
        self.cache.set(key, result)
        return result

    def run_parallel(self, test_funcs: List[Callable], max_workers: Optional[int] = None) -> List[Any]:
        """并行运行测试"""
        if max_workers is None:
            max_workers = self.resource_manager.get_optimal_workers()

        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(test_func): i for i, test_func in enumerate(test_funcs)}
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"Test failed: {e}")
                    results.append(e)

        return results

    def optimize_test_data(self, data_generator: Callable, size: int) -> List:
        """优化测试数据生成"""
        cache_key = f"test_data_{size}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        data = data_generator(size)
        self.cache.set(cache_key, data)
        return data

    def get_metrics(self) -> PerformanceMetrics:
        """获取性能指标"""
        avg = self._metrics.total_time / max(1, self._metrics.throughput)
        return PerformanceMetrics(
            total_time=self._metrics.total_time,
            avg_time=avg,
            min_time=self._metrics.min_time,
            max_time=self._metrics.max_time,
            throughput=self._metrics.throughput,
            memory_peak_mb=self.resource_manager.get_peak_memory(),
            gc_count=0,
            cache_hits=self._metrics.cache_hits,
            cache_misses=self._metrics.cache_misses,
        )

    def reset_metrics(self):
        """重置指标"""
        self._metrics = PerformanceMetrics()
        self.cache.clear()


def optimize_test_execution(test_func: Callable) -> Callable:
    """测试执行优化装饰器"""

    @functools.wraps(test_func)
    def wrapper(*args, **kwargs):
        optimizer = TestOptimizer()

        # 检查内存
        if not optimizer.resource_manager.is_memory_safe():
            optimizer.resource_manager.force_gc_if_needed()

        # 运行测试
        with optimizer.measure_time():
            result = test_func(*args, **kwargs)

        # 更新吞吐量
        optimizer._metrics.throughput += 1

        # 更新峰值内存
        optimizer.resource_manager.update_peak_memory()

        return result

    return wrapper


class PerformanceOptimizer:
    """性能优化器 - 整合所有优化功能"""

    def __init__(self, max_memory_mb: float = 2048, enable_cache: bool = True):
        self.resource_manager = ResourceManager(max_memory_mb=max_memory_mb)
        self.cache = TestCache() if enable_cache else None
        self._gc_enabled = True

    def optimize_batch(
        self,
        test_cases: List[Dict[str, Any]],
        executor_func: Callable,
        batch_size: int = 10,
    ) -> Dict[str, Any]:
        """
        批量优化执行

        Args:
            test_cases: 测试用例列表
            executor_func: 执行函数
            batch_size: 批次大小

        Returns:
            执行结果统计
        """
        results = {"success": 0, "failed": 0, "skipped": 0, "total_time": 0.0}

        for i in range(0, len(test_cases), batch_size):
            batch = test_cases[i : i + batch_size]

            # 内存检查
            if not self.resource_manager.is_memory_safe():
                gc.collect()

            start = time.perf_counter()
            for case in batch:
                try:
                    if case.get("skip", False):
                        results["skipped"] += 1
                        continue

                    result = executor_func(case)
                    if result:
                        results["success"] += 1
                    else:
                        results["failed"] += 1
                except Exception:
                    results["failed"] += 1

            results["total_time"] += time.perf_counter() - start

        return results

    def get_optimization_report(self) -> Dict[str, Any]:
        """获取优化报告"""
        memory_mb = self.resource_manager.check_memory()
        workers = self.resource_manager.get_optimal_workers()

        return {
            "current_memory_mb": round(memory_mb, 2),
            "max_memory_mb": self.resource_manager.max_memory_mb,
            "memory_safe": self.resource_manager.is_memory_safe(),
            "optimal_workers": workers,
            "cache_enabled": self.cache is not None,
            "cache_size": len(self.cache._cache) if self.cache else 0,
            "cache_hit_rate": self.cache.hit_rate if self.cache else 0.0,
        }


if __name__ == "__main__":
    print("=== Test Performance Optimizer Demo ===")

    # 创建优化器
    optimizer = PerformanceOptimizer(max_memory_mb=1024)

    # 模拟测试用例
    test_cases = [{"name": f"test_{i}", "data": list(range(100)), "skip": i % 5 == 0} for i in range(20)]

    def run_test(case):
        time.sleep(0.01)
        return case["name"]

    # 运行优化测试
    print("Running optimized batch tests...")
    result = optimizer.optimize_batch(test_cases, run_test, batch_size=5)

    print("\nResults:")
    print(f"  Success: {result['success']}")
    print(f"  Failed: {result['failed']}")
    print(f"  Skipped: {result['skipped']}")
    print(f"  Total Time: {result['total_time']:.3f}s")

    # 获取优化报告
    report = optimizer.get_optimization_report()
    print("\nOptimization Report:")
    for key, value in report.items():
        print(f"  {key}: {value}")

    print("\n✅ Performance optimization complete!")
