#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能分析工具

提供详细的性能分析功能：
- CPU 分析
- 内存分析
- 函数调用链分析
- 瓶颈识别
- 优化建议
"""

import cProfile
import io
import pstats
import time
import tracemalloc
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Callable, Dict, List, Optional


@dataclass
class FunctionProfile:
    """函数性能画像"""

    function_name: str
    call_count: int
    total_time: float
    cumulative_time: float
    per_call_time: float
    local_time: float
    file_name: str
    line_number: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "function_name": self.function_name,
            "call_count": self.call_count,
            "total_time": self.total_time,
            "cumulative_time": self.cumulative_time,
            "per_call_time": self.per_call_time,
            "local_time": self.local_time,
            "file_name": self.file_name,
            "line_number": self.line_number,
        }


@dataclass
class MemoryProfile:
    """内存使用画像"""

    current_memory: int
    peak_memory: int
    memory_blocks: int
    traceback: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_memory_mb": self.current_memory / 1024 / 1024,
            "peak_memory_mb": self.peak_memory / 1024 / 1024,
            "memory_blocks": self.memory_blocks,
            "traceback": self.traceback,
        }


@dataclass
class PerformanceReport:
    """性能分析报告"""

    function_profiles: List[FunctionProfile] = field(default_factory=list)
    memory_profiles: List[MemoryProfile] = field(default_factory=list)
    bottlenecks: List[Dict[str, Any]] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    total_execution_time: float = 0
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S"))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_execution_time": self.total_execution_time,
            "function_count": len(self.function_profiles),
            "top_functions": [f.to_dict() for f in self.function_profiles[:10]],
            "memory_profiles": [m.to_dict() for m in self.memory_profiles],
            "bottlenecks": self.bottlenecks,
            "suggestions": self.suggestions,
            "timestamp": self.timestamp,
        }


class PerformanceProfiler:
    """性能分析器"""

    def __init__(self, sort_by: str = "cumulative", limit: int = 20):
        """
        初始化性能分析器

        Args:
            sort_by: 排序方式 (calls, cumulative, cumulative, file, line, name, nfl, stdname, ttime)
            limit: 显示条数限制
        """
        self.sort_by = sort_by
        self.limit = limit
        self.profiler = None
        self.tracemalloc_started = False

    def start_profiling(self):
        """开始 CPU 分析"""
        self.profiler = cProfile.Profile()
        self.profiler.enable()

    def stop_profiling(self) -> pstats.Stats:
        """停止 CPU 分析并返回统计"""
        self.profiler.disable()
        stream = io.StringIO()
        stats = pstats.Stats(self.profiler, stream=stream)
        stats.sort_stats(self.sort_by)
        return stats

    def get_function_profiles(self) -> List[FunctionProfile]:
        """获取函数性能画像列表"""
        if not self.profiler:
            return []

        profiles = []
        stats = self.stop_profiling()

        for func, (cc, nc, tt, ct, callers) in stats.stats.items():
            profile = FunctionProfile(
                function_name=f"{func[2]}" if func[2] else f"{func[0]}:{func[1]}",
                call_count=nc,
                total_time=tt,
                cumulative_time=ct,
                per_call_time=tt / nc if nc > 0 else 0,
                local_time=tt,
                file_name=func[0],
                line_number=func[1],
            )
            profiles.append(profile)

        profiles.sort(key=lambda x: x.cumulative_time, reverse=True)
        return profiles[: self.limit]

    def analyze_function(self, func: Callable) -> PerformanceReport:
        """
        分析单个函数的性能

        Args:
            func: 被分析的函数

        Returns:
            PerformanceReport: 性能分析报告
        """
        self.start_profiling()
        tracemalloc.start()

        try:
            start_time = time.perf_counter()
            result = func()
            self.total_execution_time = time.perf_counter() - start_time
        finally:
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

        function_profiles = self.get_function_profiles()
        memory_profile = MemoryProfile(
            current_memory=current,
            peak_memory=peak,
            memory_blocks=0,
            traceback="",
        )

        return PerformanceReport(
            function_profiles=function_profiles,
            memory_profiles=[memory_profile],
            bottlenecks=self._identify_bottlenecks(function_profiles),
            suggestions=self._generate_suggestions(function_profiles),
            total_execution_time=self.total_execution_time,
        )

    def _identify_bottlenecks(self, profiles: List[FunctionProfile]) -> List[Dict[str, Any]]:
        """识别性能瓶颈"""
        bottlenecks = []

        if not profiles:
            return bottlenecks

        avg_time = sum(p.total_time for p in profiles) / len(profiles)
        total_time = sum(p.total_time for p in profiles)

        for profile in profiles[:10]:
            if profile.total_time > avg_time * 3 and profile.call_count > 0:
                bottlenecks.append(
                    {
                        "function": profile.function_name,
                        "time_percentage": (profile.total_time / total_time * 100) if total_time > 0 else 0,
                        "severity": "high" if profile.total_time / total_time > 0.3 else "medium",
                        "recommendation": f"Consider optimizing {profile.function_name}",
                    }
                )

        return bottlenecks

    def _generate_suggestions(self, profiles: List[FunctionProfile]) -> List[str]:
        """生成优化建议"""
        suggestions = []

        if not profiles:
            return suggestions

        top_functions = profiles[:5]
        total_time = sum(p.total_time for p in top_functions)

        for profile in top_functions:
            time_ratio = profile.total_time / total_time if total_time > 0 else 0

            if profile.call_count > 100 and time_ratio > 0.1:
                suggestions.append(
                    f"函数 {profile.function_name} 被频繁调用 ({profile.call_count} 次)，"
                    f"占总执行时间的 {time_ratio * 100:.1f}%，建议考虑缓存或优化。"
                )

            if profile.per_call_time > 0.01:
                suggestions.append(
                    f"函数 {profile.function_name} 单次调用耗时 {profile.per_call_time * 1000:.2f}ms，"
                    f"建议检查并优化实现。"
                )

        return suggestions


class MemoryProfiler:
    """内存分析器"""

    def __init__(self):
        self.tracemalloc_started = False
        self.snapshot = None

    def start(self):
        """开始内存跟踪"""
        tracemalloc.start()
        self.tracemalloc_started = True

    def stop(self) -> MemoryProfile:
        """停止内存跟踪"""
        if not self.tracemalloc_started:
            return MemoryProfile(0, 0, 0, "")

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        self.tracemalloc_started = False

        return MemoryProfile(
            current_memory=current,
            peak_memory=peak,
            memory_blocks=0,
            traceback="",
        )

    def take_snapshot(self):
        """拍摄内存快照"""
        if self.tracemalloc_started:
            self.snapshot = tracemalloc.take_snapshot()

    def get_memory_stats(self) -> Dict[str, Any]:
        """获取内存统计信息"""
        if not self.snapshot:
            return {}

        stats = self.snapshot.statistics("lineno")

        result = []
        for stat in stats[:10]:
            result.append(
                {
                    "size": stat.size,
                    "count": stat.count,
                    "filename": stat.traceback.format()[-1] if stat.traceback else "unknown",
                }
            )

        return {"top_allocations": result}

    def track_memory_leak(self, func: Callable) -> Dict[str, Any]:
        """
        跟踪内存泄漏

        Args:
            func: 被跟踪的函数

        Returns:
            Dict: 内存泄漏分析结果
        """
        self.start()

        try:
            for _ in range(100):
                func()
        finally:
            profile = self.stop()

        return {
            "memory_delta_mb": profile.peak_memory / 1024 / 1024,
            "leak_detected": profile.peak_memory > 10 * 1024 * 1024,
        }


def profile(
    sort_by: str = "cumulative",
    limit: int = 20,
):
    """
    性能分析装饰器

    Args:
        sort_by: 排序方式
        limit: 显示条数限制

    Usage:
        @profile()
        def my_function():
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            profiler = PerformanceProfiler(sort_by=sort_by, limit=limit)
            profiler.start_profiling()

            try:
                result = func(*args, **kwargs)
            finally:
                profiles = profiler.get_function_profiles()
                report = profiler.analyze_function(func)

                print(f"\n[profile] {func.__name__} - Top {limit} functions:")
                for p in profiles[:limit]:
                    print(f"  {p.function_name}: {p.total_time * 1000:.2f}ms ({p.call_count} calls)")

            return result

        return wrapper

    return decorator


def trace_calls(pattern: Optional[str] = None):
    """
    跟踪函数调用装饰器

    Args:
        pattern: 匹配的函数名模式

    Usage:
        @trace_calls("process_")
        def process_data():
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if pattern and pattern not in func.__name__:
                return func(*args, **kwargs)

            print(f"[trace] Entering {func.__name__}")
            start_time = time.perf_counter()

            try:
                result = func(*args, **kwargs)
                elapsed = time.perf_counter() - start_time
                print(f"[trace] Exiting {func.__name__} ({elapsed * 1000:.2f}ms)")
                return result
            except Exception as e:
                elapsed = time.perf_counter() - start_time
                print(f"[trace] Error in {func.__name__} after {elapsed * 1000:.2f}ms: {e}")
                raise

        return wrapper

    return decorator


if __name__ == "__main__":

    def example_function():
        data = []
        for i in range(10000):
            data.append(i * 2)
        return sum(data)

    def another_function():
        time.sleep(0.01)
        return "done"

    print("=== CPU Profiling ===")
    profiler = PerformanceProfiler(limit=10)
    report = profiler.analyze_function(example_function)

    print(f"\nTotal execution time: {report.total_execution_time * 1000:.2f}ms")
    print(f"Function profiles: {len(report.function_profiles)}")

    if report.bottlenecks:
        print("\nBottlenecks identified:")
        for b in report.bottlenecks:
            print(f"  - {b['function']}: {b['time_percentage']:.1f}%")

    if report.suggestions:
        print("\nSuggestions:")
        for s in report.suggestions:
            print(f"  - {s}")

    print("\n=== Memory Profiling ===")
    mem_profiler = MemoryProfiler()
    result = mem_profiler.track_memory_leak(example_function)
    print(f"Memory delta: {result['memory_delta_mb']:.2f}MB")
    print(f"Leak detected: {result['leak_detected']}")
