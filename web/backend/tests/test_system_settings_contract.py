from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.system.settings import (
    GeneralSettingsPayload,
    SecuritySettingsPayload,
    get_system_settings_repository,
    router,
)


class _FakeSystemSettingsRepository:
    def __init__(self) -> None:
        self.sections = {
            "general": {
                "backend_url": "http://localhost:8020",
                "max_backtest_jobs": 4,
                "default_slippage_percent": 0.05,
                "fee_rate_bps": 2.5,
            },
            "security": {
                "session_timeout_minutes": 120,
                "mfa_required": False,
                "ip_allowlist_enabled": False,
                "password_policy_level": "standard",
            },
        }

    async def read_section(self, section: str) -> dict:
        return dict(self.sections[section])

    async def write_section(self, section: str, payload: dict) -> dict:
        self.sections[section] = dict(payload)
        return dict(self.sections[section])


class _UnavailableSystemSettingsRepository:
    async def read_section(self, _section: str) -> dict:
        raise RuntimeError("system_config repository unavailable")

    async def write_section(self, _section: str, _payload: dict) -> dict:
        raise RuntimeError("system_config repository unavailable")


def _build_client(repository: object) -> TestClient:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[get_system_settings_repository] = lambda: repository
    return TestClient(app)


def test_get_general_settings_reads_canonical_system_config_section() -> None:
    with _build_client(_FakeSystemSettingsRepository()) as client:
        response = client.get("/api/v1/system/settings/general")

    payload = response.json()
    assert response.status_code == 200
    assert payload["success"] is True
    assert payload["data"] == GeneralSettingsPayload().model_dump(mode="json")


def test_post_general_settings_persists_through_repository() -> None:
    repository = _FakeSystemSettingsRepository()

    with _build_client(repository) as client:
        response = client.post(
            "/api/v1/system/settings/general",
            json={
                "backend_url": "http://localhost:9123",
                "max_backtest_jobs": 6,
                "default_slippage_percent": 0.08,
                "fee_rate_bps": 3.2,
            },
        )

    payload = response.json()
    assert response.status_code == 200
    assert payload["success"] is True
    assert payload["data"]["backend_url"] == "http://localhost:9123"
    assert repository.sections["general"]["max_backtest_jobs"] == 6


def test_get_security_settings_reads_canonical_system_config_section() -> None:
    with _build_client(_FakeSystemSettingsRepository()) as client:
        response = client.get("/api/v1/system/settings/security")

    payload = response.json()
    assert response.status_code == 200
    assert payload["success"] is True
    assert payload["data"] == SecuritySettingsPayload().model_dump(mode="json")


def test_post_security_settings_persists_through_repository() -> None:
    repository = _FakeSystemSettingsRepository()

    with _build_client(repository) as client:
        response = client.post(
            "/api/v1/system/settings/security",
            json={
                "session_timeout_minutes": 90,
                "mfa_required": True,
                "ip_allowlist_enabled": True,
                "password_policy_level": "strict",
            },
        )

    payload = response.json()
    assert response.status_code == 200
    assert payload["success"] is True
    assert payload["data"]["mfa_required"] is True
    assert repository.sections["security"]["password_policy_level"] == "strict"


def test_system_settings_routes_report_repository_unavailability() -> None:
    with _build_client(_UnavailableSystemSettingsRepository()) as client:
        get_response = client.get("/api/v1/system/settings/general")
        post_response = client.post(
            "/api/v1/system/settings/security",
            json=SecuritySettingsPayload().model_dump(mode="json"),
        )

    assert get_response.status_code == 503
    assert post_response.status_code == 503
    assert "system_config repository unavailable" in get_response.json()["detail"]
    assert "system_config repository unavailable" in post_response.json()["detail"]
