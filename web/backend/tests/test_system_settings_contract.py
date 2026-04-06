from __future__ import annotations

import asyncio

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.system.settings import (
    GeneralSettingsPayload,
    PostgresSystemSettingsRepository,
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


class _AsyncContextManager:
    def __init__(self, value: object) -> None:
        self._value = value

    async def __aenter__(self) -> object:
        return self._value

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        return False


class _RecordingConnection:
    def __init__(
        self,
        *,
        data_type: str,
        udt_name: str,
        reject_on_conflict: bool = False,
        update_results: dict[tuple[str, str], str] | None = None,
        existing_keys: set[tuple[str, str]] | None = None,
    ) -> None:
        self._column_row = {"data_type": data_type, "udt_name": udt_name}
        self._reject_on_conflict = reject_on_conflict
        self._update_results = update_results or {}
        self._existing_keys = existing_keys or set()
        self.execute_calls: list[tuple[str, tuple[object, ...]]] = []
        self.fetchrow_calls: list[tuple[str, tuple[object, ...]]] = []
        self.fetchval_calls: list[tuple[str, tuple[object, ...]]] = []

    def transaction(self) -> _AsyncContextManager:
        return _AsyncContextManager(object())

    async def fetchrow(self, query: str, *args: object) -> dict[str, str]:
        self.fetchrow_calls.append((query, args))
        return self._column_row

    async def fetchval(self, query: str, *args: object) -> object:
        self.fetchval_calls.append((query, args))
        if len(args) >= 2 and isinstance(args[0], str) and isinstance(args[1], str):
            return 1 if (args[0], args[1]) in self._existing_keys else None
        return None

    async def execute(self, query: str, *args: object) -> str:
        if self._reject_on_conflict and "ON CONFLICT" in query:
            raise AssertionError("unexpected ON CONFLICT usage against legacy system_config schema")
        self.execute_calls.append((query, args))
        if query.lstrip().startswith("UPDATE system_config") and len(args) >= 6:
            key = (str(args[4]), str(args[5]))
            return self._update_results.get(key, "UPDATE 0")
        return "INSERT 0 1"


class _RecordingPool:
    def __init__(self, conn: _RecordingConnection) -> None:
        self._conn = conn

    def acquire(self) -> _AsyncContextManager:
        return _AsyncContextManager(self._conn)


class _FakePostgresAccess:
    def __init__(self, conn: _RecordingConnection) -> None:
        self.pool = _RecordingPool(conn)

    def is_connected(self) -> bool:
        return True


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


def test_repository_ensure_defaults_uses_smallint_zero_for_legacy_is_readonly_schema() -> None:
    connection = _RecordingConnection(data_type="smallint", udt_name="int2", reject_on_conflict=True)
    repository = PostgresSystemSettingsRepository(_FakePostgresAccess(connection))

    asyncio.run(repository._ensure_defaults("general", repository._require_pool()))

    assert connection.fetchrow_calls
    assert connection.execute_calls
    assert all(args[6] == 0 for _, args in connection.execute_calls)


def test_repository_write_section_uses_boolean_false_for_boolean_is_readonly_schema() -> None:
    connection = _RecordingConnection(data_type="boolean", udt_name="bool", reject_on_conflict=True)
    repository = PostgresSystemSettingsRepository(_FakePostgresAccess(connection))

    asyncio.run(
        repository.write_section(
            "security",
            {
                "session_timeout_minutes": 90,
                "mfa_required": True,
                "ip_allowlist_enabled": True,
                "password_policy_level": "strict",
            },
        )
    )

    assert connection.fetchrow_calls
    assert connection.execute_calls
    insert_calls = [(query, args) for query, args in connection.execute_calls if query.lstrip().startswith("INSERT INTO system_config")]
    update_calls = [(query, args) for query, args in connection.execute_calls if query.lstrip().startswith("UPDATE system_config")]

    assert insert_calls
    assert update_calls
    assert all(args[6] is False for _, args in insert_calls)
