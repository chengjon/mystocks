from __future__ import annotations

import importlib
import inspect
import sys
from pathlib import Path
from typing import Any

import pytest
from fastapi.params import Depends as DependsParam


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture
def governance_dashboard_module(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("POSTGRESQL_HOST", "localhost")
    monkeypatch.setenv("POSTGRESQL_USER", "postgres")
    monkeypatch.setenv("POSTGRESQL_PASSWORD", "password")
    monkeypatch.setenv("POSTGRESQL_DATABASE", "mystocks")
    monkeypatch.setenv("POSTGRESQL_PORT", "5438")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("BACKEND_PORT", "8020")
    monkeypatch.setenv("BACKEND_BACKUP_PORT", "8021")
    return importlib.import_module("app.api.governance_dashboard")


def test_governance_dashboard_routes_use_postgres_provider(governance_dashboard_module: Any) -> None:
    provider = governance_dashboard_module.get_governance_dashboard_postgres_connection

    target_handlers = [
        governance_dashboard_module.get_quality_overview,
        governance_dashboard_module.get_lineage_stats,
        governance_dashboard_module.get_assets_catalog,
        governance_dashboard_module.get_compliance_metrics,
        governance_dashboard_module.get_dashboard_summary,
    ]

    for handler in target_handlers:
        signature = inspect.signature(handler)
        matching_dependencies = [
            parameter.default
            for parameter in signature.parameters.values()
            if isinstance(parameter.default, DependsParam) and parameter.default.dependency is provider
        ]

        assert matching_dependencies, f"{handler.__name__} must depend on the governance dashboard provider"
        assert "await get_postgres_connection()" not in inspect.getsource(handler)
        assert "conn.close()" not in inspect.getsource(handler)


@pytest.mark.asyncio
async def test_governance_dashboard_postgres_provider_closes_connection(
    governance_dashboard_module: Any,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeConnection:
        closed = False

        async def close(self) -> None:
            self.closed = True

    fake_connection = FakeConnection()

    async def fake_get_postgres_connection() -> FakeConnection:
        return fake_connection

    monkeypatch.setattr(governance_dashboard_module, "get_postgres_connection", fake_get_postgres_connection)

    provider = governance_dashboard_module.get_governance_dashboard_postgres_connection()
    provided_connection = await provider.__anext__()

    assert provided_connection is fake_connection
    assert fake_connection.closed is False

    with pytest.raises(StopAsyncIteration):
        await provider.__anext__()

    assert fake_connection.closed is True
