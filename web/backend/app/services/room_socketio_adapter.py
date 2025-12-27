"""
房间Socket.IO适配器 - Room Socket.IO Adapter

Task 9: 多房间订阅扩展

功能特性:
- 房间与Socket.IO连接的映射管理
- 房间权限检查和访问控制
- 消息广播集成
- 连接生命周期管理
- 房间事件处理 (加入、离开、消息)

Author: Claude Code
Date: 2025-11-07
"""

from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime
import structlog

from app.services.room_management import (
    get_room_manager,
    RoomManager,
)
from app.services.room_permission_service import (
    get_permission_manager,
    get_access_control,
    RoomPermissionManager,
    RoomAccessControl,
    RoomRole,
)
from app.services.room_broadcast_service import (
    get_broadcaster,
    RoomBroadcaster,
    RoomMessage,
    MessageType,
)

logger = structlog.get_logger()


@dataclass
class RoomConnection:
    """房间连接信息"""

    sid: str = ""
    user_id: str = ""
    username: str = ""
    room_id: str = ""
    role: RoomRole = RoomRole.MEMBER
    joined_at: datetime = field(default_factory=datetime.utcnow)
    message_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "sid": self.sid,
            "user_id": self.user_id,
            "username": self.username,
            "room_id": self.room_id,
            "role": self.role.value,
            "joined_at": self.joined_at.isoformat(),
            "message_count": self.message_count,
        }


class RoomSocketIOAdapter:
    """房间Socket.IO适配器"""

    def __init__(
        self,
        room_manager: Optional[RoomManager] = None,
        permission_manager: Optional[RoomPermissionManager] = None,
        access_control: Optional[RoomAccessControl] = None,
        broadcaster: Optional[RoomBroadcaster] = None,
    ):
        """初始化适配器

        Args:
            room_manager: 房间管理器
            permission_manager: 权限管理器
            access_control: 访问控制
            broadcaster: 广播器
        """
        self.room_manager = room_manager or get_room_manager()
        self.permission_manager = permission_manager or get_permission_manager()
        self.access_control = access_control or get_access_control()
        self.broadcaster = broadcaster or get_broadcaster()

        # Socket.IO特定的映射
        self.sid_to_connection: Dict[str, RoomConnection] = {}
        self.user_room_subscriptions: Dict[str, Set[str]] = {}  # user_id -> set of room_ids
        self.socketio_callbacks: List[Callable[[str, str, Dict[str, Any]], Any]] = []

        # 统计
        self.total_joins = 0
        self.total_messages = 0
        self.total_room_broadcasts = 0

        # 注册广播回调
        self._register_broadcast_callback()

        logger.info("✅ Room SocketIO Adapter initialized")

    def _register_broadcast_callback(self) -> None:
        """注册广播回调以通过SocketIO发送消息"""

        def socketio_delivery_callback(user_id: str, message: RoomMessage) -> bool:
            """通过SocketIO发送消息给用户"""
            # 查找用户的所有连接
            sids = self._get_user_sids(user_id)
            if not sids:
                logger.warning("⚠️ No active connections for user", user_id=user_id)
                return False

            # 发送消息给所有连接
            success_count = 0
            for sid in sids:
                try:
                    # 检查连接是否在对应的房间中
                    connection = self.sid_to_connection.get(sid)
                    if connection and connection.room_id == message.room_id:
                        # 通过回调发送消息
                        self._emit_room_message(sid, message)
                        success_count += 1
                except Exception as e:
                    logger.warning(
                        "⚠️ Failed to deliver message via SocketIO",
                        sid=sid,
                        user_id=user_id,
                        error=str(e),
                    )

            return success_count > 0

        self.broadcaster.register_delivery_callback(socketio_delivery_callback)
        logger.info("✅ Broadcast callback registered")

    def _get_user_sids(self, user_id: str) -> List[str]:
        """获取用户的所有连接SID"""
        sids = []
        for sid, connection in self.sid_to_connection.items():
            if connection.user_id == user_id:
                sids.append(sid)
        return sids

    def _emit_room_message(self, sid: str, message: RoomMessage) -> None:
        """通过回调发送房间消息"""
        for callback in self.socketio_callbacks:
            try:
                callback(sid, "room_message", message.to_dict())
            except Exception as e:
                logger.warning(
                    "⚠️ Callback emission failed",
                    sid=sid,
                    error=str(e),
                )

    async def handle_join_room(
        self,
        sid: str,
        user_id: str,
        username: str,
        room_id: str,
        role: RoomRole = RoomRole.MEMBER,
    ) -> Dict[str, Any]:
        """处理用户加入房间

        Args:
            sid: Socket.IO会话ID
            user_id: 用户ID
            username: 用户名
            room_id: 房间ID
            role: 用户角色

        Returns:
            操作结果
        """
        try:
            # 检查房间是否存在
            room = self.room_manager.get_room(room_id)
            if not room:
                return {"success": False, "error": "Room not found"}

            # 检查权限
            can_join = self.access_control.can_join_room(user_id, room_id, role)
            if not can_join:
                return {"success": False, "error": "Permission denied"}

            # 加入房间
            join_result = self.room_manager.join_room(room_id, user_id, username)
            if not join_result:
                return {"success": False, "error": "Failed to join room"}

            # 记录连接信息
            connection = RoomConnection(
                sid=sid,
                user_id=user_id,
                username=username,
                room_id=room_id,
                role=role,
            )
            self.sid_to_connection[sid] = connection

            # 记录用户房间订阅
            if user_id not in self.user_room_subscriptions:
                self.user_room_subscriptions[user_id] = set()
            self.user_room_subscriptions[user_id].add(room_id)

            self.total_joins += 1

            logger.info(
                "✅ User joined room",
                user_id=user_id,
                room_id=room_id,
                sid=sid,
                role=role.value,
            )

            # 广播加入事件
            await self._broadcast_room_event(
                room_id,
                "user_joined",
                {
                    "user_id": user_id,
                    "username": username,
                    "role": role.value,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

            return {
                "success": True,
                "room": room.to_dict(),
                "connection": connection.to_dict(),
            }

        except Exception as e:
            logger.error(
                "❌ Failed to handle join room",
                sid=sid,
                room_id=room_id,
                error=str(e),
            )
            return {"success": False, "error": "Internal server error"}

    async def handle_leave_room(self, sid: str, user_id: str, room_id: str) -> Dict[str, Any]:
        """处理用户离开房间

        Args:
            sid: Socket.IO会话ID
            user_id: 用户ID
            room_id: 房间ID

        Returns:
            操作结果
        """
        try:
            # 离开房间
            leave_result = self.room_manager.leave_room(room_id, user_id)
            if not leave_result:
                return {"success": False, "error": "Failed to leave room"}

            # 移除连接信息
            if sid in self.sid_to_connection:
                del self.sid_to_connection[sid]

            # 移除用户房间订阅
            if user_id in self.user_room_subscriptions:
                self.user_room_subscriptions[user_id].discard(room_id)
                if not self.user_room_subscriptions[user_id]:
                    del self.user_room_subscriptions[user_id]

            logger.info(
                "✅ User left room",
                user_id=user_id,
                room_id=room_id,
                sid=sid,
            )

            # 广播离开事件
            room = self.room_manager.get_room(room_id)
            if room:
                await self._broadcast_room_event(
                    room_id,
                    "user_left",
                    {
                        "user_id": user_id,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )

            return {"success": True}

        except Exception as e:
            logger.error(
                "❌ Failed to handle leave room",
                sid=sid,
                room_id=room_id,
                error=str(e),
            )
            return {"success": False, "error": "Internal server error"}

    async def handle_room_message(self, sid: str, user_id: str, room_id: str, content: str) -> Dict[str, Any]:
        """处理房间消息

        Args:
            sid: Socket.IO会话ID
            user_id: 用户ID
            room_id: 房间ID
            content: 消息内容

        Returns:
            操作结果
        """
        try:
            # 获取连接信息
            connection = self.sid_to_connection.get(sid)
            if not connection or connection.room_id != room_id:
                return {"success": False, "error": "Not in this room"}

            # 检查权限
            can_send = self.access_control.can_send_message(user_id, room_id, connection.role)
            if not can_send:
                return {"success": False, "error": "Permission denied"}

            # 创建消息
            message = self.broadcaster.send_message(
                room_id=room_id,
                sender_id=user_id,
                sender_name=connection.username,
                content=content,
                message_type=MessageType.TEXT,
            )

            # 增加消息计数
            connection.message_count += 1
            self.total_messages += 1
            self.room_manager.increment_message_count(room_id)

            # 广播消息
            room_members = self.room_manager.get_room_members(room_id)
            member_ids = [m.user_id for m in room_members]
            self.broadcaster.broadcast_to_users(message, member_ids)

            self.total_room_broadcasts += 1

            logger.info(
                "✅ Room message processed",
                message_id=message.id,
                room_id=room_id,
                user_id=user_id,
            )

            return {"success": True, "message": message.to_dict()}

        except Exception as e:
            logger.error(
                "❌ Failed to handle room message",
                sid=sid,
                room_id=room_id,
                error=str(e),
            )
            return {"success": False, "error": "Internal server error"}

    async def handle_disconnect(self, sid: str) -> None:
        """处理连接断开

        Args:
            sid: Socket.IO会话ID
        """
        try:
            connection = self.sid_to_connection.pop(sid, None)
            if connection:
                # 自动离开房间
                await self.handle_leave_room(sid, connection.user_id, connection.room_id)

                logger.info(
                    "✅ Cleaned up room connection on disconnect",
                    sid=sid,
                    user_id=connection.user_id,
                    room_id=connection.room_id,
                )

        except Exception as e:
            logger.warning(
                "⚠️ Error handling disconnect",
                sid=sid,
                error=str(e),
            )

    async def _broadcast_room_event(self, room_id: str, event: str, data: Dict[str, Any]) -> None:
        """广播房间事件给所有成员

        Args:
            room_id: 房间ID
            event: 事件名称
            data: 事件数据
        """
        # 获取房间所有成员
        room_members = self.room_manager.get_room_members(room_id)
        if not room_members:
            return

        # 通过回调发送事件给所有在该房间的连接
        for sid, connection in self.sid_to_connection.items():
            if connection.room_id == room_id:
                try:
                    self._emit_room_message(sid, RoomMessage(room_id=room_id))
                    # 实际上应该使用专门的事件发送，这里通过回调发送
                    for callback in self.socketio_callbacks:
                        try:
                            callback(sid, f"room_{event}", data)
                        except Exception as e:
                            logger.warning(
                                "⚠️ Failed to broadcast event",
                                sid=sid,
                                event=event,
                                error=str(e),
                            )
                except Exception as e:
                    logger.warning(
                        "⚠️ Failed to emit room event",
                        sid=sid,
                        event=event,
                        error=str(e),
                    )

    def register_socketio_callback(self, callback: Callable[[str, str, Dict[str, Any]], Any]) -> None:
        """注册Socket.IO回调用于发送消息

        Args:
            callback: 回调函数 (sid, event, data) -> None
        """
        self.socketio_callbacks.append(callback)
        logger.info("✅ SocketIO callback registered")

    def get_room_users(self, room_id: str) -> List[Dict[str, Any]]:
        """获取房间内的用户列表

        Args:
            room_id: 房间ID

        Returns:
            用户信息列表
        """
        users = []
        for connection in self.sid_to_connection.values():
            if connection.room_id == room_id:
                users.append(connection.to_dict())
        return users

    def get_user_rooms(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户加入的房间列表

        Args:
            user_id: 用户ID

        Returns:
            房间信息列表
        """
        rooms = []
        room_ids = self.user_room_subscriptions.get(user_id, set())
        for room_id in room_ids:
            room = self.room_manager.get_room(room_id)
            if room:
                rooms.append(room.to_dict())
        return rooms

    def get_connection_info(self, sid: str) -> Optional[Dict[str, Any]]:
        """获取连接信息

        Args:
            sid: Socket.IO会话ID

        Returns:
            连接信息
        """
        connection = self.sid_to_connection.get(sid)
        return connection.to_dict() if connection else None

    def get_stats(self) -> Dict[str, Any]:
        """获取适配器统计"""
        return {
            "active_connections": len(self.sid_to_connection),
            "active_users": len(self.user_room_subscriptions),
            "active_rooms": len(set(c.room_id for c in self.sid_to_connection.values())),
            "total_joins": self.total_joins,
            "total_messages": self.total_messages,
            "total_room_broadcasts": self.total_room_broadcasts,
            "room_manager_stats": self.room_manager.get_stats(),
            "broadcaster_stats": self.broadcaster.get_stats(),
            "permission_manager_stats": self.permission_manager.get_stats(),
        }


# 全局单例
_adapter: Optional[RoomSocketIOAdapter] = None


def get_room_socketio_adapter() -> RoomSocketIOAdapter:
    """获取房间Socket.IO适配器单例

    Returns:
        适配器实例
    """
    global _adapter
    if _adapter is None:
        _adapter = RoomSocketIOAdapter()
    return _adapter


def reset_room_socketio_adapter() -> None:
    """重置适配器单例（仅用于测试）"""
    global _adapter
    _adapter = None
