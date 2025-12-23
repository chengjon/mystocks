"""
房间消息广播服务 - Room Message Broadcasting Service

Task 9: 多房间订阅扩展

功能特性:
- 实时房间消息广播
- 离线消息队列存储
- 角色和用户指定广播
- 消息传递追踪
- WebSocket集成支持

Author: Claude Code
Date: 2025-11-07
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import structlog
from collections import defaultdict
import uuid

logger = structlog.get_logger()


class MessageType(str, Enum):
    """消息类型"""

    TEXT = "text"  # 文本消息
    NOTIFICATION = "notification"  # 通知
    ALERT = "alert"  # 告警
    SYSTEM = "system"  # 系统消息
    DATA = "data"  # 数据消息


class BroadcastTarget(str, Enum):
    """广播目标类型"""

    ALL = "all"  # 广播给所有成员
    ROLE = "role"  # 广播给特定角色
    USER = "user"  # 广播给特定用户
    USERS = "users"  # 广播给用户列表


@dataclass
class RoomMessage:
    """房间消息"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    room_id: str = ""
    sender_id: str = ""
    sender_name: str = ""
    message_type: MessageType = MessageType.TEXT
    content: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "room_id": self.room_id,
            "sender_id": self.sender_id,
            "sender_name": self.sender_name,
            "message_type": self.message_type.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class BroadcastTask:
    """广播任务"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    room_id: str = ""
    message: RoomMessage = field(default_factory=RoomMessage)
    target_type: BroadcastTarget = BroadcastTarget.ALL
    target_value: Any = None  # 角色或用户ID/列表
    created_at: datetime = field(default_factory=datetime.utcnow)
    delivered_count: int = 0
    failed_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "room_id": self.room_id,
            "message": self.message.to_dict(),
            "target_type": self.target_type.value,
            "target_value": self.target_value,
            "created_at": self.created_at.isoformat(),
            "delivered_count": self.delivered_count,
            "failed_count": self.failed_count,
        }


class OfflineMessageQueue:
    """离线消息队列"""

    def __init__(self, max_queue_size: int = 1000):
        """初始化离线消息队列

        Args:
            max_queue_size: 最大队列大小
        """
        self.max_queue_size = max_queue_size
        self.queues: Dict[str, List[RoomMessage]] = defaultdict(list)
        logger.info("✅ Offline Message Queue initialized")

    def enqueue(self, user_id: str, message: RoomMessage) -> bool:
        """添加消息到离线队列

        Args:
            user_id: 用户ID
            message: 消息

        Returns:
            是否成功添加
        """
        if len(self.queues[user_id]) >= self.max_queue_size:
            # 移除最早的消息
            self.queues[user_id].pop(0)

        self.queues[user_id].append(message)
        return True

    def dequeue(self, user_id: str, count: int = 100) -> List[RoomMessage]:
        """从离线队列获取消息

        Args:
            user_id: 用户ID
            count: 获取数量

        Returns:
            消息列表
        """
        if user_id not in self.queues:
            return []

        messages = self.queues[user_id][:count]
        self.queues[user_id] = self.queues[user_id][count:]

        return messages

    def get_queue_size(self, user_id: str) -> int:
        """获取队列大小

        Args:
            user_id: 用户ID

        Returns:
            队列大小
        """
        return len(self.queues.get(user_id, []))

    def clear_queue(self, user_id: str) -> bool:
        """清空队列

        Args:
            user_id: 用户ID

        Returns:
            是否成功清空
        """
        if user_id in self.queues:
            del self.queues[user_id]
            return True
        return False

    def get_stats(self) -> Dict[str, Any]:
        """获取队列统计"""
        total_messages = sum(len(msgs) for msgs in self.queues.values())
        return {
            "users_with_offline_messages": len(self.queues),
            "total_offline_messages": total_messages,
            "max_queue_size": self.max_queue_size,
        }


class RoomBroadcaster:
    """房间广播器"""

    def __init__(self):
        """初始化广播器"""
        self.offline_queue = OfflineMessageQueue()
        self.delivery_callbacks: List[Callable[[str, RoomMessage], bool]] = []
        self.broadcast_history: List[BroadcastTask] = []
        self.max_history = 10000

        # 统计
        self.total_messages_sent = 0
        self.total_messages_delivered = 0
        self.total_delivery_failures = 0

        logger.info("✅ Room Broadcaster initialized")

    def register_delivery_callback(
        self, callback: Callable[[str, RoomMessage], bool]
    ) -> None:
        """注册消息传递回调

        Args:
            callback: 回调函数 (user_id, message) -> bool
        """
        self.delivery_callbacks.append(callback)
        logger.info("✅ Delivery callback registered")

    def send_message(
        self,
        room_id: str,
        sender_id: str,
        sender_name: str,
        content: str,
        message_type: MessageType = MessageType.TEXT,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RoomMessage:
        """发送消息到房间

        Args:
            room_id: 房间ID
            sender_id: 发送者ID
            sender_name: 发送者名称
            content: 消息内容
            message_type: 消息类型
            metadata: 元数据

        Returns:
            创建的消息对象
        """
        message = RoomMessage(
            room_id=room_id,
            sender_id=sender_id,
            sender_name=sender_name,
            message_type=message_type,
            content=content,
            metadata=metadata or {},
        )

        self.total_messages_sent += 1
        logger.info(
            "✅ Message created",
            message_id=message.id,
            room_id=room_id,
            sender_id=sender_id,
        )

        return message

    def broadcast_to_all(self, message: RoomMessage, room_members: List[str]) -> bool:
        """广播消息给所有房间成员

        Args:
            message: 消息
            room_members: 房间成员ID列表

        Returns:
            是否广播成功
        """
        task = BroadcastTask(
            room_id=message.room_id,
            message=message,
            target_type=BroadcastTarget.ALL,
        )

        delivered = 0
        failed = 0

        for member_id in room_members:
            success = self._deliver_message(member_id, message)
            if success:
                delivered += 1
                self.total_messages_delivered += 1
            else:
                failed += 1
                self.total_delivery_failures += 1

        task.delivered_count = delivered
        task.failed_count = failed
        self._record_broadcast(task)

        return failed == 0

    def broadcast_to_role(
        self,
        message: RoomMessage,
        room_members: Dict[str, str],
        target_role: str,
    ) -> bool:
        """广播消息给特定角色的成员

        Args:
            message: 消息
            room_members: 房间成员ID -> 角色 映射
            target_role: 目标角色

        Returns:
            是否广播成功
        """
        task = BroadcastTask(
            room_id=message.room_id,
            message=message,
            target_type=BroadcastTarget.ROLE,
            target_value=target_role,
        )

        delivered = 0
        failed = 0

        for member_id, role in room_members.items():
            if role == target_role:
                success = self._deliver_message(member_id, message)
                if success:
                    delivered += 1
                    self.total_messages_delivered += 1
                else:
                    failed += 1
                    self.total_delivery_failures += 1

        task.delivered_count = delivered
        task.failed_count = failed
        self._record_broadcast(task)

        return failed == 0

    def broadcast_to_user(self, message: RoomMessage, target_user_id: str) -> bool:
        """广播消息给特定用户

        Args:
            message: 消息
            target_user_id: 目标用户ID

        Returns:
            是否广播成功
        """
        task = BroadcastTask(
            room_id=message.room_id,
            message=message,
            target_type=BroadcastTarget.USER,
            target_value=target_user_id,
        )

        success = self._deliver_message(target_user_id, message)
        if success:
            task.delivered_count = 1
            self.total_messages_delivered += 1
        else:
            task.failed_count = 1
            self.total_delivery_failures += 1

        self._record_broadcast(task)
        return success

    def broadcast_to_users(
        self, message: RoomMessage, target_user_ids: List[str]
    ) -> bool:
        """广播消息给用户列表

        Args:
            message: 消息
            target_user_ids: 目标用户ID列表

        Returns:
            是否广播成功
        """
        task = BroadcastTask(
            room_id=message.room_id,
            message=message,
            target_type=BroadcastTarget.USERS,
            target_value=target_user_ids,
        )

        delivered = 0
        failed = 0

        for user_id in target_user_ids:
            success = self._deliver_message(user_id, message)
            if success:
                delivered += 1
                self.total_messages_delivered += 1
            else:
                failed += 1
                self.total_delivery_failures += 1

        task.delivered_count = delivered
        task.failed_count = failed
        self._record_broadcast(task)

        return failed == 0

    def _deliver_message(self, user_id: str, message: RoomMessage) -> bool:
        """尝试传递消息给用户

        Args:
            user_id: 用户ID
            message: 消息

        Returns:
            是否成功传递
        """
        # 尝试所有注册的回调
        for callback in self.delivery_callbacks:
            try:
                if callback(user_id, message):
                    return True
            except Exception as e:
                logger.warning(
                    "⚠️ Delivery callback failed",
                    user_id=user_id,
                    message_id=message.id,
                    error=str(e),
                )

        # 如果所有在线传递都失败，加入离线队列
        self.offline_queue.enqueue(user_id, message)
        return False

    def _record_broadcast(self, task: BroadcastTask) -> None:
        """记录广播任务

        Args:
            task: 广播任务
        """
        self.broadcast_history.append(task)

        # 限制历史大小
        if len(self.broadcast_history) > self.max_history:
            self.broadcast_history = self.broadcast_history[-self.max_history :]

    def get_offline_messages(self, user_id: str, count: int = 100) -> List[RoomMessage]:
        """获取用户的离线消息

        Args:
            user_id: 用户ID
            count: 获取数量

        Returns:
            消息列表
        """
        return self.offline_queue.dequeue(user_id, count)

    def get_broadcast_history(
        self, room_id: str, limit: int = 100
    ) -> List[BroadcastTask]:
        """获取房间的广播历史

        Args:
            room_id: 房间ID
            limit: 限制数量

        Returns:
            广播任务列表
        """
        filtered = [task for task in self.broadcast_history if task.room_id == room_id]
        return filtered[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        """获取广播器统计"""
        return {
            "total_messages_sent": self.total_messages_sent,
            "total_messages_delivered": self.total_messages_delivered,
            "total_delivery_failures": self.total_delivery_failures,
            "broadcast_history_size": len(self.broadcast_history),
            "offline_queue_stats": self.offline_queue.get_stats(),
            "delivery_callbacks_registered": len(self.delivery_callbacks),
        }


# 全局单例
_broadcaster: Optional[RoomBroadcaster] = None


def get_broadcaster() -> RoomBroadcaster:
    """获取房间广播器单例

    Returns:
        广播器实例
    """
    global _broadcaster
    if _broadcaster is None:
        _broadcaster = RoomBroadcaster()
    return _broadcaster


def reset_broadcaster() -> None:
    """重置广播器单例（仅用于测试）"""
    global _broadcaster
    _broadcaster = None
