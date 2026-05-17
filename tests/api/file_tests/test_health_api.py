"""
File-level route and helper contract tests for health.py.

这里覆盖当前实际暴露的健康检查路由，以及几个纯函数分支。
"""

from __future__ import annotations

import importlib
import io
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture
def health_module(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("POSTGRESQL_HOST", "localhost")
    monkeypatch.setenv("POSTGRESQL_USER", "postgres")
    monkeypatch.setenv("POSTGRESQL_PASSWORD", "password")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("BACKEND_PORT", "8020")
    monkeypatch.setenv("BACKEND_BACKUP_PORT", "8021")
    return importlib.import_module("app.api.health")


class TestHealthAPIFile:
    @pytest.mark.file_test
    def test_router_registers_expected_health_routes(self, health_module):
        route_methods = {(route.path, tuple(sorted(route.methods or []))) for route in health_module.router.routes}

        assert health_module.router.tags == ["health"]
        assert ("/health/services", ("GET",)) in route_methods
        assert ("/health/detailed", ("GET",)) in route_methods
        assert ("/reports/health/{timestamp}", ("GET",)) in route_methods

    @pytest.mark.file_test
    def test_route_names_remain_stable(self, health_module):
        route_names = {(route.path, tuple(sorted(route.methods or []))): route.name for route in health_module.router.routes}

        assert route_names[("/health/services", ("GET",))] == "check_system_health"
        assert route_names[("/health/detailed", ("GET",))] == "detailed_health_check"
        assert route_names[("/reports/health/{timestamp}", ("GET",))] == "get_health_report"

    @pytest.mark.file_test
    def test_health_models_expose_expected_fields(self, health_module):
        health_fields = set(health_module.HealthStatus.model_fields)
        response_fields = set(health_module.HealthResponse.model_fields)

        assert health_fields == {"service", "status", "details", "response_time"}
        assert response_fields == {"timestamp", "overall_status", "services", "report_url"}

    @pytest.mark.file_test
    def test_resolve_ports_filters_invalid_values(self, health_module, monkeypatch):
        monkeypatch.setenv("PORT_OK", "8020")
        monkeypatch.setenv("PORT_BAD", "abc")
        monkeypatch.setenv("PORT_ZERO", "0")
        monkeypatch.delenv("PORT_MISSING", raising=False)

        ports = health_module._resolve_ports("PORT_OK", "PORT_BAD", "PORT_ZERO", "PORT_MISSING")

        assert ports == [8020]

    @pytest.mark.file_test
    @pytest.mark.asyncio
    async def test_check_mongodb_service_maps_optional_unavailable_to_warning(self, health_module, monkeypatch):
        monkeypatch.setattr(
            health_module,
            "check_mongodb_readiness",
            Mock(return_value={"status": "optional_unavailable", "detail": "not configured", "latency_ms": 12.5}),
        )

        status = await health_module.check_mongodb_service()

        assert status.service == "mongodb"
        assert status.status == "warning"
        assert status.details == "not configured"
        assert status.response_time == 12.5

    @pytest.mark.file_test
    @pytest.mark.asyncio
    async def test_check_mongodb_service_maps_ready_to_normal(self, health_module, monkeypatch):
        monkeypatch.setattr(
            health_module,
            "check_mongodb_readiness",
            Mock(return_value={"status": "ready", "detail": "ok", "latency_ms": 4.2}),
        )

        status = await health_module.check_mongodb_service()

        assert status.status == "normal"
        assert status.details == "ok"

    @pytest.mark.file_test
    @pytest.mark.asyncio
    async def test_check_contract_health_maps_no_open_drift_to_normal(self, health_module):
        from app.api.contract.services.drift_incidents import clear_contract_drift_incidents

        clear_contract_drift_incidents()

        status = await health_module.check_contract_health()

        assert status.service == "contract"
        assert status.status == "normal"
        assert status.details == "contract validation ok; open drift incidents=0"

    @pytest.mark.file_test
    @pytest.mark.asyncio
    async def test_check_contract_health_maps_open_drift_to_warning(self, health_module):
        from app.api.contract.services.drift_incidents import (
            ContractDriftIncident,
            clear_contract_drift_incidents,
            record_contract_drift_incident,
        )

        clear_contract_drift_incidents()
        record_contract_drift_incident(
            ContractDriftIncident(
                kind="endpoint_removed",
                severity="warning",
                path="paths./api/example",
                message="删除API端点: /api/example",
            )
        )

        status = await health_module.check_contract_health()

        assert status.service == "contract"
        assert status.status == "warning"
        assert status.details == "contract validation drift incidents open=1"

        clear_contract_drift_incidents()

    @pytest.mark.file_test
    @pytest.mark.asyncio
    async def test_system_health_includes_contract_health_status(self, health_module, monkeypatch):
        normal_services = {
            "check_postgresql_service": "postgresql",
            "check_tdengine_service": "tdengine",
            "check_mongodb_service": "mongodb",
            "check_disk_space": "disk",
            "check_system_resources": "system",
        }
        for function_name, service_name in normal_services.items():
            monkeypatch.setattr(
                health_module,
                function_name,
                AsyncMock(return_value=health_module.HealthStatus(service=service_name, status="normal")),
            )
        monkeypatch.setattr(
            health_module,
            "check_contract_health",
            AsyncMock(return_value=health_module.HealthStatus(service="contract", status="warning")),
        )

        response = await health_module.check_system_health(SimpleNamespace(state=SimpleNamespace(request_id="req-1")))

        assert response.data["overall_status"] == "degraded"
        assert response.data["services"]["contract"].status == "warning"
        assert response.request_id == "req-1"

    @pytest.mark.file_test
    def test_system_health_example_lists_contract_service(self, health_module):
        services = health_module.SYSTEM_SERVICES_HEALTH_RESPONSE_EXAMPLE["data"]["services"]

        assert services["contract"] == {"service": "contract", "status": "normal"}

    @pytest.mark.file_test
    @pytest.mark.asyncio
    async def test_get_health_report_returns_loaded_json(self, health_module, monkeypatch):
        monkeypatch.setattr(health_module.os.path, "exists", Mock(return_value=True))
        monkeypatch.setattr(health_module, "open", Mock(return_value=io.StringIO('{"status":"ok"}')), raising=False)

        payload = await health_module.get_health_report("20260401", current_user=SimpleNamespace(username="tester"))

        assert payload.data == {"status": "ok"}
        assert payload.message == "健康检查报告获取成功"

    @pytest.mark.file_test
    @pytest.mark.asyncio
    async def test_get_health_report_raises_not_found_when_file_missing(self, health_module, monkeypatch):
        monkeypatch.setattr(health_module.os.path, "exists", Mock(return_value=False))

        with pytest.raises(health_module.NotFoundException):
            await health_module.get_health_report("missing", current_user=SimpleNamespace(username="tester"))

    @pytest.mark.file_test
    def test_health_endpoint_docstrings_cover_report_and_detailed_checks(self, health_module):
        assert "系统健康检查API端点" in (health_module.check_system_health.__doc__ or "")
        assert "详细健康检查" in (health_module.detailed_health_check.__doc__ or "")
        assert "获取健康检查报告" in (health_module.get_health_report.__doc__ or "")

    @pytest.mark.file_test
    def test_route_path_and_method_pairs_are_unique(self, health_module):
        route_pairs = [(route.path, tuple(sorted(route.methods or []))) for route in health_module.router.routes]

        assert len(route_pairs) == len(set(route_pairs))
