import sys
from pathlib import Path
from unittest.mock import patch

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
