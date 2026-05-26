from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.core import socketio_manager
from app.core.socketio_manager import MySocketIOManager, MySocketIONamespace


class FakeStreamingService:
    def __init__(self) -> None:
        self.stats_calls = 0
        self.stream_lookups: list[str] = []
        self.broadcasts: list[tuple[str, dict]] = []
        self.subscriptions: list[tuple[str, str, str | None, set[str] | None]] = []
        self.unsubscriptions: list[tuple[str, str]] = []

    def get_stats(self) -> dict:
        self.stats_calls += 1
        return {"source": "fake-streaming-service"}

    def get_stream(self, symbol: str) -> object:
        self.stream_lookups.append(symbol)
        return object()

    def broadcast_data(self, symbol: str, data: dict) -> None:
        self.broadcasts.append((symbol, data))

    def subscribe(
        self,
        sid: str,
        symbol: str,
        user_id: str | None = None,
        fields: set[str] | None = None,
    ) -> bool:
        self.subscriptions.append((sid, symbol, user_id, fields))
        return True

    def unsubscribe(self, sid: str, symbol: str) -> bool:
        self.unsubscriptions.append((sid, symbol))
        return True


def _reject_global_streaming_getter():
    raise AssertionError("Socket.IO manager should use its injected streaming service")


@pytest.mark.asyncio
async def test_manager_uses_injected_streaming_service(monkeypatch):
    fake = FakeStreamingService()
    monkeypatch.setattr(socketio_manager, "get_streaming_service", _reject_global_streaming_getter)

    manager = MySocketIOManager(streaming_service=fake)
    manager.sio.emit = AsyncMock()

    assert manager.get_streaming_stats() == {"source": "fake-streaming-service"}

    await manager.emit_stream_data("600000", {"price": 12.34})

    assert fake.stats_calls == 1
    assert fake.stream_lookups == ["600000"]
    assert fake.broadcasts == [("600000", {"price": 12.34})]
    manager.sio.emit.assert_awaited_once()


@pytest.mark.asyncio
async def test_namespace_stream_events_use_manager_injected_streaming_service(monkeypatch):
    fake = FakeStreamingService()
    monkeypatch.setattr(socketio_manager, "get_streaming_service", _reject_global_streaming_getter)

    manager = MySocketIOManager(streaming_service=fake)
    manager.connection_manager.add_connection("sid-1", user_id="user-1")
    namespace = MySocketIONamespace("/", manager)
    namespace.emit = AsyncMock()

    await namespace.on_subscribe_market_stream(
        "sid-1",
        {
            "symbol": "600000",
            "fields": ["price", "volume"],
        },
    )
    await namespace.on_unsubscribe_market_stream("sid-1", {"symbol": "600000"})

    assert fake.subscriptions == [("sid-1", "600000", "user-1", {"price", "volume"})]
    assert fake.unsubscriptions == [("sid-1", "600000")]
    assert namespace.emit.await_count == 2
