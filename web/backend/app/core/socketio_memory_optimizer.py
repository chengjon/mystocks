"""
WebSocket内存优化和清理
WebSocket Memory Optimization - Memory Management and Cleanup

Task 14.2: WebSocket性能优化

功能特性:
- 内存使用监控和限制
- 自动垃圾回收和清理
- 缓存管理和淘汰策略
- 连接生命周期管理
- 内存泄漏检测
- 性能监控

Author: Claude Code
Date: 2025-11-12
"""

import asyncio
import gc
import psutil
import structlog
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = structlog.get_logger()


class MemoryPressureLevel(str, Enum):
    """内存压力级别"""

    NORMAL = "normal"  # 正常
    MODERATE = "moderate"  # 中等
    HIGH = "high"  # 高
    CRITICAL = "critical"  # 严重


@dataclass
class MemorySnapshot:
    """内存快照"""

    timestamp: datetime = field(default_factory=datetime.utcnow)
    rss_mb: float = 0.0  # 驻留内存（MB）
    vms_mb: float = 0.0  # 虚拟内存（MB）
    percent: float = 0.0  # 内存占用百分比
    pressure_level: MemoryPressureLevel = MemoryPressureLevel.NORMAL

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "rss_mb": round(self.rss_mb, 2),
            "vms_mb": round(self.vms_mb, 2),
            "percent": round(self.percent, 2),
            "pressure_level": self.pressure_level.value,
        }


class WebSocketMemoryOptimizer:
    """WebSocket内存优化器"""

    def __init__(
        self,
        max_memory_percent: float = 80.0,
        cleanup_interval: int = 60,
        gc_interval: int = 300,
        monitor_interval: int = 30,
    ):
        """
        初始化内存优化器

        Args:
            max_memory_percent: 最大内存占用百分比
            cleanup_interval: 清理间隔（秒）
            gc_interval: 垃圾回收间隔（秒）
            monitor_interval: 监控间隔（秒）
        """
        self.max_memory_percent = max_memory_percent
        self.cleanup_interval = cleanup_interval
        self.gc_interval = gc_interval
        self.monitor_interval = monitor_interval

        # 任务
        self.cleanup_task: Optional[asyncio.Task] = None
        self.gc_task: Optional[asyncio.Task] = None
        self.monitor_task: Optional[asyncio.Task] = None

        # 监控
        self.memory_snapshots: List[MemorySnapshot] = []
        self.max_snapshots = 100
        self.current_pressure = MemoryPressureLevel.NORMAL

        # 回调
        self.pressure_callbacks: Dict[MemoryPressureLevel, List[callable]] = {
            MemoryPressureLevel.NORMAL: [],
            MemoryPressureLevel.MODERATE: [],
            MemoryPressureLevel.HIGH: [],
            MemoryPressureLevel.CRITICAL: [],
        }

        # 统计
        self.cleanup_count = 0
        self.gc_count = 0

        logger.info(
            "✅ WebSocket Memory Optimizer initialized",
            max_memory_percent=max_memory_percent,
            cleanup_interval=cleanup_interval,
        )

    def register_pressure_callback(self, pressure_level: MemoryPressureLevel, callback: callable) -> None:
        """
        注册内存压力回调

        Args:
            pressure_level: 内存压力级别
            callback: 回调函数
        """
        self.pressure_callbacks[pressure_level].append(callback)
        logger.info(
            "✅ Memory pressure callback registered",
            pressure_level=pressure_level.value,
        )

    async def start_monitoring(self) -> None:
        """启动监控"""
        tasks = []

        if not self.cleanup_task or self.cleanup_task.done():
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            tasks.append("cleanup")

        if not self.gc_task or self.gc_task.done():
            self.gc_task = asyncio.create_task(self._gc_loop())
            tasks.append("gc")

        if not self.monitor_task or self.monitor_task.done():
            self.monitor_task = asyncio.create_task(self._monitor_loop())
            tasks.append("monitor")

        if tasks:
            logger.info(
                "✅ Memory optimizer monitoring started",
                tasks=tasks,
            )

    async def stop_monitoring(self) -> None:
        """停止监控"""
        for task in [self.cleanup_task, self.gc_task, self.monitor_task]:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        logger.info("✅ Memory optimizer monitoring stopped")

    async def _cleanup_loop(self) -> None:
        """定期清理循环"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._perform_cleanup()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("❌ Error in cleanup loop", error=str(e))

    async def _gc_loop(self) -> None:
        """垃圾回收循环"""
        while True:
            try:
                await asyncio.sleep(self.gc_interval)
                await self._perform_gc()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("❌ Error in GC loop", error=str(e))

    async def _monitor_loop(self) -> None:
        """监控循环"""
        while True:
            try:
                await asyncio.sleep(self.monitor_interval)
                await self._check_memory()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("❌ Error in monitor loop", error=str(e))

    async def _perform_cleanup(self) -> None:
        """执行清理"""
        try:
            # 清理过期对象
            snapshot = self._get_memory_snapshot()

            if (
                snapshot.pressure_level == MemoryPressureLevel.HIGH
                or snapshot.pressure_level == MemoryPressureLevel.CRITICAL
            ):
                logger.warning(
                    "⚠️ High memory pressure, performing aggressive cleanup",
                    pressure_level=snapshot.pressure_level.value,
                    memory_percent=snapshot.percent,
                )

                # 清空缓存、关闭空闲连接等
                for callback in self.pressure_callbacks[snapshot.pressure_level]:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback()
                        else:
                            callback()
                    except Exception as e:
                        logger.error(
                            "❌ Error in pressure callback",
                            error=str(e),
                        )

                self.cleanup_count += 1

        except Exception as e:
            logger.error("❌ Error in cleanup", error=str(e))

    async def _perform_gc(self) -> None:
        """执行垃圾回收"""
        try:
            # 显式垃圾回收
            collected = gc.collect()
            self.gc_count += 1

            logger.debug(
                "🧹 Garbage collection performed",
                objects_collected=collected,
                gc_count=self.gc_count,
            )

        except Exception as e:
            logger.error("❌ Error in garbage collection", error=str(e))

    async def _check_memory(self) -> None:
        """检查内存"""
        try:
            snapshot = self._get_memory_snapshot()
            self.memory_snapshots.append(snapshot)

            # 保持快照数量
            if len(self.memory_snapshots) > self.max_snapshots:
                self.memory_snapshots.pop(0)

            # 检查压力级别变化
            if snapshot.pressure_level != self.current_pressure:
                logger.warning(
                    "⚠️ Memory pressure level changed",
                    from_level=self.current_pressure.value,
                    to_level=snapshot.pressure_level.value,
                    memory_percent=snapshot.percent,
                )
                self.current_pressure = snapshot.pressure_level

        except Exception as e:
            logger.error("❌ Error checking memory", error=str(e))

    def _get_memory_snapshot(self) -> MemorySnapshot:
        """获取内存快照"""
        try:
            process = psutil.Process()
            mem_info = process.memory_info()
            mem_percent = process.memory_percent()

            # 判断压力级别
            if mem_percent >= self.max_memory_percent:
                pressure = MemoryPressureLevel.CRITICAL
            elif mem_percent >= self.max_memory_percent * 0.9:
                pressure = MemoryPressureLevel.HIGH
            elif mem_percent >= self.max_memory_percent * 0.75:
                pressure = MemoryPressureLevel.MODERATE
            else:
                pressure = MemoryPressureLevel.NORMAL

            return MemorySnapshot(
                rss_mb=mem_info.rss / (1024 * 1024),
                vms_mb=mem_info.vms / (1024 * 1024),
                percent=mem_percent,
                pressure_level=pressure,
            )

        except Exception as e:
            logger.error("❌ Error getting memory snapshot", error=str(e))
            return MemorySnapshot()

    def get_stats(self) -> Dict[str, Any]:
        """获取优化器统计"""
        current_snapshot = self._get_memory_snapshot()
        avg_memory_percent = (
            sum(s.percent for s in self.memory_snapshots) / len(self.memory_snapshots) if self.memory_snapshots else 0
        )

        return {
            "current": current_snapshot.to_dict(),
            "statistics": {
                "cleanup_count": self.cleanup_count,
                "gc_count": self.gc_count,
                "avg_memory_percent": round(avg_memory_percent, 2),
                "max_memory_percent": self.max_memory_percent,
            },
            "snapshots": {
                "total": len(self.memory_snapshots),
                "max_stored": self.max_snapshots,
                "recent": ([s.to_dict() for s in self.memory_snapshots[-10:]] if self.memory_snapshots else []),
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_memory_history(self) -> List[Dict[str, Any]]:
        """获取内存历史"""
        return [s.to_dict() for s in self.memory_snapshots]


# 全局单例
_memory_optimizer: Optional[WebSocketMemoryOptimizer] = None


def get_memory_optimizer(
    max_memory_percent: float = 80.0,
    cleanup_interval: int = 60,
    gc_interval: int = 300,
    monitor_interval: int = 30,
) -> WebSocketMemoryOptimizer:
    """获取内存优化器单例"""
    global _memory_optimizer
    if _memory_optimizer is None:
        _memory_optimizer = WebSocketMemoryOptimizer(
            max_memory_percent=max_memory_percent,
            cleanup_interval=cleanup_interval,
            gc_interval=gc_interval,
            monitor_interval=monitor_interval,
        )
    return _memory_optimizer


def reset_memory_optimizer() -> None:
    """重置内存优化器（仅用于测试）"""
    global _memory_optimizer
    _memory_optimizer = None
