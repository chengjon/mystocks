from __future__ import annotations

import inspect
from types import SimpleNamespace

import pytest

from app.api import tdx as tdx_routes
from app.services import tdx_service as tdx_service_module


def test_tdx_service_dependency_installs_app_state_when_missing(monkeypatch):
    fake_service = object()
    fake_app = SimpleNamespace(state=SimpleNamespace())
    request = SimpleNamespace(app=fake_app)

    monkeypatch.setattr(tdx_service_module, "get_tdx_service", lambda: fake_service)

    assert tdx_service_module.get_tdx_service_dependency(request) is fake_service
    assert getattr(fake_app.state, tdx_service_module.TDX_SERVICE_STATE_KEY) is fake_service


def test_install_tdx_service_accepts_explicit_service():
    fake_service = object()
    fake_app = SimpleNamespace(state=SimpleNamespace())

    assert tdx_service_module.install_tdx_service(fake_app, fake_service) is fake_service
    assert getattr(fake_app.state, tdx_service_module.TDX_SERVICE_STATE_KEY) is fake_service


def test_tdx_routes_use_tdx_service_dependency_provider():
    for function_name in [
        "get_stock_quote",
        "get_stock_kline",
        "get_index_quote",
        "get_index_kline",
        "health_check",
    ]:
        signature = inspect.signature(getattr(tdx_routes, function_name))
        service_parameter = signature.parameters["service"]
        assert service_parameter.default.dependency is tdx_service_module.get_tdx_service_dependency


@pytest.mark.asyncio
async def test_tdx_health_check_uses_injected_tdx_service():
    class FakeTdxService:
        def __init__(self):
            self.called = False

        def check_connection(self):
            self.called = True
            return {
                "status": "healthy",
                "tdx_connected": True,
                "timestamp": "2026-05-24 00:00:00",
                "server_info": {"host": "fake"},
            }

    fake_service = FakeTdxService()

    result = await tdx_routes.health_check(service=fake_service)

    assert fake_service.called is True
    assert result.status == "healthy"
    assert result.tdx_connected is True
    assert result.server_info == {"host": "fake"}
