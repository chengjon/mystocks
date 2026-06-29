"""SOT §五.2 unit parse tests for NORTHBOUND_HOLDING category.

Phase 1.1 fund-flow domain (B4.014). Covers:
- OpenStock real JSON shape mapping (normalized fields per OpenStock API_REFERENCE.md)
- Empty data list tolerance
- Null optional fields tolerance (live probe confirmed add_shares/add_amount/
  holding_market_cap_change are frequently null)
- Symbol normalization acceptance (sh/sz/sz000001 prefixes)
- Missing data key rejection

Reference live response shape captured 2026-06-29 (sh600519, limit=2):
    data: [{
        "add_amount": float | None,         # frequently null
        "add_shares": float | None,          # frequently null
        "change_pct": float,
        "close": float,
        "holding_market_cap": float,
        "holding_market_cap_change": None,   # frequently null
        "holding_shares": float,
        "holding_shares_ratio": float,
        "symbol": str,
        "trade_date": str
    }]
"""

from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from web.backend.app.services.openstock_client import (
    OpenStockClient,
    OpenStockClientConfig,
    OpenStockInvalidResponse,
)


def _build_client(handler_response: dict[str, Any]) -> OpenStockClient:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=handler_response)

    return OpenStockClient(
        OpenStockClientConfig(base_url="http://openstock.local", timeout_seconds=2.0),
        transport=httpx.MockTransport(handler),
    )


def _capture_payload_client(
    captured: list[dict[str, object]], response_json: dict[str, Any]
) -> OpenStockClient:
    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(
            {
                "path": request.url.path,
                "payload": json.loads(request.content.decode()),
            }
        )
        return httpx.Response(200, json=response_json)

    return OpenStockClient(
        OpenStockClientConfig(base_url="http://openstock.local"),
        transport=httpx.MockTransport(handler),
    )


@pytest.mark.asyncio
async def test_northbound_holding_normal_payload_preserves_all_fields() -> None:
    payload = {
        "data": [
            {
                "symbol": "sh600519",
                "trade_date": "2026-06-27",
                "close": 1685.50,
                "change_pct": 1.23,
                "holding_shares": 150000000.0,
                "holding_market_cap": 252825000000.0,
                "holding_shares_ratio": 9.5,
                "add_shares": 500000.0,
                "add_amount": 842750000.0,
                "holding_market_cap_change": 5000000000.0,
            }
        ],
        "source": "akshare",
        "endpoint_name": "akshare.stock_hsgt_north_acc_flow_in_em",
        "data_category": "NORTHBOUND_HOLDING",
        "request_id": "req-nh-1",
    }

    captured: list[dict[str, object]] = []
    client = _capture_payload_client(captured, payload)

    result = await client.fetch(
        "NORTHBOUND_HOLDING",
        params={"symbol": "sh600519", "limit": 5},
        request_id="req-nh-1",
    )

    assert captured == [
        {
            "path": "/data/fetch",
            "payload": {
                "data_category": "NORTHBOUND_HOLDING",
                "params": {"symbol": "sh600519", "limit": 5},
                "request_id": "req-nh-1",
            },
        }
    ]
    row = result.data[0]
    assert row["symbol"] == "sh600519"
    assert row["trade_date"] == "2026-06-27"
    assert row["close"] == pytest.approx(1685.50)
    assert row["holding_shares"] == pytest.approx(150000000.0)
    assert row["holding_shares_ratio"] == pytest.approx(9.5)
    assert row["add_shares"] == pytest.approx(500000.0)
    assert result.data_category == "NORTHBOUND_HOLDING"
    assert result.source == "akshare"


@pytest.mark.asyncio
async def test_northbound_holding_null_optional_fields_preserved_as_none() -> None:
    """Live probe confirmed add_shares/add_amount/holding_market_cap_change
    are frequently null when there is no period-over-period change."""
    payload = {
        "data": [
            {
                "symbol": "sh600519",
                "trade_date": "2026-06-27",
                "close": 1685.50,
                "change_pct": 0.0,
                "holding_shares": 150000000.0,
                "holding_market_cap": 252825000000.0,
                "holding_shares_ratio": 9.5,
                "add_shares": None,
                "add_amount": None,
                "holding_market_cap_change": None,
            }
        ],
        "source": "akshare",
        "data_category": "NORTHBOUND_HOLDING",
    }

    client = _build_client(payload)
    result = await client.fetch(
        "NORTHBOUND_HOLDING", params={"symbol": "sh600519"}
    )

    row = result.data[0]
    assert row["add_shares"] is None
    assert row["add_amount"] is None
    assert row["holding_market_cap_change"] is None
    assert row["holding_shares"] == pytest.approx(150000000.0)


@pytest.mark.asyncio
async def test_northbound_holding_empty_data_list_is_valid() -> None:
    payload = {
        "data": [],
        "source": "akshare",
        "data_category": "NORTHBOUND_HOLDING",
        "request_id": "req-nh-empty",
    }

    client = _build_client(payload)
    result = await client.fetch(
        "NORTHBOUND_HOLDING",
        params={"symbol": "sh600519"},
        request_id="req-nh-empty",
    )

    assert result.data == []
    assert result.data_category == "NORTHBOUND_HOLDING"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "symbol",
    ["sh600519", "sz000001", "sh601318", "sz300750"],
)
async def test_northbound_holding_accepts_normalized_symbol_prefixes(symbol: str) -> None:
    payload = {
        "data": [
            {
                "symbol": symbol,
                "trade_date": "2026-06-27",
                "close": 10.0,
                "holding_shares": 1000.0,
            }
        ],
        "source": "akshare",
        "data_category": "NORTHBOUND_HOLDING",
    }

    captured: list[dict[str, object]] = []
    client = _capture_payload_client(captured, payload)

    result = await client.fetch(
        "NORTHBOUND_HOLDING", params={"symbol": symbol, "limit": 1}
    )

    assert captured[0]["payload"] == {
        "data_category": "NORTHBOUND_HOLDING",
        "params": {"symbol": symbol, "limit": 1},
    }
    assert result.data[0]["symbol"] == symbol


@pytest.mark.asyncio
async def test_northbound_holding_partial_fields_tolerated() -> None:
    payload = {
        "data": [
            {
                "symbol": "sh600519",
                "trade_date": "2026-06-27",
                "close": 1685.50,
            }
        ],
        "source": "akshare",
        "data_category": "NORTHBOUND_HOLDING",
    }

    client = _build_client(payload)
    result = await client.fetch(
        "NORTHBOUND_HOLDING", params={"symbol": "sh600519"}
    )

    row = result.data[0]
    assert row["symbol"] == "sh600519"
    assert row["close"] == pytest.approx(1685.50)
    assert "holding_shares" not in row


@pytest.mark.asyncio
async def test_northbound_holding_missing_data_key_raises_invalid_response() -> None:
    payload = {
        "source": "akshare",
        "data_category": "NORTHBOUND_HOLDING",
    }

    client = _build_client(payload)
    with pytest.raises(OpenStockInvalidResponse):
        await client.fetch(
            "NORTHBOUND_HOLDING", params={"symbol": "sh600519"}
        )


@pytest.mark.asyncio
async def test_northbound_holding_metadata_route_and_latency_parsed() -> None:
    payload = {
        "data": [
            {
                "symbol": "sh600519",
                "trade_date": "2026-06-27",
                "close": 1685.50,
                "holding_shares": 150000000.0,
            }
        ],
        "source": "akshare",
        "endpoint_name": "akshare.stock_hsgt_north_acc_flow_in_em",
        "data_category": "NORTHBOUND_HOLDING",
        "request_id": "req-nh-meta",
        "route_decision_id": "route-nh-1",
        "latency_ms": 88.2,
        "staleness_ms": 1200.0,
    }

    client = _build_client(payload)
    result = await client.fetch(
        "NORTHBOUND_HOLDING",
        params={"symbol": "sh600519"},
        request_id="req-nh-meta",
    )

    assert result.route_decision_id == "route-nh-1"
    assert result.latency_ms == pytest.approx(88.2)
    assert result.staleness_ms == pytest.approx(1200.0)
    assert (
        result.endpoint_name == "akshare.stock_hsgt_north_acc_flow_in_em"
    )
