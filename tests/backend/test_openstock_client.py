from __future__ import annotations

import json

import httpx
import pytest

from web.backend.app.services.openstock_client import (
    OpenStockClient,
    OpenStockClientConfig,
    OpenStockInvalidResponse,
    OpenStockProviderUnavailable,
    OpenStockUnsupportedCategory,
)


@pytest.mark.asyncio
async def test_fetch_posts_data_fetch_and_preserves_runtime_metadata() -> None:
    captured: list[dict[str, object]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(
            {
                "method": request.method,
                "path": request.url.path,
                "payload": json.loads(request.content.decode()),
            }
        )
        return httpx.Response(
            200,
            json={
                "data": [{"symbol": "000001.SZ", "price": 12.3}],
                "source": "akshare",
                "endpoint_name": "akshare.stock_zh_a_spot",
                "data_category": "REALTIME_QUOTES",
                "request_id": "req-quotes-1",
                "route_decision_id": "route-1",
                "latency_ms": 12.4,
                "staleness_ms": 0,
            },
        )

    client = OpenStockClient(
        OpenStockClientConfig(base_url="http://openstock.local", timeout_seconds=2.0),
        transport=httpx.MockTransport(handler),
    )

    result = await client.fetch(
        "REALTIME_QUOTES",
        params={"symbols": ["000001.SZ"]},
        request_id="req-quotes-1",
    )

    assert captured == [
        {
            "method": "POST",
            "path": "/data/fetch",
            "payload": {
                "data_category": "REALTIME_QUOTES",
                "params": {"symbols": ["000001.SZ"]},
                "request_id": "req-quotes-1",
            },
        }
    ]
    assert result.data == [{"symbol": "000001.SZ", "price": 12.3}]
    assert result.source == "akshare"
    assert result.data_category == "REALTIME_QUOTES"
    assert result.request_id == "req-quotes-1"
    assert result.route_decision_id == "route-1"
    assert result.latency_ms == 12.4
    assert result.staleness_ms == 0


@pytest.mark.asyncio
async def test_fetch_bars_posts_data_bars_payload() -> None:
    captured: list[dict[str, object]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(json.loads(request.content.decode()))
        return httpx.Response(
            200,
            json={
                "data": [{"date": "2026-06-16", "close": 10.5}],
                "source": "eltdx",
                "endpoint_name": "eltdx.tdx_7709",
                "data_category": "KLINES",
                "request_id": "bars-1",
            },
        )

    client = OpenStockClient(
        OpenStockClientConfig(base_url="http://openstock.local"),
        transport=httpx.MockTransport(handler),
    )

    result = await client.fetch_bars(
        symbol="000001.SZ",
        period="day",
        count=120,
        request_id="bars-1",
    )

    assert captured == [
        {
            "symbol": "000001.SZ",
            "period": "day",
            "count": 120,
            "request_id": "bars-1",
        }
    ]
    assert result.data == [{"date": "2026-06-16", "close": 10.5}]
    assert result.source == "eltdx"
    assert result.data_category == "KLINES"


@pytest.mark.asyncio
async def test_provider_unavailable_is_mapped_without_raw_provider_leak() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            503,
            json={
                "detail": {
                    "code": "provider_unavailable",
                    "message": "Provider adapter failed while fetching data.",
                    "category": "REALTIME_QUOTES",
                    "provider": "akshare",
                    "request_id": "req-failed",
                }
            },
        )

    client = OpenStockClient(
        OpenStockClientConfig(base_url="http://openstock.local"),
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(OpenStockProviderUnavailable) as exc_info:
        await client.fetch("REALTIME_QUOTES", request_id="req-failed")

    error = exc_info.value
    assert error.code == "provider_unavailable"
    assert error.category == "REALTIME_QUOTES"
    assert error.provider == "akshare"
    assert error.request_id == "req-failed"
    assert "stack" not in str(error).lower()


@pytest.mark.asyncio
async def test_unsupported_category_is_mapped_to_typed_error() -> None:
    called = False

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal called
        called = True
        return httpx.Response(422, json={"detail": "Unsupported data_category: LHB"})

    client = OpenStockClient(
        OpenStockClientConfig(base_url="http://openstock.local"),
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(OpenStockUnsupportedCategory) as exc_info:
        await client.fetch("LHB", request_id="lhb-1")

    assert exc_info.value.category == "LHB"
    assert exc_info.value.request_id == "lhb-1"
    assert called is False


@pytest.mark.asyncio
async def test_invalid_success_payload_is_rejected() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"source": "akshare"})

    client = OpenStockClient(
        OpenStockClientConfig(base_url="http://openstock.local"),
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(OpenStockInvalidResponse):
        await client.fetch("REALTIME_QUOTES")
