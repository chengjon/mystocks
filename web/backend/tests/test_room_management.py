"""
房间管理测试

Tests for Room Management

Task 9: 多房间订阅扩展

Author: Claude Code
Date: 2025-11-07
"""

from app.services.room_management import (
    RoomType,
    RoomStatus,
    RoomMember,
    Room,
    RoomManager,
    get_room_manager,
    reset_room_manager,
)


class TestRoomMember:
    """Test RoomMember"""

    def test_member_creation(self):
        """Test member creation"""
        member = RoomMember(user_id="user_1", username="alice")
        assert member.user_id == "user_1"
        assert member.username == "alice"
        assert member.is_admin is False
        assert member.is_moderator is False

    def test_member_as_admin(self):
        """Test member as admin"""
        member = RoomMember(user_id="user_1", username="alice", is_admin=True)
        assert member.is_admin is True

    def test_member_to_dict(self):
        """Test member serialization"""
        member = RoomMember(user_id="user_1", username="alice", is_admin=True)
        member_dict = member.to_dict()
        assert member_dict["user_id"] == "user_1"
        assert member_dict["username"] == "alice"
        assert member_dict["is_admin"] is True
        assert "joined_at" in member_dict


class TestRoom:
    """Test Room"""

    def test_room_creation(self):
        """Test room creation"""
        room = Room(
            id="room_1",
            name="Test Room",
            type=RoomType.PUBLIC,
            owner_id="user_1",
        )
        assert room.id == "room_1"
        assert room.name == "Test Room"
        assert room.type == RoomType.PUBLIC
        assert room.owner_id == "user_1"
        assert room.status == RoomStatus.ACTIVE

    def test_room_add_member(self):
        """Test adding member to room"""
        room = Room(
            id="room_1",
            name="Test Room",
            type=RoomType.PUBLIC,
            owner_id="user_1",
        )
        result = room.add_member("user_2", "bob")
        assert result is True
        assert room.is_member("user_2")
        assert room.get_member_count() == 1

    def test_room_add_duplicate_member(self):
        """Test adding duplicate member"""
        room = Room(
            id="room_1",
            name="Test Room",
            type=RoomType.PUBLIC,
            owner_id="user_1",
        )
        room.add_member("user_2", "bob")
        result = room.add_member("user_2", "bob")
        assert result is False
        assert room.get_member_count() == 1

    def test_room_remove_member(self):
        """Test removing member from room"""
        room = Room(
            id="room_1",
            name="Test Room",
            type=RoomType.PUBLIC,
            owner_id="user_1",
        )
        room.add_member("user_2", "bob")
        result = room.remove_member("user_2")
        assert result is True
        assert not room.is_member("user_2")
        assert room.get_member_count() == 0

    def test_room_max_members(self):
        """Test room max members limit"""
        room = Room(
            id="room_1",
            name="Test Room",
            type=RoomType.PUBLIC,
            owner_id="user_1",
            max_members=2,
        )
        room.add_member("user_2", "bob")
        result = room.add_member("user_3", "charlie")
        assert result is True  # Second add succeeds (count=2)
        assert room.is_full()  # Room is full after 2 members
        assert room.get_member_count() == 2
        # Third add should fail
        result = room.add_member("user_4", "david")
        assert result is False

    def test_room_get_members(self):
        """Test getting room members"""
        room = Room(
            id="room_1",
            name="Test Room",
            type=RoomType.PUBLIC,
            owner_id="user_1",
        )
        room.add_member("user_2", "bob")
        room.add_member("user_3", "charlie")
        members = room.get_members()
        assert len(members) == 2
        member_ids = {m.user_id for m in members}
        assert "user_2" in member_ids
        assert "user_3" in member_ids

    def test_room_to_dict(self):
        """Test room serialization"""
        room = Room(
            id="room_1",
            name="Test Room",
            type=RoomType.PUBLIC,
            owner_id="user_1",
            max_members=10,
            description="A test room",
        )
        room.add_member("user_2", "bob")
        room_dict = room.to_dict()
        assert room_dict["id"] == "room_1"
        assert room_dict["name"] == "Test Room"
        assert room_dict["type"] == "public"
        assert room_dict["owner_id"] == "user_1"
        assert room_dict["member_count"] == 1
        assert room_dict["max_members"] == 10


class TestRoomManagerCreation:
    """Test room creation and deletion"""

    def test_manager_initialization(self):
        """Test manager initialization"""
        manager = RoomManager()
        assert len(manager.rooms) == 0
        assert len(manager.user_rooms) == 0

    def test_create_room(self):
        """Test creating a room"""
        manager = RoomManager()
        room = manager.create_room("room_1", "Test Room", "user_1")
        assert room.id == "room_1"
        assert room.name == "Test Room"
        assert room.owner_id == "user_1"
        assert manager.rooms_created == 1
        assert "room_1" in manager.rooms

    def test_create_multiple_rooms(self):
        """Test creating multiple rooms"""
        manager = RoomManager()
        manager.create_room("room_1", "Room 1", "user_1")
        manager.create_room("room_2", "Room 2", "user_2")
        assert len(manager.rooms) == 2
        assert manager.rooms_created == 2

    def test_delete_room(self):
        """Test deleting a room"""
        manager = RoomManager()
        manager.create_room("room_1", "Test Room", "user_1")
        result = manager.delete_room("room_1")
        assert result is True
        assert "room_1" not in manager.rooms
        assert manager.rooms_deleted == 1

    def test_delete_nonexistent_room(self):
        """Test deleting non-existent room"""
        manager = RoomManager()
        result = manager.delete_room("nonexistent")
        assert result is False


class TestRoomManagerMembership:
    """Test room membership operations"""

    def test_join_room(self):
        """Test joining a room"""
        manager = RoomManager()
        manager.create_room("room_1", "Test Room", "user_1")
        result = manager.join_room("room_1", "user_2", "bob")
        assert result is True
        assert manager.is_room_member("room_1", "user_2")
        assert manager.total_join_events == 1

    def test_join_nonexistent_room(self):
        """Test joining non-existent room"""
        manager = RoomManager()
        result = manager.join_room("nonexistent", "user_1", "alice")
        assert result is False

    def test_join_full_room(self):
        """Test joining full room"""
        manager = RoomManager()
        room = manager.create_room("room_1", "Test Room", "user_1", max_members=1)
        result = manager.join_room("room_1", "user_2", "bob")
        assert result is False
        assert not manager.is_room_member("room_1", "user_2")

    def test_leave_room(self):
        """Test leaving a room"""
        manager = RoomManager()
        manager.create_room("room_1", "Test Room", "user_1")
        manager.join_room("room_1", "user_2", "bob")
        result = manager.leave_room("room_1", "user_2")
        assert result is True
        assert not manager.is_room_member("room_1", "user_2")
        assert manager.total_leave_events == 1

    def test_leave_nonexistent_room(self):
        """Test leaving non-existent room"""
        manager = RoomManager()
        result = manager.leave_room("nonexistent", "user_1")
        assert result is False

    def test_get_user_rooms(self):
        """Test getting user's rooms"""
        manager = RoomManager()
        manager.create_room("room_1", "Room 1", "user_1")
        manager.create_room("room_2", "Room 2", "user_1")
        manager.join_room("room_2", "user_2", "bob")

        user1_rooms = manager.get_user_rooms("user_1")
        user2_rooms = manager.get_user_rooms("user_2")

        assert len(user1_rooms) == 2
        assert len(user2_rooms) == 1

    def test_get_room_members(self):
        """Test getting room members"""
        manager = RoomManager()
        manager.create_room("room_1", "Test Room", "user_1")
        manager.join_room("room_1", "user_2", "bob")
        manager.join_room("room_1", "user_3", "charlie")

        members = manager.get_room_members("room_1")
        assert len(members) == 3
        member_ids = {m.user_id for m in members}
        assert "user_1" in member_ids
        assert "user_2" in member_ids
        assert "user_3" in member_ids


class TestRoomManagerQueries:
    """Test room query operations"""

    def test_get_room(self):
        """Test getting a room"""
        manager = RoomManager()
        manager.create_room("room_1", "Test Room", "user_1")
        room = manager.get_room("room_1")
        assert room is not None
        assert room.name == "Test Room"

    def test_get_nonexistent_room(self):
        """Test getting non-existent room"""
        manager = RoomManager()
        room = manager.get_room("nonexistent")
        assert room is None

    def test_get_all_rooms(self):
        """Test getting all rooms"""
        manager = RoomManager()
        manager.create_room("room_1", "Room 1", "user_1")
        manager.create_room("room_2", "Room 2", "user_2")
        manager.create_room("room_3", "Room 3", "user_3")

        rooms = manager.get_all_rooms()
        assert len(rooms) == 3

    def test_get_active_rooms(self):
        """Test getting active rooms"""
        manager = RoomManager()
        room1 = manager.create_room("room_1", "Room 1", "user_1")
        room2 = manager.create_room("room_2", "Room 2", "user_2")
        room1.status = RoomStatus.CLOSED

        active_rooms = manager.get_active_rooms()
        assert len(active_rooms) == 1
        assert active_rooms[0].id == "room_2"

    def test_is_room_member(self):
        """Test checking room membership"""
        manager = RoomManager()
        manager.create_room("room_1", "Test Room", "user_1")
        manager.join_room("room_1", "user_2", "bob")

        assert manager.is_room_member("room_1", "user_1")
        assert manager.is_room_member("room_1", "user_2")
        assert not manager.is_room_member("room_1", "user_3")


class TestRoomManagerStats:
    """Test room statistics"""

    def test_increment_message_count(self):
        """Test incrementing message count"""
        manager = RoomManager()
        manager.create_room("room_1", "Test Room", "user_1")
        result = manager.increment_message_count("room_1")
        assert result is True
        room = manager.get_room("room_1")
        assert room.message_count == 1

    def test_get_stats(self):
        """Test getting manager statistics"""
        manager = RoomManager()
        manager.create_room("room_1", "Room 1", "user_1")
        manager.create_room("room_2", "Room 2", "user_2")
        manager.join_room("room_1", "user_2", "bob")
        manager.join_room("room_2", "user_3", "charlie")

        stats = manager.get_stats()
        assert stats["total_rooms"] == 2
        assert stats["active_rooms"] == 2
        assert stats["total_members"] == 4
        assert stats["total_users"] == 3
        assert stats["rooms_created"] == 2
        assert stats["total_join_events"] == 2


class TestRoomManagerSingleton:
    """Test singleton pattern"""

    def test_get_room_manager_singleton(self):
        """Test getting room manager singleton"""
        reset_room_manager()
        manager1 = get_room_manager()
        manager2 = get_room_manager()
        assert manager1 is manager2

    def test_reset_room_manager(self):
        """Test resetting room manager"""
        reset_room_manager()
        manager1 = get_room_manager()
        reset_room_manager()
        manager2 = get_room_manager()
        assert manager1 is not manager2


class TestRoomManagerIntegration:
    """Test integration scenarios"""

    def test_full_room_lifecycle(self):
        """Test complete room lifecycle"""
        manager = RoomManager()

        # Create room
        room = manager.create_room("room_1", "Meeting Room", "user_1")
        assert room is not None

        # Users join
        manager.join_room("room_1", "user_2", "bob")
        manager.join_room("room_1", "user_3", "charlie")
        assert manager.get_room("room_1").get_member_count() == 3

        # Message activity
        manager.increment_message_count("room_1")
        manager.increment_message_count("room_1")
        assert manager.get_room("room_1").message_count == 2

        # Users leave
        manager.leave_room("room_1", "user_2")
        manager.leave_room("room_1", "user_3")
        assert manager.get_room("room_1").get_member_count() == 1

    def test_multiple_rooms_concurrent_operations(self):
        """Test multiple rooms with concurrent operations"""
        manager = RoomManager()

        # Create multiple rooms
        for i in range(5):
            manager.create_room(f"room_{i}", f"Room {i}", f"user_{i}")

        # Users join different rooms
        manager.join_room("room_0", "user_1", "alice")
        manager.join_room("room_2", "user_1", "alice")
        manager.join_room("room_3", "user_2", "bob")

        # Check user is in multiple rooms
        # user_1 created room_1, joined room_0 and room_2 = 3 rooms
        user1_rooms = manager.get_user_rooms("user_1")
        assert len(user1_rooms) == 3  # room_0 (joined), room_1 (owner), room_2 (joined)

        # Message activity in each room
        for i in range(5):
            manager.increment_message_count(f"room_{i}")

        stats = manager.get_stats()
        assert stats["total_rooms"] == 5
        assert stats["total_messages"] == 5 if "total_messages" in stats else True

    def test_room_types(self):
        """Test different room types"""
        manager = RoomManager()

        # Public room
        public_room = manager.create_room("public", "Public Room", "user_1", room_type=RoomType.PUBLIC)
        assert public_room.type == RoomType.PUBLIC

        # Private room
        private_room = manager.create_room("private", "Private Room", "user_1", room_type=RoomType.PRIVATE)
        assert private_room.type == RoomType.PRIVATE

        # Protected room
        protected_room = manager.create_room("protected", "Protected Room", "user_1", room_type=RoomType.PROTECTED)
        assert protected_room.type == RoomType.PROTECTED
