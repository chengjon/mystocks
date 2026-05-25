from __future__ import annotations

import inspect
from types import SimpleNamespace

import pytest

from app.api import advanced_analysis_api as advanced_analysis_routes
from app.services import advanced_analysis_service as advanced_analysis_service_module


@pytest.mark.asyncio
async def test_advanced_analysis_service_dependency_fallback_uses_private_initializer(monkeypatch):
    class FakeAdvancedAnalysisService:
        initialized = False

        async def initialize(self):
            self.initialized = True

    fake_service = FakeAdvancedAnalysisService()
    fake_app = SimpleNamespace(state=SimpleNamespace())
    request = SimpleNamespace(app=fake_app)

    async def fail_if_public_getter_called():
        raise AssertionError("provider fallback must not call the public compatibility getter")

    monkeypatch.setattr(advanced_analysis_service_module, "advanced_analysis_service", fake_service)
    monkeypatch.setattr(
        advanced_analysis_service_module,
        "get_advanced_analysis_service",
        fail_if_public_getter_called,
    )

    result = await advanced_analysis_service_module.get_advanced_analysis_service_dependency(request)

    assert result is fake_service
    assert fake_service.initialized is True
    assert getattr(fake_app.state, advanced_analysis_service_module.ADVANCED_ANALYSIS_SERVICE_STATE_KEY) is fake_service


@pytest.mark.asyncio
async def test_advanced_analysis_service_dependency_prefers_installed_app_state(monkeypatch):
    fake_service = object()
    fake_app = SimpleNamespace(state=SimpleNamespace())
    setattr(fake_app.state, advanced_analysis_service_module.ADVANCED_ANALYSIS_SERVICE_STATE_KEY, fake_service)
    request = SimpleNamespace(app=fake_app)

    async def fail_if_fallback_called():
        raise AssertionError("compatibility fallback should not be called when app state has a service")

    monkeypatch.setattr(
        advanced_analysis_service_module,
        "get_advanced_analysis_service",
        fail_if_fallback_called,
    )

    assert await advanced_analysis_service_module.get_advanced_analysis_service_dependency(request) is fake_service


def test_install_advanced_analysis_service_accepts_explicit_service():
    fake_service = object()
    fake_app = SimpleNamespace(state=SimpleNamespace())

    assert advanced_analysis_service_module.install_advanced_analysis_service(fake_app, fake_service) is fake_service
    assert getattr(fake_app.state, advanced_analysis_service_module.ADVANCED_ANALYSIS_SERVICE_STATE_KEY) is fake_service


def test_advanced_analysis_routes_use_route_provider_dependency():
    for function_name in [
        "analyze_fundamental",
        "analyze_technical",
        "analyze_trading_signals",
        "analyze_time_series",
        "analyze_market_panorama",
        "analyze_capital_flow",
        "analyze_chip_distribution",
        "analyze_anomaly_tracking",
        "analyze_financial_valuation",
        "analyze_sentiment",
        "analyze_decision_models",
        "analyze_multidimensional_radar",
        "analyze_batch",
        "health_check",
    ]:
        signature = inspect.signature(getattr(advanced_analysis_routes, function_name))
        service_parameter = signature.parameters["service"]
        assert (
            service_parameter.default.dependency
            is advanced_analysis_service_module.get_advanced_analysis_service_dependency
        )
