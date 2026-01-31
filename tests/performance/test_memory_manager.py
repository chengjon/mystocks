#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试内存管理模块

提供测试过程中的内存优化功能：
1. 内存使用监控
2. 自动垃圾回收
3. 大对象管理
4. 内存泄漏检测
5. 资源清理
"""

import gc
import os
import sys
import threading
import time
import traceback
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import psutil


@dataclass
class MemorySnapshot:
    """内存快照"""

    timestamp: datetime
    rss_mb: float
    vms_mb: float
    objects_count: int
    gc_counts: tuple
    top_objects: List[Dict] = field(default_factory=list)


@dataclass
class MemoryStats:
    """内存统计"""

    current_mb: float = 0.0
    peak_mb: float = 0.0
    average_mb: float = 0.0
    gc_runs: int = 0
    leak_warnings: int = 0
    cleaned_objects: int = 0


class MemoryTracker:
    """内存追踪器"""

    def __init__(self, warning_threshold_mb: float = 500, critical_threshold_mb: float = 1000):
        self.warning_threshold = warning_threshold_mb
        self.critical_threshold = critical_threshold_mb
        self._process = psutil.Process(os.getpid())
        self._snapshots: List[MemorySnapshot] = []
        self._lock = threading.Lock()
        self._peak_memory = 0.0
        self._gc_count = 0
        self._tracked_objects: Dict[int, Dict] = {}

    def check_memory(self) -> float:
        """检查当前内存使用"""
        return self._process.memory_info().rss / 1024 / 1024

    def snapshot(self) -> MemorySnapshot:
        """拍摄内存快照"""
        info = self._process.memory_info()
        gc.collect()
        gc_counts = gc.get_count()

        snapshot = MemorySnapshot(
            timestamp=datetime.now(),
            rss_mb=info.rss / 1024 / 1024,
            vms_mb=info.vms / 1024 / 1024,
            objects_count=len(gc.get_objects()),
            gc_counts=gc_counts,
            top_objects=self._get_top_objects(5),
        )

        with self._lock:
            self._snapshots.append(snapshot)
            if snapshot.rss_mb > self._peak_memory:
                self._peak_memory = snapshot.rss_mb

        return snapshot

    def _get_top_objects(self, limit: int = 5) -> List[Dict]:
        """获取占用最大的对象类型"""
        try:
            objects = gc.get_objects()
            type_counts = {}
            for obj in objects[:10000]:
                obj_type = type(obj).__name__
                if obj_type not in type_counts:
                    type_counts[obj_type] = 0
                type_counts[obj_type] += 1

            sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
            return [{"type": t, "count": c} for t, c in sorted_types[:limit]]
        except Exception:
            return []

    def check_for_leaks(self, baseline_snapshot: Optional[MemorySnapshot] = None) -> Dict[str, Any]:
        """检查内存泄漏"""
        current = self.snapshot()

        if baseline_snapshot is None:
            if len(self._snapshots) < 2:
                return {"leak_detected": False, "message": "Not enough snapshots"}
            baseline_snapshot = self._snapshots[0]

        growth_mb = current.rss_mb - baseline_snapshot.rss_mb
        growth_percent = (growth_mb / baseline_snapshot.rss_mb * 100) if baseline_snapshot.rss_mb > 0 else 0

        leak_detected = growth_mb > 100 or growth_percent > 20

        return {
            "leak_detected": leak_detected,
            "baseline_mb": round(baseline_snapshot.rss_mb, 2),
            "current_mb": round(current.rss_mb, 2),
            "growth_mb": round(growth_mb, 2),
            "growth_percent": round(growth_percent, 2),
            "timestamp": current.timestamp.isoformat(),
        }

    def track_object(self, obj: Any, name: str):
        """跟踪对象"""
        obj_id = id(obj)
        with self._lock:
            self._tracked_objects[obj_id] = {
                "name": name,
                "size": sys.getsizeof(obj),
                "created_at": datetime.now(),
                "traceback": traceback.format_stack(),
            }

    def untrack_object(self, obj: Any):
        """取消跟踪对象"""
        obj_id = id(obj)
        with self._lock:
            if obj_id in self._tracked_objects:
                del self._tracked_objects[obj_id]

    def get_stats(self) -> MemoryStats:
        """获取内存统计"""
        current = self.snapshot()
        return MemoryStats(
            current_mb=current.rss_mb,
            peak_mb=self._peak_memory,
            average_mb=sum(s.rss_mb for s in self._snapshots) / len(self._snapshots) if self._snapshots else 0,
            gc_runs=self._gc_count,
        )


class GarbageCollectionManager:
    """垃圾回收管理器"""

    def __init__(self, enabled: bool = True, threshold_mb: float = 500):
        self.enabled = enabled
        self.threshold_mb = threshold_mb
        self._gc_history: List[Dict] = []

    def set_thresholds(self, gen0: int = 700, gen1: int = 10, gen2: int = 10):
        """设置 GC 阈值"""
        gc.set_threshold(gen0, gen1, gen2)

    def collect(self, generations: Optional[List[int]] = None) -> int:
        """执行垃圾回收"""
        if generations is None:
            generations = [0, 1, 2]

        before = gc.get_allocated_objects()
        for gen in generations:
            gc.collect(gen)
        after = gc.get_allocated_objects()

        collected = len(before) - len(after)
        self._gc_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "collected": collected,
                "generations": generations,
            }
        )

        return collected

    def force_collect_if_needed(self, current_memory_mb: float) -> int:
        """必要时强制回收"""
        if not self.enabled:
            return 0

        if current_memory_mb > self.threshold_mb:
            return self.collect()
        return 0

    def get_history(self) -> List[Dict]:
        """获取 GC 历史"""
        return self._gc_history[-10:]


class LargeObjectManager:
    """大对象管理器"""

    def __init__(self, size_threshold_kb: float = 100):
        self.size_threshold_kb = size_threshold_kb
        self._large_objects: Dict[int, Dict] = {}
        self._lock = threading.Lock()

    def register(self, obj: Any, name: str):
        """注册大对象"""
        size_kb = sys.getsizeof(obj) / 1024
        if size_kb >= self.size_threshold_kb:
            obj_id = id(obj)
            with self._lock:
                self._large_objects[obj_id] = {
                    "name": name,
                    "size_kb": size_kb,
                    "type": type(obj).__name__,
                    "registered_at": datetime.now(),
                }

    def unregister(self, obj: Any):
        """取消注册"""
        obj_id = id(obj)
        with self._lock:
            if obj_id in self._large_objects:
                del self._large_objects[obj_id]

    def get_large_objects(self) -> List[Dict]:
        """获取大对象列表"""
        with self._lock:
            return list(self._large_objects.values())

    def clear_all(self):
        """清除所有大对象引用"""
        with self._lock:
            self._large_objects.clear()


@contextmanager
def memory_tracked(name: str = "operation"):
    """内存跟踪上下文"""
    tracker = get_global_tracker()
    tracker.snapshot()

    yield

    after = tracker.snapshot()
    diff = after.rss_mb - tracker._snapshots[-2].rss_mb if len(tracker.snapshot().top_objects) > 0 else 0


def get_global_tracker() -> MemoryTracker:
    """获取全局内存追踪器"""
    global _global_tracker
    if "_global_tracker" not in globals():
        _global_tracker = MemoryTracker()
    return _global_tracker


class TestMemoryManager:
    """测试内存管理器 - 整合所有功能"""

    def __init__(self, warning_threshold_mb: float = 500, critical_threshold_mb: float = 1000):
        self.tracker = MemoryTracker(warning_threshold_mb, critical_threshold_mb)
        self.gc_manager = GarbageCollectionManager()
        self.large_obj_manager = LargeObjectManager()
        self._baseline_snapshot: Optional[MemorySnapshot] = None

    def start_monitoring(self):
        """开始监控"""
        self._baseline_snapshot = self.tracker.snapshot()

    def stop_monitoring(self) -> Dict[str, Any]:
        """停止监控并获取报告"""
        leak_report = self.tracker.check_for_leaks(self._baseline_snapshot)
        stats = self.tracker.get_stats()

        return {
            "stats": {
                "current_mb": round(stats.current_mb, 2),
                "peak_mb": round(stats.peak_mb, 2),
                "average_mb": round(stats.average_mb, 2),
            },
            "leak_check": leak_report,
            "gc_history": self.gc_manager.get_history(),
            "large_objects": len(self.large_obj_manager.get_large_objects()),
        }

    def cleanup(self):
        """执行清理"""
        self.large_obj_manager.clear_all()
        collected = self.gc_manager.collect()
        gc.collect()
        return collected

    def check_and_cleanup(self) -> bool:
        """检查并清理"""
        memory_mb = self.tracker.check_memory()
        if memory_mb > self.tracker.warning_threshold:
            self.cleanup()
            return True
        return False


if __name__ == "__main__":
    print("=== Test Memory Management Demo ===")

    # 创建管理器
    manager = TestMemoryManager(warning_threshold_mb=100, critical_threshold_mb=500)

    # 开始监控
    manager.start_monitoring()

    # 模拟测试过程中的内存使用
    print("Simulating test execution...")
    for i in range(5):
        # 创建大对象
        large_data = [list(range(10000)) for _ in range(100)]
        manager.large_obj_manager.register(large_data, f"test_data_{i}")

        # 模拟处理
        time.sleep(0.01)

        # 清理
        if manager.check_and_cleanup():
            print(f"  Cleaned up after iteration {i}")

    # 停止监控
    report = manager.stop_monitoring()

    print("\nMemory Report:")
    print(f"  Current: {report['stats']['current_mb']:.2f} MB")
    print(f"  Peak: {report['stats']['peak_mb']:.2f} MB")
    print(f"  Average: {report['stats']['average_mb']:.2f} MB")
    print(f"  Leak Detected: {report['leak_check']['leak_detected']}")
    print(f"  Large Objects: {report['large_objects']}")

    print("\n✅ Memory management complete!")
