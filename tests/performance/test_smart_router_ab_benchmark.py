from __future__ import annotations

import time

from src.core.data_source.smart_router import SmartRouter


def _build_candidate_endpoints() -> list[dict]:
    return [
        {
            "endpoint_name": f"endpoint_{index}",
            "source_type": "akshare" if index % 2 == 0 else "tushare",
            "location": "beijing" if index % 3 == 0 else "shanghai",
            "priority": index + 1,
            "data_quality_score": 100 - index,
            "cost": {"is_free": index % 2 == 0},
        }
        for index in range(12)
    ]


def _legacy_select(endpoints: list[dict]) -> dict:
    ranked = sorted(endpoints, key=lambda item: (item.get("priority", 999), -item.get("data_quality_score", 0)))
    return ranked[0]


def test_smart_router_ab_benchmark_against_legacy_priority_sort():
    endpoints = _build_candidate_endpoints()
    router = SmartRouter()

    for index, endpoint in enumerate(endpoints):
        router.record_call(endpoint["endpoint_name"], latency=0.05 + index * 0.01, success=index % 4 != 0)
        router.record_call_complete(endpoint["endpoint_name"])

    iterations = 5000

    legacy_started = time.perf_counter()
    for _ in range(iterations):
        legacy_selected = _legacy_select(endpoints)
    legacy_elapsed = time.perf_counter() - legacy_started

    smart_started = time.perf_counter()
    for _ in range(iterations):
        smart_selected = router.route(endpoints, data_category="DAILY_KLINE", caller_location="beijing")
    smart_elapsed = time.perf_counter() - smart_started

    assert legacy_selected["endpoint_name"] == "endpoint_0"
    assert smart_selected is not None
    assert smart_selected["endpoint_name"] in {endpoint["endpoint_name"] for endpoint in endpoints}
    assert legacy_elapsed > 0
    assert smart_elapsed > 0
    assert smart_elapsed < legacy_elapsed * 20
