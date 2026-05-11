from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def _load_module():
    sys.modules.pop("app.api.v1.strategy.machine_learning", None)
    sys.modules.pop("app.api.v1.strategy.batch_analysis", None)
    return importlib.import_module("app.api.v1.strategy.machine_learning")


def _reset_batch_state() -> None:
    batch_module = importlib.import_module("app.api.v1.strategy.batch_analysis")
    batch_module.batch_analysis_store.reset()


def test_v1_batch_analysis_registers_canonical_routes():
    module = _load_module()
    route_methods = {(route.path, tuple(sorted(route.methods or []))) for route in module.router.routes}

    assert ("/strategies/batch-analysis/runtime-status", ("GET",)) in route_methods
    assert ("/strategies/batch-analysis/submit", ("POST",)) in route_methods
    assert ("/strategies/batch-analysis/tasks", ("GET",)) in route_methods
    assert ("/strategies/batch-analysis/tasks/{task_id}", ("GET",)) in route_methods


async def test_v1_batch_analysis_runtime_status_is_machine_readable():
    module = _load_module()

    payload = await module.get_batch_analysis_runtime_status()

    assert payload.success is True
    assert payload.code == 200
    assert payload.data["service_available"] is True
    assert payload.data["max_symbols"] == 20
    assert {"batch_backtest", "batch_screening", "batch_monitoring"}.issubset(
        set(payload.data["supported_operations"])
    )
    assert payload.data["safety"]["analytical_output_only"] is True
    assert "not automated trading" in payload.data["safety"]["disclaimer"]


async def test_v1_batch_analysis_submit_list_and_detail_are_canonical():
    _reset_batch_state()
    module = _load_module()

    payload = await module.submit_batch_analysis_task(
        module.BatchAnalysisRequest(
            operation="batch_screening",
            symbols=["600519.SH", "000001.SZ", "510300.SH"],
            start_date="2024-01-01",
            end_date="2024-12-31",
            options={"factor": "momentum"},
        )
    )

    assert payload.success is True
    assert payload.code == 200
    assert payload.data["task_id"].startswith("batch_")
    assert payload.data["status"] == "completed"
    assert payload.data["operation"] == "batch_screening"
    assert payload.data["summary"]["total_symbols"] == 3
    assert payload.data["summary"]["completed_symbols"] == 3
    assert payload.data["safety"]["analytical_output_only"] is True
    assert len(payload.data["results"]) == 3

    list_payload = await module.list_batch_analysis_tasks()
    assert list_payload.success is True
    assert list_payload.data["total"] == 1
    assert list_payload.data["tasks"][0]["task_id"] == payload.data["task_id"]

    detail_payload = await module.get_batch_analysis_task_detail(payload.data["task_id"])
    assert detail_payload.success is True
    assert detail_payload.data["task_id"] == payload.data["task_id"]
    assert detail_payload.data["results"][0]["symbol"] == "600519.SH"


async def test_v1_batch_analysis_rejects_oversized_first_batch_request():
    _reset_batch_state()
    module = _load_module()

    with pytest.raises(module.HTTPException) as excinfo:
        await module.submit_batch_analysis_task(
            module.BatchAnalysisRequest(
                operation="batch_backtest",
                symbols=[f"{idx:06d}.SH" for idx in range(21)],
                start_date="2024-01-01",
                end_date="2024-12-31",
            )
        )

    assert excinfo.value.status_code == 400
    assert "supports at most 20 symbols" in excinfo.value.detail
    assert (await module.list_batch_analysis_tasks()).data["total"] == 0


async def test_v1_batch_analysis_request_rejects_blank_symbol():
    module = _load_module()

    with pytest.raises(ValueError, match="symbols must not contain blank values"):
        module.BatchAnalysisRequest(
            operation="batch_screening",
            symbols=["600519.SH", "   "],
            start_date="2024-01-01",
            end_date="2024-12-31",
        )


async def test_v1_batch_analysis_request_rejects_invalid_date_range():
    module = _load_module()

    with pytest.raises(ValueError, match="start_date must be earlier than or equal to end_date"):
        module.BatchAnalysisRequest(
            operation="batch_screening",
            symbols=["600519.SH"],
            start_date="2024-12-31",
            end_date="2024-01-01",
        )


async def test_v1_batch_analysis_request_rejects_non_date_iso_datetime():
    module = _load_module()

    with pytest.raises(ValueError, match="start_date and end_date must be ISO date strings"):
        module.BatchAnalysisRequest(
            operation="batch_screening",
            symbols=["600519.SH"],
            start_date="2024-01-01T09:30:00",
            end_date="2024-12-31",
        )


async def test_v1_batch_analysis_detail_rejects_missing_task():
    _reset_batch_state()
    module = _load_module()

    with pytest.raises(module.HTTPException) as excinfo:
        await module.get_batch_analysis_task_detail("missing_task")

    assert excinfo.value.status_code == 404
    assert "Unknown batch task" in excinfo.value.detail
