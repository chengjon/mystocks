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
from app.core.reconnection_manager import get_reconnection_manager
from app.services.realtime_streaming_service import (
    get_streaming_service,
    StreamEventType,
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

        # 在重连管理器中注册连接
        reconnection_manager = get_reconnection_manager()
        reconnection_manager.register_connection(sid, user_id)

        # 获取并补发缓冲的消息（用于重连）
        buffered_messages = reconnection_manager.get_buffered_messages(sid)
        if buffered_messages:
            logger.info(
                "📨 Resending buffered messages after reconnection",
                sid=sid,
                message_count=len(buffered_messages),
            )
            for msg in buffered_messages:
                await self.emit(msg.event, msg.data, to=sid)
                reconnection_manager.mark_message_sent(sid, msg.id)

        # 标记已重连成功
        reconnection_manager.mark_reconnected(sid)

        # Initialize streaming state for this connection
        streaming_service = get_streaming_service()
        # Note: Streaming subscriptions are explicitly managed via on_subscribe_market_stream
        logger.info(
            "🎬 Streaming support initialized for connection",
            sid=sid,
            user_id=user_id,
        )

        await self.emit("connect_response", {"status": "connected", "sid": sid})

    async def on_disconnect(self, sid: str):
        """断开连接事件处理"""
        self.sio.connection_manager.remove_connection(sid)

        # 在重连管理器中标记为已断开
        reconnection_manager = get_reconnection_manager()
        reconnection_manager.mark_disconnected(sid)

        # Clean up streaming subscriptions for this connection
        streaming_service = get_streaming_service()
        active_symbols = streaming_service.get_active_symbols()
        for symbol in active_symbols:
            streaming_service.unsubscribe(sid, symbol)

        logger.info(
            "🎬 Streaming subscriptions cleaned up on disconnect",
            sid=sid,
        )

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

    async def on_subscribe_market_stream(self, sid: str, data: dict):
        """Market data stream subscription event handler"""
        self.sio.connection_manager.update_activity(sid)

        try:
            symbol = data.get("symbol")
            if not symbol:
                await self.emit(
                    "stream_error",
                    {
                        "error_code": "INVALID_SYMBOL",
                        "message": "Stock symbol cannot be empty",
                    },
                    to=sid,
                )
                return

            # Extract optional fields filter
            fields = data.get("fields")
            if fields and isinstance(fields, list):
                fields = set(fields)
            else:
                fields = None

            # Subscribe to streaming service
            streaming_service = get_streaming_service()
            connection = self.sio.connection_manager.get_connection(sid)
            user_id = connection.get("user_id") if connection else None

            success = streaming_service.subscribe(sid, symbol, user_id, fields)

            if success:
                logger.info(
                    "✅ Market stream subscription",
                    sid=sid,
                    symbol=symbol,
                    fields=fields,
                )

                await self.emit(
                    "stream_subscribed",
                    {
                        "symbol": symbol,
                        "status": "subscribed",
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                    to=sid,
                )
            else:
                await self.emit(
                    "stream_error",
                    {
                        "error_code": "SUBSCRIPTION_FAILED",
                        "message": f"Failed to subscribe to {symbol}",
                    },
                    to=sid,
                )

        except Exception as e:
            logger.error("❌ Market stream subscription failed", error=str(e), sid=sid)
            await self.emit(
                "stream_error",
                {
                    "error_code": "INTERNAL_ERROR",
                    "message": "Server error during subscription",
                },
                to=sid,
            )

    async def on_unsubscribe_market_stream(self, sid: str, data: dict):
        """Market data stream unsubscription event handler"""
        self.sio.connection_manager.update_activity(sid)

        try:
            symbol = data.get("symbol")
            if not symbol:
                await self.emit(
                    "stream_error",
                    {
                        "error_code": "INVALID_SYMBOL",
                        "message": "Stock symbol cannot be empty",
                    },
                    to=sid,
                )
                return

            # Unsubscribe from streaming service
            streaming_service = get_streaming_service()
            success = streaming_service.unsubscribe(sid, symbol)

            if success:
                logger.info("✅ Market stream unsubscription", sid=sid, symbol=symbol)

                await self.emit(
                    "stream_unsubscribed",
                    {
                        "symbol": symbol,
                        "status": "unsubscribed",
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                    to=sid,
                )
            else:
                await self.emit(
                    "stream_error",
                    {
                        "error_code": "UNSUBSCRIPTION_FAILED",
                        "message": f"Failed to unsubscribe from {symbol}",
                    },
                    to=sid,
                )

        except Exception as e:
            logger.error(
                "❌ Market stream unsubscription failed", error=str(e), sid=sid
            )
            await self.emit(
                "stream_error",
                {
                    "error_code": "INTERNAL_ERROR",
                    "message": "Server error during unsubscription",
                },
                to=sid,
            )

    async def on_stream_filter_update(self, sid: str, data: dict):
        """Update field filter for market data stream"""
        self.sio.connection_manager.update_activity(sid)

        try:
            symbol = data.get("symbol")
            fields = data.get("fields")

            if not symbol or not fields:
                await self.emit(
                    "stream_error",
                    {
                        "error_code": "INVALID_PARAMETERS",
                        "message": "Symbol and fields are required",
                    },
                    to=sid,
                )
                return

            # Get streaming service and update subscriber fields
            streaming_service = get_streaming_service()
            stream = streaming_service.get_stream(symbol)

            if not stream:
                await self.emit(
                    "stream_error",
                    {
                        "error_code": "STREAM_NOT_FOUND",
                        "message": f"Stream for {symbol} not found",
                    },
                    to=sid,
                )
                return

            # Update subscriber fields
            if sid in stream.subscribers:
                stream.subscribers[sid].fields = set(fields)
                logger.info(
                    "✅ Stream filter updated",
                    sid=sid,
                    symbol=symbol,
                    fields=fields,
                )

                await self.emit(
                    "stream_filter_updated",
                    {
                        "symbol": symbol,
                        "fields": fields,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                    to=sid,
                )
            else:
                await self.emit(
                    "stream_error",
                    {
                        "error_code": "SUBSCRIBER_NOT_FOUND",
                        "message": f"No subscription found for {symbol}",
                    },
                    to=sid,
                )

        except Exception as e:
            logger.error("❌ Stream filter update failed", error=str(e), sid=sid)
            await self.emit(
                "stream_error",
                {
                    "error_code": "INTERNAL_ERROR",
                    "message": "Server error during filter update",
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

        # 添加重连管理器统计
        reconnection_manager = get_reconnection_manager()
        reconnection_stats = reconnection_manager.get_all_stats()
        stats["reconnection"] = reconnection_stats

        # 添加流服务统计
        streaming_service = get_streaming_service()
        streaming_stats = streaming_service.get_stats()
        stats["streaming"] = streaming_stats

        return stats

    async def emit_stream_data(
        self,
        symbol: str,
        data: Dict[str, Any],
    ) -> None:
        """Emit market data to stream subscribers (room-based broadcast)"""
        try:
            streaming_service = get_streaming_service()
            stream = streaming_service.get_stream(symbol)

            if not stream:
                logger.warning(
                    "⚠️ Stream not found for symbol",
                    symbol=symbol,
                )
                return

            # Broadcast data to all subscribers in the stream
            # Use symbol as room name for Socket.IO broadcast
            await self.sio.emit(
                "stream_data",
                {
                    "symbol": symbol,
                    "data": data,
                    "timestamp": datetime.utcnow().isoformat(),
                },
                to=f"stream_{symbol}",
            )

            # Also record the broadcast in the stream
            streaming_service.broadcast_data(symbol, data)

        except Exception as e:
            logger.error(
                "❌ Error emitting stream data",
                symbol=symbol,
                error=str(e),
            )

    def get_streaming_stats(self) -> Dict[str, Any]:
        """Get real-time streaming service statistics"""
        streaming_service = get_streaming_service()
        return streaming_service.get_stats()


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
