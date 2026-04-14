from __future__ import annotations

import importlib
import sys
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
        if "COUNT(*) as signal_count" in query:
            return {
                "signal_count": 4,
                "avg_latency": 20.0,
                "p95_latency": 40.0,
                "p99_latency": 60.0,
                "gpu_count": 2,
            }
        if "FROM strategy_health" in query:
            return {"health_status": 1}
        if "status IN ('generated', 'executed')" in query:
            return {"total": 9}
        raise AssertionError(f"unexpected query: {query}")

    async def fetch(self, query, *params):
        return [
            {
                "id": 1,
                "symbol": "600519.SH",
                "signal_type": "BUY",
                "generated_at": SimpleNamespace(isoformat=lambda: "2026-01-08T15:30:00"),
            }
        ]


class _FakePool:
    def acquire(self):
        return _FakeAcquire(_FakeConn())


class _FakePostgres:
    pool = _FakePool()

    def is_connected(self):
        return True


async def test_get_strategy_realtime_monitoring_uses_runtime_gpu_and_active_counts():
    module = importlib.import_module("app.api.signal_monitoring.signal_history_response")

    fake_pg_module = ModuleType("src.monitoring.infrastructure.postgresql_async_v3")
    fake_pg_module.get_postgres_async = lambda: _FakePostgres()
    previous_pg = sys.modules.get("src.monitoring.infrastructure.postgresql_async_v3")
    sys.modules["src.monitoring.infrastructure.postgresql_async_v3"] = fake_pg_module

    original_gpu_util = module._get_runtime_gpu_utilization

    async def fake_gpu_util():
        return 66.6

    module._get_runtime_gpu_utilization = fake_gpu_util

    try:
        response = await module.get_strategy_realtime_monitoring(
            strategy_id="macd_strategy",
            current_user=SimpleNamespace(id=1),
        )
    finally:
        module._get_runtime_gpu_utilization = original_gpu_util
        if previous_pg is None:
            sys.modules.pop("src.monitoring.infrastructure.postgresql_async_v3", None)
        else:
            sys.modules["src.monitoring.infrastructure.postgresql_async_v3"] = previous_pg

    assert response.active_signals_count == 9
    assert response.gpu_enabled is True
    assert response.gpu_utilization == 66.6
    assert response.signal_generation_rate == 0.8
    assert response.recent_signals[0]["symbol"] == "600519.SH"
