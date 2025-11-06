"""
Socket.IO服务器管理器
Socket.IO Server Manager - Real-time WebSocket Communication

Task 4.1: 实现Socket.IO服务器

实现Socket.IO服务器的以下功能:
- WebSocket连接管理
- 异步事件处理
- 房间管理 (Room-based subscriptions)
- 消息路由 (Message routing)
- 连接生命周期管理

Author: Claude Code
Date: 2025-11-06
"""

import uuid
from typing import Dict, List, Optional, Callable, Any, Set
from datetime import datetime
import structlog

try:
    from socketio import AsyncServer, AsyncNamespace
except ImportError:
    raise ImportError(
        "python-socketio is not installed. Install it with: pip install python-socketio"
    )

from app.models.websocket_message import (
    WebSocketMessageType,
    WebSocketRequestMessage,
    WebSocketResponseMessage,
    WebSocketErrorMessage,
    WebSocketErrorCode,
    WebSocketSubscribeMessage,
    WebSocketHeartbeatMessage,
    create_response_message,
    create_error_message,
    create_pong_message,
)

logger = structlog.get_logger()


class ConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        """初始化连接管理器"""
        self.active_connections: Dict[str, Dict[str, Any]] = {}
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> set of sid
        self.room_members: Dict[str, Set[str]] = {}  # room_name -> set of sid

    def add_connection(self, sid: str, user_id: Optional[str] = None) -> None:
        """添加新连接"""
        self.active_connections[sid] = {
            "sid": sid,
            "user_id": user_id,
            "connected_at": datetime.utcnow(),
            "rooms": set(),
            "message_count": 0,
            "last_activity": datetime.utcnow(),
        }

        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(sid)

        logger.info(
            "✅ 新连接已建立",
            sid=sid,
            user_id=user_id,
            total_connections=len(self.active_connections),
        )

    def remove_connection(self, sid: str) -> Optional[str]:
        """移除连接"""
        if sid not in self.active_connections:
            return None

        connection = self.active_connections.pop(sid)
        user_id = connection.get("user_id")

        # 从用户连接映射中移除
        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].discard(sid)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

        # 从房间移除
        for room in connection.get("rooms", set()):
            if room in self.room_members:
                self.room_members[room].discard(sid)
                if not self.room_members[room]:
                    del self.room_members[room]

        logger.info(
            "✅ 连接已断开",
            sid=sid,
            user_id=user_id,
            rooms=list(connection.get("rooms", [])),
            total_connections=len(self.active_connections),
        )

        return user_id

    def get_connection(self, sid: str) -> Optional[Dict[str, Any]]:
        """获取连接信息"""
        return self.active_connections.get(sid)

    def is_connected(self, sid: str) -> bool:
        """检查连接是否活跃"""
        return sid in self.active_connections

    def subscribe_to_room(self, sid: str, room: str) -> bool:
        """订阅房间"""
        if sid not in self.active_connections:
            logger.warning("⚠️ 尝试订阅不存在的连接", sid=sid, room=room)
            return False

        self.active_connections[sid]["rooms"].add(room)

        if room not in self.room_members:
            self.room_members[room] = set()
        self.room_members[room].add(sid)

        logger.info(
            "✅ 已订阅房间",
            sid=sid,
            room=room,
            room_members=len(self.room_members[room]),
        )

        return True

    def unsubscribe_from_room(self, sid: str, room: str) -> bool:
        """取消订阅房间"""
        if sid not in self.active_connections:
            return False

        self.active_connections[sid]["rooms"].discard(room)

        if room in self.room_members:
            self.room_members[room].discard(sid)
            if not self.room_members[room]:
                del self.room_members[room]

        logger.info("✅ 已取消订阅房间", sid=sid, room=room)

        return True

    def get_room_members(self, room: str) -> Set[str]:
        """获取房间成员"""
        return self.room_members.get(room, set()).copy()

    def get_user_connections(self, user_id: str) -> List[str]:
        """获取用户所有连接"""
        return list(self.user_connections.get(user_id, set()))

    def update_activity(self, sid: str) -> None:
        """更新连接活动时间"""
        if sid in self.active_connections:
            self.active_connections[sid]["last_activity"] = datetime.utcnow()

    def increment_message_count(self, sid: str) -> None:
        """增加消息计数"""
        if sid in self.active_connections:
            self.active_connections[sid]["message_count"] += 1

    def get_stats(self) -> Dict[str, Any]:
        """获取连接统计"""
        return {
            "total_connections": len(self.active_connections),
            "total_users": len(self.user_connections),
            "total_rooms": len(self.room_members),
            "timestamp": datetime.utcnow().isoformat(),
        }


class MySocketIONamespace(AsyncNamespace):
    """MyStocks Socket.IO命名空间"""

    def __init__(self, namespace: str, sio: "MySocketIOManager"):
        super().__init__(namespace)
        self.sio = sio

    async def on_connect(self, sid: str, environ: dict):
        """连接事件处理"""
        user_id = environ.get("HTTP_X_USER_ID")
        self.sio.connection_manager.add_connection(sid, user_id)
        await self.emit("connect_response", {"status": "connected", "sid": sid})

    async def on_disconnect(self, sid: str):
        """断开连接事件处理"""
        self.sio.connection_manager.remove_connection(sid)

    async def on_subscribe(self, sid: str, data: dict):
        """订阅事件处理"""
        room = data.get("room")
        if not room:
            await self.emit(
                "error",
                {
                    "error_code": WebSocketErrorCode.INVALID_PARAMETERS,
                    "message": "房间名称不能为空",
                },
                to=sid,
            )
            return

        success = self.sio.connection_manager.subscribe_to_room(sid, room)
        if success:
            await self.emit(
                "subscribed",
                {"room": room, "status": "subscribed"},
                to=sid,
            )

            # 广播进房通知给房间其他成员
            await self.emit(
                "room_member_joined",
                {
                    "room": room,
                    "sid": sid,
                    "timestamp": datetime.utcnow().isoformat(),
                },
                to=room,
                skip_sid=sid,
            )
        else:
            await self.emit(
                "error",
                {
                    "error_code": WebSocketErrorCode.SUBSCRIPTION_FAILED,
                    "message": "订阅失败",
                },
                to=sid,
            )

    async def on_unsubscribe(self, sid: str, data: dict):
        """取消订阅事件处理"""
        room = data.get("room")
        if not room:
            return

        success = self.sio.connection_manager.unsubscribe_from_room(sid, room)
        if success:
            await self.emit(
                "unsubscribed",
                {"room": room, "status": "unsubscribed"},
                to=sid,
            )

            # 广播离房通知
            await self.emit(
                "room_member_left",
                {
                    "room": room,
                    "sid": sid,
                    "timestamp": datetime.utcnow().isoformat(),
                },
                to=room,
            )

    async def on_ping(self, sid: str, data: dict):
        """心跳PING事件处理"""
        self.sio.connection_manager.update_activity(sid)
        pong_message = create_pong_message()
        await self.emit(
            "pong",
            pong_message.model_dump(mode="json"),
            to=sid,
        )

    async def on_request(self, sid: str, data: dict):
        """请求事件处理"""
        self.sio.connection_manager.update_activity(sid)
        self.sio.connection_manager.increment_message_count(sid)

        try:
            # 验证请求消息格式
            request = WebSocketRequestMessage(**data)

            # 调用注册的请求处理器
            if request.action in self.sio.request_handlers:
                handler = self.sio.request_handlers[request.action]
                result = await handler(sid, request)

                if result.get("success"):
                    response = create_response_message(
                        request_id=request.request_id,
                        data=result.get("data"),
                        trace_id=request.trace_id,
                    )
                else:
                    response = create_error_message(
                        error_code=result.get("error_code", "INTERNAL_ERROR"),
                        error_message=result.get("error_message", "处理失败"),
                        request_id=request.request_id,
                        trace_id=request.trace_id,
                    )
            else:
                response = create_error_message(
                    error_code=WebSocketErrorCode.INVALID_ACTION,
                    error_message=f"未知的操作: {request.action}",
                    request_id=request.request_id,
                )

            # 发送响应
            await self.emit(
                "response",
                response.model_dump(mode="json"),
                to=sid,
            )

        except Exception as e:
            logger.error("❌ 请求处理失败", error=str(e), sid=sid)
            await self.emit(
                "error",
                {
                    "error_code": WebSocketErrorCode.INTERNAL_ERROR,
                    "message": "服务器处理错误",
                },
                to=sid,
            )


class MySocketIOManager:
    """MyStocks Socket.IO服务器管理器"""

    def __init__(self, async_mode: str = "asgi"):
        """初始化Socket.IO管理器"""
        self.sio = AsyncServer(
            async_mode=async_mode,
            cors_allowed_origins="*",
            logger=False,  # 禁用Socket.IO日志（使用structlog）
            engineio_logger=False,
        )

        self.connection_manager = ConnectionManager()
        self.request_handlers: Dict[str, Callable] = {}

        # 注册命名空间
        self.sio.register_namespace(MySocketIONamespace("/", self))

        logger.info("✅ Socket.IO服务器管理器已初始化")

    def register_request_handler(self, action: str, handler: Callable) -> None:
        """注册请求处理器"""
        self.request_handlers[action] = handler
        logger.info(f"✅ 已注册请求处理器: {action}")

    async def emit_to_room(
        self,
        room: str,
        event: str,
        data: Dict[str, Any],
        skip_sid: Optional[str] = None,
    ) -> None:
        """向房间广播消息"""
        await self.sio.emit(
            event,
            data,
            to=room,
            skip_sid=skip_sid,
        )

    async def emit_to_user(
        self,
        user_id: str,
        event: str,
        data: Dict[str, Any],
    ) -> None:
        """向用户广播消息（所有连接）"""
        sids = self.connection_manager.get_user_connections(user_id)
        for sid in sids:
            await self.sio.emit(event, data, to=sid)

    async def emit_to_sid(
        self,
        sid: str,
        event: str,
        data: Dict[str, Any],
    ) -> None:
        """向特定连接发送消息"""
        await self.sio.emit(event, data, to=sid)

    def get_stats(self) -> Dict[str, Any]:
        """获取Socket.IO统计信息"""
        stats = self.connection_manager.get_stats()
        stats["namespace"] = "/"
        return stats


# 全局单例
_socketio_manager: Optional[MySocketIOManager] = None


def get_socketio_manager() -> MySocketIOManager:
    """获取Socket.IO管理器单例"""
    global _socketio_manager
    if _socketio_manager is None:
        _socketio_manager = MySocketIOManager()
    return _socketio_manager


def reset_socketio_manager() -> None:
    """重置Socket.IO管理器（仅用于测试）"""
    global _socketio_manager
    _socketio_manager = None
