"""OpenStockMarketDataSourceAdapter 单元测试 (B4.014 S5 / M1k-2 / M1m step 6)

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
from unittest.mock import AsyncMock

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
    return a
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


def test_init_injects_api_key_from_env(monkeypatch):
    """B4.014-M1o: OPENSTOCK_SECURITY_API_KEY env 自动注入到 client headers。"""
    monkeypatch.setenv("OPENSTOCK_SECURITY_API_KEY", "sk-test-12345")
    a = OpenStockMarketDataSourceAdapter({"base_url": "http://h:1"})
    headers = a._client_config.headers
    assert headers is not None
    assert headers.get("X-API-Key") == "sk-test-12345"


def test_init_merges_custom_headers_from_config(monkeypatch):
    """config.custom_headers 与 env API key 合并(env 优先级高)。"""
    monkeypatch.setenv("OPENSTOCK_SECURITY_API_KEY", "sk-env-key")
    custom = {"User-Agent": "test/1.0", "Accept": "application/json"}
    a = OpenStockMarketDataSourceAdapter({"base_url": "http://h:1", "custom_headers": custom})
    headers = a._client_config.headers
    assert headers is not None
    assert headers["User-Agent"] == "test/1.0"
    assert headers["Accept"] == "application/json"
    assert headers["X-API-Key"] == "sk-env-key"


def test_init_no_api_key_when_env_missing(monkeypatch):
    """Env OPENSTOCK_SECURITY_API_KEY 未设时,headers 为 None(向后兼容)。"""
    monkeypatch.delenv("OPENSTOCK_SECURITY_API_KEY", raising=False)
    a = OpenStockMarketDataSourceAdapter({"base_url": "http://h:1"})
    # 无 custom_headers 也无 env key → None
    assert a._client_config.headers is None


@pytest.mark.asyncio
async def test_get_quotes_success_normalizes_fields(adapter):
    """B4.014-M1n: 多 symbol 循环调用(每次单 symbol),合并结果。
    OpenStock 不支持 symbol=000001,600519 逗号分隔(provider 503)。
    """
    # 每次单 symbol 调用返 1 行
    def _fetch_side_effect(category, *, params=None, request_id=None):
        sym = (params or {}).get("symbol")
        return _make_fetch_result(
            [{"Symbol": sym, "Price": 12.34, "Volume": 1000, "pct_chg": 1.5}],
            category="REALTIME_QUOTES",
        )

    mock_client = type("StubClient", (), {})()
    mock_client.fetch = AsyncMock(side_effect=_fetch_side_effect)
    mock_client.aclose = AsyncMock()
    adapter._client = mock_client

    result = await adapter.get_data("quotes", {"symbols": ["000001", "600519"]})

    assert result["status"] == "success"
    assert result["endpoint"] == "quotes"
    assert result["source"] == "openstock"
    assert isinstance(result["data"], list)
    assert result["data"] == result["quotes"]
    # 2 个 symbol → 2 次调用 → 2 行结果
    assert len(result["quotes"]) == 2
    # B4.014-M1n 修复:pct_chg → change_percent 字段映射
    assert "change_percent" in result["quotes"][0]
    assert result["quotes"][0]["change_percent"] == 1.5
    # symbol 去前缀 + lowercase 归一(此处无 sz/sh 前缀,直接 small symbol)
    assert result["quotes"][0]["symbol"] in ("000001", "600519")
    # 调用次数 == symbols 数量(每个单 symbol 一次)
    assert mock_client.fetch.await_count == 2
    # 每次调用都用单数 symbol
    for call in mock_client.fetch.call_args_list:
        args, kwargs = call
        assert args[0] == "REALTIME_QUOTES"
        # B4.014-M1n 修复:必须用 symbol 单数
        assert "symbol" in kwargs["params"]
        assert "symbols" not in kwargs["params"]


@pytest.mark.asyncio
async def test_get_quotes_accepts_scalar_symbol_string(adapter):
    """单 symbol 字符串输入也应正常工作(内部统一成 list 处理)。"""
    mock_client = type("StubClient", (), {})()
    mock_client.fetch = AsyncMock(return_value=_make_fetch_result([], category="REALTIME_QUOTES"))
    mock_client.aclose = AsyncMock()
    adapter._client = mock_client

    await adapter.get_data("quotes", {"symbols": "000001"})

    _, kwargs = mock_client.fetch.call_args
    # B4.014-M1n 修复:单数 symbol
    assert kwargs["params"] == {"symbol": "000001"}


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


# ===========================================================================
# B4.014-M1n: 生产烟测修复测试(发现 #2, #3, #5)
# ====================================================================================


def test_transform_quote_row_maps_pct_chg_to_change_percent():
    """发现 #2 SHOWSTOPPER:OpenStock 返 pct_chg,前端期望 change_percent。"""
    row = {
        "symbol": "sz000001",
        "name": "平安银行",
        "price": 10.16,
        "pct_chg": 1.0945273631840737,
        "change": 0.11,
        "volume": 90688900,
    }
    out = OpenStockMarketDataSourceAdapter._transform_quote_row(row)
    assert "change_percent" in out
    assert out["change_percent"] == 1.0945273631840737
    # 原 pct_chg 保留(无害)
    assert "pct_chg" in out


def test_transform_quote_row_preserves_existing_change_percent():
    """如果数据源已经给 change_percent,不覆盖。"""
    row = {"symbol": "X", "change_percent": 2.5, "pct_chg": 1.0}
    out = OpenStockMarketDataSourceAdapter._transform_quote_row(row)
    assert out["change_percent"] == 2.5  # 不被 pct_chg 覆盖


def test_transform_quote_row_strips_sz_sh_bj_prefix():
    """发现 #5 LOW:OpenStock 返 sz000001/sh600519/bj430047,前端期望 000001/600519/430047。"""
    for raw, expected in [
        ("sz000001", "000001"),
        ("sh600519", "600519"),
        ("bj430047", "430047"),
        ("SZ000001", "SZ000001"),  # 大写前缀不去(保守)
        ("000001", "000001"),       # 无前缀原样
        ("szabcdef", "szabcdef"),   # 后缀非数字不去
        ("sz12345", "sz12345"),     # 长度 < 8 不去(sz+5 位)
    ]:
        out = OpenStockMarketDataSourceAdapter._transform_quote_row({"symbol": raw})
        assert out["symbol"] == expected, f"raw={raw!r} got={out['symbol']!r}"


def test_transform_kline_row_strips_symbol_prefix_and_truncates_iso8601():
    """发现 #3 HIGH + #5 LOW:ISO8601 截断到 10 字符日期 + symbol 去前缀。"""
    row = {
        "symbol": "sz000001",
        "time": "2026-06-30T15:00:00+08:00",
        "open": 10.22,
        "high": 10.22,
        "low": 10.04,
        "close": 10.05,
        "volume": 111135200,
        "amount": 1121201536.0,
        "period": "day",
    }
    out = OpenStockMarketDataSourceAdapter._transform_kline_row(row)
    # 发现 #3: ISO8601 截断到日期
    assert out["datetime"] == "2026-06-30"
    assert len(out["datetime"]) == 10
    # 发现 #5: symbol 去前缀
    assert out["symbol"] == "000001"
    # 其他字段透传
    assert out["open"] == 10.22
    assert out["close"] == 10.05
    assert out["period"] == "day"


def test_transform_kline_row_date_field_also_truncated():
    """Date 字段(若存在)也截断到 10 字符。"""
    row = {"date": "2026-06-30T00:00:00+08:00", "open": 1.0}
    out = OpenStockMarketDataSourceAdapter._transform_kline_row(row)
    assert out["datetime"] == "2026-06-30"


def test_strip_exchange_prefix_safety():
    """单独验证 _strip_exchange_prefix 不会误剥。"""
    strip = OpenStockMarketDataSourceAdapter._strip_exchange_prefix
    # 不剥的情况
    assert strip("000001") == "000001"
    assert strip("sh689009") == "689009"
    # 不误剥:虽然以 "sh" 开头但后缀非全数字
    assert strip("shabc123") == "shabc123"
    # None / 非字符串原样返回
    assert strip(None) is None
    assert strip(123) == 123
    assert strip("") == ""


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
