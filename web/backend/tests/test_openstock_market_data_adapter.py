"""
OpenStockMarketDataSourceAdapter 单元测试 (B4.014 S5 / M1k-2 / M1m step 6)

覆盖:
- get_data("quotes", ...) 正常 + 字段归一
- get_data("klines", ...) 正常 + time→datetime 字段映射
- get_data("<unknown>", ...) 抛 ValueError
- health_check() /health/live 200 OK → HEALTHY
- health_check() HTTPError → FAILED
- get_metrics() 累计统计
- 异常路径 metrics error_count 累计

Plan ref: docs/architecture/M1K_M1M_EXECUTION_PLAN_2026-07-01.md §三 步骤 6
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.services.data_source_interface import HealthStatusEnum
from app.services.openstock_client import OpenStockClientError, OpenStockFetchResult
from app.services.openstock_market_data_adapter import (
    DEFAULT_BASE_URL,
    ENDPOINT_ROUTES,
    PERIOD_MAP,
    OpenStockMarketDataSourceAdapter,
)


def _make_fetch_result(data: Any, *, source: str = "openstock", category: str = None) -> OpenStockFetchResult:
    return OpenStockFetchResult(
        data=data,
        source=source,
        endpoint_name="test_endpoint",
        data_category=category,
        request_id="test_req",
    )


@pytest.fixture
def adapter():
    a = OpenStockMarketDataSourceAdapter({"base_url": "http://test:8040", "timeout": 1.0})
    yield a
    # no async cleanup needed since _client is None unless _get_client was called


def test_constants_are_well_formed():
    assert PERIOD_MAP == {"daily": "day", "weekly": "week", "monthly": "month"}
    assert ENDPOINT_ROUTES == {"quotes": "REALTIME_QUOTES"}
    assert DEFAULT_BASE_URL == "http://192.168.123.104:8040"


def test_init_defaults_when_config_missing():
    a = OpenStockMarketDataSourceAdapter({})
    assert a._client_config.base_url == DEFAULT_BASE_URL
    # type comes from IDataSource.__init__ which falls back to "unknown"
    assert a.type == "unknown"


def test_init_with_explicit_config():
    a = OpenStockMarketDataSourceAdapter({"type": "openstock_market", "base_url": "http://h:1", "timeout": 7.5})
    assert a.type == "openstock_market"
    assert a._client_config.base_url == "http://h:1"
    assert a._client_config.timeout_seconds == 7.5


@pytest.mark.asyncio
async def test_get_quotes_success_normalizes_fields(adapter):
    rows = [
        {"Symbol": "000001", "Price": 12.34, "Volume": 1000},
        {"symbol": "600519", "price": 1800.0},
    ]
    mock_client = type("StubClient", (), {})()
    mock_client.fetch = AsyncMock(return_value=_make_fetch_result(rows, category="REALTIME_QUOTES"))
    mock_client.aclose = AsyncMock()
    adapter._client = mock_client

    result = await adapter.get_data("quotes", {"symbols": ["000001", "600519"]})

    assert result["status"] == "success"
    assert result["endpoint"] == "quotes"
    assert result["source"] == "openstock"
    # both "data" and "quotes" keys for back-compat
    assert isinstance(result["data"], list)
    assert result["data"] == result["quotes"]
    # lowercase normalization
    assert result["quotes"][0] == {"symbol": "000001", "price": 12.34, "volume": 1000}
    assert result["quotes"][1] == {"symbol": "600519", "price": 1800.0}
    # symbols joined for fetch call
    mock_client.fetch.assert_awaited_once()
    args, kwargs = mock_client.fetch.call_args
    assert args[0] == "REALTIME_QUOTES"
    assert kwargs["params"] == {"symbols": "000001,600519"}


@pytest.mark.asyncio
async def test_get_quotes_accepts_scalar_symbol_string(adapter):
    mock_client = type("StubClient", (), {})()
    mock_client.fetch = AsyncMock(return_value=_make_fetch_result([], category="REALTIME_QUOTES"))
    mock_client.aclose = AsyncMock()
    adapter._client = mock_client

    await adapter.get_data("quotes", {"symbols": "000001"})

    _, kwargs = mock_client.fetch.call_args
    assert kwargs["params"] == {"symbols": "000001"}


@pytest.mark.asyncio
async def test_get_klines_success_maps_time_to_datetime(adapter):
    rows = [
        {"time": "2026-06-01", "open": 10.0, "high": 11.0, "low": 9.5, "close": 10.5, "volume": 1000},
        {"date": "2026-06-02", "open": 10.5, "high": 12.0, "low": 10.4, "close": 11.8, "volume": 2000},
    ]
    mock_client = type("StubClient", (), {})()
    mock_client.fetch_bars = AsyncMock(return_value=_make_fetch_result(rows, category="KLINES"))
    mock_client.aclose = AsyncMock()
    adapter._client = mock_client

    result = await adapter.get_data("klines", {"symbol": "000001", "period": "daily", "count": 2})

    assert result["status"] == "success"
    assert result["endpoint"] == "klines"
    assert result["candles"] == result["data"]
    # time → datetime mapping
    assert result["candles"][0]["datetime"] == "2026-06-01"
    assert result["candles"][0]["open"] == 10.0
    # date → datetime (fallback)
    assert result["candles"][1]["datetime"] == "2026-06-02"

    # fetch_bars called with PERIOD_MAP-translated period
    mock_client.fetch_bars.assert_awaited_once_with(symbol="000001", period="day", count=2)


@pytest.mark.asyncio
async def test_get_klines_period_mapping(adapter):
    mock_client = type("StubClient", (), {})()
    mock_client.fetch_bars = AsyncMock(return_value=_make_fetch_result([], category="KLINES"))
    mock_client.aclose = AsyncMock()
    adapter._client = mock_client

    await adapter.get_data("klines", {"symbol": "S", "period": "weekly"})
    _, kwargs = mock_client.fetch_bars.call_args
    assert kwargs["period"] == "week"

    # default count when missing
    await adapter.get_data("klines", {"symbol": "S"})
    _, kwargs = mock_client.fetch_bars.call_args
    assert kwargs["count"] == 100


@pytest.mark.asyncio
async def test_get_klines_requires_symbol(adapter):
    mock_client = type("StubClient", (), {})()
    mock_client.fetch_bars = AsyncMock()
    adapter._client = mock_client

    with pytest.raises(ValueError, match="symbol"):
        await adapter.get_data("klines", {})


@pytest.mark.asyncio
async def test_get_data_unsupported_endpoint_raises(adapter):
    with pytest.raises(ValueError, match="Unsupported endpoint"):
        await adapter.get_data("trades", {})


@pytest.mark.asyncio
async def test_get_data_records_error_metrics_on_exception(adapter):
    mock_client = type("StubClient", (), {})()
    mock_client.fetch = AsyncMock(side_effect=OpenStockClientError("boom"))
    adapter._client = mock_client

    with pytest.raises(OpenStockClientError):
        await adapter.get_data("quotes", {"symbols": "000001"})

    metrics = adapter.get_metrics()
    assert metrics["total_requests"] == 1
    assert metrics["error_count"] == 1
    assert metrics["success_count"] == 0
    assert "boom" in metrics["last_error"]
    assert metrics["availability"] == 0.0


@pytest.mark.asyncio
async def test_get_data_success_metrics_includes_availability_and_base_url(adapter):
    mock_client = type("StubClient", (), {})()
    mock_client.fetch = AsyncMock(return_value=_make_fetch_result([], category="REALTIME_QUOTES"))
    adapter._client = mock_client

    await adapter.get_data("quotes", {"symbols": "X"})

    m = adapter.get_metrics()
    assert m["total_requests"] == 1
    assert m["success_count"] == 1
    assert m["error_count"] == 0
    assert m["last_error"] is None
    assert m["last_latency_ms"] is not None
    assert m["availability"] == 100.0
    assert m["base_url"] == "http://test:8040"
    assert m["type"] == "unknown"  # config didn't include "type"


@pytest.mark.asyncio
async def test_health_check_healthy_on_2xx(monkeypatch, adapter):
    class FakeResponse:
        status_code = 200

    class FakeAsyncClient:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_a):
            return False

        async def get(self, path):
            assert path == "/health/live"
            return FakeResponse()

    monkeypatch.setattr(httpx, "AsyncClient", FakeAsyncClient)

    health = await adapter.health_check()
    assert health.status == HealthStatusEnum.HEALTHY
    assert "200" in health.message


@pytest.mark.asyncio
async def test_health_check_degraded_on_5xx(monkeypatch, adapter):
    class FakeResponse:
        status_code = 503

    class FakeAsyncClient:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_a):
            return False

        async def get(self, path):
            return FakeResponse()

    monkeypatch.setattr(httpx, "AsyncClient", FakeAsyncClient)

    health = await adapter.health_check()
    assert health.status == HealthStatusEnum.DEGRADED


@pytest.mark.asyncio
async def test_health_check_failed_on_http_error(monkeypatch, adapter):
    class FailingAsyncClient:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_a):
            return False

        async def get(self, path):
            raise httpx.ConnectError("conn refused")

    monkeypatch.setattr(httpx, "AsyncClient", FailingAsyncClient)

    health = await adapter.health_check()
    assert health.status == HealthStatusEnum.FAILED
    assert "conn refused" in health.message


def test_transform_kline_row_handles_non_mapping():
    out = OpenStockMarketDataSourceAdapter._transform_kline_row("not a dict")
    assert out == {}


def test_transform_kline_row_preserves_unknown_keys_as_lowercase():
    # "TIME" (case-insensitive) maps to "datetime"; "Close" → "close"
    out = OpenStockMarketDataSourceAdapter._transform_kline_row({"TIME": "x", "Close": 1.0})
    assert out == {"datetime": "x", "close": 1.0}


def test_transform_quote_row_lowercases():
    out = OpenStockMarketDataSourceAdapter._transform_quote_row({"SYMBOL": "X", "Price": 1.0})
    assert out == {"symbol": "X", "price": 1.0}


def test_coerce_rows_handles_various_shapes():
    coerce = OpenStockMarketDataSourceAdapter._coerce_rows
    assert coerce(None) == []
    assert coerce([{"a": 1}]) == [{"a": 1}]
    assert coerce({"rows": [{"b": 2}]}) == [{"b": 2}]
    assert coerce({"data": [{"c": 3}]}) == [{"c": 3}]
    assert coerce({"items": [{"d": 4}]}) == [{"d": 4}]
    assert coerce({"quotes": [{"e": 5}]}) == [{"e": 5}]
    assert coerce({"candles": [{"f": 6}]}) == [{"f": 6}]
    # no known key
    assert coerce({"unrelated": 1}) == []
