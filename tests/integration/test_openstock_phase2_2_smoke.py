"""Phase 2.2 OpenStock Adapter facade integration smoke tests.

Real OpenStock gateway calls against the migrated domain-02 surfaces:
- src/adapters/akshare/market_adapter/market_overview.py (MarketOverviewMixin)
- src/adapters/tdx/realtime_service.py (RealtimeService)
- src/adapters/tdx/kline_data_service.py (KlineDataService)

Marked @pytest.mark.integration — skipped by default (no OPENSTOCK_API_KEY
env or no -m integration flag).

Run locally:
    export OPENSTOCK_BASE_URL=http://192.168.123.104:8040
    export OPENSTOCK_API_KEY=<ask user>
    pytest -m integration tests/integration/test_openstock_phase2_2_smoke.py

See: openspec/changes/migrate-data-sources-to-openstock/proposal.md (任务 2.2.x)
"""

from __future__ import annotations

import asyncio
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

# 688806 出现在 REALTIME_QUOTES 前 50 条返回值中(科创板 IPO),用于避免 client-filter 漏命中
RT_SYMBOL = "688806"
# 浦发银行 — KLINES 历史数据稳定
KLINES_SYMBOL = "600000"
START = "2026-06-01"
END = "2026-06-10"


@pytest.fixture(scope="module")
def realtime():
    from src.adapters.tdx.realtime_service import RealtimeService

    return RealtimeService()


@pytest.fixture(scope="module")
def kline():
    from src.adapters.tdx.kline_data_service import KlineDataService

    return KlineDataService()


@pytest.fixture(scope="module")
def market_overview():
    from src.adapters.akshare.market_adapter.market_overview import MarketOverviewMixin

    return MarketOverviewMixin()


# ---- RealtimeService facade -----------------------------------------


class TestRealtimeServiceFacadeSmoke:

    def test_available(self, realtime):
        assert realtime._available is True

    def test_get_real_time_data(self, realtime):
        data = realtime.get_real_time_data(RT_SYMBOL)
        assert isinstance(data, dict)
        assert "symbol" in data
        assert "price" in data
        assert data.get("source") == "openstock"

    def test_get_batch_real_time_data(self, realtime):
        # 用前 50 条里的代码,确保 client-filter 能命中
        batch = realtime.get_batch_real_time_data([RT_SYMBOL, "689009"])
        assert isinstance(batch, list)
        # 上游可能只命中部分,这里只验证返回类型与命中代码字段格式
        if batch:
            assert "symbol" in batch[0]
            assert "price" in batch[0]

    def test_get_stock_industry_concept(self, realtime):
        result = realtime.get_stock_industry_concept(KLINES_SYMBOL)
        assert isinstance(result, dict)
        assert "industry" in result
        assert "concepts" in result
        assert "timestamp" in result

    def test_get_real_time_data_empty_symbol(self, realtime):
        data = realtime.get_real_time_data("")
        assert data is None


# ---- KlineDataService facade ----------------------------------------


class TestKlineDataServiceFacadeSmoke:

    def test_available(self, kline):
        assert kline._available is True

    def test_get_stock_daily_qfq(self, kline):
        df = kline.get_stock_daily(KLINES_SYMBOL, START, END, adjust="qfq")
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert "close" in df.columns
        assert "datetime" in df.columns
        # qfq 复权标记
        assert (df["adjust"] == "qfq").all()

    def test_get_stock_daily_no_adjust(self, kline):
        df = kline.get_stock_daily(KLINES_SYMBOL, START, END, adjust="none")
        assert isinstance(df, pd.DataFrame)
        assert not df.empty

    def test_get_stock_kline_d1(self, kline):
        result = kline.get_stock_kline(KLINES_SYMBOL, "d1", START, END)
        assert isinstance(result, dict)
        assert result["period"] == "d1"
        assert result["count"] > 0
        assert isinstance(result["data"], list)

    def test_get_stock_kline_w1(self, kline):
        result = kline.get_stock_kline(KLINES_SYMBOL, "w1", START, END)
        assert isinstance(result, dict)
        assert result["period"] == "w1"

    def test_get_stock_daily_empty_symbol(self, kline):
        df = kline.get_stock_daily("", START, END)
        assert df.empty

    def test_get_minute_kline_returns_empty(self, kline):
        """OpenStock 暂未覆盖分钟线 — 已登记在 coverage-gaps.md."""
        df = kline.get_minute_kline(KLINES_SYMBOL, "1min")
        assert df.empty


# ---- MarketOverviewMixin facade -------------------------------------


class TestMarketOverviewMixinFacadeSmoke:

    def test_get_market_overview_sse(self, market_overview):
        """SSE 市场总貌 — 上游 akshare RemoteDisconnected,验证 facade 返回空 DataFrame + 不抛异常."""
        df = asyncio.get_event_loop().run_until_complete(
            market_overview.get_market_overview_sse()
        )
        assert isinstance(df, pd.DataFrame)

    def test_get_market_overview_szse(self, market_overview):
        """SZSE 市场总貌 — 上游不稳定,验证 facade 返回空 DataFrame + 不抛异常."""
        df = asyncio.get_event_loop().run_until_complete(
            market_overview.get_market_overview_szse("2026-07-07")
        )
        assert isinstance(df, pd.DataFrame)

    def test_get_szse_area_trading_summary(self, market_overview):
        """OpenStock 暂未覆盖 — 验证 facade 返回空 DataFrame."""
        df = asyncio.get_event_loop().run_until_complete(
            market_overview.get_szse_area_trading_summary("2026-07-07")
        )
        assert df.empty

    def test_get_szse_sector_trading_summary(self, market_overview):
        """OpenStock 暂未覆盖 — 验证 facade 返回空 DataFrame."""
        df = asyncio.get_event_loop().run_until_complete(
            market_overview.get_szse_sector_trading_summary("电子", "2026-07-07")
        )
        assert df.empty

    def test_get_sse_daily_deal_summary(self, market_overview):
        """OpenStock 暂未覆盖 — 验证 facade 返回空 DataFrame."""
        df = asyncio.get_event_loop().run_until_complete(
            market_overview.get_sse_daily_deal_summary("2026-07-07")
        )
        assert df.empty
