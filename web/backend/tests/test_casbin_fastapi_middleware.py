"""
Casbin FastAPI 中间件集成测试

Tests for Casbin FastAPI Integration Middleware

Task 10: Casbin权限集成

Author: Claude Code
Date: 2025-11-07
"""

import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
import jwt
from datetime import datetime, timedelta

from app.core.casbin_manager import (
    get_casbin_manager,
    reset_casbin_manager,
)
from app.core.casbin_middleware import (
    get_current_user_from_token,
    require_permission,
    require_admin,
    require_vip,
    get_user_id_from_request,
    check_row_level_permission,
)


def create_test_token(user_id: str, role: str = "user") -> str:
    """创建测试JWT token

    Args:
        user_id: 用户ID
        role: 用户角色

    Returns:
        JWT token字符串
    """
    payload = {
        "sub": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    token = jwt.encode(payload, "test-secret", algorithm="HS256")
    return token


class TestCasbinFastAPIIntegration:
    """Test Casbin FastAPI integration"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup and teardown for each test"""
        reset_casbin_manager()
        manager = get_casbin_manager()

        # 设置默认权限
        manager.add_role("admin", "read", "indicator")
        manager.add_role("admin", "write", "indicator")
        manager.add_role("admin", "delete", "indicator")

        manager.add_role("vip", "read", "indicator")
        manager.add_role("vip", "write", "indicator")

        manager.add_role("user", "read", "indicator")

        yield

        reset_casbin_manager()

    def test_get_current_user_from_token(self):
        """Test extracting user from JWT token"""
        app = FastAPI()

        @app.get("/test")
        async def test_endpoint(
            user: dict = Depends(get_current_user_from_token),
        ):
            return user

        client = TestClient(app)

        # Test with valid token
        token = create_test_token("user_123", "admin")
        response = client.get(
            "/test",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "user_123"
        assert data["role"] == "admin"

    def test_get_current_user_missing_token(self):
        """Test missing auth token"""
        app = FastAPI()

        @app.get("/test")
        async def test_endpoint(
            user: dict = Depends(get_current_user_from_token),
        ):
            return user

        client = TestClient(app)

        # Test without token - should return 401 Unauthorized
        response = client.get("/test")
        assert response.status_code == 401

    def test_require_permission_success(self):
        """Test successful permission check"""
        app = FastAPI()

        @app.get("/indicators")
        async def get_indicators(
            user: dict = Depends(get_current_user_from_token),
            _=Depends(require_permission("indicator", "read")),
        ):
            return {"indicators": []}

        client = TestClient(app)

        # Admin can read indicators
        token = create_test_token("user_123", "admin")
        response = client.get(
            "/indicators",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200

    def test_require_permission_denied(self):
        """Test permission denied"""
        app = FastAPI()

        @app.post("/indicators")
        async def create_indicator(
            user: dict = Depends(get_current_user_from_token),
            _=Depends(require_permission("indicator", "write")),
        ):
            return {"id": "ind_1"}

        client = TestClient(app)

        # Regular user cannot write indicators
        token = create_test_token("user_123", "user")
        response = client.post(
            "/indicators",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
        assert "Permission denied" in response.json()["detail"]

    def test_require_admin_success(self):
        """Test admin requirement - success"""
        app = FastAPI()

        @app.delete("/indicators/{id}")
        async def delete_indicator(
            id: str,
            user: dict = Depends(require_admin),
        ):
            return {"deleted": id}

        client = TestClient(app)

        # Admin can delete
        token = create_test_token("admin_123", "admin")
        response = client.delete(
            "/indicators/ind_1",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200

    def test_require_admin_denied(self):
        """Test admin requirement - denied"""
        app = FastAPI()

        @app.delete("/indicators/{id}")
        async def delete_indicator(
            id: str,
            user: dict = Depends(require_admin),
        ):
            return {"deleted": id}

        client = TestClient(app)

        # Regular user cannot delete
        token = create_test_token("user_123", "user")
        response = client.delete(
            "/indicators/ind_1",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
        assert "Admin access required" in response.json()["detail"]

    def test_require_vip_success(self):
        """Test VIP requirement - success"""
        app = FastAPI()

        @app.post("/indicators")
        async def create_indicator(
            user: dict = Depends(require_vip),
        ):
            return {"id": "ind_1"}

        client = TestClient(app)

        # VIP can create
        token = create_test_token("vip_123", "vip")
        response = client.post(
            "/indicators",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200

    def test_require_vip_denied(self):
        """Test VIP requirement - denied"""
        app = FastAPI()

        @app.post("/indicators")
        async def create_indicator(
            user: dict = Depends(require_vip),
        ):
            return {"id": "ind_1"}

        client = TestClient(app)

        # Regular user cannot create (needs VIP)
        token = create_test_token("user_123", "user")
        response = client.post(
            "/indicators",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
        assert "VIP access required" in response.json()["detail"]

    def test_get_user_id_from_request(self):
        """Test extracting user ID from request"""
        app = FastAPI()

        @app.get("/user-info")
        async def get_user_info(
            user_id: str = Depends(get_user_id_from_request),
        ):
            return {"user_id": user_id}

        client = TestClient(app)

        token = create_test_token("user_123", "user")
        response = client.get(
            "/user-info",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert response.json()["user_id"] == "user_123"

    def test_check_row_level_permission_owner(self):
        """Test row-level permission - data owner"""
        # User can access their own data
        can_access = check_row_level_permission(
            user_id="user_123",
            resource_owner_id="user_123",
        )
        assert can_access is True

    def test_check_row_level_permission_not_owner(self):
        """Test row-level permission - not data owner"""
        # User cannot access others' data when allow_admin=False
        can_access = check_row_level_permission(
            user_id="user_123",
            resource_owner_id="user_456",
            allow_admin=False,
        )
        assert can_access is False

    def test_check_row_level_permission_admin(self):
        """Test row-level permission - admin override"""
        reset_casbin_manager()
        manager = get_casbin_manager()
        manager.add_role("admin", "read", "data")

        # Admin can access all data
        can_access = check_row_level_permission(
            user_id="admin_123",
            resource_owner_id="user_456",
            allow_admin=True,
        )
        assert can_access is True


class TestMultiResourcePermissions:
    """Test multiple resources with different permissions"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for multi-resource tests"""
        reset_casbin_manager()
        manager = get_casbin_manager()

        # Setup complex permissions
        manager.add_role("analyst", "read", "indicator")
        manager.add_role("analyst", "read", "dashboard")
        manager.add_role("analyst", "write", "alert")

        manager.add_role("trader", "read", "indicator")
        manager.add_role("trader", "write", "indicator")
        manager.add_role("trader", "execute", "trade")

        yield
        reset_casbin_manager()

    def test_analyst_permissions(self):
        """Test analyst role permissions"""
        app = FastAPI()

        @app.get("/indicators")
        async def get_indicators(
            user: dict = Depends(get_current_user_from_token),
            _=Depends(require_permission("indicator", "read")),
        ):
            return {"indicators": []}

        @app.post("/alerts")
        async def create_alert(
            user: dict = Depends(get_current_user_from_token),
            _=Depends(require_permission("alert", "write")),
        ):
            return {"alert_id": "alert_1"}

        @app.post("/indicators")
        async def create_indicator(
            user: dict = Depends(get_current_user_from_token),
            _=Depends(require_permission("indicator", "write")),
        ):
            return {"indicator_id": "ind_1"}

        client = TestClient(app)
        token = create_test_token("analyst_1", "analyst")

        # Analyst can read indicators
        response = client.get(
            "/indicators",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

        # Analyst can create alerts
        response = client.post(
            "/alerts",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

        # Analyst cannot write indicators
        response = client.post(
            "/indicators",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403

    def test_trader_permissions(self):
        """Test trader role permissions"""
        app = FastAPI()

        @app.post("/trades")
        async def execute_trade(
            user: dict = Depends(get_current_user_from_token),
            _=Depends(require_permission("trade", "execute")),
        ):
            return {"trade_id": "trade_1"}

        @app.put("/indicators/{id}")
        async def update_indicator(
            id: str,
            user: dict = Depends(get_current_user_from_token),
            _=Depends(require_permission("indicator", "write")),
        ):
            return {"indicator_id": id}

        client = TestClient(app)
        token = create_test_token("trader_1", "trader")

        # Trader can execute trades
        response = client.post(
            "/trades",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

        # Trader can write indicators
        response = client.put(
            "/indicators/ind_1",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200


class TestPermissionWithQueryFilters:
    """Test permissions with query parameter filtering"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for query filter tests"""
        reset_casbin_manager()
        manager = get_casbin_manager()

        manager.add_role("user", "read", "profile")
        manager.add_role("admin", "read", "profile")

        yield
        reset_casbin_manager()

    def test_profile_access_with_permission(self):
        """Test accessing profile with permission"""
        app = FastAPI()

        @app.get("/users/{user_id}")
        async def get_user_profile(
            user_id: str,
            current_user: dict = Depends(get_current_user_from_token),
            _=Depends(require_permission("profile", "read")),
        ):
            return {"user_id": user_id, "profile": "data"}

        client = TestClient(app)

        # User can access profiles if they have read permission
        token = create_test_token("user_1", "user")
        response = client.get(
            "/users/user_1",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

        # Admin can also access profiles
        admin_token = create_test_token("admin_1", "admin")
        response = client.get(
            "/users/user_2",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200


class TestDynamicRoleCreation:
    """Test dynamic role and permission creation"""

    def test_dynamic_role_permission_grant(self):
        """Test dynamically granting permissions"""
        reset_casbin_manager()
        manager = get_casbin_manager()

        # Initially no permissions
        assert manager.enforce("analyst", "report", "generate") is False

        # Grant permission dynamically
        manager.add_role("analyst", "generate", "report")

        # Now permission is granted
        assert manager.enforce("analyst", "report", "generate") is True

    def test_dynamic_role_permission_revoke(self):
        """Test dynamically revoking permissions"""
        reset_casbin_manager()
        manager = get_casbin_manager()

        # Add permission
        manager.add_role("analyst", "generate", "report")
        assert manager.enforce("analyst", "report", "generate") is True

        # Revoke permission
        manager.remove_role("analyst", "generate", "report")

        # Permission removed
        assert manager.enforce("analyst", "report", "generate") is False

    def test_batch_permission_grant(self):
        """Test batch permission granting"""
        from app.core.casbin_manager import PermissionRule

        reset_casbin_manager()
        manager = get_casbin_manager()

        # PermissionRule fields are (subject, object, action)
        permissions = [
            PermissionRule("data_scientist", "model", "generate"),
            PermissionRule("data_scientist", "model", "deploy"),
            PermissionRule("data_scientist", "dataset", "read"),
        ]

        count = manager.batch_add_permissions(permissions)

        assert count == 3
        assert manager.enforce("data_scientist", "model", "generate") is True
        assert manager.enforce("data_scientist", "model", "deploy") is True
        assert manager.enforce("data_scientist", "dataset", "read") is True
