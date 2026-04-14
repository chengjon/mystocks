from __future__ import annotations

import sys
import importlib
from types import ModuleType, SimpleNamespace


class _FakeAcquire:
    def __init__(self, conn):
        self._conn = conn

    async def __aenter__(self):
        return self._conn

    async def __aexit__(self, exc_type, exc, tb):
        return False


class _FakeConn:
    async def fetchrow(self, query, *params):
        return {"total": 3}


class _FakePool:
    def acquire(self):
        return _FakeAcquire(_FakeConn())


class _FakePostgres:
    pool = _FakePool()

    def is_connected(self):
        return True


class _FakeTracker:
    async def update_strategy_health_status(self, strategy_id):
        return {
            "health_status": 1,
            "success_rate": 95.5,
            "accuracy": 78.2,
            "avg_latency_ms": 45.2,
            "status_text": "healthy",
        }


async def test_get_strategy_detailed_health_uses_runtime_component_states():
    module = importlib.import_module("app.api.signal_monitoring.get_signal_statistics")

    fake_pg_module = ModuleType("src.monitoring.infrastructure.postgresql_async_v3")
    fake_pg_module.get_postgres_async = lambda: _FakePostgres()

    fake_tracker_module = ModuleType("src.monitoring.signal_result_tracker")
    fake_tracker_module.get_signal_result_tracker = lambda: _FakeTracker()

    previous_pg = sys.modules.get("src.monitoring.infrastructure.postgresql_async_v3")
    previous_tracker = sys.modules.get("src.monitoring.signal_result_tracker")

    sys.modules["src.monitoring.infrastructure.postgresql_async_v3"] = fake_pg_module
    sys.modules["src.monitoring.signal_result_tracker"] = fake_tracker_module

    original_push_status = module._get_signal_push_component_status
    original_gpu_status = module._get_gpu_component_status
    module._get_signal_push_component_status = lambda: "healthy"

    async def fake_gpu_status():
        return "healthy"

    module._get_gpu_component_status = fake_gpu_status

    try:
        response = await module.get_strategy_detailed_health("macd_strategy", current_user=SimpleNamespace(id=1))
    finally:
        module._get_signal_push_component_status = original_push_status
        module._get_gpu_component_status = original_gpu_status

        if previous_pg is None:
            sys.modules.pop("src.monitoring.infrastructure.postgresql_async_v3", None)
        else:
            sys.modules["src.monitoring.infrastructure.postgresql_async_v3"] = previous_pg

        if previous_tracker is None:
            sys.modules.pop("src.monitoring.signal_result_tracker", None)
        else:
            sys.modules["src.monitoring.signal_result_tracker"] = previous_tracker

    assert response.components["signal_push"] == "healthy"
    assert response.components["gpu"] == "healthy"
    assert response.metrics["active_signals_count"] == 3
