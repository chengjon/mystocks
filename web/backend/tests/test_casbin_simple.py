"""
Casbin 简化版集成测试 (单用户系统)

Simplified Casbin Integration Tests for Single-User System

Task 10: Casbin权限集成

Author: Claude Code
Date: 2025-11-07
"""

import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from app.core.casbin_manager import (
    get_casbin_manager,
    reset_casbin_manager,
)
from app.core.casbin_middleware import (
    require_permission,
    check_permission,
    get_current_role,
)


class TestSimplifiedPermissions:
    """Test simplified permission system for single-user"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup and teardown for each test"""
        reset_casbin_manager()
        manager = get_casbin_manager()

        # 设置默认权限
        manager.add_role("user", "read", "indicator")
        manager.add_role("user", "read", "dashboard")

        manager.add_role("admin", "read", "indicator")
        manager.add_role("admin", "write", "indicator")
        manager.add_role("admin", "delete", "indicator")
        manager.add_role("admin", "write", "dashboard")

        yield

        reset_casbin_manager()

    def test_get_current_role(self):
        """Test getting current role"""
        role = get_current_role("user")
        assert role == "user"

        role = get_current_role("admin")
        assert role == "admin"

    def test_check_permission_direct(self):
        """Test direct permission checking"""
        # User can read indicators
        assert check_permission("indicator", "read", "user") is True

        # User cannot write indicators
        assert check_permission("indicator", "write", "user") is False

        # Admin can write indicators
        assert check_permission("indicator", "write", "admin") is True

    def test_require_permission_dependency_success(self):
        """Test require_permission dependency - success case"""
        app = FastAPI()

        @app.get("/indicators")
        async def get_indicators(
            _=Depends(require_permission("indicator", "read", "user")),
        ):
            return {"indicators": []}

        client = TestClient(app)
        response = client.get("/indicators")
        assert response.status_code == 200
        assert response.json() == {"indicators": []}

    def test_require_permission_dependency_denied(self):
        """Test require_permission dependency - access denied"""
        app = FastAPI()

        @app.post("/indicators")
        async def create_indicator(
            _=Depends(require_permission("indicator", "write", "user")),
        ):
            return {"id": "ind_1"}

        client = TestClient(app)
        response = client.post("/indicators")
        assert response.status_code == 403
        assert "Permission denied" in response.json()["detail"]

    def test_admin_vs_user_permissions(self):
        """Test different permissions for admin vs user"""
        assert check_permission("indicator", "read", "user") is True
        assert check_permission("indicator", "write", "user") is False
        assert check_permission("indicator", "delete", "user") is False

        assert check_permission("indicator", "read", "admin") is True
        assert check_permission("indicator", "write", "admin") is True
        assert check_permission("indicator", "delete", "admin") is True

    def test_multiple_resources(self):
        """Test permissions across multiple resources"""
        assert check_permission("indicator", "read", "user") is True
        assert check_permission("dashboard", "read", "user") is True
        assert check_permission("alert", "read", "user") is False

    def test_route_with_direct_check(self):
        """Test route with direct permission checking"""
        app = FastAPI()

        @app.get("/indicators")
        async def get_indicators():
            if not check_permission("indicator", "read", "user"):
                from fastapi import HTTPException

                raise HTTPException(status_code=403, detail="Permission denied")
            return {"indicators": []}

        @app.post("/indicators")
        async def create_indicator():
            if not check_permission("indicator", "write", "admin"):
                from fastapi import HTTPException

                raise HTTPException(status_code=403, detail="Permission denied")
            return {"id": "ind_1"}

        client = TestClient(app)

        # User can read
        response = client.get("/indicators")
        assert response.status_code == 200

        # Admin can write
        response = client.post("/indicators")
        assert response.status_code == 200

    def test_dynamic_permission_changes(self):
        """Test dynamic permission updates"""
        # Initially user cannot delete
        assert check_permission("indicator", "delete", "user") is False

        # Grant delete permission
        manager = get_casbin_manager()
        manager.add_role("user", "delete", "indicator")

        # Now user can delete
        assert check_permission("indicator", "delete", "user") is True

        # Revoke delete permission
        manager.remove_role("user", "delete", "indicator")

        # User cannot delete again
        assert check_permission("indicator", "delete", "user") is False

    def test_batch_permissions(self):
        """Test batch permission checking"""
        permissions = [
            ("indicator", "read"),
            ("dashboard", "read"),
            ("alert", "read"),
        ]

        # Check all permissions for user
        results = [check_permission(resource, action, "user") for resource, action in permissions]

        assert results == [True, True, False]  # indicator, dashboard OK, alert denied

    def test_permission_statistics(self):
        """Test permission enforcement statistics"""
        manager = get_casbin_manager()

        # Make several permission checks
        check_permission("indicator", "read", "user")
        check_permission("indicator", "write", "user")
        check_permission("indicator", "delete", "admin")

        stats = manager.get_stats()
        assert stats["total_enforce_calls"] == 3
        assert stats["total_allow_decisions"] == 2  # read (user) + delete (admin)
        assert stats["total_deny_decisions"] == 1  # write (user denied)


class TestRoleBasedScenarios:
    """Test realistic role-based scenarios"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup role scenarios"""
        reset_casbin_manager()
        manager = get_casbin_manager()

        # Guest role - minimal permissions
        manager.add_role("guest", "read", "indicator")

        # User role - standard permissions
        manager.add_role("user", "read", "indicator")
        manager.add_role("user", "read", "dashboard")
        manager.add_role("user", "write", "alert")

        # Admin role - full permissions
        manager.add_role("admin", "read", "indicator")
        manager.add_role("admin", "write", "indicator")
        manager.add_role("admin", "delete", "indicator")
        manager.add_role("admin", "read", "dashboard")
        manager.add_role("admin", "write", "dashboard")

        yield
        reset_casbin_manager()

    def test_guest_scenario(self):
        """Test guest user scenario"""
        assert check_permission("indicator", "read", "guest") is True
        assert check_permission("indicator", "write", "guest") is False
        assert check_permission("dashboard", "read", "guest") is False

    def test_user_scenario(self):
        """Test regular user scenario"""
        assert check_permission("indicator", "read", "user") is True
        assert check_permission("indicator", "write", "user") is False
        assert check_permission("dashboard", "read", "user") is True
        assert check_permission("alert", "write", "user") is True

    def test_admin_scenario(self):
        """Test admin user scenario"""
        assert check_permission("indicator", "read", "admin") is True
        assert check_permission("indicator", "write", "admin") is True
        assert check_permission("indicator", "delete", "admin") is True
        assert check_permission("dashboard", "write", "admin") is True

    def test_role_progression(self):
        """Test accessing features based on role progression"""
        features = [
            ("indicator", "read"),
            ("indicator", "write"),
            ("indicator", "delete"),
            ("dashboard", "write"),
        ]

        # Check what each role can do
        guest_access = [check_permission(resource, action, "guest") for resource, action in features]
        user_access = [check_permission(resource, action, "user") for resource, action in features]
        admin_access = [check_permission(resource, action, "admin") for resource, action in features]

        assert guest_access == [True, False, False, False]
        assert user_access == [True, False, False, False]
        assert admin_access == [True, True, True, True]


class TestPermissionWithFastAPI:
    """Test permission integration with FastAPI routes"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup routes test"""
        reset_casbin_manager()
        manager = get_casbin_manager()

        manager.add_role("analyst", "read", "indicator")
        manager.add_role("analyst", "read", "dashboard")
        manager.add_role("analyst", "write", "alert")

        manager.add_role("trader", "read", "indicator")
        manager.add_role("trader", "write", "indicator")
        manager.add_role("trader", "execute", "trade")

        yield
        reset_casbin_manager()

    def test_analyst_routes(self):
        """Test analyst role routes"""
        app = FastAPI()

        @app.get("/indicators")
        async def get_indicators(
            _=Depends(require_permission("indicator", "read", "analyst")),
        ):
            return {"indicators": []}

        @app.post("/alerts")
        async def create_alert(
            _=Depends(require_permission("alert", "write", "analyst")),
        ):
            return {"alert_id": "alert_1"}

        @app.post("/indicators")
        async def create_indicator(
            _=Depends(require_permission("indicator", "write", "analyst")),
        ):
            return {"indicator_id": "ind_1"}

        client = TestClient(app)

        # Analyst can read indicators
        assert client.get("/indicators").status_code == 200

        # Analyst can write alerts
        assert client.post("/alerts").status_code == 200

        # Analyst cannot write indicators
        assert client.post("/indicators").status_code == 403

    def test_trader_routes(self):
        """Test trader role routes"""
        app = FastAPI()

        @app.post("/trades")
        async def execute_trade(
            _=Depends(require_permission("trade", "execute", "trader")),
        ):
            return {"trade_id": "trade_1"}

        @app.put("/indicators/{id}")
        async def update_indicator(
            id: str,
            _=Depends(require_permission("indicator", "write", "trader")),
        ):
            return {"indicator_id": id}

        client = TestClient(app)

        # Trader can execute trades
        assert client.post("/trades").status_code == 200

        # Trader can update indicators
        assert client.put("/indicators/ind_1").status_code == 200
