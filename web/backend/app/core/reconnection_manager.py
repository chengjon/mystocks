"""
WebSocket客户端重连机制管理器

Client Reconnection Manager - Handle auto-reconnect with message buffering

Task 4.4: 实现客户端重连机制

Features:
- Exponential backoff reconnection strategy (3s base interval, up to 30s)
- Local message buffering for offline messages
- Automatic message resend on successful reconnection
- Reconnection state tracking per connection
- Max retry limits (default 5 retries)
- Message deduplication on resend

Author: Claude Code
Date: 2025-11-06
"""

import uuid
from typing import Dict, Optional, List, Any
from datetime import datetime
from enum import Enum
import structlog
import time

logger = structlog.get_logger()


class ReconnectionState(str, Enum):
    """重连状态枚举"""

    CONNECTED = "connected"  # 已连接
    DISCONNECTED = "disconnected"  # 已断开
    RECONNECTING = "reconnecting"  # 重连中
    RECONNECT_FAILED = "reconnect_failed"  # 重连失败


class OfflineMessage:
    """离线消息"""

    def __init__(
        self,
        event: str,
        data: Dict[str, Any],
        room: Optional[str] = None,
    ):
        """
        初始化离线消息

        Args:
            event: 事件名称
            data: 消息数据
            room: 房间名称
        """
        self.id = str(uuid.uuid4())
        self.event = event
        self.data = data
        self.room = room
        self.created_at = datetime.utcnow()
        self.retry_count = 0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "event": self.event,
            "data": self.data,
            "room": self.room,
            "created_at": self.created_at.isoformat(),
            "retry_count": self.retry_count,
        }


class MessageBuffer:
    """离线消息缓冲区"""

    def __init__(self, max_size: int = 100):
        """
        初始化消息缓冲区

        Args:
            max_size: 最大缓冲消息数量
        """
        self.max_size = max_size
        self.messages: List[OfflineMessage] = []
        self.sent_message_ids: set[str] = set()  # 已发送消息的ID

    def add_message(
        self,
        event: str,
        data: Dict[str, Any],
        room: Optional[str] = None,
    ) -> None:
        """添加离线消息"""
        if len(self.messages) >= self.max_size:
            # 移除最早的消息
            removed = self.messages.pop(0)
            logger.warning(
                "⚠️ Message buffer full, removing oldest message",
                removed_id=removed.id,
                buffer_size=len(self.messages),
            )

        message = OfflineMessage(event, data, room)
        self.messages.append(message)

        logger.debug(
            "💾 Offline message buffered",
            event_name=event,
            room=room,
            buffer_size=len(self.messages),
        )

    def get_unsent_messages(self) -> List[OfflineMessage]:
        """获取未发送的消息"""
        return [msg for msg in self.messages if msg.id not in self.sent_message_ids]

    def mark_sent(self, message_id: str) -> None:
        """标记消息已发送"""
        self.sent_message_ids.add(message_id)

    def mark_all_sent(self) -> None:
        """标记所有消息已发送"""
        for msg in self.messages:
            self.sent_message_ids.add(msg.id)

    def clear(self) -> None:
        """清空缓冲区"""
        count = len(self.messages)
        self.messages.clear()
        self.sent_message_ids.clear()
        logger.info("🗑️ Message buffer cleared", cleared_count=count)

    def get_stats(self) -> Dict[str, Any]:
        """获取缓冲区统计"""
        total = len(self.messages)
        unsent = len(self.get_unsent_messages())

        return {
            "total_messages": total,
            "unsent_messages": unsent,
            "sent_messages": total - unsent,
            "max_size": self.max_size,
            "buffer_usage_percent": (
                (total / self.max_size * 100) if self.max_size > 0 else 0
            ),
        }


class ReconnectionManager:
    """客户端重连管理器"""

    def __init__(
        self,
        base_interval: float = 3.0,
        max_interval: float = 30.0,
        max_retries: int = 5,
    ):
        """
        初始化重连管理器

        Args:
            base_interval: 基础重连间隔（秒）
            max_interval: 最大重连间隔（秒）
            max_retries: 最大重试次数
        """
        self.base_interval = base_interval
        self.max_interval = max_interval
        self.max_retries = max_retries

        # 连接级重连状态
        self.reconnection_states: Dict[str, ReconnectionState] = {}
        self.reconnection_attempts: Dict[str, int] = {}
        self.last_reconnect_time: Dict[str, datetime] = {}
        self.message_buffers: Dict[str, MessageBuffer] = {}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}

    def register_connection(self, sid: str, user_id: Optional[str] = None) -> None:
        """注册新连接"""
        self.reconnection_states[sid] = ReconnectionState.CONNECTED
        self.reconnection_attempts[sid] = 0
        self.last_reconnect_time[sid] = datetime.utcnow()
        self.message_buffers[sid] = MessageBuffer()
        self.connection_metadata[sid] = {
            "user_id": user_id,
            "registered_at": datetime.utcnow().isoformat(),
        }

        logger.info(
            "📝 Connection registered for reconnection",
            sid=sid,
            user_id=user_id,
        )

    def unregister_connection(self, sid: str) -> None:
        """注销连接"""
        self.reconnection_states.pop(sid, None)
        self.reconnection_attempts.pop(sid, None)
        self.last_reconnect_time.pop(sid, None)
        self.message_buffers.pop(sid, None)
        self.connection_metadata.pop(sid, None)

        logger.info("🗑️ Connection unregistered from reconnection", sid=sid)

    def mark_disconnected(self, sid: str) -> None:
        """标记连接为已断开"""
        if sid not in self.reconnection_states:
            return

        self.reconnection_states[sid] = ReconnectionState.DISCONNECTED
        self.reconnection_attempts[sid] = 0

        logger.info("🔌 Connection marked as disconnected", sid=sid)

    def buffer_message(
        self,
        sid: str,
        event: str,
        data: Dict[str, Any],
        room: Optional[str] = None,
    ) -> None:
        """缓冲消息（用于离线状态）"""
        if sid not in self.message_buffers:
            self.message_buffers[sid] = MessageBuffer()

        self.message_buffers[sid].add_message(event, data, room)

    def should_attempt_reconnect(self, sid: str) -> bool:
        """检查是否应该尝试重连"""
        if sid not in self.reconnection_states:
            return False

        state = self.reconnection_states[sid]
        if state != ReconnectionState.DISCONNECTED:
            return False

        attempts = self.reconnection_attempts.get(sid, 0)
        if attempts >= self.max_retries:
            self.reconnection_states[sid] = ReconnectionState.RECONNECT_FAILED
            logger.error(
                "❌ Max reconnection retries reached",
                sid=sid,
                max_retries=self.max_retries,
            )
            return False

        return True

    def get_next_reconnect_interval(self, sid: str) -> float:
        """计算下次重连间隔（指数退避）"""
        attempts = self.reconnection_attempts.get(sid, 0)
        # 指数退避：base_interval * (2 ^ attempts)，上限为 max_interval
        interval = min(
            self.base_interval * (2**attempts),
            self.max_interval,
        )
        return interval

    def record_reconnect_attempt(self, sid: str) -> None:
        """记录重连尝试"""
        if sid not in self.reconnection_attempts:
            self.reconnection_attempts[sid] = 0

        self.reconnection_attempts[sid] += 1
        self.last_reconnect_time[sid] = datetime.utcnow()
        # 保持状态为DISCONNECTED，直到成功重连或达到最大重试次数

        interval = self.get_next_reconnect_interval(sid)
        logger.info(
            "🔄 Reconnection attempt recorded",
            sid=sid,
            attempt=self.reconnection_attempts[sid],
            next_interval_seconds=interval,
        )

    def mark_reconnected(self, sid: str) -> None:
        """标记已重连成功"""
        if sid not in self.reconnection_states:
            return

        self.reconnection_states[sid] = ReconnectionState.CONNECTED
        self.reconnection_attempts[sid] = 0

        logger.info("✅ Connection successfully reconnected", sid=sid)

    def get_buffered_messages(self, sid: str) -> List[OfflineMessage]:
        """获取缓冲的消息"""
        if sid not in self.message_buffers:
            return []

        return self.message_buffers[sid].get_unsent_messages()

    def mark_message_sent(self, sid: str, message_id: str) -> None:
        """标记消息已发送"""
        if sid in self.message_buffers:
            self.message_buffers[sid].mark_sent(message_id)

    def mark_all_messages_sent(self, sid: str) -> None:
        """标记所有消息已发送"""
        if sid in self.message_buffers:
            self.message_buffers[sid].mark_all_sent()

    def clear_buffer(self, sid: str) -> None:
        """清空缓冲区"""
        if sid in self.message_buffers:
            self.message_buffers[sid].clear()

    def get_reconnection_state(self, sid: str) -> Optional[ReconnectionState]:
        """获取重连状态"""
        return self.reconnection_states.get(sid)

    def get_stats(self, sid: str) -> Dict[str, Any]:
        """获取单个连接的统计信息"""
        if sid not in self.reconnection_states:
            return {}

        buffer_stats = (
            self.message_buffers[sid].get_stats() if sid in self.message_buffers else {}
        )

        return {
            "sid": sid,
            "state": self.reconnection_states[sid],
            "attempts": self.reconnection_attempts.get(sid, 0),
            "max_retries": self.max_retries,
            "next_interval_seconds": self.get_next_reconnect_interval(sid),
            "last_reconnect": (
                self.last_reconnect_time[sid].isoformat()
                if sid in self.last_reconnect_time
                else None
            ),
            "message_buffer": buffer_stats,
        }

    def get_all_stats(self) -> Dict[str, Any]:
        """获取所有连接的统计信息"""
        total_connections = len(self.reconnection_states)
        connected = sum(
            1
            for state in self.reconnection_states.values()
            if state == ReconnectionState.CONNECTED
        )
        disconnected = sum(
            1
            for state in self.reconnection_states.values()
            if state == ReconnectionState.DISCONNECTED
        )
        reconnecting = sum(
            1
            for state in self.reconnection_states.values()
            if state == ReconnectionState.RECONNECTING
        )
        failed = sum(
            1
            for state in self.reconnection_states.values()
            if state == ReconnectionState.RECONNECT_FAILED
        )

        total_buffered = sum(len(buf.messages) for buf in self.message_buffers.values())

        return {
            "total_connections": total_connections,
            "connected": connected,
            "disconnected": disconnected,
            "reconnecting": reconnecting,
            "failed": failed,
            "total_buffered_messages": total_buffered,
            "timestamp": datetime.utcnow().isoformat(),
        }


# 全局单例
_reconnection_manager: Optional[ReconnectionManager] = None


def get_reconnection_manager() -> ReconnectionManager:
    """获取重连管理器单例"""
    global _reconnection_manager
    if _reconnection_manager is None:
        _reconnection_manager = ReconnectionManager()
    return _reconnection_manager


def reset_reconnection_manager() -> None:
    """重置重连管理器（仅用于测试）"""
    global _reconnection_manager
    _reconnection_manager = None
