from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def _load_module():
    sys.modules.pop("app.api.backtest_ws", None)
    return importlib.import_module("app.api.backtest_ws")


class _FakeManager:
    def __init__(self):
        self.messages = []
        self.disconnected = []

    async def connect(self, websocket, backtest_id):
        return None

    def disconnect(self, websocket, backtest_id):
        self.disconnected.append((websocket, backtest_id))

    async def send_personal_message(self, message, websocket):
        self.messages.append(json.loads(message))


class _FakeWebSocket:
    def __init__(self, module, messages):
        self._module = module
        self._messages = list(messages)

    async def receive_text(self):
        if self._messages:
            return self._messages.pop(0)
        raise self._module.WebSocketDisconnect()


async def test_backtest_ws_cancel_revokes_runtime_task(monkeypatch):
    module = _load_module()
    fake_manager = _FakeManager()
    websocket = _FakeWebSocket(module, ['{"type":"cancel"}'])
    revoked = {}

    monkeypatch.setattr(module, "manager", fake_manager)
    monkeypatch.setattr(module, "get_backtest_task_id", lambda backtest_id: "celery-task-42")
    monkeypatch.setattr(module, "unregister_progress_callback", lambda backtest_id: revoked.setdefault("callback", backtest_id))
    monkeypatch.setattr(module, "unregister_backtest_task", lambda backtest_id: revoked.setdefault("mapping", backtest_id))
    monkeypatch.setattr(module, "_mark_backtest_cancelled", lambda backtest_id: revoked.setdefault("status", backtest_id))
    monkeypatch.setattr(
        module.celery_app.control,
        "revoke",
        lambda task_id, terminate=False: revoked.setdefault("revoke", (task_id, terminate)),
    )

    await module.websocket_backtest_progress(websocket, "42")

    assert fake_manager.messages[0]["type"] == "connected"
    assert fake_manager.messages[1] == {
        "type": "cancelled",
        "backtest_id": "42",
        "task_id": "celery-task-42",
        "message": "回测已取消",
    }
    assert revoked == {
        "revoke": ("celery-task-42", True),
        "callback": "42",
        "mapping": "42",
        "status": "42",
    }
    assert fake_manager.disconnected == [(websocket, "42")]


async def test_backtest_ws_cancel_fails_honestly_without_runtime_mapping(monkeypatch):
    module = _load_module()
    fake_manager = _FakeManager()
    websocket = _FakeWebSocket(module, ['{"type":"cancel"}'])

    monkeypatch.setattr(module, "manager", fake_manager)
    monkeypatch.setattr(module, "get_backtest_task_id", lambda backtest_id: None)

    await module.websocket_backtest_progress(websocket, "77")

    assert fake_manager.messages[0]["type"] == "connected"
    assert fake_manager.messages[1] == {
        "type": "cancel_failed",
        "backtest_id": "77",
        "message": "未找到可取消的运行中回测任务",
    }
    assert fake_manager.disconnected == [(websocket, "77")]
