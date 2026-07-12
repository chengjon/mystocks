import os

import pytest
from fastapi.testclient import TestClient


os.environ.setdefault("TESTING", "true")
os.environ.setdefault("DEVELOPMENT_MODE", "true")
os.environ.setdefault("MOCK_AUTH_ENABLED", "true")
os.environ.setdefault("POSTGRESQL_HOST", "localhost")
os.environ.setdefault("POSTGRESQL_PORT", "5438")
os.environ.setdefault("POSTGRESQL_USER", "postgres")
os.environ.setdefault("POSTGRESQL_PASSWORD", "test_password")
os.environ.setdefault("POSTGRESQL_DATABASE", "mystocks_test")
os.environ.setdefault("JWT_SECRET_KEY", "test_secret_key_for_testing_only_do_not_use_in_production")
os.environ.setdefault("BACKEND_PORT", "8020")
os.environ.setdefault("BACKEND_BACKUP_PORT", "8021")
os.environ.setdefault("ADMIN_INITIAL_PASSWORD", "admin123")

from app.api.auth import get_current_active_user
from app.core.security import User
from app.main import app


@pytest.fixture
def auth_client():
    user = User(
        id=1,
        username="test_admin",
        email="admin@example.com",
        role="admin",
        is_active=True,
    )
    app.dependency_overrides[get_current_active_user] = lambda: user
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_v1_indicator_registry_returns_raw_registry(auth_client: TestClient):
    response = auth_client.get("/api/v1/indicators/registry")

    assert response.status_code == 200

    payload = response.json()
    assert "total_count" in payload
    assert "categories" in payload
    assert "indicators" in payload
    assert payload["total_count"] >= 20
    assert isinstance(payload["indicators"], list)
