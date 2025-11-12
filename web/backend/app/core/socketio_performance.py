"""
WebSocket性能优化集成
WebSocket Performance Optimization Integration - Complete Optimization System

Task 14.2: WebSocket性能优化

整合以下优化模块:
- 连接池管理 (Connection Pool)
- 消息批处理 (Message Batching)
- 内存优化 (Memory Optimization)
- 性能监控 (Performance Monitoring)

Author: Claude Code
Date: 2025-11-12
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import structlog

from app.core.socketio_connection_pool import (
    get_connection_pool,
    WebSocketConnectionPool,
)
from app.core.socketio_message_batch import (
    get_message_batcher,
    WebSocketMessageBatcher,
    BatchMessage,
    BatchMessageType,
)
from app.core.socketio_memory_optimizer import (
    get_memory_optimizer,
    WebSocketMemoryOptimizer,
    MemoryPressureLevel,
)

logger = structlog.get_logger()


@dataclass
class PerformanceMetrics:
    """性能指标"""

    timestamp: datetime
    active_connections: int
    idle_connections: int
    buffer_messages: int
    memory_percent: float
    memory_pressure: str
    messages_sent_per_sec: float
    avg_batch_size: float
    connection_reuse_rate: float
    gc_count: int


class WebSocketPerformanceManager:
    """WebSocket性能管理器 - 整合所有优化模块"""

    def __init__(
        self,
        # 连接池配置
        pool_min_size: int = 10,
        pool_max_size: int = 1000,
        pool_stale_timeout: int = 300,
        # 消息批处理配置
        batch_size: int = 100,
        batch_timeout_ms: int = 50,
        batch_max_bytes: int = 1024 * 64,
        # 内存优化配置
        max_memory_percent: float = 80.0,
        cleanup_interval: int = 60,
    ):
        """
        初始化性能管理器

        Args:
            pool_min_size: 连接池最小大小
            pool_max_size: 连接池最大大小
            pool_stale_timeout: 连接陈旧超时
            batch_size: 批处理大小
            batch_timeout_ms: 批处理超时
            batch_max_bytes: 批处理最大字节数
            max_memory_percent: 最大内存占用百分比
            cleanup_interval: 清理间隔
        """
        # 初始化所有优化模块
        self.connection_pool = get_connection_pool(
            min_size=pool_min_size,
            max_size=pool_max_size,
            stale_timeout=pool_stale_timeout,
        )

        self.message_batcher = get_message_batcher(
            batch_size=batch_size,
            batch_timeout_ms=batch_timeout_ms,
            max_batch_bytes=batch_max_bytes,
        )

        self.memory_optimizer = get_memory_optimizer(
            max_memory_percent=max_memory_percent,
            cleanup_interval=cleanup_interval,
        )

        # 配置内存压力回调
        self.memory_optimizer.register_pressure_callback(
            MemoryPressureLevel.HIGH, self._on_high_memory_pressure
        )
        self.memory_optimizer.register_pressure_callback(
            MemoryPressureLevel.CRITICAL, self._on_critical_memory_pressure
        )

        # 统计
        self.metrics_history: List[PerformanceMetrics] = []
        self.max_metrics = 1440  # 保持24小时的分钟级数据

        logger.info(
            "✅ WebSocket Performance Manager initialized",
            pool_min=pool_min_size,
            pool_max=pool_max_size,
            batch_size=batch_size,
            batch_timeout_ms=batch_timeout_ms,
        )

    async def initialize(self) -> None:
        """初始化性能管理器"""
        # 启动连接池清理
        await self.connection_pool.start_cleanup()

        # 启动内存监控
        await self.memory_optimizer.start_monitoring()

        logger.info("✅ Performance Manager initialized and monitoring started")

    async def shutdown(self) -> None:
        """关闭性能管理器"""
        # 停止所有监控任务
        await self.connection_pool.stop_cleanup()
        await self.memory_optimizer.stop_monitoring()

        # 冲刷所有缓冲区
        await self.message_batcher.flush_all()

        # 清空连接池
        await self.connection_pool.drain()

        logger.info("✅ Performance Manager shut down")

    async def acquire_connection(self, user_id: Optional[str] = None):
        """获取连接"""
        return await self.connection_pool.acquire_connection(user_id)

    async def release_connection(self, sid: str, error: bool = False) -> None:
        """释放连接"""
        await self.connection_pool.release_connection(sid, error)

    async def queue_message(
        self,
        sid: str,
        event: str,
        data: Any,
        message_type: BatchMessageType = BatchMessageType.INDIVIDUAL,
        send_immediately: bool = False,
    ) -> None:
        """
        排队消息发送

        Args:
            sid: 连接ID
            event: 事件名称
            data: 消息数据
            message_type: 消息类型
            send_immediately: 是否立即发送
        """
        message = BatchMessage(
            sid=sid,
            event=event,
            data=data,
            message_type=message_type,
        )
        await self.message_batcher.queue_message(message, send_immediately)

    async def flush_messages(self) -> None:
        """冲刷所有缓冲的消息"""
        await self.message_batcher.flush_all()

    async def _on_high_memory_pressure(self) -> None:
        """高内存压力回调"""
        logger.warning("⚠️ High memory pressure detected, flushing message buffers")
        await self.message_batcher.flush_all()

    async def _on_critical_memory_pressure(self) -> None:
        """严重内存压力回调"""
        logger.critical(
            "❌ Critical memory pressure detected, aggressive cleanup initiated"
        )
        # 冲刷所有缓冲区
        await self.message_batcher.flush_all()

        # 可选：关闭一些空闲连接
        # 这里可以添加更激进的清理策略

    async def collect_metrics(self) -> PerformanceMetrics:
        """收集性能指标"""
        pool_stats = self.connection_pool.get_stats()
        batch_stats = self.message_batcher.get_stats()
        memory_stats = self.memory_optimizer.get_stats()

        metrics = PerformanceMetrics(
            timestamp=datetime.utcnow(),
            active_connections=pool_stats["pool_size"]["active"],
            idle_connections=pool_stats["pool_size"]["idle"],
            buffer_messages=batch_stats["current_buffers"]["buffered_messages"],
            memory_percent=memory_stats["current"]["percent"],
            memory_pressure=memory_stats["current"]["pressure_level"],
            messages_sent_per_sec=(
                batch_stats["statistics"]["total_messages_sent"]
                / max(1, batch_stats["statistics"]["total_batches_sent"])
            ),
            avg_batch_size=batch_stats["statistics"]["avg_batch_size"],
            connection_reuse_rate=pool_stats["statistics"]["reuse_rate"],
            gc_count=memory_stats["statistics"]["gc_count"],
        )

        # 保持最近的指标历史
        self.metrics_history.append(metrics)
        if len(self.metrics_history) > self.max_metrics:
            self.metrics_history.pop(0)

        return metrics

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """获取综合统计信息"""
        pool_stats = self.connection_pool.get_stats()
        batch_stats = self.message_batcher.get_stats()
        memory_stats = self.memory_optimizer.get_stats()

        return {
            "connection_pool": pool_stats,
            "message_batcher": batch_stats,
            "memory_optimizer": memory_stats,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能总结"""
        if not self.metrics_history:
            return {
                "status": "no_data",
                "message": "No metrics collected yet",
            }

        recent_metrics = self.metrics_history[-60:]  # 最近60个数据点

        avg_active = sum(m.active_connections for m in recent_metrics) / len(
            recent_metrics
        )
        avg_memory = sum(m.memory_percent for m in recent_metrics) / len(
            recent_metrics
        )
        avg_batch_size = sum(m.avg_batch_size for m in recent_metrics) / len(
            recent_metrics
        )

        return {
            "period": "last_60_measurements",
            "average_active_connections": round(avg_active, 2),
            "average_memory_percent": round(avg_memory, 2),
            "average_batch_size": round(avg_batch_size, 2),
            "peak_active_connections": max(m.active_connections for m in recent_metrics),
            "peak_memory_percent": max(m.memory_percent for m in recent_metrics),
            "connection_reuse_rate": (
                sum(m.connection_reuse_rate for m in recent_metrics)
                / len(recent_metrics)
            ),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def export_metrics_history(self) -> List[Dict[str, Any]]:
        """导出指标历史"""
        return [
            {
                "timestamp": m.timestamp.isoformat(),
                "active_connections": m.active_connections,
                "idle_connections": m.idle_connections,
                "buffer_messages": m.buffer_messages,
                "memory_percent": round(m.memory_percent, 2),
                "memory_pressure": m.memory_pressure,
                "messages_sent_per_sec": round(m.messages_sent_per_sec, 2),
                "avg_batch_size": round(m.avg_batch_size, 2),
                "connection_reuse_rate": round(m.connection_reuse_rate, 2),
                "gc_count": m.gc_count,
            }
            for m in self.metrics_history
        ]


# 全局单例
_performance_manager: Optional[WebSocketPerformanceManager] = None


def get_performance_manager(
    pool_min_size: int = 10,
    pool_max_size: int = 1000,
    pool_stale_timeout: int = 300,
    batch_size: int = 100,
    batch_timeout_ms: int = 50,
    batch_max_bytes: int = 1024 * 64,
    max_memory_percent: float = 80.0,
    cleanup_interval: int = 60,
) -> WebSocketPerformanceManager:
    """获取性能管理器单例"""
    global _performance_manager
    if _performance_manager is None:
        _performance_manager = WebSocketPerformanceManager(
            pool_min_size=pool_min_size,
            pool_max_size=pool_max_size,
            pool_stale_timeout=pool_stale_timeout,
            batch_size=batch_size,
            batch_timeout_ms=batch_timeout_ms,
            batch_max_bytes=batch_max_bytes,
            max_memory_percent=max_memory_percent,
            cleanup_interval=cleanup_interval,
        )
    return _performance_manager


def reset_performance_manager() -> None:
    """重置性能管理器（仅用于测试）"""
    global _performance_manager
    _performance_manager = None
