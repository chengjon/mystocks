from __future__ import annotations

import json

import httpx
import pytest

from web.backend.app.services.windows_bridge_adapter import (
    BRIDGE_CONTRACT_VERSION_HEADER,
    MultiSourceBridgeAdapter,
)


class _AsyncClientStub:
    def __init__(self, *, response: httpx.Response | None = None, error: Exception | None = None) -> None:
        self.response = response
        self.error = error
        self.post_calls: list[dict[str, object]] = []
        self.get_calls: list[dict[str, object]] = []

    async def __aenter__(self) -> _AsyncClientStub:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        return False

    async def post(self, url: str, *, json: dict[str, object], headers: dict[str, str]) -> httpx.Response:
        self.post_calls.append({"url": url, "json": json, "headers": dict(headers)})
        if self.error is not None:
            raise self.error
        assert self.response is not None
        return self.response

    async def get(self, url: str, *, headers: dict[str, str]) -> httpx.Response:
        self.get_calls.append({"url": url, "headers": dict(headers)})
        if self.error is not None:
            raise self.error
        assert self.response is not None
        return self.response


def _build_response(
    status_code: int,
    payload: object,
    *,
    bridge_contract_version: str | None = "1",
) -> httpx.Response:
    headers: dict[str, str] = {}
    if bridge_contract_version is not None:
        headers[BRIDGE_CONTRACT_VERSION_HEADER] = bridge_contract_version
    content = payload if isinstance(payload, (bytes, bytearray)) else json.dumps(payload).encode("utf-8")
    return httpx.Response(status_code, headers=headers, content=content)


@pytest.mark.asyncio
async def test_windows_bridge_adapter_adds_auth_and_version_headers_to_execute_request(monkeypatch) -> None:
    stub = _AsyncClientStub(
        response=_build_response(
            200,
            {
                "status": "accepted",
                "task_id": "bridge-task-0201",
                "timestamp": "2026-04-29T11:00:00+00:00",
                "source": "qmt",
                "bridge_contract_version": "1",
            },
        )
    )
    monkeypatch.setattr(
        "web.backend.app.services.windows_bridge_adapter.httpx.AsyncClient",
        lambda timeout: stub,
    )

    adapter = MultiSourceBridgeAdapter(
        {
            "providers": {"qmt": "http://bridge.local"},
            "bridge_token": "secret-token",
            "bridge_contract_version": "1",
        }
    )

    result = await adapter.get_data("qmt/submit_order", params={"symbol": "000001"})

    assert result["task_id"] == "bridge-task-0201"
    assert result["bridge_contract_version"] == "1"
    assert stub.post_calls[0]["url"] == "http://bridge.local/api/v1/task/execute"
    assert stub.post_calls[0]["headers"] == {
        "Authorization": "Bearer secret-token",
        BRIDGE_CONTRACT_VERSION_HEADER: "1",
    }
    assert stub.post_calls[0]["json"] == {
        "provider": "qmt",
        "method": "submit_order",
        "params": {"symbol": "000001"},
        "write_to_nas": True,
    }


@pytest.mark.asyncio
async def test_windows_bridge_adapter_rejects_unsupported_execute_target_without_network() -> None:
    adapter = MultiSourceBridgeAdapter(
        {
            "providers": {"qmt": "http://bridge.local"},
            "bridge_token": "secret-token",
            "bridge_contract_version": "1",
        }
    )

    result = await adapter.get_data("qmt/cancel_order", params={"order_id": "order-0202"})

    assert result["status"] == "error"
    assert result["reason_code"] == "live_bridge_unsupported_method"
    assert result["method"] == "cancel_order"


@pytest.mark.asyncio
async def test_windows_bridge_adapter_normalizes_result_auth_failure(monkeypatch) -> None:
    stub = _AsyncClientStub(
        response=_build_response(
            401,
            {
                "reason_code": "unauthorized",
                "reason_detail": "token expired",
                "bridge_contract_version": "1",
            },
        )
    )
    monkeypatch.setattr(
        "web.backend.app.services.windows_bridge_adapter.httpx.AsyncClient",
        lambda timeout: stub,
    )

    adapter = MultiSourceBridgeAdapter(
        {
            "providers": {"qmt": "http://bridge.local"},
            "bridge_token": "secret-token",
            "bridge_contract_version": "1",
        }
    )

    result = await adapter.get_task_result("qmt", "bridge-task-0203")

    assert result["reason_code"] == "live_bridge_auth_failed"
    assert result["failure_class"] == "live_bridge_auth_failed"
    assert result["task_id"] == "bridge-task-0203"
    assert result["bridge_contract_version"] == "1"
    assert stub.get_calls[0]["headers"] == {
        "Authorization": "Bearer secret-token",
        BRIDGE_CONTRACT_VERSION_HEADER: "1",
    }


@pytest.mark.asyncio
async def test_windows_bridge_adapter_marks_invalid_result_payload(monkeypatch) -> None:
    stub = _AsyncClientStub(
        response=httpx.Response(
            200,
            headers={BRIDGE_CONTRACT_VERSION_HEADER: "1"},
            content=b"not-json",
        )
    )
    monkeypatch.setattr(
        "web.backend.app.services.windows_bridge_adapter.httpx.AsyncClient",
        lambda timeout: stub,
    )

    adapter = MultiSourceBridgeAdapter(
        {
            "providers": {"qmt": "http://bridge.local"},
            "bridge_token": "secret-token",
            "bridge_contract_version": "1",
        }
    )

    result = await adapter.get_task_result("qmt", "bridge-task-0204")

    assert result["reason_code"] == "live_bridge_invalid_result"
    assert result["bridge_contract_version"] == "1"


@pytest.mark.asyncio
async def test_windows_bridge_adapter_marks_request_errors_unavailable(monkeypatch) -> None:
    request = httpx.Request("POST", "http://bridge.local/api/v1/task/execute")
    stub = _AsyncClientStub(error=httpx.RequestError("bridge offline", request=request))
    monkeypatch.setattr(
        "web.backend.app.services.windows_bridge_adapter.httpx.AsyncClient",
        lambda timeout: stub,
    )

    adapter = MultiSourceBridgeAdapter(
        {
            "providers": {"qmt": "http://bridge.local"},
            "bridge_token": "secret-token",
            "bridge_contract_version": "1",
        }
    )

    result = await adapter.get_data("qmt/submit_order", params={"symbol": "000001"})

    assert result["reason_code"] == "live_bridge_unavailable"
    assert result["failure_class"] == "live_bridge_unavailable"
