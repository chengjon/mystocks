from __future__ import annotations

import importlib
import inspect
from types import SimpleNamespace

import pytest

from app.api.market import market_data_request as market_routes
from app.services import market_data_service


ROUTE_HANDLER_NAMES = [
    "refresh_fund_flow",
    "get_etf_list",
    "refresh_etf_data",
    "get_chip_race",
    "refresh_chip_race",
    "get_lhb_detail",
    "refresh_lhb_detail",
]


def test_market_data_service_package_reexports_provider_symbols():
    for symbol_name in [
        "MARKET_DATA_SERVICE_STATE_KEY",
        "install_market_data_service",
        "get_market_data_service_dependency",
    ]:
        assert hasattr(market_data_service, symbol_name)


def test_market_data_service_dependency_installs_app_state_when_missing(monkeypatch):
    provider_module = importlib.import_module("app.services.market_data_service.get_market_data_service")
    fake_service = object()
    fake_app = SimpleNamespace(state=SimpleNamespace())
    request = SimpleNamespace(app=fake_app)

    monkeypatch.setattr(provider_module, "MarketDataService", lambda: fake_service)

    assert provider_module.get_market_data_service_dependency(request) is fake_service
    assert getattr(fake_app.state, provider_module.MARKET_DATA_SERVICE_STATE_KEY) is fake_service


def test_install_market_data_service_accepts_explicit_service():
    getter_module = importlib.import_module("app.services.market_data_service.get_market_data_service")
    fake_service = object()
    fake_app = SimpleNamespace(state=SimpleNamespace())

    assert getter_module.install_market_data_service(fake_app, fake_service) is fake_service
    assert getattr(fake_app.state, getter_module.MARKET_DATA_SERVICE_STATE_KEY) is fake_service


def test_market_routes_use_market_data_service_dependency_provider():
    getter_module = importlib.import_module("app.services.market_data_service.get_market_data_service")

    for function_name in ROUTE_HANDLER_NAMES:
        signature = inspect.signature(getattr(market_routes, function_name))
        service_default = signature.parameters["service"].default

        assert getattr(service_default, "dependency", None) is getter_module.get_market_data_service_dependency


@pytest.mark.asyncio
async def test_refresh_etf_data_uses_injected_market_data_service():
    class FakeMarketDataService:
        def __init__(self):
            self.called = False

        def fetch_and_save_etf_spot(self):
            self.called = True
            return {"success": True, "message": "ok"}

    fake_service = FakeMarketDataService()

    result = await market_routes.refresh_etf_data(service=fake_service)

    assert result.message == "ok"
    assert fake_service.called is True
