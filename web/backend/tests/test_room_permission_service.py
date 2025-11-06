"""
房间权限控制服务测试

Tests for Room Permission Control Service

Task 9: 多房间订阅扩展

Author: Claude Code
Date: 2025-11-07
"""

import pytest
from app.services.room_permission_service import (
    RoomRole,
    RoomPermission,
    RoomPermissionManager,
    RoomAccessControl,
    get_permission_manager,
    get_access_control,
    reset_permission_manager,
    reset_access_control,
)


class TestRoomRole:
    """Test room roles"""

    def test_owner_role(self):
        """Test owner role"""
        assert RoomRole.OWNER == "owner"

    def test_admin_role(self):
        """Test admin role"""
        assert RoomRole.ADMIN == "admin"

    def test_moderator_role(self):
        """Test moderator role"""
        assert RoomRole.MODERATOR == "moderator"

    def test_member_role(self):
        """Test member role"""
        assert RoomRole.MEMBER == "member"

    def test_guest_role(self):
        """Test guest role"""
        assert RoomRole.GUEST == "guest"


class TestRoomPermission:
    """Test room permissions"""

    def test_view_permission(self):
        """Test view permission"""
        assert RoomPermission.VIEW == "view"

    def test_send_message_permission(self):
        """Test send message permission"""
        assert RoomPermission.SEND_MESSAGE == "send_message"

    def test_delete_message_permission(self):
        """Test delete message permission"""
        assert RoomPermission.DELETE_MESSAGE == "delete_message"

    def test_kick_member_permission(self):
        """Test kick member permission"""
        assert RoomPermission.KICK_MEMBER == "kick_member"

    def test_delete_room_permission(self):
        """Test delete room permission"""
        assert RoomPermission.DELETE_ROOM == "delete_room"


class TestPermissionManagerInitialization:
    """Test permission manager initialization"""

    def test_manager_creation(self):
        """Test creating permission manager"""
        manager = RoomPermissionManager(use_casbin=False)
        assert manager is not None
        assert manager.use_casbin is False

    def test_default_permissions_initialized(self):
        """Test default permissions are initialized"""
        manager = RoomPermissionManager(use_casbin=False)
        assert len(manager.role_permissions) == 5
        assert RoomRole.OWNER in manager.role_permissions
        assert RoomRole.ADMIN in manager.role_permissions
        assert RoomRole.MODERATOR in manager.role_permissions
        assert RoomRole.MEMBER in manager.role_permissions
        assert RoomRole.GUEST in manager.role_permissions

    def test_owner_has_all_permissions(self):
        """Test owner role has all permissions"""
        manager = RoomPermissionManager(use_casbin=False)
        owner_perms = manager.role_permissions[RoomRole.OWNER]
        assert len(owner_perms) == len(RoomPermission)

    def test_guest_has_minimal_permissions(self):
        """Test guest role has minimal permissions"""
        manager = RoomPermissionManager(use_casbin=False)
        guest_perms = manager.role_permissions[RoomRole.GUEST]
        assert RoomPermission.VIEW in guest_perms
        assert RoomPermission.LIST_MEMBERS in guest_perms
        assert RoomPermission.SEND_MESSAGE not in guest_perms


class TestDefaultPermissions:
    """Test default role permissions"""

    def test_owner_permissions(self):
        """Test owner has all permissions"""
        manager = RoomPermissionManager(use_casbin=False)
        owner_perms = manager.get_role_permissions(RoomRole.OWNER)
        assert RoomPermission.DELETE_ROOM in owner_perms
        assert RoomPermission.MANAGE_PERMISSIONS in owner_perms
        assert RoomPermission.SEND_MESSAGE in owner_perms

    def test_admin_permissions(self):
        """Test admin lacks only delete room permission"""
        manager = RoomPermissionManager(use_casbin=False)
        admin_perms = manager.get_role_permissions(RoomRole.ADMIN)
        assert RoomPermission.DELETE_ROOM not in admin_perms
        assert RoomPermission.MANAGE_PERMISSIONS in admin_perms
        assert RoomPermission.SEND_MESSAGE in admin_perms

    def test_moderator_permissions(self):
        """Test moderator permissions"""
        manager = RoomPermissionManager(use_casbin=False)
        mod_perms = manager.get_role_permissions(RoomRole.MODERATOR)
        assert RoomPermission.SEND_MESSAGE in mod_perms
        assert RoomPermission.KICK_MEMBER in mod_perms
        assert RoomPermission.MANAGE_ROOM_INFO not in mod_perms
        assert RoomPermission.DELETE_ROOM not in mod_perms

    def test_member_permissions(self):
        """Test member permissions"""
        manager = RoomPermissionManager(use_casbin=False)
        member_perms = manager.get_role_permissions(RoomRole.MEMBER)
        assert RoomPermission.SEND_MESSAGE in member_perms
        assert RoomPermission.MENTION_ALL in member_perms
        assert RoomPermission.KICK_MEMBER not in member_perms
        assert RoomPermission.DELETE_ROOM not in member_perms

    def test_guest_permissions(self):
        """Test guest permissions"""
        manager = RoomPermissionManager(use_casbin=False)
        guest_perms = manager.get_role_permissions(RoomRole.GUEST)
        assert RoomPermission.VIEW in guest_perms
        assert RoomPermission.LIST_MEMBERS in guest_perms
        assert RoomPermission.SEND_MESSAGE not in guest_perms


class TestPermissionChecking:
    """Test permission checking"""

    def test_check_owner_permission(self):
        """Test checking owner permission"""
        manager = RoomPermissionManager(use_casbin=False)
        result = manager.check_permission(
            "user_1", "room_1", RoomPermission.DELETE_ROOM, RoomRole.OWNER
        )
        assert result is True

    def test_check_guest_denied_permission(self):
        """Test guest denied permission"""
        manager = RoomPermissionManager(use_casbin=False)
        result = manager.check_permission(
            "user_2", "room_1", RoomPermission.SEND_MESSAGE, RoomRole.GUEST
        )
        assert result is False

    def test_check_member_send_message(self):
        """Test member can send message"""
        manager = RoomPermissionManager(use_casbin=False)
        result = manager.check_permission(
            "user_3", "room_1", RoomPermission.SEND_MESSAGE, RoomRole.MEMBER
        )
        assert result is True

    def test_check_member_cannot_delete_room(self):
        """Test member cannot delete room"""
        manager = RoomPermissionManager(use_casbin=False)
        result = manager.check_permission(
            "user_3", "room_1", RoomPermission.DELETE_ROOM, RoomRole.MEMBER
        )
        assert result is False

    def test_check_moderator_can_kick(self):
        """Test moderator can kick member"""
        manager = RoomPermissionManager(use_casbin=False)
        result = manager.check_permission(
            "user_4", "room_1", RoomPermission.KICK_MEMBER, RoomRole.MODERATOR
        )
        assert result is True


class TestPermissionCache:
    """Test permission caching"""

    def test_cache_stores_result(self):
        """Test cache stores permission result"""
        manager = RoomPermissionManager(use_casbin=False)
        # First check populates cache
        manager.check_permission(
            "user_1", "room_1", RoomPermission.SEND_MESSAGE, RoomRole.MEMBER
        )
        cache_key = "user_1:room_1:send_message"
        assert cache_key in manager.permission_cache

    def test_cache_returns_cached_result(self):
        """Test cache returns same result"""
        manager = RoomPermissionManager(use_casbin=False)
        result1 = manager.check_permission(
            "user_1", "room_1", RoomPermission.SEND_MESSAGE, RoomRole.MEMBER
        )
        result2 = manager.check_permission(
            "user_1", "room_1", RoomPermission.SEND_MESSAGE, RoomRole.MEMBER
        )
        assert result1 == result2

    def test_cache_cleared_on_permission_change(self):
        """Test cache cleared when permissions change"""
        manager = RoomPermissionManager(use_casbin=False)
        manager.check_permission(
            "user_1", "room_1", RoomPermission.SEND_MESSAGE, RoomRole.MEMBER
        )
        assert len(manager.permission_cache) > 0

        # Change permissions
        manager.add_role_permission(RoomRole.GUEST, RoomPermission.SEND_MESSAGE)
        assert len(manager.permission_cache) == 0


class TestRolePermissionManagement:
    """Test managing role permissions"""

    def test_add_permission_to_role(self):
        """Test adding permission to role"""
        manager = RoomPermissionManager(use_casbin=False)
        guest_perms_before = len(manager.get_role_permissions(RoomRole.GUEST))
        manager.add_role_permission(RoomRole.GUEST, RoomPermission.SEND_MESSAGE)
        guest_perms_after = len(manager.get_role_permissions(RoomRole.GUEST))
        assert guest_perms_after == guest_perms_before + 1

    def test_remove_permission_from_role(self):
        """Test removing permission from role"""
        manager = RoomPermissionManager(use_casbin=False)
        manager.remove_role_permission(RoomRole.MEMBER, RoomPermission.SEND_MESSAGE)
        member_perms = manager.get_role_permissions(RoomRole.MEMBER)
        assert RoomPermission.SEND_MESSAGE not in member_perms

    def test_add_duplicate_permission(self):
        """Test adding duplicate permission"""
        manager = RoomPermissionManager(use_casbin=False)
        perms_before = len(manager.get_role_permissions(RoomRole.MEMBER))
        manager.add_role_permission(RoomRole.MEMBER, RoomPermission.SEND_MESSAGE)
        perms_after = len(manager.get_role_permissions(RoomRole.MEMBER))
        # Set prevents duplicates
        assert perms_after == perms_before

    def test_get_role_permissions_copy(self):
        """Test get role permissions returns copy"""
        manager = RoomPermissionManager(use_casbin=False)
        perms1 = manager.get_role_permissions(RoomRole.MEMBER)
        perms2 = manager.get_role_permissions(RoomRole.MEMBER)
        # Should be equal but different objects
        assert perms1 == perms2
        perms1.add(RoomPermission.DELETE_ROOM)
        assert RoomPermission.DELETE_ROOM not in perms2


class TestAccessControl:
    """Test access control"""

    def test_can_join_room_member(self):
        """Test member can join room"""
        manager = RoomPermissionManager(use_casbin=False)
        control = RoomAccessControl(manager)
        result = control.can_join_room("user_1", "room_1", RoomRole.MEMBER)
        assert result is True

    def test_can_join_room_guest(self):
        """Test guest cannot join room"""
        manager = RoomPermissionManager(use_casbin=False)
        control = RoomAccessControl(manager)
        result = control.can_join_room("user_2", "room_1", RoomRole.GUEST)
        assert result is False

    def test_can_send_message_member(self):
        """Test member can send message"""
        manager = RoomPermissionManager(use_casbin=False)
        control = RoomAccessControl(manager)
        result = control.can_send_message("user_1", "room_1", RoomRole.MEMBER)
        assert result is True

    def test_can_send_message_guest(self):
        """Test guest cannot send message"""
        manager = RoomPermissionManager(use_casbin=False)
        control = RoomAccessControl(manager)
        result = control.can_send_message("user_2", "room_1", RoomRole.GUEST)
        assert result is False

    def test_can_delete_own_message(self):
        """Test user can delete own message"""
        manager = RoomPermissionManager(use_casbin=False)
        control = RoomAccessControl(manager)
        result = control.can_delete_message(
            "user_1", "room_1", "user_1", RoomRole.GUEST
        )
        assert result is True

    def test_can_delete_others_message(self):
        """Test member cannot delete others' message"""
        manager = RoomPermissionManager(use_casbin=False)
        control = RoomAccessControl(manager)
        result = control.can_delete_message(
            "user_1", "room_1", "user_2", RoomRole.MEMBER
        )
        assert result is False

    def test_moderator_can_delete_message(self):
        """Test moderator can delete message"""
        manager = RoomPermissionManager(use_casbin=False)
        control = RoomAccessControl(manager)
        result = control.can_delete_message(
            "user_1", "room_1", "user_2", RoomRole.MODERATOR
        )
        assert result is True

    def test_cannot_kick_self(self):
        """Test user cannot kick themselves"""
        manager = RoomPermissionManager(use_casbin=False)
        control = RoomAccessControl(manager)
        result = control.can_kick_member(
            "user_1", "room_1", "user_1", RoomRole.MODERATOR
        )
        assert result is False

    def test_moderator_can_kick(self):
        """Test moderator can kick member"""
        manager = RoomPermissionManager(use_casbin=False)
        control = RoomAccessControl(manager)
        result = control.can_kick_member(
            "user_1", "room_1", "user_2", RoomRole.MODERATOR
        )
        assert result is True

    def test_member_cannot_kick(self):
        """Test member cannot kick"""
        manager = RoomPermissionManager(use_casbin=False)
        control = RoomAccessControl(manager)
        result = control.can_kick_member("user_1", "room_1", "user_2", RoomRole.MEMBER)
        assert result is False

    def test_can_change_role_admin(self):
        """Test admin can change role"""
        manager = RoomPermissionManager(use_casbin=False)
        control = RoomAccessControl(manager)
        result = control.can_change_role("user_1", "room_1", RoomRole.ADMIN)
        assert result is True

    def test_cannot_change_role_member(self):
        """Test member cannot change role"""
        manager = RoomPermissionManager(use_casbin=False)
        control = RoomAccessControl(manager)
        result = control.can_change_role("user_1", "room_1", RoomRole.MEMBER)
        assert result is False

    def test_owner_can_delete_room(self):
        """Test owner can delete room"""
        manager = RoomPermissionManager(use_casbin=False)
        control = RoomAccessControl(manager)
        result = control.can_delete_room("user_1", "room_1", RoomRole.OWNER)
        assert result is True

    def test_admin_cannot_delete_room(self):
        """Test admin cannot delete room"""
        manager = RoomPermissionManager(use_casbin=False)
        control = RoomAccessControl(manager)
        result = control.can_delete_room("user_1", "room_1", RoomRole.ADMIN)
        assert result is False


class TestAccessLogging:
    """Test access logging"""

    def test_logs_access_attempt(self):
        """Test logging access attempt"""
        manager = RoomPermissionManager(use_casbin=False)
        control = RoomAccessControl(manager)
        control.can_join_room("user_1", "room_1", RoomRole.MEMBER)
        assert len(control.access_log) == 1

    def test_logs_action_details(self):
        """Test log contains action details"""
        manager = RoomPermissionManager(use_casbin=False)
        control = RoomAccessControl(manager)
        control.can_join_room("user_1", "room_1", RoomRole.MEMBER)
        log_entry = control.access_log[0]
        assert log_entry["action"] == "join"
        assert log_entry["user_id"] == "user_1"
        assert log_entry["room_id"] == "room_1"
        assert log_entry["success"] is True

    def test_logs_failed_access(self):
        """Test logging failed access"""
        manager = RoomPermissionManager(use_casbin=False)
        control = RoomAccessControl(manager)
        control.can_join_room("user_2", "room_1", RoomRole.GUEST)
        log_entry = control.access_log[0]
        assert log_entry["success"] is False

    def test_get_access_log_limit(self):
        """Test get access log with limit"""
        manager = RoomPermissionManager(use_casbin=False)
        control = RoomAccessControl(manager)
        for i in range(150):
            control.can_join_room(f"user_{i}", "room_1", RoomRole.MEMBER)

        logs = control.get_access_log(limit=50)
        assert len(logs) == 50


class TestPermissionManagerSingleton:
    """Test permission manager singleton"""

    def test_get_permission_manager(self):
        """Test getting permission manager"""
        reset_permission_manager()
        manager1 = get_permission_manager()
        manager2 = get_permission_manager()
        assert manager1 is manager2

    def test_reset_permission_manager(self):
        """Test resetting permission manager"""
        reset_permission_manager()
        manager1 = get_permission_manager()
        reset_permission_manager()
        manager2 = get_permission_manager()
        assert manager1 is not manager2


class TestAccessControlSingleton:
    """Test access control singleton"""

    def test_get_access_control(self):
        """Test getting access control"""
        reset_access_control()
        reset_permission_manager()
        control1 = get_access_control()
        control2 = get_access_control()
        assert control1 is control2

    def test_reset_access_control(self):
        """Test resetting access control"""
        reset_access_control()
        reset_permission_manager()
        control1 = get_access_control()
        reset_access_control()
        reset_permission_manager()
        control2 = get_access_control()
        assert control1 is not control2


class TestPermissionManagerStats:
    """Test permission manager statistics"""

    def test_get_stats(self):
        """Test getting statistics"""
        manager = RoomPermissionManager(use_casbin=False)
        stats = manager.get_stats()
        assert "use_casbin" in stats
        assert "cache_size" in stats
        assert "roles_defined" in stats
        assert stats["roles_defined"] == 5

    def test_stats_cache_size(self):
        """Test cache size in stats"""
        manager = RoomPermissionManager(use_casbin=False)
        manager.check_permission(
            "user_1", "room_1", RoomPermission.SEND_MESSAGE, RoomRole.MEMBER
        )
        stats = manager.get_stats()
        assert stats["cache_size"] == 1


class TestAccessControlStats:
    """Test access control statistics"""

    def test_access_control_stats(self):
        """Test access control statistics"""
        manager = RoomPermissionManager(use_casbin=False)
        control = RoomAccessControl(manager)
        control.can_join_room("user_1", "room_1", RoomRole.MEMBER)

        stats = control.get_stats()
        assert "total_access_logs" in stats
        assert stats["total_access_logs"] == 1

    def test_stats_include_permission_manager(self):
        """Test stats include permission manager stats"""
        manager = RoomPermissionManager(use_casbin=False)
        control = RoomAccessControl(manager)
        stats = control.get_stats()
        assert "permission_manager_stats" in stats


class TestIntegrationScenarios:
    """Test integration scenarios"""

    def test_permission_manager_and_access_control_integration(self):
        """Test permission manager works with access control"""
        manager = RoomPermissionManager(use_casbin=False)
        control = RoomAccessControl(manager)

        # Both should be initialized
        assert manager is not None
        assert control is not None
        assert control.permission_manager is manager

    def test_multiple_rooms_with_different_users(self):
        """Test handling multiple rooms with different users"""
        manager = RoomPermissionManager(use_casbin=False)
        control = RoomAccessControl(manager)

        # User 1 as member in room 1
        assert control.can_send_message("user_1", "room_1", RoomRole.MEMBER) is True

        # User 2 as guest in room 2
        assert control.can_send_message("user_2", "room_2", RoomRole.GUEST) is False

        # User 3 as moderator in room 3
        assert (
            control.can_kick_member("user_3", "room_3", "user_4", RoomRole.MODERATOR)
            is True
        )

    def test_permission_changes_affect_access_control(self):
        """Test that permission changes affect access control checks"""
        manager = RoomPermissionManager(use_casbin=False)
        control = RoomAccessControl(manager)

        # Initially guest cannot send message
        assert control.can_send_message("user_1", "room_1", RoomRole.GUEST) is False

        # Grant permission to guest
        manager.add_role_permission(RoomRole.GUEST, RoomPermission.SEND_MESSAGE)

        # Now guest can send message
        assert control.can_send_message("user_1", "room_1", RoomRole.GUEST) is True

    def test_access_control_logging_integration(self):
        """Test access control logging"""
        manager = RoomPermissionManager(use_casbin=False)
        control = RoomAccessControl(manager)

        # Perform various access checks
        control.can_join_room("user_1", "room_1", RoomRole.MEMBER)
        control.can_send_message("user_2", "room_1", RoomRole.GUEST)
        control.can_kick_member("user_3", "room_1", "user_4", RoomRole.MODERATOR)

        # Verify logs were recorded
        assert len(control.access_log) == 3
        assert control.access_log[0]["user_id"] == "user_1"
        assert control.access_log[1]["user_id"] == "user_2"
        assert control.access_log[2]["user_id"] == "user_3"

    def test_cross_room_permission_isolation(self):
        """Test that permissions are isolated per role, not per room"""
        manager = RoomPermissionManager(use_casbin=False)
        control = RoomAccessControl(manager)

        # Same role has same permissions in different rooms
        user_1_room_1 = control.can_send_message("user_1", "room_1", RoomRole.MEMBER)
        user_1_room_2 = control.can_send_message("user_1", "room_2", RoomRole.MEMBER)

        # Should be the same
        assert user_1_room_1 == user_1_room_2

    def test_statistics_collection(self):
        """Test that statistics are collected properly"""
        manager = RoomPermissionManager(use_casbin=False)
        control = RoomAccessControl(manager)

        # Perform some checks
        control.can_join_room("user_1", "room_1", RoomRole.MEMBER)
        control.can_send_message("user_2", "room_1", RoomRole.GUEST)

        # Check stats
        stats = control.get_stats()
        assert stats["total_access_logs"] == 2
        assert "permission_manager_stats" in stats
