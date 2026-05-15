from __future__ import annotations

import asyncio
import importlib
import sys
from datetime import date, datetime
from pathlib import Path

import dotenv
import pytest

ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture
def market_routes_module(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("POSTGRESQL_HOST", "localhost")
    monkeypatch.setenv("POSTGRESQL_USER", "postgres")
    monkeypatch.setenv("POSTGRESQL_PASSWORD", "password")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key")
    monkeypatch.setattr(dotenv, "load_dotenv", lambda *args, **kwargs: False)
    return importlib.import_module("app.api.monitoring_market_routes")


def realtime_response(market_routes_module, *, symbol="600519"):
    return market_routes_module.RealtimeMonitoringResponse(
        id=1,
        symbol=symbol,
        stock_name="贵州茅台",
        timestamp=datetime(2026, 5, 14, 10, 30),
        trade_date=date(2026, 5, 14),
        price=1688.0,
        change_percent=1.25,
        volume=1000,
        amount=1688000.0,
        indicators={"rsi": 62},
        market_strength="strong",
        is_limit_up=False,
        is_limit_down=False,
    )


def dragon_tiger_response(market_routes_module):
    return market_routes_module.DragonTigerListResponse(
        id=9,
        symbol="000001",
        stock_name="平安银行",
        trade_date=date(2026, 5, 14),
        reason="日涨幅偏离值达7%",
        total_buy_amount=32000000.0,
        total_sell_amount=12000000.0,
        net_amount=20000000.0,
        institution_buy_count=2,
        institution_sell_count=1,
        institution_net_amount=18000000.0,
        detail_data={"seats": []},
        impact_score=85,
    )


@pytest.mark.file_test
def test_realtime_market_routes_delegate_to_market_data_service(market_routes_module, monkeypatch):
    class FakeMarketDataService:
        def __init__(self):
            self.calls = []

        def get_realtime_monitoring(self, symbol):
            self.calls.append(("get_realtime_monitoring", symbol))
            return realtime_response(market_routes_module, symbol=symbol)

        def list_realtime_monitoring(self, *, symbols, limit, is_limit_up, is_limit_down):
            self.calls.append(("list_realtime_monitoring", symbols, limit, is_limit_up, is_limit_down))
            return [
                realtime_response(market_routes_module, symbol="600519"),
                realtime_response(market_routes_module, symbol="000001"),
            ]

        def fetch_realtime_data(self, symbols):
            self.calls.append(("fetch_realtime_data", tuple(symbols)))
            return {"stocks_count": 2, "saved_count": 2, "alerts_triggered": 1}

    fake_service = FakeMarketDataService()
    monkeypatch.setattr(market_routes_module, "_monitoring_market_data_service", fake_service, raising=False)

    detail_result = asyncio.run(market_routes_module.get_realtime_monitoring("600519", object()))
    list_result = asyncio.run(
        market_routes_module.get_realtime_monitoring_list("600519,000001", 50, True, False, object())
    )
    fetch_result = asyncio.run(market_routes_module.fetch_realtime_data(["600519", "000001"], object()))

    assert detail_result.data.symbol == "600519"
    assert [item.symbol for item in list_result.data] == ["600519", "000001"]
    assert fetch_result.data == {"stocks_count": 2, "saved_count": 2, "alerts_triggered": 1}
    assert fake_service.calls == [
        ("get_realtime_monitoring", "600519"),
        ("list_realtime_monitoring", "600519,000001", 50, True, False),
        ("fetch_realtime_data", ("600519", "000001")),
    ]


@pytest.mark.file_test
def test_realtime_market_fetch_route_returns_empty_response_without_saving(market_routes_module, monkeypatch):
    class FakeMarketDataService:
        def fetch_realtime_data(self, symbols):
            return None

    monkeypatch.setattr(market_routes_module, "_monitoring_market_data_service", FakeMarketDataService(), raising=False)

    result = asyncio.run(market_routes_module.fetch_realtime_data(["600519"], object()))

    assert result.success is False
    assert result.message == "未获取到数据"
    assert result.data is None


@pytest.mark.file_test
def test_dragon_tiger_market_routes_delegate_to_market_data_service(market_routes_module, monkeypatch):
    trade_date = date(2026, 5, 14)

    class FakeMarketDataService:
        def __init__(self):
            self.calls = []

        def list_dragon_tiger(self, *, trade_date, symbol, min_net_amount, limit):
            self.calls.append(("list_dragon_tiger", trade_date, symbol, min_net_amount, limit))
            return [dragon_tiger_response(market_routes_module)]

        def fetch_dragon_tiger_data(self, trade_date):
            self.calls.append(("fetch_dragon_tiger_data", trade_date))
            return {"trade_date": "2026-05-14", "count": 3}

    fake_service = FakeMarketDataService()
    monkeypatch.setattr(market_routes_module, "_monitoring_market_data_service", fake_service, raising=False)

    list_result = asyncio.run(
        market_routes_module.get_dragon_tiger_list(trade_date, "000001", 10000000.0, 20, object())
    )
    fetch_result = asyncio.run(market_routes_module.fetch_dragon_tiger_data(trade_date, object()))

    assert list_result.data[0].symbol == "000001"
    assert fetch_result.data == {"trade_date": "2026-05-14", "count": 3}
    assert fake_service.calls == [
        ("list_dragon_tiger", trade_date, "000001", 10000000.0, 20),
        ("fetch_dragon_tiger_data", trade_date),
    ]


@pytest.mark.file_test
def test_dragon_tiger_fetch_route_returns_empty_response_without_saving(market_routes_module, monkeypatch):
    trade_date = date(2026, 5, 14)

    class FakeMarketDataService:
        def fetch_dragon_tiger_data(self, trade_date):
            return None

    monkeypatch.setattr(market_routes_module, "_monitoring_market_data_service", FakeMarketDataService(), raising=False)

    result = asyncio.run(market_routes_module.fetch_dragon_tiger_data(trade_date, object()))

    assert result.success is False
    assert result.message == "2026-05-14 无龙虎榜数据"
    assert result.data is None
