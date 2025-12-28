#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks 内存管理器

提供统一的内存管理功能，包括：
1. 内存使用监控
2. 资源自动清理
3. 内存限制管理
4. 缓存大小控制
5. 内存泄漏检测

作者: MyStocks项目组
版本: v1.0
日期: 2025-12-06
"""

import gc
import psutil
import threading
import time
import weakref
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger("MyStocksMemoryManager")


@dataclass
class MemoryStats:
    """内存统计信息"""

    timestamp: datetime
    process_memory_mb: float
    system_memory_percent: float
    active_objects: int
    total_objects: int
    leak_candidates: List[str]


class MemoryLimit:
    """内存限制管理器"""

    def __init__(self, max_memory_mb: int = 1024, warning_threshold: float = 0.8):
        """
        初始化内存限制

        Args:
            max_memory_mb: 最大内存使用量（MB）
            warning_threshold: 警告阈值（0-1）
        """
        self.max_memory_mb = max_memory_mb
        self.warning_threshold = warning_threshold
        self.warning_threshold_mb = max_memory_mb * warning_threshold
        self._lock = threading.Lock()
        self._monitors: List[Callable] = []

    def check_memory_usage(self) -> float:
        """
        检查当前内存使用量

        Returns:
            float: 当前内存使用量（MB）
        """
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        return memory_mb

    def is_approaching_limit(self) -> bool:
        """检查是否接近内存限制"""
        current = self.check_memory_usage()
        return current >= self.warning_threshold_mb

    def is_over_limit(self) -> bool:
        """检查是否超过内存限制"""
        current = self.check_memory_usage()
        return current >= self.max_memory_mb

    def register_monitor(self, callback: Callable[[float], None]):
        """注册内存监控回调"""
        with self._lock:
            self._monitors.append(callback)

    def notify_monitors(self, memory_mb: float):
        """通知所有监控器"""
        with self._lock:
            for callback in self._monitors:
                try:
                    callback(memory_mb)
                except Exception as e:
                    logger.error("内存监控器回调失败: %s", str(e))


class ResourceManager:
    """资源管理器 - 自动管理生命周期"""

    def __init__(self):
        """初始化资源管理器"""
        self._resources: Dict[str, Any] = {}
        self._weak_refs: Dict[str, weakref.ref] = {}
        self._cleanup_callbacks: Dict[str, Callable] = {}
        self._lock = threading.RLock()
        self._memory_stats = []

    def register_resource(
        self,
        resource_id: str,
        resource: Any,
        cleanup_callback: Optional[Callable] = None,
        weak_ref: bool = False,
    ):
        """
        注册资源进行管理

        Args:
            resource_id: 资源ID
            resource: 资源对象
            cleanup_callback: 清理回调函数
            weak_ref: 是否使用弱引用
        """
        with self._lock:
            if resource_id in self._resources:
                logger.warning("资源已存在，将被替换", resource_id=resource_id)

            self._resources[resource_id] = resource

            if cleanup_callback:
                self._cleanup_callbacks[resource_id] = cleanup_callback

            if weak_ref:
                self._weak_refs[resource_id] = weakref.ref(resource, lambda ref: self._auto_cleanup(resource_id))

    def unregister_resource(self, resource_id: str):
        """注销资源"""
        with self._lock:
            if resource_id in self._resources:
                self._cleanup_resource(resource_id)
                self._resources.pop(resource_id, None)
                self._weak_refs.pop(resource_id, None)
                self._cleanup_callbacks.pop(resource_id, None)

    def _cleanup_resource(self, resource_id: str):
        """清理单个资源"""
        if resource_id in self._cleanup_callbacks:
            try:
                self._cleanup_callbacks[resource_id]()
                logger.debug("资源清理成功: %s", resource_id)
            except Exception as e:
                logger.error("资源清理失败: %s, 错误: %s", resource_id, str(e))

        self._cleanup_callbacks.pop(resource_id, None)

    def _auto_cleanup(self, resource_id: str):
        """自动清理资源（弱引用回调）"""
        logger.info("弱引用触发资源清理: %s", resource_id)
        self.unregister_resource(resource_id)

    def get_resource(self, resource_id: str) -> Optional[Any]:
        """获取资源"""
        with self._lock:
            return self._resources.get(resource_id)

    def cleanup_all(self):
        """清理所有资源"""
        with self._lock:
            logger.info("开始清理所有资源，数量: %s", len(self._resources))

            # 按顺序清理资源
            for resource_id in list(self._resources.keys()):
                self._cleanup_resource(resource_id)

            # 清空存储
            self._resources.clear()
            self._weak_refs.clear()

            logger.info("所有资源清理完成")

    def get_stats(self) -> Dict[str, Any]:
        """获取资源统计信息"""
        with self._lock:
            return {
                "total_resources": len(self._resources),
                "total_cleanup_callbacks": len(self._cleanup_callbacks),
                "weak_refs": len(self._weak_refs),
                "resource_ids": list(self._resources.keys()),
            }


class MemoryMonitor:
    """内存监控器"""

    def __init__(self, check_interval: int = 60, max_history: int = 1000):
        """
        初始化内存监控器

        Args:
            check_interval: 检查间隔（秒）
            max_history: 最大历史记录数
        """
        self.check_interval = check_interval
        self.max_history = max_history
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._stats_lock = threading.Lock()
        self._stats_history: List[MemoryStats] = []
        self._memory_limit = MemoryLimit()

    def start(self):
        """启动内存监控"""
        if self._running:
            logger.warning("内存监控器已在运行")
            return

        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        logger.info("内存监控器已启动，检查间隔: %s秒", self.check_interval)

    def stop(self):
        """停止内存监控"""
        if not self._running:
            return

        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

        logger.info("内存监控器已停止")

    def _monitor_loop(self):
        """监控循环"""
        while self._running:
            try:
                stats = self._collect_stats()
                self._update_stats_history(stats)
                self._check_memory_limits(stats)

                # 强制垃圾回收（但不回收循环引用）
                if len(self._stats_history) % 10 == 0:
                    collected = gc.collect()
                    if collected > 0:
                        logger.debug("垃圾回收: 回收了 %s 个对象", collected)

            except Exception as e:
                logger.error("内存监控失败: %s", str(e))

            time.sleep(self.check_interval)

    def _collect_stats(self) -> MemoryStats:
        """收集内存统计信息"""
        process = psutil.Process()

        # 进程内存使用
        memory_mb = process.memory_info().rss / 1024 / 1024

        # 系统内存使用率
        system_memory = psutil.virtual_memory()
        system_percent = system_memory.percent

        # 对象统计
        all_objects = len(gc.get_objects())
        active_objects = len([obj for obj in gc.get_objects() if obj is not None])

        # 检测可能的内存泄漏（长期存在的对象）
        leak_candidates = self._detect_leak_candidates()

        return MemoryStats(
            timestamp=datetime.now(),
            process_memory_mb=memory_mb,
            system_memory_percent=system_percent,
            active_objects=active_objects,
            total_objects=all_objects,
            leak_candidates=leak_candidates,
        )

    def _update_stats_history(self, stats: MemoryStats):
        """更新统计历史"""
        with self._stats_lock:
            self._stats_history.append(stats)

            # 保持历史记录在限制范围内
            if len(self._stats_history) > self.max_history:
                self._stats_history = self._stats_history[-self.max_history :]

    def _check_memory_limits(self, stats: MemoryStats):
        """检查内存限制"""
        # 检查是否超过警告阈值
        if self._memory_limit.is_approaching_limit():
            logger.warning("内存使用接近限制: %sMB/%sMB", stats.process_memory_mb, self._memory_limit.max_memory_mb)

        # 检查是否超过限制
        if self._memory_limit.is_over_limit():
            logger.error("内存使用超过限制: %sMB/%sMB", stats.process_memory_mb, self._memory_limit.max_memory_mb)

            # 触发紧急清理
            self._emergency_cleanup()

        # 通知监控器
        self._memory_limit.notify_monitors(stats.process_memory_mb)

    def _detect_leak_candidates(self) -> List[str]:
        """检测可能的内存泄漏候选者"""
        candidates = []

        # 获取所有对象类型统计
        type_counts = {}
        for obj in gc.get_objects():
            obj_type = type(obj).__name__
            type_counts[obj_type] = type_counts.get(obj_type, 0) + 1

        # 找出数量异常的类型
        for obj_type, count in type_counts.items():
            if count > 1000:  # 阈值可配置
                candidates.append(f"{obj_type}:{count}")

        return candidates[-5:]  # 返回前5个

    def _emergency_cleanup(self):
        """紧急清理"""
        logger.warning("执行紧急内存清理")

        # 清理所有可回收的对象
        collected = gc.collect()
        logger.info("紧急垃圾回收: 回收了 %s 个对象", collected)

        # 清理资源管理器中的资源
        from src.core.memory_manager import resource_manager

        resource_manager.cleanup_all()

    def get_current_stats(self) -> MemoryStats:
        """获取当前统计信息"""
        with self._stats_lock:
            return (
                self._stats_history[-1]
                if self._stats_history
                else MemoryStats(
                    timestamp=datetime.now(),
                    process_memory_mb=0,
                    system_memory_percent=0,
                    active_objects=0,
                    total_objects=0,
                    leak_candidates=[],
                )
            )

    def get_history(self) -> List[MemoryStats]:
        """获取历史统计"""
        with self._stats_lock:
            return self._stats_history.copy()


# 全局实例
_resource_manager = ResourceManager()
_memory_monitor = MemoryMonitor()


def get_resource_manager() -> ResourceManager:
    """获取全局资源管理器"""
    return _resource_manager


def get_memory_monitor() -> MemoryMonitor:
    """获取全局内存监控器"""
    return _memory_monitor


def initialize_memory_management():
    """初始化内存管理系统"""
    logger.info("初始化内存管理系统")

    # 启动内存监控
    _memory_monitor.start()

    # 注册清理钩子
    import atexit

    atexit.register(shutdown_memory_management)

    logger.info("内存管理系统初始化完成")


def shutdown_memory_management():
    """关闭内存管理系统"""
    logger.info("关闭内存管理系统")

    # 停止监控
    _memory_monitor.stop()

    # 清理所有资源
    _resource_manager.cleanup_all()

    # 最终垃圾回收
    gc.collect()

    logger.info("内存管理系统已关闭")


# 自动初始化
initialize_memory_management()


# 便利函数
def register_resource(resource_id: str, resource: Any, cleanup_callback=None):
    """注册资源进行管理"""
    _resource_manager.register_resource(resource_id, resource, cleanup_callback)


def unregister_resource(resource_id: str):
    """注销资源"""
    _resource_manager.unregister_resource(resource_id)


def cleanup_all_resources():
    """清理所有资源"""
    _resource_manager.cleanup_all()


def get_memory_stats() -> Dict[str, Any]:
    """获取内存统计信息"""
    current = _memory_monitor.get_current_stats()
    history = _memory_monitor.get_history()

    return {
        "current": {
            "timestamp": current.timestamp.isoformat(),
            "process_memory_mb": current.process_memory_mb,
            "system_memory_percent": current.system_memory_percent,
            "active_objects": current.active_objects,
            "total_objects": current.total_objects,
            "leak_candidates": current.leak_candidates,
        },
        "resource_manager": _resource_manager.get_stats(),
        "history_length": len(history),
    }
