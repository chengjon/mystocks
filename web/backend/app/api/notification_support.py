"""
通知管理 API 运行时辅助组件
"""

from datetime import datetime, timezone
from functools import wraps
from typing import Dict, List

import structlog
from fastapi import HTTPException, WebSocket

from app.api.notification_models import RealTimeNotification

logger = structlog.get_logger()


class RateLimiter:
    """内存速率限制器"""

    def __init__(self):
        self.requests = {}

    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """检查是否允许请求"""
        now = datetime.now(timezone.utc)

        if key not in self.requests:
            self.requests[key] = []

        self.requests[key] = [req_time for req_time in self.requests[key] if (now - req_time).seconds < window]

        if len(self.requests[key]) >= limit:
            return False

        self.requests[key].append(now)
        return True


rate_limiter = RateLimiter()


def rate_limit(limit: int, window: int):
    """速率限制装饰器"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = None
            for arg in args:
                if hasattr(arg, "id"):
                    current_user = arg
                    break

            if not current_user:
                for value in kwargs.values():
                    if hasattr(value, "id"):
                        current_user = value
                        break

            user_key = f"user_{current_user.id}" if current_user else "anonymous"

            if not rate_limiter.is_allowed(user_key, limit, window):
                raise HTTPException(status_code=429, detail=f"请求过于频繁，请在{window}秒后重试")

            return await func(*args, **kwargs)

        return wrapper

    return decorator


class ConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """接受WebSocket连接"""
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = []

        self.active_connections[user_id].append(websocket)
        logger.info("WebSocket连接建立", user_id=user_id)

    def disconnect(self, websocket: WebSocket, user_id: int):
        """断开WebSocket连接"""
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)

            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

        logger.info("WebSocket连接断开", user_id=user_id)

    async def send_personal_notification(self, notification: RealTimeNotification):
        """发送个人实时通知"""
        user_id = notification.user_id

        if user_id in self.active_connections:
            message = notification.dict()
            dead_connections = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    dead_connections.append(connection)

            for dead_connection in dead_connections:
                self.disconnect(dead_connection, user_id)

    async def broadcast_system_notification(self, notification: RealTimeNotification):
        """广播系统通知"""
        message = notification.dict()
        dead_connections = []
        for user_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception:
                    dead_connections.append((user_id, connection))

        for user_id, connection in dead_connections:
            self.disconnect(connection, user_id)


connection_manager = ConnectionManager()


def validate_notification_preferences(user_id: int, notification_type: str) -> bool:
    """验证用户通知偏好（简化实现）"""
    return True


def is_in_quiet_hours(user_id: int) -> bool:
    """检查是否在免打扰时间"""
    return False
