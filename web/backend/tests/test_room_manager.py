"""
房间管理器单元测试

Test Room Manager - Room-based pub/sub messaging

Task 4.3: 房间订阅测试

Author: Claude Code
Date: 2025-11-06
"""

from app.core.room_manager import (
    RoomManager,
    Room,
    RoomMember,
    RoomEventType,
    get_room_manager,
    reset_room_manager,
)


class TestRoomMember:
    """测试房间成员"""

    def test_room_member_creation(self):
        """测试房间成员创建"""
        member = RoomMember("sid_001", user_id="user_001")

        assert member.sid == "sid_001"
        assert member.user_id == "user_001"
        assert member.message_count == 0

    def test_record_message(self):
        """测试记录成员消息"""
        member = RoomMember("sid_001")
        old_activity = member.last_activity

        member.record_message()

        assert member.message_count == 1
        assert member.last_activity >= old_activity

    def test_member_to_dict(self):
        """测试成员转换为字典"""
        member = RoomMember("sid_001", user_id="user_001")
        data = member.to_dict()

        assert data["sid"] == "sid_001"
        assert data["user_id"] == "user_001"
        assert data["message_count"] == 0
        assert "joined_at" in data


class TestRoom:
    """测试房间"""

    def test_room_creation(self):
        """测试房间创建"""
        room = Room("stock_600519")

        assert room.name == "stock_600519"
        assert room.room_id is not None
        assert len(room.members) == 0

    def test_add_member(self):
        """测试添加成员"""
        room = Room("room_001")
        member = room.add_member("sid_001", user_id="user_001")

        assert room.has_member("sid_001")
        assert member.user_id == "user_001"
        assert len(room.members) == 1

    def test_remove_member(self):
        """测试移除成员"""
        room = Room("room_001")
        room.add_member("sid_001")
        member = room.remove_member("sid_001")

        assert not room.has_member("sid_001")
        assert member.sid == "sid_001"

    def test_get_member(self):
        """测试获取成员"""
        room = Room("room_001")
        room.add_member("sid_001", user_id="user_001")

        member = room.get_member("sid_001")

        assert member is not None
        assert member.user_id == "user_001"

    def test_get_all_members(self):
        """测试获取所有成员"""
        room = Room("room_001")
        room.add_member("sid_001")
        room.add_member("sid_002")
        room.add_member("sid_003")

        members = room.get_all_members()

        assert len(members) == 3

    def test_is_empty(self):
        """测试房间是否为空"""
        room = Room("room_001")

        assert room.is_empty()

        room.add_member("sid_001")
        assert not room.is_empty()

        room.remove_member("sid_001")
        assert room.is_empty()

    def test_room_stats(self):
        """测试房间统计"""
        room = Room("room_001")
        room.add_member("sid_001")
        room.add_member("sid_002")

        stats = room.get_stats()

        assert stats["name"] == "room_001"
        assert stats["member_count"] == 2
        assert len(stats["members"]) == 2


class TestRoomManager:
    """测试房间管理器"""

    def setup_method(self):
        """测试前初始化"""
        reset_room_manager()
        self.manager = RoomManager()

    def test_create_room(self):
        """测试创建房间"""
        room = self.manager.create_room("room_001")

        assert room.name == "room_001"
        assert self.manager.room_exists("room_001")

    def test_destroy_room(self):
        """测试销毁房间"""
        self.manager.create_room("room_001")
        success = self.manager.destroy_room("room_001")

        assert success
        assert not self.manager.room_exists("room_001")

    def test_add_member_to_room(self):
        """测试添加成员到房间"""
        success = self.manager.add_member_to_room("room_001", "sid_001", user_id="user_001")

        assert success
        assert self.manager.room_exists("room_001")
        assert self.manager.get_member_room("sid_001") == "room_001"

    def test_remove_member_from_room(self):
        """测试从房间移除成员"""
        self.manager.add_member_to_room("room_001", "sid_001")
        success = self.manager.remove_member_from_room("room_001", "sid_001")

        assert success
        assert self.manager.get_member_room("sid_001") is None
        # 房间应该被销毁（因为为空）
        assert not self.manager.room_exists("room_001")

    def test_member_switch_rooms(self):
        """测试成员切换房间"""
        self.manager.add_member_to_room("room_001", "sid_001")
        assert self.manager.get_member_room("sid_001") == "room_001"

        self.manager.add_member_to_room("room_002", "sid_001")
        assert self.manager.get_member_room("sid_001") == "room_002"
        # room_001应该被销毁
        assert not self.manager.room_exists("room_001")

    def test_get_room_members(self):
        """测试获取房间成员"""
        self.manager.add_member_to_room("room_001", "sid_001")
        self.manager.add_member_to_room("room_001", "sid_002")

        members = self.manager.get_room_members("room_001")

        assert len(members) == 2

    def test_get_room_member_sids(self):
        """测试获取房间成员SID列表"""
        self.manager.add_member_to_room("room_001", "sid_001")
        self.manager.add_member_to_room("room_001", "sid_002")

        sids = self.manager.get_room_member_sids("room_001")

        assert len(sids) == 2
        assert "sid_001" in sids
        assert "sid_002" in sids

    def test_record_member_message(self):
        """测试记录成员消息"""
        self.manager.add_member_to_room("room_001", "sid_001")
        self.manager.record_member_message("room_001", "sid_001")

        room = self.manager.get_room("room_001")
        member = room.get_member("sid_001")

        assert member.message_count == 1

    def test_get_all_rooms(self):
        """测试获取所有房间"""
        self.manager.add_member_to_room("room_001", "sid_001")
        self.manager.add_member_to_room("room_002", "sid_002")

        rooms = self.manager.get_all_rooms()

        assert len(rooms) == 2

    def test_get_stats(self):
        """测试获取统计信息"""
        self.manager.add_member_to_room("room_001", "sid_001")
        self.manager.add_member_to_room("room_001", "sid_002")
        self.manager.add_member_to_room("room_002", "sid_003")

        stats = self.manager.get_stats()

        assert stats["total_rooms"] == 2
        assert stats["total_members"] == 3
        assert "timestamp" in stats


class TestRoomEvents:
    """测试房间事件"""

    def setup_method(self):
        """测试前初始化"""
        reset_room_manager()
        self.manager = RoomManager()
        self.events = []

    def event_handler(self, data):
        """事件处理器"""
        self.events.append(data)

    def test_register_event_handler(self):
        """测试注册事件处理器"""
        self.manager.register_event_handler(RoomEventType.MEMBER_JOINED, self.event_handler)

        assert len(self.manager.event_callbacks[RoomEventType.MEMBER_JOINED]) > 0

    def test_member_joined_event(self):
        """测试成员加入事件"""
        self.manager.register_event_handler(RoomEventType.MEMBER_JOINED, self.event_handler)

        self.manager.add_member_to_room("room_001", "sid_001", user_id="user_001")

        assert len(self.events) == 1
        assert self.events[0]["room"] == "room_001"
        assert self.events[0]["sid"] == "sid_001"

    def test_member_left_event(self):
        """测试成员离开事件"""
        self.manager.add_member_to_room("room_001", "sid_001")
        self.manager.register_event_handler(RoomEventType.MEMBER_LEFT, self.event_handler)

        self.manager.remove_member_from_room("room_001", "sid_001")

        assert len(self.events) == 1
        assert self.events[0]["room"] == "room_001"
        assert self.events[0]["sid"] == "sid_001"

    def test_room_created_event(self):
        """测试房间创建事件"""
        self.manager.register_event_handler(RoomEventType.ROOM_CREATED, self.event_handler)

        self.manager.create_room("room_001")

        assert len(self.events) == 1
        assert self.events[0]["room"] == "room_001"

    def test_room_destroyed_event(self):
        """测试房间销毁事件"""
        self.manager.create_room("room_001")
        self.manager.register_event_handler(RoomEventType.ROOM_DESTROYED, self.event_handler)

        self.manager.destroy_room("room_001")

        assert len(self.events) == 1
        assert self.events[0]["room"] == "room_001"


class TestRoomManagerSingleton:
    """测试房间管理器单例"""

    def test_get_singleton_manager(self):
        """测试获取单例管理器"""
        reset_room_manager()

        manager1 = get_room_manager()
        manager2 = get_room_manager()

        assert manager1 is manager2

    def test_reset_singleton_manager(self):
        """测试重置单例管理器"""
        reset_room_manager()
        manager1 = get_room_manager()

        reset_room_manager()
        manager2 = get_room_manager()

        assert manager1 is not manager2


class TestMultiRoomScenarios:
    """测试多房间场景"""

    def setup_method(self):
        """测试前初始化"""
        reset_room_manager()
        self.manager = RoomManager()

    def test_multiple_rooms_multiple_members(self):
        """测试多个房间和多个成员"""
        # 创建房间1：成员1、2、3
        for i in range(1, 4):
            self.manager.add_member_to_room("stock_600519", f"sid_{i}", user_id=f"user_{i}")

        # 创建房间2：成员4、5
        for i in range(4, 6):
            self.manager.add_member_to_room("stock_600000", f"sid_{i}", user_id=f"user_{i}")

        assert self.manager.get_stats()["total_rooms"] == 2
        assert self.manager.get_stats()["total_members"] == 5
        assert len(self.manager.get_room_members("stock_600519")) == 3
        assert len(self.manager.get_room_members("stock_600000")) == 2

    def test_member_isolation_between_rooms(self):
        """测试房间间成员隔离"""
        self.manager.add_member_to_room("room_1", "sid_001")
        self.manager.add_member_to_room("room_2", "sid_002")

        room1_members = self.manager.get_room_member_sids("room_1")
        room2_members = self.manager.get_room_member_sids("room_2")

        assert "sid_001" in room1_members
        assert "sid_001" not in room2_members
        assert "sid_002" not in room1_members
        assert "sid_002" in room2_members
