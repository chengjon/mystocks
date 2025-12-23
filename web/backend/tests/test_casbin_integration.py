"""
Casbin权限管理集成测试

Tests for Casbin RBAC Integration

Task 10: Casbin权限集成

Author: Claude Code
Date: 2025-11-07
"""

from app.core.casbin_manager import (
    CasbinManager,
    RoleDefinition,
    PermissionRule,
    get_casbin_manager,
    reset_casbin_manager,
)


class TestCasbinManagerInitialization:
    """Test CasbinManager initialization"""

    def test_manager_creation(self):
        """Test creating a CasbinManager instance"""
        manager = CasbinManager()
        assert manager is not None
        assert manager.enforcer is not None

    def test_manager_singleton(self):
        """Test singleton pattern"""
        reset_casbin_manager()
        manager1 = get_casbin_manager()
        manager2 = get_casbin_manager()
        assert manager1 is manager2

    def test_manager_reset(self):
        """Test resetting singleton"""
        reset_casbin_manager()
        manager1 = get_casbin_manager()
        reset_casbin_manager()
        manager2 = get_casbin_manager()
        assert manager1 is not manager2


class TestRoleDefinition:
    """Test role definitions"""

    def test_role_definition_creation(self):
        """Test creating role definition"""
        role = RoleDefinition(
            name="admin",
            description="Administrator",
            permissions=["read", "write", "delete"],
        )
        assert role.name == "admin"
        assert role.description == "Administrator"
        assert "read" in role.permissions

    def test_role_definition_to_dict(self):
        """Test role serialization"""
        role = RoleDefinition(
            name="user",
            description="Regular user",
            permissions=["read"],
        )
        role_dict = role.to_dict()
        assert role_dict["name"] == "user"
        assert role_dict["description"] == "Regular user"
        assert "read" in role_dict["permissions"]


class TestPermissionRule:
    """Test permission rules"""

    def test_permission_rule_creation(self):
        """Test creating permission rule"""
        rule = PermissionRule(
            subject="user_1",
            object="indicator",
            action="read",
        )
        assert rule.subject == "user_1"
        assert rule.object == "indicator"
        assert rule.action == "read"

    def test_permission_rule_to_list(self):
        """Test permission rule as list"""
        rule = PermissionRule(
            subject="admin_role",
            object="dashboard",
            action="write",
        )
        rule_list = rule.to_list()
        assert rule_list == ["admin_role", "dashboard", "write"]


class TestBasicAccessControl:
    """Test basic access control"""

    def test_admin_can_read(self):
        """Test admin can read resources"""
        reset_casbin_manager()
        manager = get_casbin_manager()

        # Add admin role permissions
        manager.add_role("admin", "read", "indicator")

        # Check permission
        result = manager.enforce("admin", "indicator", "read")
        assert result is True

    def test_user_can_read(self):
        """Test user can read resources"""
        reset_casbin_manager()
        manager = get_casbin_manager()

        manager.add_role("user", "read", "indicator")

        result = manager.enforce("user", "indicator", "read")
        assert result is True

    def test_guest_cannot_write(self):
        """Test guest cannot write"""
        reset_casbin_manager()
        manager = get_casbin_manager()

        manager.add_role("guest", "read", "indicator")

        result = manager.enforce("guest", "indicator", "write")
        assert result is False

    def test_user_cannot_delete(self):
        """Test regular user cannot delete"""
        reset_casbin_manager()
        manager = get_casbin_manager()

        manager.add_role("user", "read", "indicator")
        manager.add_role("user", "write", "indicator")

        result = manager.enforce("user", "indicator", "delete")
        assert result is False


class TestRoleHierarchy:
    """Test role hierarchy and inheritance"""

    def test_role_inheritance(self):
        """Test role inheritance"""
        reset_casbin_manager()
        manager = get_casbin_manager()

        # Define role hierarchy: admin > moderator > user > guest
        manager.add_role_inheritance("moderator", "user")
        manager.add_role("user", "read", "indicator")

        # Moderator should inherit user permissions
        result = manager.enforce("moderator", "indicator", "read")
        assert result is True

    def test_multi_level_inheritance(self):
        """Test multi-level role inheritance"""
        reset_casbin_manager()
        manager = get_casbin_manager()

        manager.add_role_inheritance("admin", "moderator")
        manager.add_role_inheritance("moderator", "user")
        manager.add_role("user", "read", "indicator")

        # Admin should inherit through moderator -> user
        result = manager.enforce("admin", "indicator", "read")
        assert result is True


class TestResourceBasedControl:
    """Test resource-level access control"""

    def test_user_owns_resource(self):
        """Test user owns their own resource"""
        reset_casbin_manager()
        manager = get_casbin_manager()

        # User can read their own data
        manager.add_permission("user_1", "profile", "read", {"owner": "user_1"})

        result = manager.enforce("user_1", "profile", "read")
        assert result is True

    def test_user_cannot_read_others_resource(self):
        """Test user cannot read others' resources"""
        reset_casbin_manager()
        manager = get_casbin_manager()

        # User 1 can read their own data
        manager.add_permission("user_1", "profile", "read", {"owner": "user_1"})

        # But not user 2's data
        result = manager.enforce("user_2", "profile", "read")
        assert result is False


class TestDynamicPermissions:
    """Test dynamic permission management"""

    def test_add_permission(self):
        """Test adding permission dynamically"""
        reset_casbin_manager()
        manager = get_casbin_manager()

        manager.add_role("analyst", "read", "indicator")
        assert manager.enforce("analyst", "indicator", "read") is True

    def test_remove_permission(self):
        """Test removing permission"""
        reset_casbin_manager()
        manager = get_casbin_manager()

        manager.add_role("analyst", "read", "indicator")
        assert manager.enforce("analyst", "indicator", "read") is True

        manager.remove_role("analyst", "read", "indicator")
        assert manager.enforce("analyst", "indicator", "read") is False

    def test_update_permission(self):
        """Test updating permissions"""
        reset_casbin_manager()
        manager = get_casbin_manager()

        manager.add_role("analyst", "read", "indicator")
        manager.add_role("analyst", "write", "indicator")

        assert manager.enforce("analyst", "indicator", "read") is True
        assert manager.enforce("analyst", "indicator", "write") is True
        assert manager.enforce("analyst", "indicator", "delete") is False


class TestMultiResourceControl:
    """Test multi-resource access control"""

    def test_different_permissions_per_resource(self):
        """Test different permissions for different resources"""
        reset_casbin_manager()
        manager = get_casbin_manager()

        # User can read indicators but only write dashboards
        manager.add_role("analyst", "read", "indicator")
        manager.add_role("analyst", "write", "dashboard")

        assert manager.enforce("analyst", "indicator", "read") is True
        assert manager.enforce("analyst", "indicator", "write") is False
        assert manager.enforce("analyst", "dashboard", "write") is True
        assert manager.enforce("analyst", "dashboard", "read") is False

    def test_role_based_resource_access(self):
        """Test role-based resource access"""
        reset_casbin_manager()
        manager = get_casbin_manager()

        # Admin can do everything
        manager.add_role("admin", "read", "indicator")
        manager.add_role("admin", "write", "indicator")
        manager.add_role("admin", "delete", "indicator")

        # User can only read
        manager.add_role("user", "read", "indicator")

        # Verify
        assert manager.enforce("admin", "indicator", "read") is True
        assert manager.enforce("admin", "indicator", "write") is True
        assert manager.enforce("admin", "indicator", "delete") is True

        assert manager.enforce("user", "indicator", "read") is True
        assert manager.enforce("user", "indicator", "write") is False


class TestPolicyManagement:
    """Test policy file management"""

    def test_load_policy_from_file(self):
        """Test loading policy from file"""
        reset_casbin_manager()
        manager = get_casbin_manager()

        # Should have loaded default policies
        assert manager.enforcer is not None
        assert manager.get_policy() is not None

    def test_save_policy_to_file(self):
        """Test saving policy to file"""
        reset_casbin_manager()
        manager = get_casbin_manager()

        manager.add_role("test_role", "read", "test_resource")
        result = manager.save_policy()

        assert result is True

    def test_reload_policy(self):
        """Test reloading policy"""
        reset_casbin_manager()
        manager = get_casbin_manager()

        manager.add_role("analyst", "read", "indicator")
        assert manager.enforce("analyst", "indicator", "read") is True

        # Save policy before reload
        manager.save_policy()

        # Reload should preserve the policy
        manager.reload_policy()
        assert manager.enforce("analyst", "indicator", "read") is True


class TestBatchOperations:
    """Test batch permission operations"""

    def test_batch_add_permissions(self):
        """Test adding multiple permissions at once"""
        reset_casbin_manager()
        manager = get_casbin_manager()

        permissions = [
            PermissionRule("analyst", "indicator", "read"),
            PermissionRule("analyst", "dashboard", "read"),
            PermissionRule("analyst", "alert", "read"),
        ]

        manager.batch_add_permissions(permissions)

        assert manager.enforce("analyst", "indicator", "read") is True
        assert manager.enforce("analyst", "dashboard", "read") is True
        assert manager.enforce("analyst", "alert", "read") is True

    def test_batch_remove_permissions(self):
        """Test removing multiple permissions"""
        reset_casbin_manager()
        manager = get_casbin_manager()

        permissions = [
            PermissionRule("analyst", "indicator", "read"),
            PermissionRule("analyst", "dashboard", "read"),
        ]

        manager.batch_add_permissions(permissions)
        manager.batch_remove_permissions(permissions)

        assert manager.enforce("analyst", "indicator", "read") is False
        assert manager.enforce("analyst", "dashboard", "read") is False


class TestPolicyStats:
    """Test policy statistics"""

    def test_get_policy(self):
        """Test getting policy"""
        reset_casbin_manager()
        manager = get_casbin_manager()

        manager.add_role("analyst", "read", "indicator")
        manager.add_role("admin", "write", "indicator")

        policy = manager.get_policy()
        assert policy is not None
        assert len(policy) >= 2

    def test_get_roles(self):
        """Test getting all roles"""
        reset_casbin_manager()
        manager = get_casbin_manager()

        manager.add_role("analyst", "read", "indicator")
        manager.add_role("admin", "read", "dashboard")

        roles = manager.get_all_roles()
        assert "analyst" in roles or len(roles) >= 2

    def test_get_permissions_for_role(self):
        """Test getting permissions for specific role"""
        reset_casbin_manager()
        manager = get_casbin_manager()

        manager.add_role("analyst", "read", "indicator")
        manager.add_role("analyst", "write", "dashboard")

        perms = manager.get_permissions_for_role("analyst")
        assert len(perms) >= 2

    def test_get_stats(self):
        """Test getting manager statistics"""
        reset_casbin_manager()
        manager = get_casbin_manager()

        manager.add_role("analyst", "read", "indicator")
        manager.add_role("admin", "write", "indicator")

        stats = manager.get_stats()
        assert "total_policies" in stats
        assert "total_roles" in stats
        assert stats["total_policies"] >= 2


class TestIntegrationScenarios:
    """Test realistic integration scenarios"""

    def test_vip_user_scenario(self):
        """Test VIP user scenario"""
        reset_casbin_manager()
        manager = get_casbin_manager()

        # Setup role hierarchy
        manager.add_role("vip", "read", "indicator")
        manager.add_role("vip", "write", "indicator")
        manager.add_role("vip", "read", "dashboard")
        manager.add_role("vip", "write", "dashboard")

        # VIP should have access
        assert manager.enforce("vip", "indicator", "read") is True
        assert manager.enforce("vip", "indicator", "write") is True

    def test_admin_scenario(self):
        """Test admin scenario with full permissions"""
        reset_casbin_manager()
        manager = get_casbin_manager()

        # Admin has all permissions
        manager.add_role("admin", "read", "indicator")
        manager.add_role("admin", "write", "indicator")
        manager.add_role("admin", "delete", "indicator")
        manager.add_role("admin", "read", "user")
        manager.add_role("admin", "write", "user")
        manager.add_role("admin", "delete", "user")

        # Verify all permissions
        assert manager.enforce("admin", "indicator", "read") is True
        assert manager.enforce("admin", "indicator", "write") is True
        assert manager.enforce("admin", "indicator", "delete") is True
        assert manager.enforce("admin", "user", "read") is True
        assert manager.enforce("admin", "user", "write") is True
        assert manager.enforce("admin", "user", "delete") is True

    def test_guest_scenario(self):
        """Test guest user with limited permissions"""
        reset_casbin_manager()
        manager = get_casbin_manager()

        # Guest can only read public resources
        manager.add_role("guest", "read", "indicator")

        assert manager.enforce("guest", "indicator", "read") is True
        assert manager.enforce("guest", "indicator", "write") is False
        assert manager.enforce("guest", "indicator", "delete") is False
