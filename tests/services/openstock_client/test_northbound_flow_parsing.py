"""SOT §五.2 unit parse tests for NORTHBOUND_FLOW category.

Phase 1.1 fund-flow domain (B4.014). Covers:
- OpenStock real JSON shape mapping (normalized fields per OpenStock API_REFERENCE.md)
- Empty data list tolerance
- Missing optional fields tolerance
- Field type conversion correctness (numeric fields)

Reference live response shape captured 2026-06-29 (limit=2):
    data: [{
        "balance": float,
        "board_name": str,        # e.g. "沪股通" / "深股通"
        "down_count": int,
        "flat_count": int,
        "flow_type": str,          # e.g. "northbound"
        "fund_direction": str,
        "fund_net_inflow": float,
        "index_change_pct": float | None,
        "net_buy_amount": float,
        "related_index": str,
        "trade_date": str,
        "trade_status": str,
        "up_count": int
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
async def test_northbound_flow_normal_payload_preserves_all_normalized_fields() -> None:
    payload = {
        "data": [
            {
                "trade_date": "2026-06-27",
                "flow_type": "northbound",
                "board_name": "沪股通",
                "fund_direction": "inflow",
                "trade_status": "normal",
                "net_buy_amount": 1234567.89,
                "fund_net_inflow": 9876543.21,
                "balance": 100000.0,
                "up_count": 600,
                "down_count": 400,
                "flat_count": 50,
                "related_index": "上证指数",
                "index_change_pct": 0.45,
            },
            {
                "trade_date": "2026-06-27",
                "flow_type": "northbound",
                "board_name": "深股通",
                "fund_direction": "outflow",
                "trade_status": "normal",
                "net_buy_amount": -2345678.0,
                "fund_net_inflow": -1234567.0,
                "balance": -50000.0,
                "up_count": 300,
                "down_count": 700,
                "flat_count": 20,
                "related_index": "深证成指",
                "index_change_pct": -0.32,
            },
        ],
        "source": "akshare",
        "endpoint_name": "akshare.stock_hsgt_fund_flow_summary_em",
        "data_category": "NORTHBOUND_FLOW",
        "request_id": "req-nf-1",
    }

    captured: list[dict[str, object]] = []
    client = _capture_payload_client(captured, payload)

    result = await client.fetch(
        "NORTHBOUND_FLOW", params={"limit": 2}, request_id="req-nf-1"
    )

    assert captured == [
        {
            "path": "/data/fetch",
            "payload": {
                "data_category": "NORTHBOUND_FLOW",
                "params": {"limit": 2},
                "request_id": "req-nf-1",
            },
        }
    ]
    assert isinstance(result.data, list)
    assert len(result.data) == 2
    assert result.data[0]["board_name"] == "沪股通"
    assert result.data[0]["net_buy_amount"] == pytest.approx(1234567.89)
    assert result.data[1]["fund_direction"] == "outflow"
    assert result.data[1]["net_buy_amount"] == pytest.approx(-2345678.0)
    assert result.data_category == "NORTHBOUND_FLOW"
    assert result.source == "akshare"


@pytest.mark.asyncio
async def test_northbound_flow_empty_data_list_is_valid() -> None:
    payload = {
        "data": [],
        "source": "akshare",
        "data_category": "NORTHBOUND_FLOW",
        "request_id": "req-nf-empty",
    }

    client = _build_client(payload)
    result = await client.fetch("NORTHBOUND_FLOW", request_id="req-nf-empty")

    assert result.data == []
    assert result.data_category == "NORTHBOUND_FLOW"


@pytest.mark.asyncio
async def test_northbound_flow_partial_missing_optional_fields_tolerated() -> None:
    payload = {
        "data": [
            {
                "trade_date": "2026-06-27",
                "board_name": "沪股通",
                "net_buy_amount": 500000.0,
            }
        ],
        "source": "akshare",
        "data_category": "NORTHBOUND_FLOW",
    }

    client = _build_client(payload)
    result = await client.fetch("NORTHBOUND_FLOW")

    assert len(result.data) == 1
    assert result.data[0]["trade_date"] == "2026-06-27"
    assert result.data[0]["board_name"] == "沪股通"
    # Optional fields missing — must not raise, no assertion on absent keys
    assert "index_change_pct" not in result.data[0]


@pytest.mark.asyncio
async def test_northbound_flow_null_optional_fields_preserved_as_none() -> None:
    payload = {
        "data": [
            {
                "trade_date": "2026-06-27",
                "board_name": "沪股通",
                "index_change_pct": None,
                "related_index": None,
                "net_buy_amount": 100000.0,
            }
        ],
        "source": "akshare",
        "data_category": "NORTHBOUND_FLOW",
    }

    client = _build_client(payload)
    result = await client.fetch("NORTHBOUND_FLOW")

    assert result.data[0]["index_change_pct"] is None
    assert result.data[0]["related_index"] is None
    assert result.data[0]["net_buy_amount"] == pytest.approx(100000.0)


@pytest.mark.asyncio
async def test_northbound_flow_integer_fields_coerced_to_float_via_optional_float() -> None:
    payload = {
        "data": [
            {
                "trade_date": "2026-06-27",
                "board_name": "沪股通",
                "net_buy_amount": 1234567,
                "up_count": 600,
            }
        ],
        "source": "akshare",
        "data_category": "NORTHBOUND_FLOW",
    }

    client = _build_client(payload)
    result = await client.fetch("NORTHBOUND_FLOW")

    row = result.data[0]
    # int values pass through; client does not transform data keys, only metadata
    assert row["net_buy_amount"] == 1234567
    assert row["up_count"] == 600


@pytest.mark.asyncio
async def test_northbound_flow_missing_data_key_raises_invalid_response() -> None:
    payload = {
        "source": "akshare",
        "data_category": "NORTHBOUND_FLOW",
    }

    client = _build_client(payload)
    with pytest.raises(OpenStockInvalidResponse):
        await client.fetch("NORTHBOUND_FLOW")


@pytest.mark.asyncio
async def test_northbound_flow_metadata_latency_and_staleness_parsed_as_float() -> None:
    payload = {
        "data": [
            {"trade_date": "2026-06-27", "board_name": "沪股通"},
        ],
        "source": "akshare",
        "data_category": "NORTHBOUND_FLOW",
        "request_id": "req-nf-meta",
        "latency_ms": 42.5,
        "staleness_ms": 0,
    }

    client = _build_client(payload)
    result = await client.fetch("NORTHBOUND_FLOW", request_id="req-nf-meta")

    assert result.latency_ms == pytest.approx(42.5)
    assert result.staleness_ms == pytest.approx(0.0)
