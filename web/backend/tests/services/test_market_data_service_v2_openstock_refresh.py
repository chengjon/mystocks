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

    def get_stock_blocktrade(self, _trade_date=None):
        raise AssertionError("EastMoney block trade provider should not be called")

    def get_stock_lhb_detail(self, _trade_date):
        raise AssertionError("EastMoney dragon tiger provider should not be called")


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


@pytest.mark.asyncio
async def test_fetch_and_save_blocktrade_consumes_openstock_without_local_provider():
    openstock_client = _FakeOpenStockClient(
        [
            {
                "symbol": "000001",
                "name": "平安银行",
                "trade_date": "2026-06-17",
                "deal_price": 10.3,
                "close": 10.5,
                "premium_ratio": -1.9,
                "amount": 1030000,
                "volume": 100000,
                "amount_float_market_cap_ratio": 0.01,
                "buyer_name": "机构专用",
                "seller_name": "深南大道证券营业部",
            }
        ]
    )
    session = _FakeSession()

    service = MarketDataServiceV2()
    service.em_adapter = _FailingEastMoneyAdapter()
    service.SessionLocal = lambda: session
    service._openstock_client_factory = lambda: openstock_client

    result = service.fetch_and_save_blocktrade("2026-06-17")

    assert result == {"success": True, "message": "保存成功: 1条"}
    assert openstock_client.fetch_calls == [
        {
            "data_category": "BLOCK_TRADE",
            "params": {"trade_date": "2026-06-17"},
            "request_id": None,
        }
    ]
    assert openstock_client.closed is True
    assert session.committed is True
    assert session.closed is True
    assert len(session.added) == 1

    saved = session.added[0]
    assert saved.symbol == "000001"
    assert saved.stock_name == "平安银行"
    assert saved.trade_date == date(2026, 6, 17)
    assert saved.deal_price == 10.3
    assert saved.close_price == 10.5
    assert saved.premium_ratio == -1.9
    assert saved.deal_amount == 1030000
    assert saved.deal_volume == 100000
    assert saved.turnover_rate == 0.01
    assert saved.buyer_name == "机构专用"
    assert saved.seller_name == "深南大道证券营业部"


@pytest.mark.asyncio
async def test_fetch_and_save_lhb_detail_consumes_openstock_without_local_provider():
    openstock_client = _FakeOpenStockClient(
        [
            {
                "symbol": "000001",
                "name": "平安银行",
                "trade_date": "2026-06-17",
                "reason": "日涨幅偏离值达7%",
                "buy_amount": 1000,
                "sell_amount": 200,
                "net_amount": 800,
                "turnover": 3.4,
            }
        ]
    )
    session = _FakeSession()

    service = MarketDataServiceV2()
    service.em_adapter = _FailingEastMoneyAdapter()
    service.SessionLocal = lambda: session
    service._openstock_client_factory = lambda: openstock_client

    result = service.fetch_and_save_lhb_detail("2026-06-17")

    assert result == {"success": True, "message": "保存成功: 1条"}
    assert openstock_client.fetch_calls == [
        {
            "data_category": "DRAGON_TIGER",
            "params": {"trade_date": "2026-06-17"},
            "request_id": None,
        }
    ]
    assert openstock_client.closed is True
    assert session.committed is True
    assert session.closed is True
    assert len(session.added) == 1

    saved = session.added[0]
    assert saved.symbol == "000001"
    assert saved.name == "平安银行"
    assert saved.trade_date == date(2026, 6, 17)
    assert saved.reason == "日涨幅偏离值达7%"
    assert saved.buy_amount == 1000
    assert saved.sell_amount == 200
    assert saved.net_amount == 800
    assert saved.turnover_rate == 3.4
    assert saved.institution_buy is None
    assert saved.institution_sell is None
