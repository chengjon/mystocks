from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def _load_module():
    sys.modules.pop("app.api.monitoring", None)
    return importlib.import_module("app.api.monitoring")


async def test_monitoring_mark_all_read_returns_runtime_batch_response():
    module = _load_module()

    payload = await module.mark_all_alerts_read(current_user=SimpleNamespace(id="user-1"))

    assert payload.success is True
    assert payload.code == 200
    assert payload.data == {
        "status": "updated",
        "scope": "all_alerts",
        "updated_count": 2,
    }


async def test_monitoring_mark_all_read_marks_database_unread_alerts(monkeypatch):
    module = _load_module()
    monkeypatch.setenv("TESTING", "false")
    monkeypatch.setenv("DEVELOPMENT_MODE", "false")

    unread_records = [SimpleNamespace(id=101), SimpleNamespace(id=102), SimpleNamespace(id=103)]
    captured = []

    monkeypatch.setattr(module.monitoring_service, "get_alert_records", lambda **kwargs: (unread_records, len(unread_records)))
    monkeypatch.setattr(module.monitoring_service, "mark_alert_read", lambda alert_id: captured.append(alert_id) or True)

    payload = await module.mark_all_alerts_read(current_user=SimpleNamespace(id="user-1"))

    assert payload.success is True
    assert payload.code == 200
    assert payload.data == {
        "status": "updated",
        "scope": "all_alerts",
        "updated_count": 3,
    }
    assert captured == [101, 102, 103]


@pytest.fixture
def monitoring_control_module():
    module = _load_module()
    module._monitoring_control_state["task"] = None
    module._monitoring_control_state["interval"] = None
    module._monitoring_control_state["last_started_at"] = None
    module.monitoring_service.is_monitoring = False
    module.monitoring_service.monitored_symbols = []
    return module


async def test_monitoring_start_returns_running_state(monitoring_control_module, monkeypatch: pytest.MonkeyPatch):
    module = monitoring_control_module

    async def fake_start(symbols=None, interval=60):
        module.monitoring_service.is_monitoring = True
        module.monitoring_service.monitored_symbols = symbols or []
        return None

    monkeypatch.setattr(module.monitoring_service, "start_monitoring", fake_start)

    request = module.MonitoringControlRequest(symbols=["600519", "000001"], interval=30)
    payload = await module.start_monitoring(request=request, current_user=SimpleNamespace(id="user-1"))

    assert payload.success is True
    assert payload.code == 200
    assert payload.data == {
        "is_monitoring": True,
        "monitored_symbols": ["600519", "000001"],
        "monitored_count": 2,
        "interval": 30,
    }

    await module.stop_monitoring(current_user=SimpleNamespace(id="user-1"))


async def test_monitoring_status_reflects_running_state(monitoring_control_module):
    module = monitoring_control_module
    module.monitoring_service.is_monitoring = True
    module.monitoring_service.monitored_symbols = ["600519", "000001"]
    module._monitoring_control_state["interval"] = 45

    payload = await module.get_monitoring_status()

    assert payload["success"] is True
    assert payload["data"]["is_monitoring"] is True
    assert payload["data"]["monitored_symbols"] == ["600519", "000001"]
    assert payload["data"]["monitored_count"] == 2
    assert payload["data"]["update_interval"] == 45


async def test_monitoring_stop_returns_stopped_state(monitoring_control_module, monkeypatch: pytest.MonkeyPatch):
    module = monitoring_control_module

    async def fake_start(symbols=None, interval=60):
        module.monitoring_service.is_monitoring = True
        module.monitoring_service.monitored_symbols = symbols or []
        return None

    monkeypatch.setattr(module.monitoring_service, "start_monitoring", fake_start)

    await module.start_monitoring(
        request=module.MonitoringControlRequest(symbols=["600519"], interval=15),
        current_user=SimpleNamespace(id="user-1"),
    )

    payload = await module.stop_monitoring(current_user=SimpleNamespace(id="user-1"))

    assert payload["success"] is True
    assert payload["data"]["is_monitoring"] is False
    assert payload["data"]["monitored_symbols"] == []
    assert payload["data"]["monitored_count"] == 0
