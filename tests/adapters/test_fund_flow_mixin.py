"""
Unit tests for FundFlowMixin OpenStock integration (Wave 1, Phase 0.1).

Verifies that ``AkshareMarketDataAdapter`` correctly accepts and stores
an ``OpenStockClient``, and that ``FundFlowMixin`` methods can reach it.
"""

from __future__ import annotations

import sys
from unittest.mock import AsyncMock, MagicMock

import pytest

# Ensure web/backend is on sys.path so `app.services.openstock_client` is importable.
sys.path.insert(0, "web/backend")


@pytest.fixture
def mock_openstock_client() -> MagicMock:
    """A mock OpenStockClient whose fetch() is an AsyncMock returning empty data by default."""
    client = MagicMock()
    client.fetch = AsyncMock(return_value=MagicMock(data=[]))
    return client


class TestAdapterConstructorInjection:
    """Phase 0.1 — adapter constructor accepts ``openstock_client``."""

    def test_no_arg_constructs_default_client(self):
        """``AkshareMarketDataAdapter()`` with no args builds a default client."""
        from src.adapters.akshare.market_adapter import AkshareMarketDataAdapter

        adapter = AkshareMarketDataAdapter()
        assert adapter._openstock_client is not None
        # Default client is a real OpenStockClient (not a MagicMock).
        from app.services.openstock_client import OpenStockClient

        assert isinstance(adapter._openstock_client, OpenStockClient)

    def test_explicit_client_is_stored(self, mock_openstock_client):
        """``AkshareMarketDataAdapter(openstock_client=...)`` stores the injected client."""
        from src.adapters.akshare.market_adapter import AkshareMarketDataAdapter

        adapter = AkshareMarketDataAdapter(openstock_client=mock_openstock_client)
        assert adapter._openstock_client is mock_openstock_client

    def test_mixin_can_reach_client(self, mock_openstock_client):
        """``FundFlowMixin`` methods see ``self._openstock_client``."""
        from src.adapters.akshare.market_adapter import AkshareMarketDataAdapter

        adapter = AkshareMarketDataAdapter(openstock_client=mock_openstock_client)
        # FundFlowMixin is a parent class — verify the attribute is reachable.
        assert hasattr(adapter, "_openstock_client")
        assert adapter._openstock_client is mock_openstock_client


# ------------------------------------------------------------------
# Phase 0.2 — Mixin method tests (stubbed OpenStockClient)
# ------------------------------------------------------------------

NORTHBOUND_FLOW_ROWS = [
    {
        "board_name": "沪股通",
        "fund_direction": "北向",
        "net_buy_amount": 12.34,
        "index_change_pct": 0.56,
        "trade_date": "2026-06-29",
        "up_count": 800,
        "down_count": 600,
        "flat_count": 100,
        "related_index": "上证指数",
        "fund_net_inflow": 10.0,
    },
]

NORTHBOUND_HOLDING_ROWS = [
    {
        "trade_date": "2026-06-29",
        "close": 1850.0,
        "change_pct": 1.23,
        "holding_shares": 1000000,
        "holding_market_cap": 1.85e9,
        "holding_shares_ratio": 4.5,
        "add_shares": 50000,
        "add_amount": 9.25e7,
        "holding_market_cap_change": -1.0,
    },
]


class TestFundFlowMixinOpenStockMethods:
    """Phase 0.2 — Mixin methods call self._openstock_client.fetch()."""

    @pytest.fixture(autouse=True)
    def _adapter(self, mock_openstock_client):
        from src.adapters.akshare.market_adapter import AkshareMarketDataAdapter

        self.adapter = AkshareMarketDataAdapter(openstock_client=mock_openstock_client)
        self.mock_client = mock_openstock_client

    # ---- get_stock_hsgt_fund_flow_summary_em ----

    @pytest.mark.asyncio
    async def test_hsgt_summary_returns_dataframe_on_success(self):
        """Returns a DataFrame with translated columns when data is available."""
        self.mock_client.fetch.return_value = MagicMock(data=NORTHBOUND_FLOW_ROWS)

        df = await self.adapter.get_stock_hsgt_fund_flow_summary_em("2026-06-20", "2026-06-29")

        assert not df.empty
        assert len(df) == 1
        assert "板块" in df.columns
        assert df.iloc[0]["板块"] == "沪股通"
        assert df.iloc[0]["成交净买额"] == 12.34
        assert "start_date" in df.columns
        assert "end_date" in df.columns

    @pytest.mark.asyncio
    async def test_hsgt_summary_returns_empty_on_no_data(self):
        """Returns an empty DataFrame when OpenStock returns empty data."""
        self.mock_client.fetch.return_value = MagicMock(data=[])

        df = await self.adapter.get_stock_hsgt_fund_flow_summary_em("2026-06-20", "2026-06-29")

        assert df.empty

    @pytest.mark.asyncio
    async def test_hsgt_summary_propagates_error(self):
        """OpenStockClientError is NOT swallowed — it propagates to caller."""
        from app.services.openstock_client import OpenStockClientError

        self.mock_client.fetch.side_effect = OpenStockClientError("timeout")

        with pytest.raises(OpenStockClientError, match="timeout"):
            await self.adapter.get_stock_hsgt_fund_flow_summary_em("2026-06-20", "2026-06-29")

    # ---- get_stock_hsgt_north_acc_flow_in_em ----

    @pytest.mark.asyncio
    async def test_north_acc_returns_dataframe_on_success(self):
        """Returns a DataFrame with translated columns when data is available."""
        self.mock_client.fetch.return_value = MagicMock(data=NORTHBOUND_HOLDING_ROWS)

        df = await self.adapter.get_stock_hsgt_north_acc_flow_in_em("600519")

        assert not df.empty
        assert len(df) == 1
        assert "symbol" in df.columns
        assert df.iloc[0]["symbol"] == "600519"
        assert df.iloc[0]["持股数量"] == 1000000
        assert df.iloc[0]["持股市值"] == 1.85e9

    @pytest.mark.asyncio
    async def test_north_acc_returns_empty_on_no_data(self):
        """Returns an empty DataFrame when OpenStock returns empty data."""
        self.mock_client.fetch.return_value = MagicMock(data=[])

        df = await self.adapter.get_stock_hsgt_north_acc_flow_in_em("600519")

        assert df.empty

    @pytest.mark.asyncio
    async def test_north_acc_propagates_error(self):
        """OpenStockClientError is NOT swallowed — it propagates to caller."""
        from app.services.openstock_client import OpenStockClientError

        self.mock_client.fetch.side_effect = OpenStockClientError("timeout")

        with pytest.raises(OpenStockClientError, match="timeout"):
            await self.adapter.get_stock_hsgt_north_acc_flow_in_em("600519")
