from __future__ import annotations

import importlib
import inspect
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


class _FakeAuditQuery:
    def filter(self, *_args, **_kwargs):
        return self

    def order_by(self, *_args, **_kwargs):
        return self

    def limit(self, *_args, **_kwargs):
        return self

    def all(self):
        return []


class _FakeAuditSession:
    def __init__(self) -> None:
        self.closed = False

    def query(self, *_args, **_kwargs):
        return _FakeAuditQuery()

    def close(self) -> None:
        self.closed = True


def test_v1_audit_routes_expose_session_factory_dependency():
    module = _load_module()

    for route_handler_name in ("list_audit_logs", "get_audit_log", "get_audit_statistics"):
        signature = inspect.signature(getattr(module, route_handler_name))
        parameter = signature.parameters["session_factory"]

        assert parameter.default.dependency is module.get_admin_audit_postgresql_session_factory


def test_v1_audit_load_logs_uses_injected_session_factory_and_closes_session():
    _reset_runtime_state()
    module = _load_module()
    session = _FakeAuditSession()

    logs, source = module._load_audit_logs(
        user_id=None,
        action=None,
        resource_type=None,
        start_date=None,
        end_date=None,
        limit=1,
        session_factory=lambda: session,
    )

    assert logs
    assert source == "runtime"
    assert session.closed is True


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
