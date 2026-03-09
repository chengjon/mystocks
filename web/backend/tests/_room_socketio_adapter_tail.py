"""Support mixin extracted from `test_room_socketio_adapter.py`."""

import pytest

from app.services.room_broadcast_service import reset_broadcaster
from app.services.room_management import reset_room_manager
from app.services.room_permission_service import (
    RoomRole,
    reset_access_control,
    reset_permission_manager,
)
from app.services.room_socketio_adapter import (
    get_room_socketio_adapter,
    reset_room_socketio_adapter,
)


def reset_all_singletons_for_room_adapter_tests():
    """Reset all service singletons for test isolation."""
    reset_room_socketio_adapter()
    reset_room_manager()
    reset_permission_manager()
    reset_access_control()
    reset_broadcaster()


class RoomSocketIOAdapterIntegrationScenariosMixin:
    """Integration scenario tests for room socketio adapter."""

    @pytest.mark.asyncio
    async def test_multiple_users_in_room(self):
        """Test multiple users in same room"""
        reset_all_singletons_for_room_adapter_tests()
        adapter = get_room_socketio_adapter()

        adapter.room_manager.create_room("room_1", "Test Room", "owner_1")

        for index in range(3):
            await adapter.handle_join_room(
                sid=f"sid_{index}",
                user_id=f"user_{index}",
                username=f"user{index}",
                room_id="room_1",
                role=RoomRole.MEMBER,
            )

        for index in range(3):
            await adapter.handle_room_message(
                sid=f"sid_{index}",
                user_id=f"user_{index}",
                room_id="room_1",
                content=f"Message from user {index}",
            )

        users = adapter.get_room_users("room_1")
        assert len(users) == 3
        assert adapter.total_messages == 3

    @pytest.mark.asyncio
    async def test_user_in_multiple_rooms(self):
        """Test user in multiple rooms simultaneously"""
        reset_all_singletons_for_room_adapter_tests()
        adapter = get_room_socketio_adapter()

        adapter.room_manager.create_room("room_1", "Room 1", "owner_1")
        adapter.room_manager.create_room("room_2", "Room 2", "owner_1")
        adapter.room_manager.create_room("room_3", "Room 3", "owner_1")

        for index, room_id in enumerate(["room_1", "room_2", "room_3"]):
            await adapter.handle_join_room(
                sid=f"sid_{index}",
                user_id="user_1",
                username="alice",
                room_id=room_id,
                role=RoomRole.MEMBER,
            )

        user_rooms = adapter.get_user_rooms("user_1")
        assert len(user_rooms) == 3

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
        reset_all_singletons_for_room_adapter_tests()
        adapter = get_room_socketio_adapter()

        adapter.room_manager.create_room("room_1", "Meeting", "owner_1")

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

        await adapter.handle_leave_room(
            sid="sid_2",
            user_id="user_2",
            room_id="room_1",
        )

        await adapter.handle_disconnect(sid="sid_1")

        assert len(adapter.sid_to_connection) == 0
        assert len(adapter.user_room_subscriptions) == 0
        assert adapter.total_joins == 2
        assert adapter.total_messages == 2
