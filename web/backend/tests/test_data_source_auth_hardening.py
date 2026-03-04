"""Auth hardening regression tests for data source APIs."""

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


@pytest.fixture(autouse=True)
def _disable_csrf_for_auth_tests(monkeypatch):
    monkeypatch.setattr(settings, "csrf_enabled", False, raising=False)


def test_registry_write_endpoint_requires_auth_when_not_testing(monkeypatch):
    monkeypatch.setattr(settings, "testing", False, raising=False)

    with TestClient(app) as client:
        response = client.post("/api/v1/data-sources/health-check/all")

    assert response.status_code == 401


def test_registry_write_endpoint_bypasses_auth_when_testing(monkeypatch):
    monkeypatch.setattr(settings, "testing", True, raising=False)

    with TestClient(app) as client:
        response = client.post("/api/v1/data-sources/health-check/all")

    assert response.status_code != 401


def test_config_write_endpoint_requires_auth_when_not_testing(monkeypatch):
    monkeypatch.setattr(settings, "testing", False, raising=False)

    with TestClient(app) as client:
        response = client.put("/api/v1/data-sources/config/non-existent", json={})

    assert response.status_code == 401


def test_config_write_endpoint_bypasses_auth_when_testing(monkeypatch):
    monkeypatch.setattr(settings, "testing", True, raising=False)

    with TestClient(app) as client:
        response = client.put("/api/v1/data-sources/config/non-existent", json={})

    assert response.status_code != 401


def test_registry_read_endpoint_does_not_require_write_auth(monkeypatch):
    monkeypatch.setattr(settings, "testing", False, raising=False)

    with TestClient(app) as client:
        response = client.get("/api/v1/data-sources/non-existent-endpoint")

    assert response.status_code == 404
