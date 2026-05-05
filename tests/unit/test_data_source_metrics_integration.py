import sys
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest
from prometheus_client import CollectorRegistry

from src.core.data_source.circuit_breaker import CircuitBreaker
from src.core.data_source.metrics import DataSourceMetrics

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_record_success_updates_runtime_stats_and_prometheus_metrics(monkeypatch):
    with patch("dotenv.load_dotenv", return_value=True):
        from src.core.data_source.base import DataSourceManagerV2
        from src.core.data_source import metrics as metrics_module

    manager = DataSourceManagerV2.__new__(DataSourceManagerV2)
    manager.registry = {
        "demo.endpoint": {
            "config": {
                "data_category": "DAILY_KLINE",
                "total_calls": 0,
                "failed_calls": 0,
                "health_status": "unknown",
                "cost": {
                    "estimated_cny_per_call": 0.12,
                },
            }
        }
    }
    manager.circuit_breakers = {
        "demo.endpoint": CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60,
            name="demo.endpoint",
        )
    }
    manager._save_call_history_async = lambda **kwargs: None

    metrics = DataSourceMetrics(registry=CollectorRegistry())
    monkeypatch.setattr(metrics_module, "_global_metrics", metrics)

    manager._record_success("demo.endpoint", 0.5, 3, "unit-test")

    config = manager.registry["demo.endpoint"]["config"]
    assert config["total_calls"] == 1
    assert config["failed_calls"] == 0
    assert config["avg_response_time"] == 0.5
    assert config["health_status"] == "healthy"
    assert (
        metrics.api_calls_total.labels(
            endpoint="demo.endpoint",
            data_category="DAILY_KLINE",
            status="success",
        )._value.get()
        == 1
    )
    assert metrics.circuit_breaker_state.labels(endpoint="demo.endpoint")._value.get() == 0
    assert 'datasource_api_cost_estimated{endpoint="demo.endpoint"} 0.12' in metrics.generate_metrics().decode("utf-8")


def test_backend_metrics_endpoint_includes_canonical_datasource_metrics(monkeypatch):
    from web.backend.app.core.middleware.performance import metrics_endpoint
    from src.core.data_source import metrics as metrics_module

    metrics = DataSourceMetrics(registry=CollectorRegistry())
    metrics.record_api_call("demo.endpoint", "DAILY_KLINE", latency=0.5, success=True)
    monkeypatch.setattr(metrics_module, "_global_metrics", metrics)

    response = metrics_endpoint()
    body = response.body.decode("utf-8")

    assert "datasource_api_calls_total" in body
    assert 'endpoint="demo.endpoint"' in body


def test_backend_metrics_endpoint_merges_canonical_metrics_even_with_runtime_datasource_prefix(monkeypatch):
    from web.backend.app.core.middleware import performance
    from src.core.data_source import metrics as metrics_module

    metrics = DataSourceMetrics(registry=CollectorRegistry())
    metrics.record_api_call("demo.endpoint", "DAILY_KLINE", latency=0.5, success=True)
    monkeypatch.setattr(metrics_module, "_global_metrics", metrics)
    monkeypatch.setattr(
        performance,
        "generate_latest",
        lambda: (
            b"# HELP mystocks_datasource_availability Data source availability (1=available, 0=unavailable)\n"
            b"# TYPE mystocks_datasource_availability gauge\n"
        ),
    )

    response = performance.metrics_endpoint()
    body = response.body.decode("utf-8")

    assert "mystocks_datasource_availability" in body
    assert "datasource_api_calls_total" in body
    assert 'endpoint="demo.endpoint"' in body


@pytest.mark.asyncio
async def test_manual_datasource_test_route_records_canonical_metrics(monkeypatch):
    backend_root = REPO_ROOT / "web" / "backend"
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))

    from app.api import data_source_registry as registry_module
    from src.core.data_source import metrics as metrics_module

    class FakeManager:
        def __init__(self):
            self.registry = {
                "demo.daily_kline": {
                    "config": {
                        "data_category": "DAILY_KLINE",
                        "source_type": "mock",
                        "source_name": "demo",
                        "cost": {
                            "is_free": True,
                            "estimated_cny_per_call": 0.0,
                        },
                    }
                }
            }

    manager = FakeManager()
    metrics = DataSourceMetrics(registry=CollectorRegistry())
    monkeypatch.setattr(registry_module, "get_manager", lambda: manager)
    monkeypatch.setattr(registry_module, "_require_write_auth", lambda authorization: None)
    monkeypatch.setattr(metrics_module, "_global_metrics", metrics)

    response = await registry_module.test_data_source(
        endpoint_name="demo.daily_kline",
        request=registry_module.TestRequest(
            test_params={
                "symbol": "000001",
                "start_date": "20240102",
                "end_date": "20240103",
            }
        ),
        authorization="Bearer local-test",
    )

    assert response["success"] is True
    assert response["row_count"] >= 1
    assert response["error"] is None
    assert response["quality_checks"]["has_data"] is True
    assert (
        metrics.api_calls_total.labels(
            endpoint="demo.daily_kline",
            data_category="DAILY_KLINE",
            status="success",
        )._value.get()
        == 1
    )
    assert 'datasource_api_cost_estimated{endpoint="demo.daily_kline"} 0.0' in metrics.generate_metrics().decode("utf-8")


def test_call_endpoint_cache_miss_then_hit_records_canonical_cache_metrics(monkeypatch):
    from src.core.data_source import metrics as metrics_module
    from src.core.data_source.handler import _call_endpoint
    from src.core.data_source.smart_cache import SmartCache

    class CountingHandler:
        def __init__(self):
            self.fetch_calls = 0

        def fetch(self, **kwargs):
            self.fetch_calls += 1
            return pd.DataFrame(
                [
                    {
                        "symbol": kwargs["symbol"],
                        "close": 10.0,
                    }
                ]
            )

    class FakeManager:
        def __init__(self, handler):
            self._handler = handler
            self.registry = {
                "demo.endpoint": {
                    "config": {
                        "data_category": "DAILY_KLINE",
                    },
                    "handler": None,
                    "cache": SmartCache(maxsize=10, default_ttl=60, soft_expiry=False),
                }
            }
            self.circuit_breakers = {}
            self.success_records = []
            self.failure_records = []

        def _create_handler(self, endpoint_info):
            return self._handler

        def _identify_caller(self):
            return {"service": "unit-test"}

        def _record_success(self, *args):
            self.success_records.append(args)

        def _record_failure(self, *args):
            self.failure_records.append(args)

    handler = CountingHandler()
    manager = FakeManager(handler)
    metrics = DataSourceMetrics(registry=CollectorRegistry())
    monkeypatch.setattr(metrics_module, "_global_metrics", metrics)

    endpoint = {
        "endpoint_name": "demo.endpoint",
        "source_type": "mock",
    }

    try:
        first = _call_endpoint(manager, endpoint, symbol="000001", start_date="20240101", end_date="20240102")
        second = _call_endpoint(manager, endpoint, symbol="000001", start_date="20240101", end_date="20240102")
    finally:
        manager.registry["demo.endpoint"]["cache"].shutdown()

    assert handler.fetch_calls == 1
    assert len(manager.success_records) == 1
    assert manager.failure_records == []
    assert first.equals(second)
    assert metrics.cache_misses_total.labels(endpoint="demo.endpoint")._value.get() == 1
    assert metrics.cache_hits_total.labels(endpoint="demo.endpoint")._value.get() == 1


def test_backend_metrics_endpoint_includes_cache_hit_and_miss_samples(monkeypatch):
    from src.core.data_source import metrics as metrics_module
    from src.core.data_source.handler import _call_endpoint
    from src.core.data_source.smart_cache import SmartCache
    from web.backend.app.core.middleware.performance import metrics_endpoint

    class CountingHandler:
        def __init__(self):
            self.fetch_calls = 0

        def fetch(self, **kwargs):
            self.fetch_calls += 1
            return pd.DataFrame([{"symbol": kwargs["symbol"], "close": 10.0}])

    class FakeManager:
        def __init__(self, handler):
            self._handler = handler
            self.registry = {
                "demo.endpoint": {
                    "config": {
                        "data_category": "DAILY_KLINE",
                    },
                    "handler": None,
                    "cache": SmartCache(maxsize=10, default_ttl=60, soft_expiry=False),
                }
            }
            self.circuit_breakers = {}

        def _create_handler(self, endpoint_info):
            return self._handler

        def _identify_caller(self):
            return {"service": "unit-test"}

        def _record_success(self, *args):
            return None

        def _record_failure(self, *args):
            return None

    handler = CountingHandler()
    manager = FakeManager(handler)
    metrics = DataSourceMetrics(registry=CollectorRegistry())
    monkeypatch.setattr(metrics_module, "_global_metrics", metrics)

    endpoint = {
        "endpoint_name": "demo.endpoint",
        "source_type": "mock",
    }

    try:
        _call_endpoint(manager, endpoint, symbol="000001", start_date="20240101", end_date="20240102")
        _call_endpoint(manager, endpoint, symbol="000001", start_date="20240101", end_date="20240102")
        body = metrics_endpoint().body.decode("utf-8")
    finally:
        manager.registry["demo.endpoint"]["cache"].shutdown()

    assert 'datasource_cache_misses_total{endpoint="demo.endpoint"} 1.0' in body
    assert 'datasource_cache_hits_total{endpoint="demo.endpoint"} 1.0' in body
