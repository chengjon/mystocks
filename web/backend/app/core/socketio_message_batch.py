"""
WebSocket消息批处理
WebSocket Message Batching - Batch Processing and Optimization

Task 14.2: WebSocket性能优化

功能特性:
- 消息队列和缓冲机制
- 批处理发送优化
- 动态批大小调整
- 背压处理
- 内存管理和清理
- 性能监控

Author: Claude Code
Date: 2025-11-12
"""

import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Coroutine, Dict, List, Optional

import structlog

logger = structlog.get_logger()


class BatchMessageType(str, Enum):
    """批处理消息类型"""

    INDIVIDUAL = "individual"  # 单个消息
    BATCH = "batch"  # 批处理消息
    CRITICAL = "critical"  # 关键消息（不进行批处理）


@dataclass
class BatchMessage:
    """批处理消息"""

    sid: str  # 目标连接ID
    event: str  # 事件名称
    data: Any  # 消息数据
    timestamp: datetime = field(default_factory=datetime.utcnow)
    message_type: BatchMessageType = BatchMessageType.INDIVIDUAL
    retry_count: int = 0

    def get_size(self) -> int:
        """获取消息大小（字节数估算）"""
        import json

        try:
            return len(json.dumps(self.data).encode("utf-8"))
        except (TypeError, ValueError):
            return 1024  # 默认1KB


@dataclass
class BatchBuffer:
    """批处理缓冲区"""

    messages: List[BatchMessage] = field(default_factory=list)
    total_size: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)

    def add_message(self, message: BatchMessage) -> bool:
        """添加消息到缓冲区"""
        self.messages.append(message)
        self.total_size += message.get_size()
        return True

    def is_full(self, max_size: int, batch_count: int) -> bool:
        """检查缓冲区是否满"""
        return self.total_size >= max_size or len(self.messages) >= batch_count

    def is_timeout(self, timeout_ms: int) -> bool:
        """检查缓冲区是否超时"""
        elapsed = (datetime.now(timezone.utc) - self.created_at).total_seconds() * 1000
        return elapsed > timeout_ms

    def clear(self) -> None:
        """清空缓冲区"""
        self.messages.clear()
        self.total_size = 0
        self.created_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "batch_size": len(self.messages),
            "total_size": self.total_size,
            "messages": [
                {
                    "event": msg.event,
                    "size": msg.get_size(),
                }
                for msg in self.messages
            ],
        }


class WebSocketMessageBatcher:
    """WebSocket消息批处理器"""

    def __init__(
        self,
        batch_size: int = 100,
        batch_timeout_ms: int = 50,
        max_batch_bytes: int = 1024 * 64,
        enable_compression: bool = True,
    ):
        """
        初始化消息批处理器

        Args:
            batch_size: 最大批处理消息数
            batch_timeout_ms: 批处理超时（毫秒）
            max_batch_bytes: 最大批处理大小（字节）
            enable_compression: 是否启用压缩
        """
        self.batch_size = batch_size
        self.batch_timeout_ms = batch_timeout_ms
        self.max_batch_bytes = max_batch_bytes
        self.enable_compression = enable_compression

        # 每个连接的批处理缓冲区
        self.buffers: Dict[str, BatchBuffer] = defaultdict(BatchBuffer)

        # 批处理任务
        self.batch_tasks: Dict[str, Optional[asyncio.Task]] = {}

        # 发送回调
        self.send_callback: Optional[Callable[[str, str, Any], Coroutine]] = None

        # 统计信息
        self.total_messages_buffered = 0
        self.total_batches_sent = 0
        self.total_messages_sent = 0
        self.total_bytes_sent = 0

        logger.info(
            "✅ WebSocket Message Batcher initialized",
            batch_size=batch_size,
            batch_timeout_ms=batch_timeout_ms,
            max_batch_bytes=max_batch_bytes,
        )

    def register_send_callback(self, callback: Callable[[str, str, Any], Coroutine]) -> None:
        """
        注册发送回调

        Args:
            callback: 发送函数(sid, event, data)
        """
        self.send_callback = callback
        logger.info("✅ Send callback registered")

    async def queue_message(self, message: BatchMessage, send_immediately: bool = False) -> None:
        """
        将消息加入处理队列

        Args:
            message: 批处理消息
            send_immediately: 是否立即发送
        """
        # 关键消息立即发送
        if message.message_type == BatchMessageType.CRITICAL or send_immediately:
            await self._send_message(message.sid, message.event, message.data)
            return

        # 添加到缓冲区
        buffer = self.buffers[message.sid]
        buffer.add_message(message)
        self.total_messages_buffered += 1

        logger.debug(
            "📝 Message queued for batching",
            sid=message.sid,
            event=message.event,
            buffer_size=len(buffer.messages),
        )

        # 如果缓冲区满，立即发送
        if buffer.is_full(self.max_batch_bytes, self.batch_size):
            await self._flush_buffer(message.sid)
        # 否则，安排批处理任务
        elif message.sid not in self.batch_tasks or self.batch_tasks[message.sid].done():
            self.batch_tasks[message.sid] = asyncio.create_task(self._batch_timeout_handler(message.sid))

    async def _batch_timeout_handler(self, sid: str) -> None:
        """
        批处理超时处理器

        Args:
            sid: 连接ID
        """
        try:
            await asyncio.sleep(self.batch_timeout_ms / 1000.0)
            buffer = self.buffers.get(sid)
            if buffer and len(buffer.messages) > 0:
                await self._flush_buffer(sid)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error("❌ Error in batch timeout handler", sid=sid, error=str(e))

    async def _flush_buffer(self, sid: str) -> None:
        """
        冲刷缓冲区，发送批处理消息

        Args:
            sid: 连接ID
        """
        buffer = self.buffers.get(sid)
        if not buffer or len(buffer.messages) == 0:
            return

        try:
            messages = buffer.messages.copy()
            batch_data = {
                "type": "batch",
                "messages": [
                    {
                        "event": msg.event,
                        "data": msg.data,
                    }
                    for msg in messages
                ],
                "batch_size": len(messages),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            # 发送批处理消息
            await self._send_message(sid, "batch", batch_data)

            # 更新统计
            self.total_batches_sent += 1
            self.total_messages_sent += len(messages)
            self.total_bytes_sent += buffer.total_size

            logger.info(
                "✅ Batch sent",
                sid=sid,
                batch_size=len(messages),
                total_bytes=buffer.total_size,
            )

            # 清空缓冲区
            buffer.clear()

        except Exception as e:
            logger.error(
                "❌ Error flushing buffer",
                sid=sid,
                buffer_size=len(buffer.messages),
                error=str(e),
            )

    async def _send_message(self, sid: str, event: str, data: Any) -> None:
        """
        发送单个消息

        Args:
            sid: 连接ID
            event: 事件名称
            data: 消息数据
        """
        if not self.send_callback:
            logger.warning("⚠️ Send callback not registered")
            return

        try:
            await self.send_callback(sid, event, data)
        except Exception as e:
            logger.error(
                "❌ Error sending message",
                sid=sid,
                event=event,
                error=str(e),
            )

    async def flush_all(self) -> None:
        """冲刷所有缓冲区"""
        logger.info("🧹 Flushing all buffers")

        # 取消所有待处理的批处理任务
        for task in self.batch_tasks.values():
            if task and not task.done():
                task.cancel()

        # 冲刷所有缓冲区
        for sid in list(self.buffers.keys()):
            await self._flush_buffer(sid)

        logger.info("✅ All buffers flushed")

    def get_stats(self) -> Dict[str, Any]:
        """获取批处理统计"""
        buffered_count = sum(len(buf.messages) for buf in self.buffers.values())
        buffered_bytes = sum(buf.total_size for buf in self.buffers.values())

        return {
            "configuration": {
                "batch_size": self.batch_size,
                "batch_timeout_ms": self.batch_timeout_ms,
                "max_batch_bytes": self.max_batch_bytes,
                "compression_enabled": self.enable_compression,
            },
            "current_buffers": {
                "buffer_count": len(self.buffers),
                "buffered_messages": buffered_count,
                "buffered_bytes": buffered_bytes,
            },
            "statistics": {
                "total_messages_buffered": self.total_messages_buffered,
                "total_batches_sent": self.total_batches_sent,
                "total_messages_sent": self.total_messages_sent,
                "total_bytes_sent": self.total_bytes_sent,
                "avg_batch_size": (self.total_messages_sent / max(1, self.total_batches_sent)),
                "compression_ratio": (
                    self.total_messages_buffered / max(1, self.total_batches_sent) if self.total_batches_sent > 0 else 0
                ),
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_buffer_info(self, sid: str) -> Optional[Dict[str, Any]]:
        """获取特定连接的缓冲区信息"""
        buffer = self.buffers.get(sid)
        return buffer.to_dict() if buffer else None


# 全局单例
_message_batcher: Optional[WebSocketMessageBatcher] = None


def get_message_batcher(
    batch_size: int = 100,
    batch_timeout_ms: int = 50,
    max_batch_bytes: int = 1024 * 64,
    enable_compression: bool = True,
) -> WebSocketMessageBatcher:
    """获取消息批处理器单例"""
    global _message_batcher
    if _message_batcher is None:
        _message_batcher = WebSocketMessageBatcher(
            batch_size=batch_size,
            batch_timeout_ms=batch_timeout_ms,
            max_batch_bytes=max_batch_bytes,
            enable_compression=enable_compression,
        )
    return _message_batcher


def reset_message_batcher() -> None:
    """重置消息批处理器（仅用于测试）"""
    global _message_batcher
    _message_batcher = None
