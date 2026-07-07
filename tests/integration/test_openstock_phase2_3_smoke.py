"""Phase 2.3 OpenStock Adapter facade integration smoke tests.

Real OpenStock gateway calls against the migrated domain-03/04 surfaces:
- src/adapters/akshare/financial_data.py (get_financial_data + get_news_data)
- src/adapters/akshare/market_adapter/forecast_analysis.py (ForecastAnalysisMixin)

Marked @pytest.mark.integration — skipped by default (no OPENSTOCK_API_KEY
env or no -m integration flag).

Run locally:
    export OPENSTOCK_BASE_URL=http://192.168.123.104:8040
    export OPENSTOCK_API_KEY=<ask user>
    pytest -m integration tests/integration/test_openstock_phase2_3_smoke.py

See: openspec/changes/migrate-data-sources-to-openstock/proposal.md (任务 2.3.1, 2.3.3)
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

SYMBOL = "600000"  # 浦发银行 — fixture


@pytest.fixture(scope="module")
def forecast_mixin():
    from src.adapters.akshare.market_adapter.forecast_analysis import ForecastAnalysisMixin

    return ForecastAnalysisMixin()


# ---- financial_data free functions ---------------------------------


class TestFinancialDataFacadeSmoke:

    def test_get_financial_data(self):
        from src.adapters.akshare.financial_data import get_financial_data

        df = get_financial_data(None, SYMBOL, "annual")
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert "eps" in df.columns
        assert "net_profit" in df.columns
        assert (df["query_symbol"] == SYMBOL).all()

    def test_get_financial_data_empty_symbol(self):
        from src.adapters.akshare.financial_data import get_financial_data

        df = get_financial_data(None, "", "annual")
        assert df.empty

    def test_get_news_data_with_symbol(self):
        from src.adapters.akshare.financial_data import get_news_data

        news = get_news_data(None, SYMBOL, 5)
        assert isinstance(news, list)
        if news:
            assert "title" in news[0]
            assert "source" in news[0]

    def test_get_news_data_no_symbol_returns_empty(self):
        """OpenStock STOCK_NEWS 不接受 symbol=None — 已登记在 coverage-gaps.md."""
        from src.adapters.akshare.financial_data import get_news_data

        news = get_news_data(None, None, 3)
        assert news == []


# ---- ForecastAnalysisMixin facade ----------------------------------


class TestForecastAnalysisFacadeSmoke:

    def test_get_stock_profit_forecast_em(self, forecast_mixin):
        """FORECAST_DATA(em) 上游 OpenStock 当前返空 — 验证 facade 返空 DataFrame 不抛异常."""
        df = asyncio.get_event_loop().run_until_complete(
            forecast_mixin.get_stock_profit_forecast_em(SYMBOL)
        )
        assert isinstance(df, pd.DataFrame)

    def test_get_stock_profit_forecast_ths(self, forecast_mixin):
        """FORECAST_DATA(ths) 上游 OpenStock 当前返空 — 验证 facade 返空 DataFrame 不抛异常."""
        df = asyncio.get_event_loop().run_until_complete(
            forecast_mixin.get_stock_profit_forecast_ths(SYMBOL)
        )
        assert isinstance(df, pd.DataFrame)

    def test_get_stock_technical_indicator_em(self, forecast_mixin):
        """OpenStock 暂未覆盖技术指标 — 验证 facade 返空 DataFrame."""
        df = asyncio.get_event_loop().run_until_complete(
            forecast_mixin.get_stock_technical_indicator_em(SYMBOL)
        )
        assert df.empty

    def test_get_stock_account_statistics_em(self, forecast_mixin):
        """OpenStock 暂未覆盖股票账户统计 — 验证 facade 返空 DataFrame."""
        df = asyncio.get_event_loop().run_until_complete(
            forecast_mixin.get_stock_account_statistics_em("202606")
        )
        assert df.empty
