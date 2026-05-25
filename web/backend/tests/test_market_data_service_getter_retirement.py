from __future__ import annotations

import importlib


def test_market_data_service_package_getter_and_singleton_are_retired():
    service_package = importlib.import_module("app.services.market_data_service")
    provider_module = importlib.import_module("app.services.market_data_service.get_market_data_service")

    assert hasattr(service_package, "MarketDataService")
    assert "get_market_data_service" not in service_package.__all__
    assert not callable(getattr(service_package, "get_market_data_service", None))
    assert not hasattr(provider_module, "get_market_data_service")
    assert not hasattr(provider_module, "_market_data_service")


def test_market_data_adapter_uses_local_service_factory_without_package_getter(monkeypatch):
    adapter_module = importlib.import_module("app.services.market_data_adapter")

    class FakeMarketDataService:
        pass

    monkeypatch.setattr(adapter_module, "MarketDataService", FakeMarketDataService)

    adapter = adapter_module.MarketDataSourceAdapter({"mode": "live"})

    service = adapter._get_market_service()

    assert isinstance(service, FakeMarketDataService)
    assert adapter._get_market_service() is service
