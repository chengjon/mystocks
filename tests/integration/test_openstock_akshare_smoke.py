"""Phase 2.1b OpenStock akshare facade integration smoke tests.

Real OpenStock gateway calls. Marked @pytest.mark.integration — skipped
by default (no OPENSTOCK_API_KEY env or no -m integration flag).

Run locally:
    export OPENSTOCK_BASE_URL=http://192.168.123.104:8040
    export OPENSTOCK_API_KEY=<ask user>
    pytest -m integration tests/integration/test_openstock_akshare_smoke.py

See: openspec/changes/migrate-data-sources-to-openstock/proposal.md (任务 2.1.1 / 2.1.2)
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
STD_SYMBOL = "sh.600000"


# ---- market_data.py free functions ----------------------------------


class TestAkshareMarketDataFacadeSmoke:
    """src/adapters/akshare/market_data.py facade."""

    def test_get_stock_industry_concept_returns_dict(self):
        from src.adapters.akshare.market_data import get_stock_industry_concept

        result = get_stock_industry_concept(None, SYMBOL)
        assert isinstance(result, dict)
        assert result["symbol"] == SYMBOL
        assert "industries" in result
        assert "concepts" in result
        assert isinstance(result["industries"], list)
        assert isinstance(result["concepts"], list)

    def test_get_stock_industry_concept_industries_nonempty(self):
        """STOCK_INDUSTRY 上游 baostock 稳定,行业字段应非空."""
        from src.adapters.akshare.market_data import get_stock_industry_concept

        result = get_stock_industry_concept(None, SYMBOL)
        assert len(result["industries"]) > 0, f"industries should be non-empty: {result}"

    def test_get_stock_industry_concept_concepts_nonempty(self):
        """TOPICS_CONCEPTS 上游 eltdx 返回 13 条概念,应非空."""
        from src.adapters.akshare.market_data import get_stock_industry_concept

        result = get_stock_industry_concept(None, SYMBOL)
        assert len(result["concepts"]) > 0, f"concepts should be non-empty: {result}"

    def test_get_concept_classify_returns_dataframe(self):
        """SECTOR_QUOTES(concept) 上游 akshare 当前不稳定,本测试接受空 DataFrame."""
        from src.adapters.akshare.market_data import get_concept_classify

        df = get_concept_classify()
        assert isinstance(df, pd.DataFrame)


# ---- stock_info.py StockInfoAdapter async methods -------------------


class TestStockInfoAdapterFacadeSmoke:
    """src/adapters/akshare/stock_info.py StockInfoAdapter facade."""

    @pytest.fixture(scope="class")
    def adapter(self):
        from src.adapters.akshare.stock_info import StockInfoAdapter

        a = StockInfoAdapter()
        yield a
        try:
            a._close()
        except Exception:  # noqa: BLE001
            pass

    def test_get_stock_info_returns_dataframe(self, adapter):
        """ALL_STOCKS 客户端过滤应返回指定股票."""
        df = asyncio.get_event_loop().run_until_complete(
            adapter.get_stock_info(SYMBOL)
        )
        # 应返回 DataFrame,可能空(若 OpenStock 上游 ALL_STOCKS 该时刻未填充)
        assert df is None or isinstance(df, pd.DataFrame)

    def test_get_stock_info_found(self, adapter):
        """对 600000 浦发银行,ALL_STOCKS 应回到匹配行."""
        df = asyncio.get_event_loop().run_until_complete(
            adapter.get_stock_info(SYMBOL)
        )
        if df is None or df.empty:
            pytest.skip("ALL_STOCKS 上游未返回数据,跳过匹配检查")
        assert len(df) >= 1

    def test_get_concept_classify(self, adapter):
        """SECTOR_QUOTES(concept) 上游不稳定,接受空 DataFrame."""
        df = asyncio.get_event_loop().run_until_complete(
            adapter.get_concept_classify()
        )
        assert isinstance(df, pd.DataFrame)

    def test_get_industry_classify(self, adapter):
        """SECTOR_QUOTES(industry) 上游不稳定,接受空 DataFrame."""
        df = asyncio.get_event_loop().run_until_complete(
            adapter.get_industry_classify()
        )
        assert isinstance(df, pd.DataFrame)

    def test_get_sse_daily(self, adapter):
        """SSE_DAILY OpenStock 暂未覆盖,应返回空 DataFrame(无 raise)."""
        df = asyncio.get_event_loop().run_until_complete(
            adapter.get_sse_daily("2026-07-04")
        )
        assert isinstance(df, pd.DataFrame)
