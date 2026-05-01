from unittest.mock import patch

from prometheus_client import CollectorRegistry

from src.core.data_source.circuit_breaker import CircuitBreaker
from src.core.data_source.metrics import DataSourceMetrics


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
