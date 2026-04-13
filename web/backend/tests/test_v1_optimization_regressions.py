from __future__ import annotations

import importlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def _load_module():
    sys.modules.pop("app.api.v1.admin.optimization", None)
    return importlib.import_module("app.api.v1.admin.optimization")


async def test_v1_vacuum_returns_runtime_response():
    module = _load_module()
    async def _stub(operation: str):
        return module.OptimizationResponse(
            operation=operation,
            status="completed",
            duration_ms=12,
            result={"task_id": "opt_1", "executed_sql": "VACUUM"},
        )
    module._run_maintenance = _stub

    payload = await module.vacuum_database()

    assert payload.success is True
    assert payload.code == 200
    assert payload.data["operation"] == "vacuum"
    assert payload.data["status"] == "completed"


async def test_v1_analyze_returns_runtime_response():
    module = _load_module()
    async def _stub(operation: str):
        return module.OptimizationResponse(
            operation=operation,
            status="completed",
            duration_ms=10,
            result={"task_id": "opt_2", "executed_sql": "ANALYZE"},
        )
    module._run_maintenance = _stub

    payload = await module.analyze_database()

    assert payload.success is True
    assert payload.code == 200
    assert payload.data["operation"] == "analyze"


async def test_v1_reindex_returns_runtime_response():
    module = _load_module()
    async def _stub(operation: str):
        return module.OptimizationResponse(
            operation=operation,
            status="completed",
            duration_ms=25,
            result={"task_id": "opt_3", "executed_sql": "REINDEX DATABASE current_database()"},
        )
    module._run_maintenance = _stub

    payload = await module.reindex_database()

    assert payload.success is True
    assert payload.code == 200
    assert payload.data["operation"] == "reindex"


async def test_v1_optimization_status_returns_runtime_response():
    module = _load_module()
    module._database_status_payload = lambda: {
        "database": "mystocks",
        "pool": {"size": 20, "in_use": 1, "idle": 19, "status": "ok"},
        "performance_monitor": {"total_queries": 3, "total_slow_queries": 1},
        "recent_operations": [],
        "updated_at": "2026-04-13T08:00:00+00:00",
    }

    payload = await module.get_database_status()

    assert payload.success is True
    assert payload.code == 200
    assert payload.data["database"] == "mystocks"
    assert payload.data["pool"]["size"] == 20


async def test_v1_slow_queries_returns_runtime_response():
    module = _load_module()
    module._slow_queries_payload = lambda limit: {
        "limit": limit,
        "queries": [{"query": "SELECT 1", "duration": 0.2, "type": "select", "timestamp": "2026-04-13T08:00:00+00:00", "params": None}],
        "aggregated": [],
        "summary": {"logged": 1, "aggregated": 0},
    }

    payload = await module.get_slow_queries()

    assert payload.success is True
    assert payload.code == 200
    assert payload.data["limit"] == 10
    assert payload.data["queries"][0]["query"] == "SELECT 1"
