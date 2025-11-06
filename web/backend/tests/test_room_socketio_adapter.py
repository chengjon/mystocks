"""
房间Socket.IO适配器测试

Tests for Room Socket.IO Adapter

Task 9: 多房间订阅扩展

Author: Claude Code
Date: 2025-11-07
"""

import pytest
from datetime import datetime

from app.services.room_socketio_adapter import (
    RoomSocketIOAdapter,
    RoomConnection,
    get_room_socketio_adapter,
    reset_room_socketio_adapter,
)
from app.services.room_management import (
    RoomManager,
    RoomType,
    reset_room_manager,
)
from app.services.room_permission_service import (
    RoomRole,
    RoomPermissionManager,
    RoomAccessControl,
    reset_permission_manager,
    reset_access_control,
)
from app.services.room_broadcast_service import (
    RoomBroadcaster,
    MessageType,
    reset_broadcaster,
)


def reset_all_singletons():
    """Reset all service singletons for test isolation"""
    reset_room_socketio_adapter()
    reset_room_manager()
    reset_permission_manager()
    reset_access_control()
    reset_broadcaster()


class TestRoomConnection:
    """Test RoomConnection dataclass"""

    def test_connection_creation(self):
        """Test creating a room connection"""
        conn = RoomConnection(
            sid="sid_1",
            user_id="user_1",
            username="alice",
            room_id="room_1",
            role=RoomRole.MEMBER,
        )
        assert conn.sid == "sid_1"
        assert conn.user_id == "user_1"
        assert conn.username == "alice"
        assert conn.room_id == "room_1"
        assert conn.role == RoomRole.MEMBER
        assert conn.message_count == 0

    def test_connection_to_dict(self):
        """Test connection serialization"""
        conn = RoomConnection(
            sid="sid_1",
            user_id="user_1",
            username="alice",
            room_id="room_1",
            role=RoomRole.ADMIN,
        )
        conn_dict = conn.to_dict()
        assert conn_dict["sid"] == "sid_1"
        assert conn_dict["user_id"] == "user_1"
        assert conn_dict["username"] == "alice"
        assert conn_dict["room_id"] == "room_1"
        assert conn_dict["role"] == "admin"
        assert "joined_at" in conn_dict


class TestAdapterInitialization:
    """Test adapter initialization"""

    def test_adapter_creation_with_defaults(self):
        """Test creating adapter with default managers"""
        reset_all_singletons()

        adapter = RoomSocketIOAdapter()
        assert adapter.room_manager is not None
        assert adapter.permission_manager is not None
        assert adapter.access_control is not None
        assert adapter.broadcaster is not None

    def test_adapter_creation_with_custom_managers(self):
        """Test creating adapter with custom managers"""
        room_manager = RoomManager()
        permission_manager = RoomPermissionManager()
        access_control = RoomAccessControl(permission_manager)
        broadcaster = RoomBroadcaster()

        adapter = RoomSocketIOAdapter(
            room_manager=room_manager,
            permission_manager=permission_manager,
            access_control=access_control,
            broadcaster=broadcaster,
        )

        assert adapter.room_manager is room_manager
        assert adapter.permission_manager is permission_manager
        assert adapter.access_control is access_control
        assert adapter.broadcaster is broadcaster

    def test_adapter_singleton(self):
        """Test adapter singleton pattern"""
        reset_all_singletons()
        adapter1 = get_room_socketio_adapter()
        adapter2 = get_room_socketio_adapter()
        assert adapter1 is adapter2

    def test_adapter_reset(self):
        """Test resetting adapter singleton"""
        reset_all_singletons()
        adapter1 = get_room_socketio_adapter()
        reset_all_singletons()
        adapter2 = get_room_socketio_adapter()
        assert adapter1 is not adapter2


class TestRoomJoin:
    """Test joining rooms"""

    @pytest.mark.asyncio
    async def test_join_room_success(self):
        """Test successfully joining a room"""
        reset_all_singletons()
        adapter = get_room_socketio_adapter()

        # Create a room
        adapter.room_manager.create_room("room_1", "Test Room", "owner_1")

        # Join room
        result = await adapter.handle_join_room(
            sid="sid_1",
            user_id="user_1",
            username="alice",
            room_id="room_1",
            role=RoomRole.MEMBER,
        )

        assert result["success"] is True
        assert "room" in result
        assert "connection" in result
        assert adapter.total_joins == 1

    @pytest.mark.asyncio
    async def test_join_nonexistent_room(self):
        """Test joining a non-existent room"""
        reset_all_singletons()
        adapter = get_room_socketio_adapter()

        result = await adapter.handle_join_room(
            sid="sid_1",
            user_id="user_1",
            username="alice",
            room_id="nonexistent",
            role=RoomRole.MEMBER,
        )

        assert result["success"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_join_room_tracks_connection(self):
        """Test that join room tracks connection info"""
        reset_all_singletons()
        adapter = get_room_socketio_adapter()

        adapter.room_manager.create_room("room_1", "Test Room", "owner_1")

        await adapter.handle_join_room(
            sid="sid_1",
            user_id="user_1",
            username="alice",
            room_id="room_1",
            role=RoomRole.MEMBER,
        )

        # Check connection is tracked
        assert "sid_1" in adapter.sid_to_connection
        connection = adapter.sid_to_connection["sid_1"]
        assert connection.user_id == "user_1"
        assert connection.room_id == "room_1"

    @pytest.mark.asyncio
    async def test_join_room_tracks_user_subscriptions(self):
        """Test that join room tracks user subscriptions"""
        reset_all_singletons()
        adapter = get_room_socketio_adapter()

        adapter.room_manager.create_room("room_1", "Test Room", "owner_1")

        await adapter.handle_join_room(
            sid="sid_1",
            user_id="user_1",
            username="alice",
            room_id="room_1",
            role=RoomRole.MEMBER,
        )

        # Check user room subscription is tracked
        assert "user_1" in adapter.user_room_subscriptions
        assert "room_1" in adapter.user_room_subscriptions["user_1"]

    @pytest.mark.asyncio
    async def test_join_multiple_rooms(self):
        """Test user joining multiple rooms"""
        reset_all_singletons()
        adapter = get_room_socketio_adapter()

        adapter.room_manager.create_room("room_1", "Room 1", "owner_1")
        adapter.room_manager.create_room("room_2", "Room 2", "owner_1")

        await adapter.handle_join_room(
            sid="sid_1",
            user_id="user_1",
            username="alice",
            room_id="room_1",
            role=RoomRole.MEMBER,
        )

        await adapter.handle_join_room(
            sid="sid_2",
            user_id="user_1",
            username="alice",
            room_id="room_2",
            role=RoomRole.MEMBER,
        )

        assert len(adapter.user_room_subscriptions["user_1"]) == 2
        assert "room_1" in adapter.user_room_subscriptions["user_1"]
        assert "room_2" in adapter.user_room_subscriptions["user_1"]


class TestRoomLeave:
    """Test leaving rooms"""

    @pytest.mark.asyncio
    async def test_leave_room_success(self):
        """Test successfully leaving a room"""
        reset_all_singletons()
        adapter = get_room_socketio_adapter()

        adapter.room_manager.create_room("room_1", "Test Room", "owner_1")

        await adapter.handle_join_room(
            sid="sid_1",
            user_id="user_1",
            username="alice",
            room_id="room_1",
            role=RoomRole.MEMBER,
        )

        result = await adapter.handle_leave_room(
            sid="sid_1",
            user_id="user_1",
            room_id="room_1",
        )

        assert result["success"] is True
        assert "sid_1" not in adapter.sid_to_connection

    @pytest.mark.asyncio
    async def test_leave_nonexistent_room(self):
        """Test leaving a non-existent room"""
        reset_all_singletons()
        adapter = get_room_socketio_adapter()

        result = await adapter.handle_leave_room(
            sid="sid_1",
            user_id="user_1",
            room_id="nonexistent",
        )

        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_leave_room_clears_subscriptions(self):
        """Test that leaving room clears subscriptions"""
        reset_all_singletons()
        adapter = get_room_socketio_adapter()

        adapter.room_manager.create_room("room_1", "Test Room", "owner_1")

        await adapter.handle_join_room(
            sid="sid_1",
            user_id="user_1",
            username="alice",
            room_id="room_1",
            role=RoomRole.MEMBER,
        )

        await adapter.handle_leave_room(
            sid="sid_1",
            user_id="user_1",
            room_id="room_1",
        )

        # Check subscriptions are cleared
        assert "user_1" not in adapter.user_room_subscriptions


class TestRoomMessages:
    """Test room messaging"""

    @pytest.mark.asyncio
    async def test_send_room_message_success(self):
        """Test successfully sending a room message"""
        reset_all_singletons()
        adapter = get_room_socketio_adapter()

        adapter.room_manager.create_room("room_1", "Test Room", "owner_1")

        await adapter.handle_join_room(
            sid="sid_1",
            user_id="user_1",
            username="alice",
            room_id="room_1",
            role=RoomRole.MEMBER,
        )

        result = await adapter.handle_room_message(
            sid="sid_1",
            user_id="user_1",
            room_id="room_1",
            content="Hello, room!",
        )

        assert result["success"] is True
        assert "message" in result
        assert result["message"]["content"] == "Hello, room!"
        assert adapter.total_messages == 1

    @pytest.mark.asyncio
    async def test_send_message_not_in_room(self):
        """Test sending message when not in room"""
        reset_all_singletons()
        adapter = get_room_socketio_adapter()

        adapter.room_manager.create_room("room_1", "Test Room", "owner_1")

        result = await adapter.handle_room_message(
            sid="sid_1",
            user_id="user_1",
            room_id="room_1",
            content="Hello",
        )

        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_send_message_increments_counter(self):
        """Test that sending message increments counters"""
        reset_all_singletons()
        adapter = get_room_socketio_adapter()

        adapter.room_manager.create_room("room_1", "Test Room", "owner_1")

        await adapter.handle_join_room(
            sid="sid_1",
            user_id="user_1",
            username="alice",
            room_id="room_1",
            role=RoomRole.MEMBER,
        )

        await adapter.handle_room_message(
            sid="sid_1",
            user_id="user_1",
            room_id="room_1",
            content="Message 1",
        )

        await adapter.handle_room_message(
            sid="sid_1",
            user_id="user_1",
            room_id="room_1",
            content="Message 2",
        )

        connection = adapter.sid_to_connection["sid_1"]
        assert connection.message_count == 2
        assert adapter.total_messages == 2

    @pytest.mark.asyncio
    async def test_guest_cannot_send_message(self):
        """Test that guests cannot send messages"""
        reset_all_singletons()
        adapter = get_room_socketio_adapter()

        adapter.room_manager.create_room("room_1", "Test Room", "owner_1")

        await adapter.handle_join_room(
            sid="sid_1",
            user_id="user_1",
            username="alice",
            room_id="room_1",
            role=RoomRole.GUEST,
        )

        result = await adapter.handle_room_message(
            sid="sid_1",
            user_id="user_1",
            room_id="room_1",
            content="Hello",
        )

        assert result["success"] is False


class TestDisconnect:
    """Test handling disconnections"""

    @pytest.mark.asyncio
    async def test_disconnect_cleans_up_connection(self):
        """Test that disconnect cleans up connection"""
        reset_all_singletons()
        adapter = get_room_socketio_adapter()

        adapter.room_manager.create_room("room_1", "Test Room", "owner_1")

        await adapter.handle_join_room(
            sid="sid_1",
            user_id="user_1",
            username="alice",
            room_id="room_1",
            role=RoomRole.MEMBER,
        )

        await adapter.handle_disconnect(sid="sid_1")

        assert "sid_1" not in adapter.sid_to_connection

    @pytest.mark.asyncio
    async def test_disconnect_removes_user_subscription(self):
        """Test that disconnect removes user subscription"""
        reset_all_singletons()
        adapter = get_room_socketio_adapter()

        adapter.room_manager.create_room("room_1", "Test Room", "owner_1")

        await adapter.handle_join_room(
            sid="sid_1",
            user_id="user_1",
            username="alice",
            room_id="room_1",
            role=RoomRole.MEMBER,
        )

        await adapter.handle_disconnect(sid="sid_1")

        assert "user_1" not in adapter.user_room_subscriptions

    @pytest.mark.asyncio
    async def test_disconnect_unknown_connection(self):
        """Test disconnecting unknown connection doesn't error"""
        reset_all_singletons()
        adapter = get_room_socketio_adapter()

        # Should not raise exception
        await adapter.handle_disconnect(sid="unknown_sid")


class TestSocketIOCallbacks:
    """Test Socket.IO callback registration and usage"""

    def test_register_socketio_callback(self):
        """Test registering Socket.IO callback"""
        reset_all_singletons()
        adapter = get_room_socketio_adapter()

        callback_called = []

        def mock_callback(sid, event, data):
            callback_called.append((sid, event, data))

        adapter.register_socketio_callback(mock_callback)
        assert len(adapter.socketio_callbacks) == 1

    def test_multiple_callbacks(self):
        """Test registering multiple callbacks"""
        reset_all_singletons()
        adapter = get_room_socketio_adapter()

        calls = []

        def callback1(sid, event, data):
            calls.append("callback1")

        def callback2(sid, event, data):
            calls.append("callback2")

        adapter.register_socketio_callback(callback1)
        adapter.register_socketio_callback(callback2)

        assert len(adapter.socketio_callbacks) == 2


class TestQueries:
    """Test query methods"""

    @pytest.mark.asyncio
    async def test_get_room_users(self):
        """Test getting users in a room"""
        reset_all_singletons()
        adapter = get_room_socketio_adapter()

        adapter.room_manager.create_room("room_1", "Test Room", "owner_1")

        await adapter.handle_join_room(
            sid="sid_1",
            user_id="user_1",
            username="alice",
            room_id="room_1",
            role=RoomRole.MEMBER,
        )

        await adapter.handle_join_room(
            sid="sid_2",
            user_id="user_2",
            username="bob",
            room_id="room_1",
            role=RoomRole.MEMBER,
        )

        users = adapter.get_room_users("room_1")
        assert len(users) == 2
        usernames = {u["username"] for u in users}
        assert "alice" in usernames
        assert "bob" in usernames

    @pytest.mark.asyncio
    async def test_get_user_rooms(self):
        """Test getting user's rooms"""
        reset_all_singletons()
        adapter = get_room_socketio_adapter()

        adapter.room_manager.create_room("room_1", "Room 1", "owner_1")
        adapter.room_manager.create_room("room_2", "Room 2", "owner_1")

        await adapter.handle_join_room(
            sid="sid_1",
            user_id="user_1",
            username="alice",
            room_id="room_1",
            role=RoomRole.MEMBER,
        )

        await adapter.handle_join_room(
            sid="sid_2",
            user_id="user_1",
            username="alice",
            room_id="room_2",
            role=RoomRole.MEMBER,
        )

        rooms = adapter.get_user_rooms("user_1")
        assert len(rooms) == 2
        room_ids = {r["id"] for r in rooms}
        assert "room_1" in room_ids
        assert "room_2" in room_ids

    def test_get_connection_info(self):
        """Test getting connection info"""
        reset_all_singletons()
        adapter = get_room_socketio_adapter()

        # Create and add connection directly
        conn = RoomConnection(
            sid="sid_1",
            user_id="user_1",
            username="alice",
            room_id="room_1",
            role=RoomRole.MEMBER,
        )
        adapter.sid_to_connection["sid_1"] = conn

        info = adapter.get_connection_info("sid_1")
        assert info is not None
        assert info["user_id"] == "user_1"
        assert info["room_id"] == "room_1"

    def test_get_connection_info_unknown(self):
        """Test getting connection info for unknown sid"""
        reset_all_singletons()
        adapter = get_room_socketio_adapter()

        info = adapter.get_connection_info("unknown_sid")
        assert info is None


class TestStats:
    """Test statistics"""

    @pytest.mark.asyncio
    async def test_get_stats(self):
        """Test getting adapter statistics"""
        reset_all_singletons()
        adapter = get_room_socketio_adapter()

        adapter.room_manager.create_room("room_1", "Test Room", "owner_1")

        await adapter.handle_join_room(
            sid="sid_1",
            user_id="user_1",
            username="alice",
            room_id="room_1",
            role=RoomRole.MEMBER,
        )

        await adapter.handle_room_message(
            sid="sid_1",
            user_id="user_1",
            room_id="room_1",
            content="Hello",
        )

        stats = adapter.get_stats()
        assert stats["active_connections"] == 1
        assert stats["active_users"] == 1
        assert stats["total_joins"] == 1
        assert stats["total_messages"] == 1
        assert "room_manager_stats" in stats
        assert "broadcaster_stats" in stats
        assert "permission_manager_stats" in stats

    @pytest.mark.asyncio
    async def test_stats_after_leave(self):
        """Test stats after leaving room"""
        reset_all_singletons()
        adapter = get_room_socketio_adapter()

        adapter.room_manager.create_room("room_1", "Test Room", "owner_1")

        await adapter.handle_join_room(
            sid="sid_1",
            user_id="user_1",
            username="alice",
            room_id="room_1",
            role=RoomRole.MEMBER,
        )

        await adapter.handle_leave_room(
            sid="sid_1",
            user_id="user_1",
            room_id="room_1",
        )

        stats = adapter.get_stats()
        assert stats["active_connections"] == 0
        assert stats["active_users"] == 0


class TestIntegrationScenarios:
    """Test integration scenarios"""

    @pytest.mark.asyncio
    async def test_multiple_users_in_room(self):
        """Test multiple users in same room"""
        reset_all_singletons()
        adapter = get_room_socketio_adapter()

        adapter.room_manager.create_room("room_1", "Test Room", "owner_1")

        # Multiple users join
        for i in range(3):
            await adapter.handle_join_room(
                sid=f"sid_{i}",
                user_id=f"user_{i}",
                username=f"user{i}",
                room_id="room_1",
                role=RoomRole.MEMBER,
            )

        # Users send messages
        for i in range(3):
            await adapter.handle_room_message(
                sid=f"sid_{i}",
                user_id=f"user_{i}",
                room_id="room_1",
                content=f"Message from user {i}",
            )

        users = adapter.get_room_users("room_1")
        assert len(users) == 3
        assert adapter.total_messages == 3

    @pytest.mark.asyncio
    async def test_user_in_multiple_rooms(self):
        """Test user in multiple rooms simultaneously"""
        reset_all_singletons()
        adapter = get_room_socketio_adapter()

        adapter.room_manager.create_room("room_1", "Room 1", "owner_1")
        adapter.room_manager.create_room("room_2", "Room 2", "owner_1")
        adapter.room_manager.create_room("room_3", "Room 3", "owner_1")

        # User joins multiple rooms
        for i, room_id in enumerate(["room_1", "room_2", "room_3"]):
            await adapter.handle_join_room(
                sid=f"sid_{i}",
                user_id="user_1",
                username="alice",
                room_id=room_id,
                role=RoomRole.MEMBER,
            )

        user_rooms = adapter.get_user_rooms("user_1")
        assert len(user_rooms) == 3

        # Leave one room
        await adapter.handle_leave_room(
            sid="sid_0",
            user_id="user_1",
            room_id="room_1",
        )

        user_rooms = adapter.get_user_rooms("user_1")
        assert len(user_rooms) == 2

    @pytest.mark.asyncio
    async def test_full_room_lifecycle(self):
        """Test complete room lifecycle with adapter"""
        reset_all_singletons()
        adapter = get_room_socketio_adapter()

        # Create room
        adapter.room_manager.create_room("room_1", "Meeting", "owner_1")

        # Users join
        await adapter.handle_join_room(
            sid="sid_1",
            user_id="user_1",
            username="alice",
            room_id="room_1",
            role=RoomRole.OWNER,
        )

        await adapter.handle_join_room(
            sid="sid_2",
            user_id="user_2",
            username="bob",
            room_id="room_1",
            role=RoomRole.MEMBER,
        )

        # Send messages
        await adapter.handle_room_message(
            sid="sid_1",
            user_id="user_1",
            room_id="room_1",
            content="Hello everyone",
        )

        await adapter.handle_room_message(
            sid="sid_2",
            user_id="user_2",
            room_id="room_1",
            content="Hi alice!",
        )

        # User leaves
        await adapter.handle_leave_room(
            sid="sid_2",
            user_id="user_2",
            room_id="room_1",
        )

        # User stays and disconnects
        await adapter.handle_disconnect(sid="sid_1")

        # Verify state
        assert len(adapter.sid_to_connection) == 0
        assert len(adapter.user_room_subscriptions) == 0
        assert adapter.total_joins == 2
        assert adapter.total_messages == 2
