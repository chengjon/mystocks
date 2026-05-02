from __future__ import annotations

from tests.performance.test_smart_cache_benchmark import (
    BlockingTtlBaselineCache,
    exercise_cache,
    make_loader,
)
from src.core.data_source.smart_cache import SmartCache


def test_phase1_benchmark_summary_captures_before_after_cache_indicators():
    ttl_seconds = 0.03

    smart_loader = make_loader()
    smart_cache = SmartCache(
        maxsize=16,
        default_ttl=ttl_seconds,
        refresh_threshold=0.5,
        soft_expiry=True,
        max_refresh_workers=1,
    )
    smart_cache.set("demo", smart_loader(), ttl=ttl_seconds, refresh_func=smart_loader)

    baseline_loader = make_loader()
    baseline_cache = BlockingTtlBaselineCache(ttl_seconds=ttl_seconds)
    baseline_cache.set("demo", baseline_loader())

    def smart_get_or_load():
        value = smart_cache.get("demo")
        if value is None:
            value = smart_loader()
            smart_cache.set("demo", value, ttl=ttl_seconds, refresh_func=smart_loader)
        return value

    def baseline_get_or_load():
        value = baseline_cache.get("demo")
        if value is None:
            value = baseline_loader()
            baseline_cache.set("demo", value)
        return value

    optimized_avg_latency = exercise_cache(smart_get_or_load)
    baseline_avg_latency = exercise_cache(baseline_get_or_load)

    summary = {
        "baseline": {
            "hit_rate": baseline_cache.hit_rate,
            "avg_latency_ms": baseline_avg_latency * 1000,
        },
        "optimized": {
            "hit_rate": smart_cache.get_stats()["hit_rate"],
            "avg_latency_ms": optimized_avg_latency * 1000,
        },
    }
    summary["improvements"] = {
        "hit_rate_delta": summary["optimized"]["hit_rate"] - summary["baseline"]["hit_rate"],
        "avg_latency_reduction_ms": summary["baseline"]["avg_latency_ms"] - summary["optimized"]["avg_latency_ms"],
    }

    smart_cache.shutdown()

    assert summary["baseline"]["hit_rate"] >= 0
    assert summary["optimized"]["hit_rate"] > summary["baseline"]["hit_rate"]
    assert summary["optimized"]["avg_latency_ms"] < summary["baseline"]["avg_latency_ms"]
    assert summary["improvements"]["hit_rate_delta"] > 0
    assert summary["improvements"]["avg_latency_reduction_ms"] > 0
