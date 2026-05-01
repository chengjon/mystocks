import pytest
from prometheus_client import CollectorRegistry

from src.core.data_source.metrics import DataSourceMetrics


def test_record_api_call_tracks_success_and_failure_counts():
    metrics = DataSourceMetrics(registry=CollectorRegistry())

    metrics.record_api_call("demo.endpoint", "DAILY_KLINE", latency=0.25, success=True, cost=0.12)
    metrics.record_api_call("demo.endpoint", "DAILY_KLINE", latency=0.5, success=False)

    assert (
        metrics.api_calls_total.labels(
            endpoint="demo.endpoint",
            data_category="DAILY_KLINE",
            status="success",
        )._value.get()
        == 1
    )
    assert (
        metrics.api_calls_total.labels(
            endpoint="demo.endpoint",
            data_category="DAILY_KLINE",
            status="failure",
        )._value.get()
        == 1
    )
    assert metrics.api_cost_estimated.labels(endpoint="demo.endpoint")._value.get() == 0.12


def test_latency_histogram_supports_average_latency_lookup():
    metrics = DataSourceMetrics(registry=CollectorRegistry())

    metrics.record_api_call("demo.endpoint", "DAILY_KLINE", latency=0.25, success=True)
    metrics.record_api_call("demo.endpoint", "DAILY_KLINE", latency=0.75, success=True)

    assert metrics.get_avg_latency("demo.endpoint", "DAILY_KLINE") == pytest.approx(0.5)


def test_record_cache_hit_and_miss_updates_rate():
    metrics = DataSourceMetrics(registry=CollectorRegistry())

    metrics.record_cache_hit("demo.endpoint")
    metrics.record_cache_hit("demo.endpoint")
    metrics.record_cache_miss("demo.endpoint")

    assert metrics.cache_hits_total.labels(endpoint="demo.endpoint")._value.get() == 2
    assert metrics.cache_misses_total.labels(endpoint="demo.endpoint")._value.get() == 1
    assert metrics.get_cache_hit_rate("demo.endpoint") == pytest.approx(2 / 3)


def test_record_circuit_breaker_state_updates_gauge():
    metrics = DataSourceMetrics(registry=CollectorRegistry())

    metrics.record_circuit_breaker_state("demo.endpoint", 2)

    assert metrics.circuit_breaker_state.labels(endpoint="demo.endpoint")._value.get() == 2
