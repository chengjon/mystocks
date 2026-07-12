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

from app.core.security import User, get_current_user
from app.main import app


class _MissingDataSourceFactory:
    async def get_data(self, source_name: str, endpoint: str, params: dict | None = None):
        raise ValueError(f"Data source '{source_name}' not found or not enabled")


@pytest.fixture
def auth_client(monkeypatch: pytest.MonkeyPatch):
    async def _get_data_source_factory():
        return _MissingDataSourceFactory()

    user = User(
        id=1,
        username="test_admin",
        email="admin@example.com",
        role="admin",
        is_active=True,
    )

    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setenv("DEVELOPMENT_MODE", "true")
    monkeypatch.setattr("app.services.data_source_factory.get_data_source_factory", _get_data_source_factory)
    app.dependency_overrides[get_current_user] = lambda: user

    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()


def test_stocks_basic_uses_runtime_fallback_when_data_source_missing(auth_client: TestClient):
    response = auth_client.get("/api/v1/data/stocks/basic?limit=5")

    assert response.status_code == 200

    payload = response.json()
    assert payload["success"] is True
    assert payload["source"] == "runtime_fallback"
    assert len(payload["data"]) == 5

    first_row = payload["data"][0]
    assert first_row["symbol"]
    assert first_row["name"]
    assert "price" in first_row
    assert "change_pct" in first_row
    assert "volume" in first_row
    assert "turnover" in first_row
