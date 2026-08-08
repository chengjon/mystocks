"""OpenStockClient 单元测试.

覆盖:
- 配置注入(base_url / api_key 从构造参数或环境变量)
- X-API-Key header 携带
- 六个端点的请求 body / path / 方法
- 错误 envelope 解析(string detail / dict detail / provider_unavailable)
- provider_unavailable 触发单次重试
- transport 错误转为 OpenStockError

注: 文件中的 "000001" / "sz000001" / "sh600000" 是 mock transport 用的固定测试
fixture,不是业务股票池。所有 HTTP 通过 httpx.MockTransport 拦截,无真实数据源调用。
"""

from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from src.services.openstock import (
    DataCategory,
    OpenStockClient,
    OpenStockError,
    OpenStockProviderUnavailable,
)


def _make_transport(handler):
    """构造一个 httpx MockTransport,转发到 handler(request)->response."""

    def _handler(request: httpx.Request) -> httpx.Response:
        return handler(request)

    return httpx.MockTransport(_handler)


def _make_client(handler, **kwargs: Any) -> OpenStockClient:
    return OpenStockClient(
        base_url="http://openstock.test",
        api_key="test-key",
        transport=_make_transport(handler),
        **kwargs,
    )


# ---- 构造与配置 --------------------------------------------------------


def test_client_requires_base_url_and_api_key(monkeypatch):
    monkeypatch.delenv("OPENSTOCK_BASE_URL", raising=False)
    monkeypatch.delenv("OPENSTOCK_API_KEY", raising=False)
    with pytest.raises(OpenStockError) as exc_info:
        OpenStockClient()
    assert "OPENSTOCK_BASE_URL" in str(exc_info.value)


def test_client_reads_env_when_args_absent(monkeypatch):
    monkeypatch.setenv("OPENSTOCK_BASE_URL", "http://env.openstock/")
    monkeypatch.setenv("OPENSTOCK_API_KEY", "env-key")

    seen_headers: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen_headers.update(request.headers)
        return httpx.Response(200, json={"sources": {}})

    client = OpenStockClient(transport=_make_transport(handler))
    assert client is not None
    client.sources()
    assert seen_headers["x-api-key"] == "env-key"
    client.close()


def test_client_sends_x_api_key_header():
    seen: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen.update(request.headers)
        return httpx.Response(200, json={"data": []})

    with _make_client(handler) as client:
        client.fetch(DataCategory.REALTIME_QUOTES, {"symbol": "000001"})

    assert seen["x-api-key"] == "test-key"
    assert seen["content-type"] == "application/json"


# ---- 六个端点 ---------------------------------------------------------


def test_fetch_sends_correct_body():
    captured: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["path"] = request.url.path
        captured["body"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(200, json={"data": [{"symbol": "000001"}], "source": "eltdx"})

    with _make_client(handler) as client:
        result = client.fetch(DataCategory.REALTIME_QUOTES, {"symbol": "000001"}, request_id="req-1")

    assert captured["path"] == "/data/fetch"
    assert captured["body"] == {
        "data_category": "REALTIME_QUOTES",
        "params": {"symbol": "000001"},
        "request_id": "req-1",
    }
    assert result["source"] == "eltdx"


def test_fetch_accepts_string_category():
    captured: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(200, json={"data": []})

    with _make_client(handler) as client:
        client.fetch("FUND_FLOW", {"symbol": "sz000001"})

    assert captured["body"]["data_category"] == "FUND_FLOW"


def test_batch_validates_request_count():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"results": []})

    with _make_client(handler) as client:
        with pytest.raises(ValueError, match="at most 500"):
            client.batch([{"data_category": "REALTIME_QUOTES"} for _ in range(501)])


def test_batch_sends_requests_array():
    captured: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(200, json={"results": []})

    with _make_client(handler) as client:
        client.batch([
            {"data_category": "REALTIME_QUOTES", "params": {"symbol": "000001"}},
            {"data_category": "KLINES", "params": {"symbol": "000001", "period": "day"}},
        ])

    assert captured["body"]["requests"][0]["data_category"] == "REALTIME_QUOTES"
    assert len(captured["body"]["requests"]) == 2


def test_bars_sends_correct_body():
    captured: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["path"] = request.url.path
        captured["body"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(200, json={"data": [], "data_category": "KLINES"})

    with _make_client(handler) as client:
        client.bars(symbol="000001", period="day", count=100)

    assert captured["path"] == "/data/bars"
    assert captured["body"] == {"symbol": "000001", "period": "day", "count": 100}


def test_snapshot_uses_realtime_quotes():
    captured: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(200, json={"data": []})

    with _make_client(handler) as client:
        client.snapshot("000001")

    assert captured["body"]["data_category"] == "REALTIME_QUOTES"
    assert captured["body"]["params"] == {"symbol": "000001"}


def test_routing_best_sends_correct_body():
    captured: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["path"] = request.url.path
        captured["body"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(200, json={"data_category": "REALTIME_QUOTES", "source": "eltdx"})

    with _make_client(handler) as client:
        client.routing_best(DataCategory.REALTIME_QUOTES)

    assert captured["path"] == "/routing/best"
    assert captured["body"]["data_category"] == "REALTIME_QUOTES"


def test_sources_uses_get():
    captured: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["method"] = request.method
        captured["path"] = request.url.path
        return httpx.Response(200, json={"sources": {}, "categories": []})

    with _make_client(handler) as client:
        result = client.sources()

    assert captured["method"] == "GET"
    assert captured["path"] == "/sources"
    assert "sources" in result


# ---- 错误 envelope 解析 -----------------------------------------------


def test_string_detail_error_raises_openstock_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"detail": "Invalid or missing API key"})

    with _make_client(handler) as client:
        with pytest.raises(OpenStockError) as exc_info:
            client.sources()

    err = exc_info.value
    assert err.status_code == 401
    assert "Invalid or missing API key" in err.message


def test_dict_detail_error_extracts_code():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            422,
            json={"detail": {"code": "invalid_params", "message": "symbol required"}},
        )

    with _make_client(handler) as client:
        with pytest.raises(OpenStockError) as exc_info:
            client.fetch(DataCategory.REALTIME_QUOTES)

    err = exc_info.value
    assert err.status_code == 422
    assert err.code == "invalid_params"
    assert err.message == "symbol required"


def test_provider_unavailable_triggers_single_retry():
    call_count = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        call_count["n"] += 1
        if call_count["n"] == 1:
            return httpx.Response(
                503,
                json={"detail": {"code": "provider_unavailable", "message": "eltdx down"}},
            )
        return httpx.Response(200, json={"data": [], "source": "baostock"})

    with _make_client(handler) as client:
        result = client.fetch(DataCategory.REALTIME_QUOTES, {"symbol": "000001"})

    assert call_count["n"] == 2
    assert result["source"] == "baostock"


def test_provider_unavailable_raises_after_retry_exhausted():
    call_count = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        call_count["n"] += 1
        return httpx.Response(
            503,
            json={"detail": {"code": "provider_unavailable", "message": "eltdx down"}},
        )

    with _make_client(handler) as client:
        with pytest.raises(OpenStockProviderUnavailable) as exc_info:
            client.fetch(DataCategory.REALTIME_QUOTES)

    # 一次原始 + 一次重试 = 2 次
    assert call_count["n"] == 2
    assert exc_info.value.code == "provider_unavailable"


def test_non_provider_error_does_not_retry():
    call_count = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        call_count["n"] += 1
        return httpx.Response(429, json={"detail": "Rate limit exceeded"})

    with _make_client(handler) as client:
        with pytest.raises(OpenStockError) as exc_info:
            client.fetch(DataCategory.REALTIME_QUOTES)

    assert call_count["n"] == 1
    assert exc_info.value.status_code == 429


def test_transport_error_converted_to_openstock_error():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    with _make_client(handler) as client:
        with pytest.raises(OpenStockError) as exc_info:
            client.sources()

    assert "transport error" in str(exc_info.value)


def test_transport_error_retries_once_on_post():
    call_count = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        call_count["n"] += 1
        raise httpx.ReadTimeout("read timed out")

    with _make_client(handler) as client:
        with pytest.raises(OpenStockError):
            client.fetch(DataCategory.REALTIME_QUOTES)

    assert call_count["n"] == 2


# ---- category_mapping -----------------------------------------------


def test_data_category_enum_count():
    from src.services.openstock.category_mapping import DataCategory as DC

    assert len(list(DC)) == 69, f"expected 69 categories, got {len(list(DC))}"


def test_adapter_method_categories_skeleton():
    from src.services.openstock.category_mapping import ADAPTER_METHOD_CATEGORIES

    # 阶段 1 只填充 domain-01 骨架,Phase 2 各域 PR 会扩充
    assert "AkshareMarketAdapter.get_realtime_quote" in ADAPTER_METHOD_CATEGORIES
    assert ADAPTER_METHOD_CATEGORIES["ByapiAdapter.get_realtime_quote"] == DataCategory.REALTIME_QUOTES
