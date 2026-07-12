"""房间管理器 - Room Management System

Implements room-based pub/sub messaging with join/leave notifications

Task 4.3: 实现房间订阅

Features:
- Single room subscription per connection (one connection = one room)
- Room creation and destruction
- Member tracking and notifications
- Message broadcasting to room members
- Join/leave event handling
- Room metadata and statistics

Author: Claude Code
Date: 2025-11-06
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import structlog


logger = structlog.get_logger()


class RoomEventType(str, Enum):
    """房间事件类型"""

    MEMBER_JOINED = "member_joined"  # 成员加入
    MEMBER_LEFT = "member_left"  # 成员离开
    ROOM_CREATED = "room_created"  # 房间创建
    ROOM_DESTROYED = "room_destroyed"  # 房间销毁


class RoomMember:
    """房间成员信息"""

    def __init__(self, sid: str, user_id: Optional[str] = None):
        """初始化房间成员

        Args:
            sid: Socket.IO连接ID
            user_id: 用户ID

        """
        self.sid = sid
        self.user_id = user_id
        self.joined_at = datetime.now(timezone.utc)
        self.message_count = 0
        self.last_activity = datetime.now(timezone.utc)

    def record_message(self) -> None:
        """记录成员消息"""
        self.message_count += 1
        self.last_activity = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "sid": self.sid,
            "user_id": self.user_id,
            "joined_at": self.joined_at.isoformat(),
            "message_count": self.message_count,
            "last_activity": self.last_activity.isoformat(),
        }


class Room:
    """房间类"""

    def __init__(self, name: str):
        """初始化房间

        Args:
            name: 房间名称

        """
        self.name = name
        self.room_id = str(uuid.uuid4())
        self.created_at = datetime.now(timezone.utc)
        self.members: Dict[str, RoomMember] = {}
        self.metadata: Dict[str, Any] = {}

    def add_member(self, sid: str, user_id: Optional[str] = None) -> RoomMember:
        """添加成员"""
        member = RoomMember(sid, user_id)
        self.members[sid] = member

        logger.info(
            "✅ Member joined room",
            room=self.name,
            sid=sid,
            user_id=user_id,
            total_members=len(self.members),
        )

        return member

    def remove_member(self, sid: str) -> Optional[RoomMember]:
        """移除成员"""
        member = self.members.pop(sid, None)

        if member:
            logger.info(
                "✅ Member left room",
                room=self.name,
                sid=sid,
                user_id=member.user_id,
                total_members=len(self.members),
            )

        return member

    def get_member(self, sid: str) -> Optional[RoomMember]:
        """获取成员"""
        return self.members.get(sid)

    def has_member(self, sid: str) -> bool:
        """检查成员是否存在"""
        return sid in self.members

    def get_all_members(self) -> List[RoomMember]:
        """获取所有成员"""
        return list(self.members.values())

    def get_member_sids(self) -> List[str]:
        """获取所有成员SID"""
        return list(self.members.keys())

    def is_empty(self) -> bool:
        """检查房间是否为空"""
        return len(self.members) == 0

    def get_stats(self) -> Dict[str, Any]:
        """获取房间统计信息"""
        total_messages = sum(m.message_count for m in self.members.values())

        return {
            "room_id": self.room_id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "member_count": len(self.members),
            "total_messages": total_messages,
            "members": [m.to_dict() for m in self.members.values()],
        }


class RoomManager:
    """房间管理器"""

    def __init__(self):
        """初始化房间管理器"""
        self.rooms: Dict[str, Room] = {}
        self.member_to_room: Dict[str, str] = {}  # sid -> room_name
        self.event_callbacks: Dict[RoomEventType, List[Callable]] = {event_type: [] for event_type in RoomEventType}

    def create_room(self, name: str) -> Room:
        """创建房间"""
        if name in self.rooms:
            logger.warning("⚠️ Room already exists", room=name)
            return self.rooms[name]

        room = Room(name)
        self.rooms[name] = room

        logger.info("📝 Room created", room=name, room_id=room.room_id)
        self._trigger_event(
            RoomEventType.ROOM_CREATED,
            {"room": name, "room_id": room.room_id},
        )

        return room

    def destroy_room(self, name: str) -> bool:
        """销毁房间"""
        if name not in self.rooms:
            logger.warning("⚠️ Room not found", room=name)
            return False

        room = self.rooms.pop(name)

        # 清理成员到房间的映射
        for sid in room.get_member_sids():
            self.member_to_room.pop(sid, None)

        logger.info("🗑️ Room destroyed", room=name, members_removed=len(room.members))
        self._trigger_event(
            RoomEventType.ROOM_DESTROYED,
            {"room": name, "room_id": room.room_id},
        )

        return True

    def add_member_to_room(self, room_name: str, sid: str, user_id: Optional[str] = None) -> bool:
        """将成员添加到房间"""
        # 如果成员已在另一个房间，先移除
        if sid in self.member_to_room:
            old_room_name = self.member_to_room[sid]
            if old_room_name != room_name:
                self.remove_member_from_room(old_room_name, sid)

        # 创建房间如果不存在
        if room_name not in self.rooms:
            self.create_room(room_name)

        room = self.rooms[room_name]
        room.add_member(sid, user_id)
        self.member_to_room[sid] = room_name

        self._trigger_event(
            RoomEventType.MEMBER_JOINED,
            {
                "room": room_name,
                "sid": sid,
                "user_id": user_id,
                "member_count": len(room.members),
            },
        )

        return True

    def remove_member_from_room(self, room_name: str, sid: str) -> bool:
        """将成员从房间移除"""
        if room_name not in self.rooms:
            logger.warning("⚠️ Room not found", room=room_name)
            return False

        room = self.rooms[room_name]
        member = room.remove_member(sid)

        if not member:
            logger.warning("⚠️ Member not found in room", room=room_name, sid=sid)
            return False

        # 清理成员到房间的映射
        self.member_to_room.pop(sid, None)

        self._trigger_event(
            RoomEventType.MEMBER_LEFT,
            {
                "room": room_name,
                "sid": sid,
                "user_id": member.user_id,
                "member_count": len(room.members),
            },
        )

        # 如果房间为空，销毁房间
        if room.is_empty():
            self.destroy_room(room_name)

        return True

    def get_room(self, name: str) -> Optional[Room]:
        """获取房间"""
        return self.rooms.get(name)

    def get_member_room(self, sid: str) -> Optional[str]:
        """获取成员所在的房间"""
        return self.member_to_room.get(sid)

    def get_room_members(self, room_name: str) -> List[RoomMember]:
        """获取房间成员列表"""
        room = self.rooms.get(room_name)
        return room.get_all_members() if room else []

    def get_room_member_sids(self, room_name: str) -> List[str]:
        """获取房间所有成员SID"""
        room = self.rooms.get(room_name)
        return room.get_member_sids() if room else []

    def room_exists(self, name: str) -> bool:
        """检查房间是否存在"""
        return name in self.rooms

    def get_all_rooms(self) -> List[Room]:
        """获取所有房间"""
        return list(self.rooms.values())

    def record_member_message(self, room_name: str, sid: str) -> bool:
        """记录房间成员消息"""
        room = self.rooms.get(room_name)
        if not room:
            return False

        member = room.get_member(sid)
        if not member:
            return False

        member.record_message()
        return True

    def register_event_handler(self, event_type: RoomEventType, handler: Callable) -> None:
        """注册事件处理器"""
        if event_type not in self.event_callbacks:
            self.event_callbacks[event_type] = []

        self.event_callbacks[event_type].append(handler)
        logger.info("✅ Registered room event handler: %(event_type)s")

    def _trigger_event(self, event_type: RoomEventType, data: Dict[str, Any]) -> None:
        """触发事件"""
        handlers = self.event_callbacks.get(event_type, [])
        for handler in handlers:
            try:
                handler(data)
            except Exception as e:
                logger.error(
                    "❌ Error calling room event handler",
                    event_type=event_type,
                    error=str(e),
                )

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_members = sum(len(room.members) for room in self.rooms.values())

        return {
            "total_rooms": len(self.rooms),
            "total_members": total_members,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rooms": [room.get_stats() for room in self.rooms.values()],
        }


# 全局单例
_room_manager: Optional[RoomManager] = None


def get_room_manager() -> RoomManager:
    """获取房间管理器单例"""
    global _room_manager
    if _room_manager is None:
        _room_manager = RoomManager()
    return _room_manager


def reset_room_manager() -> None:
    """重置房间管理器（仅用于测试）"""
    global _room_manager
    _room_manager = None
