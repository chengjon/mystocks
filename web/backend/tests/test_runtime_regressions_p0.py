"""
P0 runtime regression tests for web/backend startup and key API paths.
"""

from __future__ import annotations

import importlib
import re
import sys
from types import SimpleNamespace

import requests


def test_stock_search_app_state_install_initialization(monkeypatch):
    """
    Regression: stock search service app-state installation should initialize cleanly.
    """
    module = importlib.import_module("app.services.stock_search_service.stock_search_service")

    class DummyStockSearchService:
        pass

    monkeypatch.setattr(module, "StockSearchService", DummyStockSearchService)
    app = SimpleNamespace(state=SimpleNamespace())

    service = module.install_stock_search_service(app)

    assert isinstance(service, DummyStockSearchService)
    assert getattr(app.state, module.STOCK_SEARCH_SERVICE_STATE_KEY) is service
    assert module.get_stock_search_service_dependency(SimpleNamespace(app=app)) is service


def test_watchlist_mock_data_keeps_success_shape():
    """
    Regression: watchlist fallback path should keep success/data response shape.
    """
    manager = importlib.import_module("app.mock.mock_data.factory").get_mock_data_manager()

    result = manager.get_data("watchlist", action="list", user_id=1)

    assert result.get("success") is True
    assert isinstance(result.get("data"), list)
    assert isinstance(result.get("total"), int)


def test_watchlist_mock_data_added_at_matches_response_schema():
    """
    Regression: watchlist mock added_at format must match API response schema.
    """
    manager = importlib.import_module("app.mock.mock_data.factory").get_mock_data_manager()

    result = manager.get_data("watchlist", action="list", user_id=1)

    assert result.get("success") is True
    for item in result.get("data", []):
        assert re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", item.get("added_at", ""))


def test_daily_calculation_module_importable():
    """
    Regression: daily_calculation module import should not fail with NameError.
    """
    module_name = "app.services.indicators.jobs.daily_calculation"
    sys.modules.pop(module_name, None)

    module = importlib.import_module(module_name)

    assert hasattr(module, "run_daily_calculation")


def test_stock_search_service_constructor_has_akshare_flag():
    """
    Regression: stock search service initialization should not crash on AKShare flag.
    """
    module = importlib.import_module("app.services.stock_search_service.stock_search_service")

    service = module.StockSearchService()

    assert isinstance(service.akshare_available, bool)


def test_stock_search_kline_fallback_on_upstream_error(monkeypatch):
    """
    Regression: kline endpoint should degrade gracefully when upstream data source fails.
    """
    module = importlib.import_module("app.services.stock_search_service.stock_search_service")
    monkeypatch.setenv("KLINE_FALLBACK_ENABLED", "true")
    service = module.StockSearchService()
    service.akshare_available = True

    class DummyAk:
        @staticmethod
        def stock_zh_a_hist(*args, **kwargs):
            raise requests.exceptions.ConnectionError("upstream unavailable")

    monkeypatch.setattr(module, "ak", DummyAk)

    result = service.get_a_stock_kline(symbol="600519")

    assert result is not None
    assert result.get("count", 0) >= 10
    assert result.get("stock_code", "").endswith(".SH")


def test_stock_search_kline_returns_none_when_fallback_disabled(monkeypatch):
    """
    Regression: kline fallback should be disable-able via env toggle.
    """
    module = importlib.import_module("app.services.stock_search_service.stock_search_service")
    monkeypatch.setenv("KLINE_FALLBACK_ENABLED", "false")
    service = module.StockSearchService()
    service.akshare_available = True

    class DummyAk:
        @staticmethod
        def stock_zh_a_hist(*args, **kwargs):
            raise requests.exceptions.ConnectionError("upstream unavailable")

    monkeypatch.setattr(module, "ak", DummyAk)

    result = service.get_a_stock_kline(symbol="600519")

    assert result is None
