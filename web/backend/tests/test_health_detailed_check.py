import os


os.environ.setdefault("POSTGRESQL_HOST", "localhost")
os.environ.setdefault("POSTGRESQL_PORT", "5432")
os.environ.setdefault("POSTGRESQL_USER", "tester")
os.environ.setdefault("POSTGRESQL_PASSWORD", "tester")
os.environ.setdefault("POSTGRESQL_DATABASE", "tester")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("BACKEND_PORT", "8126")
os.environ.setdefault("BACKEND_BACKUP_PORT", "8127")
os.environ.setdefault("TESTING", "true")
os.environ.setdefault("MOCK_AUTH_ENABLED", "true")

from subprocess import CompletedProcess

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import app.api.health as health_module
from app.core.security import get_current_user


def _payload(result):
    return result.model_dump(mode="json") if hasattr(result, "model_dump") else result


@pytest.mark.asyncio
async def test_detailed_health_check_does_not_require_chmod(monkeypatch):
    monkeypatch.setattr(health_module.os.path, "exists", lambda _path: True)

    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("os.chmod should not be called")

    monkeypatch.setattr(health_module.os, "chmod", fail_if_called)
    monkeypatch.setattr(
        health_module.subprocess,
        "run",
        lambda *args, **kwargs: CompletedProcess(args=args, returncode=0, stdout="health ok", stderr=""),
    )

    result = await health_module.detailed_health_check(current_user=None)
    payload = _payload(result)

    assert payload["data"]["status"] == "success"
    assert payload["data"]["output"] == "health ok"


@pytest.mark.asyncio
async def test_detailed_health_check_returns_warning_when_script_has_nonfatal_stderr(monkeypatch):
    monkeypatch.setattr(health_module.os.path, "exists", lambda _path: True)
    monkeypatch.setattr(
        health_module.subprocess,
        "run",
        lambda *args, **kwargs: CompletedProcess(
            args=args,
            returncode=1,
            stdout="partial health report",
            stderr="tee: read-only file system",
        ),
    )

    result = await health_module.detailed_health_check(current_user=None)
    payload = _payload(result)

    assert payload["data"]["status"] == "warning"
    assert payload["data"]["output"] == "partial health report"
    assert "read-only file system" in payload["data"]["error"]


def test_detailed_health_check_http_response_uses_unified_response(monkeypatch):
    monkeypatch.setattr(health_module.os.path, "exists", lambda _path: True)
    monkeypatch.setattr(
        health_module.subprocess,
        "run",
        lambda *args, **kwargs: CompletedProcess(args=args, returncode=0, stdout="health ok", stderr=""),
    )

    app = FastAPI()
    app.include_router(health_module.router, prefix="/api")
    app.dependency_overrides[get_current_user] = lambda: None

    with TestClient(app) as client:
        response = client.get("/api/health/detailed")

    payload = response.json()

    assert response.status_code == 200
    assert payload["success"] is True
    assert payload["data"]["status"] == "success"
