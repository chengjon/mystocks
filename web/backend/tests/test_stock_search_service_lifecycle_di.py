from __future__ import annotations

import inspect
from types import SimpleNamespace

import pytest

from app.api.market import market_data_request as market_routes
from app.api.stock_search import stock_search_result as stock_routes
from app.services import stock_search_service
from app.services.stock_search_service import stock_search_service as stock_search_service_module


def test_stock_search_service_dependency_installs_app_state_when_missing(monkeypatch):
    fake_service = object()
    fake_app = SimpleNamespace(state=SimpleNamespace())
    request = SimpleNamespace(app=fake_app)

    monkeypatch.setattr(stock_search_service_module, "StockSearchService", lambda: fake_service)

    assert stock_search_service.get_stock_search_service_dependency(request) is fake_service
    assert getattr(fake_app.state, stock_search_service.STOCK_SEARCH_SERVICE_STATE_KEY) is fake_service


def test_install_stock_search_service_accepts_explicit_service():
    fake_service = object()
    fake_app = SimpleNamespace(state=SimpleNamespace())

    assert stock_search_service.install_stock_search_service(fake_app, fake_service) is fake_service
    assert getattr(fake_app.state, stock_search_service.STOCK_SEARCH_SERVICE_STATE_KEY) is fake_service


def test_stock_search_routes_accept_injected_stock_search_service():
    for route_module, function_name in [
        (stock_routes, "search_stocks"),
        (stock_routes, "get_stock_quote"),
        (stock_routes, "get_stock_news"),
        (stock_routes, "get_market_news"),
        (stock_routes, "clear_search_cache"),
        (market_routes, "get_kline_data"),
    ]:
        signature = inspect.signature(getattr(route_module, function_name))
        assert "service" in signature.parameters


@pytest.mark.asyncio
async def test_clear_search_cache_uses_injected_stock_search_service(monkeypatch):
    class FakeStockSearchService:
        def __init__(self):
            self.cleared = False

        def clear_cache(self):
            self.cleared = True

    fake_service = FakeStockSearchService()
    current_user = SimpleNamespace(id=42, username="admin", role="admin")

    monkeypatch.setattr(stock_routes, "check_admin_privileges", lambda user: True)
    monkeypatch.setattr(stock_routes, "log_search_operation", lambda **kwargs: None)

    await stock_routes.clear_search_cache(
        current_user=current_user,
        service=fake_service,
    )

    assert fake_service.cleared is True
