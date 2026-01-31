"""
房间管理服务 - Room Management Service

Task 9: 多房间订阅扩展

功能特性:
- 房间创建和管理
- 用户加入/离开房间
- 房间状态追踪
- 房间成员管理
- 房间级别的消息广播

Author: Claude Code
Date: 2025-11-07
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

import structlog

logger = structlog.get_logger()


class RoomType(str, Enum):
    """房间类型"""

    PUBLIC = "public"  # 公开房间
    PRIVATE = "private"  # 私有房间
    PROTECTED = "protected"  # 受保护房间（需密码）


class RoomStatus(str, Enum):
    """房间状态"""

    ACTIVE = "active"  # 活跃
    INACTIVE = "inactive"  # 不活跃
    ARCHIVED = "archived"  # 已归档
    CLOSED = "closed"  # 已关闭


@dataclass
class RoomMember:
    """房间成员"""

    user_id: str
    username: str
    joined_at: datetime = field(default_factory=datetime.utcnow)
    is_admin: bool = False
    is_moderator: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "joined_at": self.joined_at.isoformat(),
            "is_admin": self.is_admin,
            "is_moderator": self.is_moderator,
            "metadata": self.metadata,
        }


@dataclass
class Room:
    """房间"""

    id: str
    name: str
    type: RoomType
    owner_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: RoomStatus = RoomStatus.ACTIVE
    max_members: Optional[int] = None
    password: Optional[str] = None
    description: str = ""
    members: Dict[str, RoomMember] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # 统计信息
    message_count: int = 0
    last_activity: datetime = field(default_factory=datetime.utcnow)

    def add_member(self, user_id: str, username: str, is_admin: bool = False) -> bool:
        """添加成员"""
        if self.max_members and len(self.members) >= self.max_members:
            return False

        if user_id in self.members:
            return False

        self.members[user_id] = RoomMember(user_id=user_id, username=username, is_admin=is_admin)
        self.last_activity = datetime.utcnow()
        return True

    def remove_member(self, user_id: str) -> bool:
        """移除成员"""
        if user_id not in self.members:
            return False

        del self.members[user_id]
        self.last_activity = datetime.utcnow()
        return True

    def get_member(self, user_id: str) -> Optional[RoomMember]:
        """获取成员"""
        return self.members.get(user_id)

    def is_member(self, user_id: str) -> bool:
        """检查是否是成员"""
        return user_id in self.members

    def is_full(self) -> bool:
        """检查房间是否满员"""
        if self.max_members is None:
            return False
        return len(self.members) >= self.max_members

    def get_member_count(self) -> int:
        """获取成员数"""
        return len(self.members)

    def get_members(self) -> List[RoomMember]:
        """获取所有成员"""
        return list(self.members.values())

    def get_member_ids(self) -> Set[str]:
        """获取所有成员ID"""
        return set(self.members.keys())

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat(),
            "status": self.status.value,
            "max_members": self.max_members,
            "description": self.description,
            "member_count": self.get_member_count(),
            "message_count": self.message_count,
            "last_activity": self.last_activity.isoformat(),
        }


class RoomManager:
    """房间管理器"""

    def __init__(self):
        """初始化房间管理器"""
        self.rooms: Dict[str, Room] = {}
        self.user_rooms: Dict[str, Set[str]] = {}  # user_id -> room_ids

        # 指标
        self.rooms_created = 0
        self.rooms_deleted = 0
        self.total_join_events = 0
        self.total_leave_events = 0
        self.last_error = None

        logger.info("✅ Room Manager initialized")

    def create_room(
        self,
        room_id: str,
        name: str,
        owner_id: str,
        room_type: RoomType = RoomType.PUBLIC,
        max_members: Optional[int] = None,
        description: str = "",
    ) -> Room:
        """创建房间"""
        room = Room(
            id=room_id,
            name=name,
            type=room_type,
            owner_id=owner_id,
            max_members=max_members,
            description=description,
        )

        # 添加房间主人作为管理员
        room.add_member(owner_id, "owner", is_admin=True)

        self.rooms[room_id] = room
        self._add_user_room(owner_id, room_id)
        self.rooms_created += 1

        logger.info(
            "✅ Room created",
            room_id=room_id,
            name=name,
            owner_id=owner_id,
            type=room_type.value,
        )

        return room

    def delete_room(self, room_id: str) -> bool:
        """删除房间"""
        if room_id not in self.rooms:
            return False

        room = self.rooms[room_id]

        # 移除所有成员的房间关联
        for user_id in room.get_member_ids():
            self._remove_user_room(user_id, room_id)

        del self.rooms[room_id]
        self.rooms_deleted += 1

        logger.info("✅ Room deleted", room_id=room_id)
        return True

    def join_room(self, room_id: str, user_id: str, username: str) -> bool:
        """加入房间"""
        if room_id not in self.rooms:
            logger.warning("⚠️ Room not found", room_id=room_id)
            return False

        room = self.rooms[room_id]

        if room.status != RoomStatus.ACTIVE:
            logger.warning("⚠️ Room is not active", room_id=room_id)
            return False

        if room.is_full():
            logger.warning("⚠️ Room is full", room_id=room_id)
            return False

        if room.add_member(user_id, username):
            self._add_user_room(user_id, room_id)
            self.total_join_events += 1

            logger.info(
                "✅ User joined room",
                room_id=room_id,
                user_id=user_id,
                member_count=room.get_member_count(),
            )
            return True

        return False

    def leave_room(self, room_id: str, user_id: str) -> bool:
        """离开房间"""
        if room_id not in self.rooms:
            return False

        room = self.rooms[room_id]

        if room.remove_member(user_id):
            self._remove_user_room(user_id, room_id)
            self.total_leave_events += 1

            logger.info(
                "✅ User left room",
                room_id=room_id,
                user_id=user_id,
                member_count=room.get_member_count(),
            )

            # 如果房间为空且不是由主人创建的，可以删除
            if room.get_member_count() == 0 and room.owner_id != user_id:
                self.delete_room(room_id)

            return True

        return False

    def get_room(self, room_id: str) -> Optional[Room]:
        """获取房间"""
        return self.rooms.get(room_id)

    def get_user_rooms(self, user_id: str) -> List[Room]:
        """获取用户的所有房间"""
        room_ids = self.user_rooms.get(user_id, set())
        return [self.rooms[rid] for rid in room_ids if rid in self.rooms]

    def get_room_members(self, room_id: str) -> List[RoomMember]:
        """获取房间的所有成员"""
        if room_id not in self.rooms:
            return []
        return self.rooms[room_id].get_members()

    def is_room_member(self, room_id: str, user_id: str) -> bool:
        """检查用户是否是房间成员"""
        if room_id not in self.rooms:
            return False
        return self.rooms[room_id].is_member(user_id)

    def get_all_rooms(self) -> List[Room]:
        """获取所有房间"""
        return list(self.rooms.values())

    def get_active_rooms(self) -> List[Room]:
        """获取所有活跃房间"""
        return [room for room in self.rooms.values() if room.status == RoomStatus.ACTIVE]

    def increment_message_count(self, room_id: str) -> bool:
        """增加房间消息计数"""
        if room_id not in self.rooms:
            return False

        room = self.rooms[room_id]
        room.message_count += 1
        room.last_activity = datetime.utcnow()
        return True

    def _add_user_room(self, user_id: str, room_id: str) -> None:
        """添加用户-房间关联"""
        if user_id not in self.user_rooms:
            self.user_rooms[user_id] = set()
        self.user_rooms[user_id].add(room_id)

    def _remove_user_room(self, user_id: str, room_id: str) -> None:
        """移除用户-房间关联"""
        if user_id in self.user_rooms:
            self.user_rooms[user_id].discard(room_id)

    def get_stats(self) -> Dict[str, Any]:
        """获取管理器统计"""
        return {
            "total_rooms": len(self.rooms),
            "active_rooms": len(self.get_active_rooms()),
            "total_members": sum(room.get_member_count() for room in self.rooms.values()),
            "total_users": len(self.user_rooms),
            "rooms_created": self.rooms_created,
            "rooms_deleted": self.rooms_deleted,
            "total_join_events": self.total_join_events,
            "total_leave_events": self.total_leave_events,
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
    """重置房间管理器单例（仅用于测试）"""
    global _room_manager
    _room_manager = None
