from __future__ import annotations

import importlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def _load_module():
    sys.modules.pop("app.api.v1.admin.audit", None)
    return importlib.import_module("app.api.v1.admin.audit")


def _reset_runtime_state() -> None:
    state = importlib.import_module("app.api.v1.admin.runtime_state")
    state.runtime_store.reset()


async def test_v1_audit_logs_returns_runtime_response():
    _reset_runtime_state()
    module = _load_module()

    payload = await module.list_audit_logs()

    assert payload.success is True
    assert payload.code == 200
    assert payload.data["logs"]
    assert payload.data["source"] in {"database", "runtime"}


async def test_v1_audit_log_detail_returns_runtime_response():
    _reset_runtime_state()
    module = _load_module()
    logs_payload = await module.list_audit_logs()
    log_id = logs_payload.data["logs"][0]["log_id"]

    payload = await module.get_audit_log(log_id)

    assert payload.success is True
    assert payload.code == 200
    assert payload.data["log_id"] == log_id
    assert payload.data["action"]


async def test_v1_audit_statistics_returns_runtime_response():
    _reset_runtime_state()
    module = _load_module()

    payload = await module.get_audit_statistics(start_date="2026-04-01", end_date="2026-04-12")

    assert payload.success is True
    assert payload.code == 200
    assert payload.data["total_logs"] >= 0
    assert "actions" in payload.data
