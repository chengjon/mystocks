from __future__ import annotations

import inspect
from types import SimpleNamespace

import pytest

from app.api import market_v2 as market_v2_routes
from app.services import market_data_service_v2


def test_market_data_service_v2_dependency_installs_app_state_when_missing(monkeypatch):
    fake_service = object()
    fake_app = SimpleNamespace(state=SimpleNamespace())
    request = SimpleNamespace(app=fake_app)

    monkeypatch.setattr(market_data_service_v2, "get_market_data_service_v2", lambda: fake_service)

    assert market_data_service_v2.get_market_data_service_v2_dependency(request) is fake_service
    assert getattr(fake_app.state, market_data_service_v2.MARKET_DATA_SERVICE_V2_STATE_KEY) is fake_service


def test_install_market_data_service_v2_accepts_explicit_service():
    fake_service = object()
    fake_app = SimpleNamespace(state=SimpleNamespace())

    assert market_data_service_v2.install_market_data_service_v2(fake_app, fake_service) is fake_service
    assert getattr(fake_app.state, market_data_service_v2.MARKET_DATA_SERVICE_V2_STATE_KEY) is fake_service


def test_market_v2_routes_accept_injected_market_data_service_v2():
    for function_name in [
        "get_fund_flow",
        "refresh_fund_flow",
        "get_etf_list",
        "refresh_etf_spot",
        "get_lhb_detail",
        "refresh_lhb_detail",
        "get_sector_fund_flow",
        "refresh_sector_fund_flow",
        "get_stock_dividend",
        "refresh_stock_dividend",
        "get_stock_blocktrade",
        "refresh_stock_blocktrade",
        "refresh_all_market_data",
    ]:
        signature = inspect.signature(getattr(market_v2_routes, function_name))
        assert "service" in signature.parameters


@pytest.mark.asyncio
async def test_refresh_etf_spot_uses_injected_market_data_service_v2():
    class FakeMarketDataServiceV2:
        def __init__(self):
            self.called = False

        def fetch_and_save_etf_spot(self):
            self.called = True
            return {"success": True, "message": "ok"}

    fake_service = FakeMarketDataServiceV2()

    result = await market_v2_routes.refresh_etf_spot(service=fake_service)

    assert result == {"success": True, "message": "ok"}
    assert fake_service.called is True
