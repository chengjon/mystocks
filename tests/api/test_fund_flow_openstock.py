"""Phase 1.1 / Wave 1 API e2e tests for fund_flow OpenStock switch (B4.014).

Verifies that the two switched endpoints (`hsgt-summary` and
`north-stock/{symbol}`) correctly:
1. Invoke FundFlowMixin (via AkshareMarketDataAdapter), which delegates to
   OpenStockClient.fetch with the right category and params.
2. Translate OpenStock normalized fields into the frontend truth-source
   contract (Chinese wide-table).
3. Propagate `source=openstock` and `provider=akshare` provenance.
4. Return DATA_NOT_FOUND when OpenStock yields an empty list.
5. Return INTERNAL_SERVER_ERROR when OpenStockClient raises.

Scope: these tests stub ``AkshareMarketDataAdapter._openstock_client``
so the adapter's Mixin methods use a fake client.  The FastAPI
request → response pipeline is exercised end-to-end (dependency override
for ``get_current_user``, real router, real Pydantic response shaping).
"""

from __future__ import annotations

import os
import sys
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

# Ensure backend import path resolves before importing app.* modules
_BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../web/backend"))
if _BACKEND_ROOT not in sys.path:
    sys.path.insert(0, _BACKEND_ROOT)

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.akshare_market import router
from app.api.akshare_market.base import akshare_market_adapter
from app.core.security import User, get_current_user
from app.services.openstock_client import (
    OpenStockClientError,
    OpenStockFetchResult,
)


def _mock_user() -> User:
    """Stand-in authenticated user; tests don't depend on user identity."""
    return User(
        id=1,
        username="test_admin",
        role="admin",
        email="test_admin@mystocks.local",
    )


@pytest.fixture()
def api_client():
    """FastAPI TestClient with auth stubbed and akshare_market router mounted."""
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: _mock_user()
    return TestClient(app)


def _result(rows: list[dict[str, Any]], data_category: str) -> OpenStockFetchResult:
    return OpenStockFetchResult(
        data=rows,
        source="akshare",
        data_category=data_category,
        endpoint_name=f"akshare.{data_category.lower()}",
        request_id="req-test",
        latency_ms=10.0,
        staleness_ms=0.0,
    )


# ---------------------------------------------------------------------------
# hsgt-summary (NORTHBOUND_FLOW)
# ---------------------------------------------------------------------------


def test_hsgt_summary_translates_openstock_northbound_flow_to_chinese_wide_table(
    api_client, monkeypatch
):
    """Endpoint should delegate to FundFlowMixin, which calls
    self._openstock_client.fetch(NORTHBOUND_FLOW) and translates
    the normalized fields into the frontend truth-source contract."""
    rows = [
        {
            "trade_date": "2026-06-29",
            "board_name": "沪股通",
            "fund_direction": "北向",
            "net_buy_amount": 1234567.89,
            "index_change_pct": 1.16,
            "up_count": 930,
            "down_count": 668,
            "flat_count": 38,
            "related_index": "上证指数",
            "fund_net_inflow": 0.0,
        },
        {
            "trade_date": "2026-06-29",
            "board_name": "深股通",
            "fund_direction": "北向",
            "net_buy_amount": 987654.0,
            "index_change_pct": 0.19,
            "up_count": 1200,
            "down_count": 500,
            "flat_count": 20,
            "related_index": "深证成指",
            "fund_net_inflow": 0.0,
        },
    ]

    fake_client = MagicMock()
    fake_client.fetch = AsyncMock(return_value=_result(rows, "NORTHBOUND_FLOW"))

    monkeypatch.setattr(akshare_market_adapter, "_openstock_client", fake_client)

    resp = api_client.get(
        "/api/akshare/market/fund-flow/hsgt-summary",
        params={"start_date": "2026-06-20", "end_date": "2026-06-29"},
    )

    assert resp.status_code == 200
    payload = resp.json()
    assert payload["success"] is True

    data = payload["data"]
    # Provenance
    assert data["source"] == "openstock"
    assert data["provider"] == "akshare"
    assert data["count"] == 2
    assert data["columns"] == ["板块", "资金方向", "成交净买额", "指数涨跌幅", "交易日"]
    assert data["date_range"] == {"start": "2026-06-20", "end": "2026-06-29"}

    # Translated first row — frontend truth-source fields present
    first = data["data"][0]
    assert first["板块"] == "沪股通"
    assert first["资金方向"] == "北向"
    assert first["成交净买额"] == pytest.approx(1234567.89)
    assert first["指数涨跌幅"] == pytest.approx(1.16)
    assert first["交易日"] == "2026-06-29"

    # OpenStock richness preserved as extras (not consumed by frontend but
    # kept for downstream observability)
    assert first["关联指数"] == "上证指数"
    assert first["同期上涨家数"] == 930

    # Verify the Mixin called fetch with the right category + params
    fake_client.fetch.assert_awaited_once_with(
        "NORTHBOUND_FLOW",
        params={"start_date": "2026-06-20", "end_date": "2026-06-29"},
    )


def test_hsgt_summary_empty_openstock_payload_returns_data_not_found(
    api_client, monkeypatch
):
    """When OpenStock returns an empty data list, the endpoint should return
    a DATA_NOT_FOUND error (HTTP 200 with success=False per project envelope)."""
    fake_client = MagicMock()
    fake_client.fetch = AsyncMock(return_value=_result([], "NORTHBOUND_FLOW"))

    monkeypatch.setattr(akshare_market_adapter, "_openstock_client", fake_client)

    resp = api_client.get(
        "/api/akshare/market/fund-flow/hsgt-summary",
        params={"start_date": "2026-06-20", "end_date": "2026-06-29"},
    )

    assert resp.status_code == 200
    payload = resp.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "DATA_NOT_FOUND"


def test_hsgt_summary_openstock_client_error_returns_internal_error(
    api_client, monkeypatch
):
    """When OpenStockClient.fetch raises OpenStockClientError, the endpoint
    must convert it to INTERNAL_SERVER_ERROR (not 500 / not crash)."""
    fake_client = MagicMock()
    fake_client.fetch = AsyncMock(
        side_effect=OpenStockClientError("simulated upstream timeout")
    )

    monkeypatch.setattr(akshare_market_adapter, "_openstock_client", fake_client)

    resp = api_client.get(
        "/api/akshare/market/fund-flow/hsgt-summary",
        params={"start_date": "2026-06-20", "end_date": "2026-06-29"},
    )

    assert resp.status_code == 200
    payload = resp.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "INTERNAL_SERVER_ERROR"


# ---------------------------------------------------------------------------
# north-stock/{symbol} (NORTHBOUND_HOLDING)
# ---------------------------------------------------------------------------


def test_north_stock_translates_openstock_northbound_holding_to_chinese_wide_table(
    api_client, monkeypatch
):
    """Endpoint should delegate to FundFlowMixin, which calls
    self._openstock_client.fetch(NORTHBOUND_HOLDING) and translates
    per-share holding rows into the akshare-era Chinese contract."""
    rows = [
        {
            "trade_date": "2017-03-16",
            "close": 374.77,
            "change_pct": 0.024020497491,
            "holding_shares": 73748969,
            "holding_market_cap": 27638901112.13,
            "holding_shares_ratio": 5.87,
            "add_shares": None,
            "add_amount": None,
            "holding_market_cap_change": None,
        },
        {
            "trade_date": "2017-06-07",
            "close": 459.37,
            "change_pct": 2.350608261664,
            "holding_shares": 72363390,
            "holding_market_cap": 33241570464.3,
            "holding_shares_ratio": 5.76,
            "add_shares": 61122.0,
            "add_amount": 27924649.2228,
            "holding_market_cap_change": 790866540.54,
        },
    ]

    fake_client = MagicMock()
    fake_client.fetch = AsyncMock(return_value=_result(rows, "NORTHBOUND_HOLDING"))

    monkeypatch.setattr(akshare_market_adapter, "_openstock_client", fake_client)

    resp = api_client.get("/api/akshare/market/fund-flow/north-stock/600519")

    assert resp.status_code == 200
    payload = resp.json()
    assert payload["success"] is True

    data = payload["data"]
    assert data["symbol"] == "600519"
    assert data["source"] == "openstock"
    assert data["provider"] == "akshare"
    assert data["fund_direction"] == "north"
    assert data["count"] == 2
    assert data["columns"] == [
        "持股日期",
        "持股数量",
        "持股市值",
        "持股比例",
        "增持数量",
        "增持金额",
    ]

    first = data["data"][0]
    assert first["symbol"] == "600519"
    assert first["持股日期"] == "2017-03-16"
    assert first["持股数量"] == 73748969
    assert first["持股市值"] == pytest.approx(27638901112.13)
    assert first["持股比例"] == pytest.approx(5.87)
    assert first["收盘价"] == pytest.approx(374.77)

    # Verify the Mixin called fetch with the right category + params
    fake_client.fetch.assert_awaited_once_with(
        "NORTHBOUND_HOLDING", params={"symbol": "600519"}
    )


def test_north_stock_empty_openstock_payload_returns_data_not_found(
    api_client, monkeypatch
):
    """An unknown symbol should produce DATA_NOT_FOUND, not an empty success
    payload (matches the akshare-era contract)."""
    fake_client = MagicMock()
    fake_client.fetch = AsyncMock(return_value=_result([], "NORTHBOUND_HOLDING"))

    monkeypatch.setattr(akshare_market_adapter, "_openstock_client", fake_client)

    resp = api_client.get("/api/akshare/market/fund-flow/north-stock/000000")

    assert resp.status_code == 200
    payload = resp.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "DATA_NOT_FOUND"


def test_north_stock_openstock_client_error_returns_internal_error(
    api_client, monkeypatch
):
    """Upstream OpenStock failure must not surface as a 500 to the frontend;
    the endpoint returns the project error envelope with INTERNAL_SERVER_ERROR."""
    fake_client = MagicMock()
    fake_client.fetch = AsyncMock(
        side_effect=OpenStockClientError("upstream 502 from OpenStock")
    )

    monkeypatch.setattr(akshare_market_adapter, "_openstock_client", fake_client)

    resp = api_client.get("/api/akshare/market/fund-flow/north-stock/600519")

    assert resp.status_code == 200
    payload = resp.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "INTERNAL_SERVER_ERROR"
