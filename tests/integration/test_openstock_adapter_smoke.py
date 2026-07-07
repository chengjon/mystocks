"""Phase 2.1a OpenStock Adapter facade integration smoke tests.

Real OpenStock gateway calls. Marked @pytest.mark.integration — skipped
by default (no OPENSTOCK_API_KEY env or no -m integration flag).

Run locally:
    export OPENSTOCK_BASE_URL=http://192.168.123.104:8040
    export OPENSTOCK_API_KEY=<ask user>
    pytest -m integration tests/integration/test_openstock_adapter_smoke.py

See: openspec/changes/migrate-data-sources-to-openstock/proposal.md (任务 6.5)
"""

from __future__ import annotations

import os

import pandas as pd
import pytest

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not os.getenv("OPENSTOCK_API_KEY"),
        reason="OPENSTOCK_API_KEY not set — integration test requires real OpenStock gateway",
    ),
]

SYMBOL = "600000"  # 浦发银行 — fixture,非业务股票池
INDEX = "000300"   # 沪深300 — fixture
START = "2026-06-01"
END = "2026-06-10"


@pytest.fixture(scope="module")
def tushare():
    from src.adapters.tushare_adapter import TushareDataSource

    return TushareDataSource()


@pytest.fixture(scope="module")
def baostock():
    from src.adapters.baostock_adapter import BaostockDataSource

    return BaostockDataSource()


@pytest.fixture(scope="module")
def byapi():
    from src.adapters.byapi_adapter import ByapiAdapter

    return ByapiAdapter()


# ---- TushareDataSource facade ----------------------------------------


class TestTushareFacadeSmoke:

    def test_available(self, tushare):
        assert tushare.available is True

    def test_get_stock_daily(self, tushare):
        df = tushare.get_stock_daily(SYMBOL, START, END)
        assert not df.empty
        assert len(df) >= 3

    def test_get_index_daily(self, tushare):
        df = tushare.get_index_daily("000001", START, END)
        assert not df.empty

    def test_get_stock_basic(self, tushare):
        info = tushare.get_stock_basic(SYMBOL)
        assert isinstance(info, dict)
        assert "code" in info or "symbol" in info

    def test_get_index_components(self, tushare):
        codes = tushare.get_index_components(INDEX)
        assert len(codes) > 0

    def test_get_real_time_data(self, tushare):
        rt = tushare.get_real_time_data(SYMBOL)
        assert isinstance(rt, dict)
        assert "error" not in rt

    def test_get_market_calendar(self, tushare):
        df = tushare.get_market_calendar(START, END)
        assert not df.empty

    def test_get_news_data(self, tushare):
        news = tushare.get_news_data(symbol=SYMBOL, limit=3)
        assert isinstance(news, list)


# ---- BaostockDataSource facade ---------------------------------------


class TestBaostockFacadeSmoke:

    def test_available(self, baostock):
        assert baostock.available is True

    def test_get_stock_daily(self, baostock):
        df = baostock.get_stock_daily(SYMBOL, START, END)
        assert not df.empty

    def test_get_index_daily(self, baostock):
        df = baostock.get_index_daily("000001", START, END)
        assert not df.empty

    def test_get_stock_basic(self, baostock):
        info = baostock.get_stock_basic(SYMBOL)
        assert isinstance(info, dict)

    def test_get_index_components(self, baostock):
        codes = baostock.get_index_components(INDEX)
        assert len(codes) > 0

    def test_get_real_time_data(self, baostock):
        rt = baostock.get_real_time_data(SYMBOL)
        assert isinstance(rt, dict)

    def test_get_market_calendar(self, baostock):
        df = baostock.get_market_calendar(START, END)
        assert not df.empty

    def test_get_news_data(self, baostock):
        news = baostock.get_news_data(symbol=SYMBOL, limit=3)
        assert isinstance(news, list)


# ---- ByapiAdapter facade ---------------------------------------------


class TestByapiFacadeSmoke:

    def test_available(self, byapi):
        assert byapi.available is True

    def test_source_name(self, byapi):
        assert byapi.source_name == "Byapi"

    def test_supported_markets(self, byapi):
        assert "CN_A" in byapi.supported_markets

    def test_get_kline_data(self, byapi):
        df = byapi.get_kline_data(SYMBOL, START, END, frequency="daily")
        assert not df.empty

    def test_get_realtime_quotes(self, byapi):
        df = byapi.get_realtime_quotes([SYMBOL])
        assert isinstance(df, pd.DataFrame)

    def test_get_stock_list(self, byapi):
        df = byapi.get_stock_list()
        # ALL_STOCKS — may return large list
        assert isinstance(df, pd.DataFrame)

    def test_get_fundamental_data(self, byapi):
        df = byapi.get_fundamental_data(SYMBOL, "latest", "income")
        assert isinstance(df, pd.DataFrame)

    def test_get_limit_up_stocks(self, byapi):
        df = byapi.get_limit_up_stocks("2026-06-03")
        assert isinstance(df, pd.DataFrame)
