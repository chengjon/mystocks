"""
File-level contract tests for backtest_ws.py.

这些测试直接验证路由注册和 WebSocket 连接管理逻辑，
替代原先只检查 fixture 的占位断言。
"""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import WebSocketDisconnect


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture
def backtest_ws_module(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("POSTGRESQL_HOST", "localhost")
    monkeypatch.setenv("POSTGRESQL_USER", "postgres")
    monkeypatch.setenv("POSTGRESQL_PASSWORD", "password")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("BACKEND_PORT", "8020")
    monkeypatch.setenv("BACKEND_BACKUP_PORT", "8021")

    module = importlib.import_module("app.api.backtest_ws")
    module.manager.connections.clear()
    return module


class DummyWebSocket:
    def __init__(self, messages: list[object] | None = None):
        self.accept = AsyncMock()
        self.send_text = AsyncMock()
        self.receive_text = AsyncMock(side_effect=messages or [WebSocketDisconnect()])


class TestBacktestWsAPIFile:
    @pytest.mark.file_test
    def test_router_registers_expected_routes(self, backtest_ws_module):
        route_map = {
            (route.path, tuple(sorted(getattr(route, "methods", set()) or [])))
            for route in backtest_ws_module.router.routes
        }
        route_paths = {route.path for route in backtest_ws_module.router.routes}

        assert backtest_ws_module.router.prefix == "/ws"
        assert "/ws/backtest/{backtest_id}" in route_paths
        assert ("/ws/status", ("GET",)) in route_map

    @pytest.mark.file_test
    @pytest.mark.asyncio
    async def test_connection_manager_connect_registers_callback(self, backtest_ws_module, monkeypatch):
        websocket = DummyWebSocket()
        register_callback = Mock()
        monkeypatch.setattr(backtest_ws_module, "register_progress_callback", register_callback)
        manager = backtest_ws_module.ConnectionManager()

        await manager.connect(websocket, "bt-1")

        websocket.accept.assert_called_once_with()
        assert websocket in manager.connections["bt-1"]
        register_callback.assert_called_once()
        assert register_callback.call_args.args[0] == "bt-1"
        assert callable(register_callback.call_args.args[1])

    @pytest.mark.file_test
    def test_connection_manager_disconnect_unregisters_last_subscription(self, backtest_ws_module, monkeypatch):
        unregister_callback = Mock()
        monkeypatch.setattr(backtest_ws_module, "unregister_progress_callback", unregister_callback)
        manager = backtest_ws_module.ConnectionManager()
        websocket = DummyWebSocket()
        manager.connections["bt-1"] = {websocket}

        manager.disconnect(websocket, "bt-1")

        assert "bt-1" not in manager.connections
        unregister_callback.assert_called_once_with("bt-1")

    @pytest.mark.file_test
    @pytest.mark.asyncio
    async def test_broadcast_serializes_payload_and_prunes_broken_connections(self, backtest_ws_module):
        healthy = DummyWebSocket()
        broken = DummyWebSocket()
        broken.send_text.side_effect = RuntimeError("socket closed")
        manager = backtest_ws_module.ConnectionManager()
        manager.connections["bt-1"] = {healthy, broken}

        await manager.broadcast("bt-1", {"type": "progress", "value": 42})

        healthy.send_text.assert_called_once_with(json.dumps({"type": "progress", "value": 42}))
        assert broken not in manager.connections["bt-1"]

    @pytest.mark.file_test
    @pytest.mark.asyncio
    async def test_websocket_handler_replies_to_ping(self, backtest_ws_module, monkeypatch):
        websocket = DummyWebSocket(messages=[json.dumps({"type": "ping"}), WebSocketDisconnect()])
        register_callback = Mock()
        unregister_callback = Mock()
        monkeypatch.setattr(backtest_ws_module, "register_progress_callback", register_callback)
        monkeypatch.setattr(backtest_ws_module, "unregister_progress_callback", unregister_callback)
        backtest_ws_module.manager = backtest_ws_module.ConnectionManager()

        await backtest_ws_module.websocket_backtest_progress(websocket, "bt-2")

        sent_messages = [json.loads(call.args[0]) for call in websocket.send_text.call_args_list]
        assert sent_messages[0]["type"] == "connected"
        assert sent_messages[0]["backtest_id"] == "bt-2"
        assert sent_messages[1] == {"type": "pong"}
        unregister_callback.assert_called_once_with("bt-2")

    @pytest.mark.file_test
    @pytest.mark.asyncio
    async def test_websocket_handler_acknowledges_cancel_and_disconnects(self, backtest_ws_module, monkeypatch):
        websocket = DummyWebSocket(messages=[json.dumps({"type": "cancel"})])
        register_callback = Mock()
        unregister_callback = Mock()
        monkeypatch.setattr(backtest_ws_module, "register_progress_callback", register_callback)
        monkeypatch.setattr(backtest_ws_module, "unregister_progress_callback", unregister_callback)
        backtest_ws_module.manager = backtest_ws_module.ConnectionManager()

        await backtest_ws_module.websocket_backtest_progress(websocket, "bt-3")

        sent_messages = [json.loads(call.args[0]) for call in websocket.send_text.call_args_list]
        assert sent_messages[-1] == {"type": "cancelled", "message": "回测已取消"}
        assert "bt-3" not in backtest_ws_module.manager.connections
        unregister_callback.assert_called_once_with("bt-3")

    @pytest.mark.file_test
    @pytest.mark.asyncio
    async def test_status_endpoint_reports_active_connection_counts(self, backtest_ws_module):
        backtest_ws_module.manager.connections = {
            "bt-1": {DummyWebSocket(), DummyWebSocket()},
            "bt-2": {DummyWebSocket()},
        }

        payload = await backtest_ws_module.get_websocket_status()

        assert payload == {
            "status": "ok",
            "total_connections": 3,
            "backtest_subscriptions": 2,
            "details": {"bt-1": 2, "bt-2": 1},
        }

    @pytest.mark.file_test
    @pytest.mark.asyncio
    async def test_send_personal_message_forwards_raw_text(self, backtest_ws_module):
        websocket = DummyWebSocket()
        manager = backtest_ws_module.ConnectionManager()

        await manager.send_personal_message('{"type":"connected"}', websocket)

        websocket.send_text.assert_called_once_with('{"type":"connected"}')
