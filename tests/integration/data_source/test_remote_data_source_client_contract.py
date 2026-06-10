from __future__ import annotations

from typing import Any

import pytest

from src.core.data_source.client import (
    DataSourceRequest,
    LocalDataSourceClient,
    ProviderTimeoutError,
    RemoteDataSourceClient,
    create_data_source_client,
)


class FakeTransport:
    def __init__(self):
        self.requests: list[tuple[str, dict[str, Any], int | None]] = []

    def post_json(self, path: str, payload: dict[str, Any], timeout_ms: int | None = None) -> dict[str, Any]:
        self.requests.append((path, payload, timeout_ms))
        if path == "/routing/best":
            return {
                "data_category": payload["data_category"],
                "endpoint_name": "akshare.daily_kline",
                "source": "akshare",
                "route_decision_id": "route-remote-1",
                "fallback_candidates": ["baostock.daily_kline"],
                "reason": "best_endpoint",
                "endpoint_info": {"endpoint_name": "akshare.daily_kline", "source": "akshare"},
            }
        if path == "/data/fetch":
            return {
                "data": [{"symbol": "000001", "close": 10.5}],
                "source": "akshare",
                "endpoint_name": "akshare.daily_kline",
                "route_decision_id": "route-remote-1",
                "request_id": payload["request_id"],
                "exchange_time": None,
                "received_at": "2026-06-09T00:00:00+00:00",
                "staleness_ms": 0,
                "cache_state": "miss",
                "quality_flags": [],
                "latency_ms": 12.5,
            }
        if path == "/data/batch":
            return {
                "results": [
                    {
                        "data": [{"symbol": request["params"]["symbol"], "close": 10.5}],
                        "source": "akshare",
                        "endpoint_name": "akshare.daily_kline",
                        "route_decision_id": f"route-{request['request_id']}",
                        "request_id": request["request_id"],
                        "exchange_time": None,
                        "received_at": "2026-06-09T00:00:00+00:00",
                        "staleness_ms": 0,
                        "cache_state": "miss",
                        "quality_flags": [],
                        "latency_ms": 12.5,
                    }
                    for request in payload["requests"]
                ]
            }
        raise AssertionError(f"unexpected path {path}")


class TimeoutTransport(FakeTransport):
    def post_json(self, path: str, payload: dict[str, Any], timeout_ms: int | None = None) -> dict[str, Any]:
        raise TimeoutError("remote runtime timeout")


def test_remote_client_fetch_snapshot_preserves_contract_metadata():
    transport = FakeTransport()
    client = RemoteDataSourceClient(base_url="http://openstock.local", transport=transport)

    result = client.fetch_snapshot(
        DataSourceRequest(
            data_category="DAILY_KLINE",
            params={"symbol": "000001"},
            request_id="req-remote-1",
            timeout_ms=500,
        )
    )

    assert result.data == [{"symbol": "000001", "close": 10.5}]
    assert result.source == "akshare"
    assert result.endpoint_name == "akshare.daily_kline"
    assert result.route_decision_id == "route-remote-1"
    assert result.request_id == "req-remote-1"
    assert result.received_at == "2026-06-09T00:00:00+00:00"
    assert result.cache_state == "miss"
    assert result.quality_flags == []
    assert result.latency_ms == 12.5
    assert transport.requests == [
        (
            "/data/fetch",
            {
                "data_category": "DAILY_KLINE",
                "params": {"symbol": "000001"},
                "request_id": "req-remote-1",
                "timeout_ms": 500,
                "freshness_ms": None,
            },
            500,
        )
    ]


def test_remote_client_resolve_route_uses_runtime_route_endpoint():
    transport = FakeTransport()
    client = RemoteDataSourceClient(base_url="http://openstock.local", transport=transport)

    decision = client.resolve_route(DataSourceRequest(data_category="DAILY_KLINE", request_id="req-route"))

    assert decision.endpoint_name == "akshare.daily_kline"
    assert decision.source == "akshare"
    assert decision.route_decision_id == "route-remote-1"
    assert decision.fallback_candidates == ("baostock.daily_kline",)
    assert transport.requests == [
        (
            "/routing/best",
            {
                "data_category": "DAILY_KLINE",
                "params": {},
                "request_id": "req-route",
                "timeout_ms": None,
                "freshness_ms": None,
            },
            None,
        )
    ]


def test_remote_client_maps_transport_timeout_to_provider_timeout():
    client = RemoteDataSourceClient(base_url="http://openstock.local", transport=TimeoutTransport())

    with pytest.raises(ProviderTimeoutError) as exc_info:
        client.fetch_snapshot(DataSourceRequest(data_category="DAILY_KLINE", request_id="req-timeout"))

    assert exc_info.value.error_type == "ProviderTimeout"
    assert exc_info.value.request_id == "req-timeout"


def test_remote_client_fetch_batch_uses_runtime_batch_endpoint():
    transport = FakeTransport()
    client = RemoteDataSourceClient(base_url="http://openstock.local", transport=transport)

    results = client.fetch_batch(
        [
            DataSourceRequest(
                data_category="DAILY_KLINE",
                params={"symbol": "000001"},
                request_id="req-batch-1",
            ),
            DataSourceRequest(
                data_category="DAILY_KLINE",
                params={"symbol": "000002"},
                request_id="req-batch-2",
            ),
        ]
    )

    assert [result.request_id for result in results] == ["req-batch-1", "req-batch-2"]
    assert [result.data[0]["symbol"] for result in results] == ["000001", "000002"]
    assert transport.requests == [
        (
            "/data/batch",
            {
                "requests": [
                    {
                        "data_category": "DAILY_KLINE",
                        "params": {"symbol": "000001"},
                        "request_id": "req-batch-1",
                        "timeout_ms": None,
                        "freshness_ms": None,
                    },
                    {
                        "data_category": "DAILY_KLINE",
                        "params": {"symbol": "000002"},
                        "request_id": "req-batch-2",
                        "timeout_ms": None,
                        "freshness_ms": None,
                    },
                ]
            },
            None,
        )
    ]


def test_create_data_source_client_selects_local_or_remote(monkeypatch):
    monkeypatch.setenv("DATA_SOURCE_CLIENT_MODE", "local")
    assert isinstance(create_data_source_client(manager=object()), LocalDataSourceClient)

    monkeypatch.setenv("DATA_SOURCE_CLIENT_MODE", "remote")
    client = create_data_source_client(base_url="http://openstock.local", transport=FakeTransport())
    assert isinstance(client, RemoteDataSourceClient)
