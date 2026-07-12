"""Singleton helpers for `MySocketIOManager`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from app.core.socketio_manager import MySocketIOManager

_socketio_manager: Optional[MySocketIOManager] = None


def get_socketio_manager() -> MySocketIOManager:
    """获取Socket.IO管理器单例"""
    global _socketio_manager
    if _socketio_manager is None:
        from app.core.socketio_manager import MySocketIOManager

        _socketio_manager = MySocketIOManager()
    return _socketio_manager


def reset_socketio_manager() -> None:
    """重置Socket.IO管理器（仅用于测试）"""
    global _socketio_manager
    _socketio_manager = None
