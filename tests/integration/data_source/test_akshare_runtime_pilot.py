from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from src.core.data_source import DataSourceRequest, RemoteDataSourceClient


class AkShareRuntimeTransport:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any], int | None]] = []

    def post_json(self, endpoint: str, payload: dict[str, Any], timeout_ms: int | None = None) -> dict[str, Any]:
        self.calls.append((endpoint, payload, timeout_ms))
        if endpoint == "/routing/best":
            return {
                "data_category": "REALTIME_QUOTES",
                "endpoint_name": "akshare.stock_zh_a_spot",
                "source": "akshare",
                "endpoint_info": {
                    "endpoint_name": "akshare.stock_zh_a_spot",
                    "source": "akshare",
                    "data_category": "REALTIME_QUOTES",
                    "transport": "rest_pull",
                },
                "route_decision_id": "route-akshare",
                "fallback_candidates": [
                    "akshare.stock_info_a_code_name",
                    "legacy_mystocks_akshare",
                    "local_cache",
                ],
                "reason": "akshare_realtime_quotes_primary",
            }
        if endpoint == "/data/fetch":
            return {
                "data": [{"symbol": "000001", "name": "平安银行", "price": 10.5}],
                "source": "akshare",
                "endpoint_name": "akshare.stock_zh_a_spot",
                "route_decision_id": "route-akshare",
                "request_id": payload["request_id"],
                "exchange_time": None,
                "received_at": "2026-06-10T00:00:00+00:00",
                "staleness_ms": 0,
                "cache_state": "miss",
                "quality_flags": [],
                "latency_ms": 12.5,
            }
        raise AssertionError(f"unexpected endpoint: {endpoint}")


def test_remote_client_preserves_akshare_runtime_contract_metadata():
    transport = AkShareRuntimeTransport()
    client = RemoteDataSourceClient("http://openstock.local", transport=transport)

    result = client.fetch_snapshot(
        DataSourceRequest(
            data_category="REALTIME_QUOTES",
            params={"limit": 1},
            request_id="req-akshare-runtime",
            timeout_ms=5000,
        )
    )

    assert result.source == "akshare"
    assert result.endpoint_name == "akshare.stock_zh_a_spot"
    assert result.request_id == "req-akshare-runtime"
    assert result.data == [{"symbol": "000001", "name": "平安银行", "price": 10.5}]
    assert result.cache_state == "miss"
    assert result.quality_flags == []
    assert transport.calls == [
        (
            "/data/fetch",
            {
                "data_category": "REALTIME_QUOTES",
                "params": {"limit": 1},
                "request_id": "req-akshare-runtime",
                "timeout_ms": 5000,
                "freshness_ms": None,
            },
            5000,
        )
    ]


def test_remote_client_exposes_akshare_route_fallback_candidates():
    transport = AkShareRuntimeTransport()
    client = RemoteDataSourceClient("http://openstock.local", transport=transport)

    decision = client.resolve_route(DataSourceRequest(data_category="REALTIME_QUOTES", request_id="req-route"))

    assert decision.source == "akshare"
    assert decision.endpoint_name == "akshare.stock_zh_a_spot"
    assert decision.reason == "akshare_realtime_quotes_primary"
    assert decision.fallback_candidates == (
        "akshare.stock_info_a_code_name",
        "legacy_mystocks_akshare",
        "local_cache",
    )


def test_openstock_akshare_remote_config_entry_exists():
    registry_path = Path("config/data_sources_registry.yaml")
    registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))

    entry = registry["data_sources"]["openstock_akshare_realtime_quotes"]

    assert entry["source_name"] == "openstock"
    assert entry["source_type"] == "remote_runtime"
    assert entry["endpoint_name"] == "akshare.stock_zh_a_spot"
    assert entry["data_category"] == "REALTIME_QUOTES"
    assert entry["remote_runtime"]["base_url_env"] == "OPENSTOCK_BASE_URL"
    assert entry["remote_runtime"]["fetch_path"] == "/data/fetch"
