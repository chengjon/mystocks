import os
from datetime import date

import pytest

os.environ.setdefault("POSTGRESQL_HOST", "localhost")
os.environ.setdefault("POSTGRESQL_PORT", "5432")
os.environ.setdefault("POSTGRESQL_USER", "tester")
os.environ.setdefault("POSTGRESQL_PASSWORD", "tester")
os.environ.setdefault("POSTGRESQL_DATABASE", "tester")

from web.backend.app.services.market_data_service_v2 import MarketDataServiceV2
from web.backend.app.services.openstock_client import OpenStockFetchResult


class _FailingEastMoneyAdapter:
    def get_etf_spot(self):
        raise AssertionError("EastMoney ETF provider should not be called")


class _FakeOpenStockClient:
    def __init__(self, records):
        self.records = records
        self.fetch_calls = []
        self.closed = False

    async def fetch(self, data_category, *, params=None, request_id=None):
        self.fetch_calls.append(
            {
                "data_category": data_category,
                "params": params,
                "request_id": request_id,
            }
        )
        return OpenStockFetchResult(
            data=self.records,
            source="openstock",
            endpoint_name="akshare.fund_etf_spot_em",
            data_category=data_category,
            request_id=request_id,
        )

    async def aclose(self):
        self.closed = True


class _FakeQuery:
    def filter(self, *_args, **_kwargs):
        return self

    def first(self):
        return None


class _FakeSession:
    def __init__(self):
        self.added = []
        self.committed = False
        self.closed = False

    def query(self, *_args, **_kwargs):
        return _FakeQuery()

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        self.committed = True

    def close(self):
        self.closed = True


@pytest.mark.asyncio
async def test_fetch_and_save_etf_spot_consumes_openstock_without_local_provider():
    openstock_client = _FakeOpenStockClient(
        [
            {
                "symbol": "510300",
                "name": "沪深300ETF",
                "price": 4.123,
                "pct_chg": 1.2,
                "change": 0.049,
                "volume": 1200000,
                "amount": 4947600,
                "open": 4.08,
                "high": 4.15,
                "low": 4.01,
                "prev_close": 4.074,
                "turnover_rate": 0.87,
                "market_cap": 12000000000,
                "float_market_cap": 11000000000,
            }
        ]
    )
    session = _FakeSession()

    service = MarketDataServiceV2()
    service.em_adapter = _FailingEastMoneyAdapter()
    service.SessionLocal = lambda: session
    service._openstock_client_factory = lambda: openstock_client

    result = service.fetch_and_save_etf_spot()

    assert result == {
        "success": True,
        "message": "保存成功: 1条",
        "total": 1,
        "saved": 1,
    }
    assert openstock_client.fetch_calls == [
        {
            "data_category": "ETF_SPOT",
            "params": {"limit": 500},
            "request_id": None,
        }
    ]
    assert openstock_client.closed is True
    assert session.committed is True
    assert session.closed is True
    assert len(session.added) == 1

    saved = session.added[0]
    assert saved.symbol == "510300"
    assert saved.name == "沪深300ETF"
    assert saved.trade_date == date.today()
    assert saved.latest_price == 4.123
    assert saved.change_percent == 1.2
    assert saved.change_amount == 0.049
    assert saved.volume == 1200000
    assert saved.amount == 4947600
    assert saved.open_price == 4.08
    assert saved.high_price == 4.15
    assert saved.low_price == 4.01
    assert saved.prev_close == 4.074
    assert saved.turnover_rate == 0.87
    assert saved.total_market_cap == 12000000000
    assert saved.circulating_market_cap == 11000000000
