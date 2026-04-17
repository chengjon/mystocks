from __future__ import annotations

import sys
from pathlib import Path

import httpx
import pytest


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.external.kronos_client import (  # noqa: E402
    KronosClientError,
    KronosServiceClient,
    KronosServiceUnavailableError,
)


class _FakeResponse:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload if payload is not None else {}
        self.text = text

    def raise_for_status(self):
        if self.status_code >= 400:
            request = httpx.Request("POST", "http://kronos.test")
            raise httpx.HTTPStatusError("error", request=request, response=self)

    def json(self):
        return self._payload


class _FakeAsyncClient:
    responses = []
    calls = []

    def __init__(self, *args, **kwargs):
        self.timeout = kwargs.get("timeout")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url, json):
        self.calls.append((url, json))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    async def get(self, url):
        self.calls.append((url, None))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


@pytest.fixture(autouse=True)
def _reset_fake_client():
    _FakeAsyncClient.responses = []
    _FakeAsyncClient.calls = []


async def test_kronos_client_retries_after_timeout(monkeypatch):
    request = httpx.Request("POST", "http://kronos.test")
    _FakeAsyncClient.responses = [
        httpx.TimeoutException("timeout", request=request),
        _FakeResponse(
            payload={
                "success": True,
                "data": {"predictions": []},
                "meta": {"model": "small", "cached": False},
                "message": "ok",
            }
        ),
    ]

    async def _no_sleep(_seconds):
        return None

    monkeypatch.setattr(httpx, "AsyncClient", _FakeAsyncClient)

    client = KronosServiceClient(
        base_url="http://kronos.test",
        timeout=0.1,
        max_retries=2,
        retry_interval_seconds=0,
        cache_ttl_seconds=300,
    )

    result = await client.predict_ohlcv({"candles": [1]})

    assert result["data"]["predictions"] == []
    assert len(_FakeAsyncClient.calls) == 2


async def test_kronos_client_marks_cache_hit_on_repeat(monkeypatch):
    _FakeAsyncClient.responses = [
        _FakeResponse(
            payload={
                "success": True,
                "data": {"predictions": [{"close": 1.0}]},
                "meta": {"model": "small", "cached": False},
                "message": "ok",
            }
        )
    ]
    monkeypatch.setattr(httpx, "AsyncClient", _FakeAsyncClient)

    client = KronosServiceClient(
        base_url="http://kronos.test",
        timeout=0.1,
        max_retries=1,
        retry_interval_seconds=0,
        cache_ttl_seconds=300,
    )

    payload = {"candles": [1], "pred_len": 5}
    first = await client.predict_ohlcv(payload)
    second = await client.predict_ohlcv(payload)

    assert first["meta"]["cached"] is False
    assert second["meta"]["cached"] is True
    assert len(_FakeAsyncClient.calls) == 1


async def test_kronos_client_maps_4xx_to_client_error(monkeypatch):
    _FakeAsyncClient.responses = [
        _FakeResponse(
            status_code=400,
            payload={"code": "PARAM_ERROR", "message": "bad payload"},
        )
    ]
    monkeypatch.setattr(httpx, "AsyncClient", _FakeAsyncClient)

    client = KronosServiceClient(
        base_url="http://kronos.test",
        timeout=0.1,
        max_retries=1,
        retry_interval_seconds=0,
        cache_ttl_seconds=300,
    )

    with pytest.raises(KronosClientError) as exc_info:
        await client.encode_kline({"candles": [1]})

    assert exc_info.value.code == "PARAM_ERROR"


async def test_kronos_client_maps_5xx_to_service_unavailable(monkeypatch):
    _FakeAsyncClient.responses = [
        _FakeResponse(
            status_code=503,
            payload={"code": "SERVICE_DOWN", "message": "down"},
        )
    ]
    monkeypatch.setattr(httpx, "AsyncClient", _FakeAsyncClient)

    client = KronosServiceClient(
        base_url="http://kronos.test",
        timeout=0.1,
        max_retries=1,
        retry_interval_seconds=0,
        cache_ttl_seconds=300,
    )

    with pytest.raises(KronosServiceUnavailableError) as exc_info:
        await client.predict_ohlcv({"candles": [1]})

    assert exc_info.value.code == "SERVICE_DOWN"


async def test_kronos_client_can_fetch_status(monkeypatch):
    _FakeAsyncClient.responses = [
        _FakeResponse(
            payload={
                "success": True,
                "data": {
                    "health": "healthy",
                    "active_model": "small",
                    "queue_depth": 0,
                },
                "meta": {"model": "small", "cached": False},
                "message": "ok",
            }
        )
    ]
    monkeypatch.setattr(httpx, "AsyncClient", _FakeAsyncClient)

    client = KronosServiceClient(
        base_url="http://kronos.test",
        timeout=0.1,
        max_retries=1,
        retry_interval_seconds=0,
        cache_ttl_seconds=300,
    )

    result = await client.get_status()

    assert result["data"]["health"] == "healthy"
    assert _FakeAsyncClient.calls == [("http://kronos.test/v1/kronos/status", None)]
