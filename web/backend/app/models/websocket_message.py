"""
WebSocket消息格式定义
WebSocket Message Format Specification

定义统一的WebSocket通信消息格式，包括：
- 请求消息 (Request)
- 响应消息 (Response)
- 错误消息 (Error)
- 心跳消息 (Heartbeat)

Author: Claude Code
Date: 2025-11-06
"""

from enum import Enum
from typing import Any, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class WebSocketMessageType(str, Enum):
    """WebSocket消息类型枚举"""

    # 客户端->服务器
    REQUEST = "request"  # 数据请求
    SUBSCRIBE = "subscribe"  # 房间订阅
    UNSUBSCRIBE = "unsubscribe"  # 取消订阅
    PING = "ping"  # 心跳请求

    # 服务器->客户端
    RESPONSE = "response"  # 数据响应
    ERROR = "error"  # 错误响应
    NOTIFICATION = "notification"  # 服务器推送通知
    PONG = "pong"  # 心跳响应


class WebSocketRequestMessage(BaseModel):
    """
    WebSocket请求消息格式

    客户端发送给服务器的消息统一格式

    Example:
        ```python
        {
            "type": "request",
            "request_id": "req_1234567890",
            "action": "get_market_data",
            "payload": {
                "symbol": "600519",
                "data_type": "fund_flow",
                "timeframe": "1d"
            },
            "user_id": "user_001",
            "timestamp": 1699267200000,
            "trace_id": "trace_abc123"
        }
        ```
    """

    type: WebSocketMessageType = Field(
        default=WebSocketMessageType.REQUEST, description="消息类型 (固定为request)"
    )
    request_id: str = Field(..., description="请求唯一标识符 (用于请求-响应匹配)")
    action: str = Field(
        ..., description="请求操作类型 (如: get_market_data, subscribe_room)"
    )
    payload: Dict[str, Any] = Field(default_factory=dict, description="请求数据负载")
    user_id: Optional[str] = Field(None, description="用户ID (已认证用户)")
    timestamp: int = Field(
        default_factory=lambda: int(datetime.utcnow().timestamp() * 1000),
        description="UTC毫秒级时间戳",
    )
    trace_id: Optional[str] = Field(None, description="追踪ID (用于分布式追踪)")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "request",
                "request_id": "req_1234567890",
                "action": "get_market_data",
                "payload": {
                    "symbol": "600519",
                    "data_type": "fund_flow",
                    "timeframe": "1d",
                },
                "user_id": "user_001",
                "timestamp": 1699267200000,
                "trace_id": "trace_abc123",
            }
        }


class WebSocketResponseMessage(BaseModel):
    """
    WebSocket响应消息格式

    服务器返回给客户端的成功响应

    Example:
        ```python
        {
            "type": "response",
            "request_id": "req_1234567890",
            "success": true,
            "data": {
                "symbol": "600519",
                "fund_flow": {
                    "main_inflow": 123.45,
                    "retail_outflow": -67.89
                }
            },
            "timestamp": 1699267201500,
            "server_time": 1699267201500,
            "trace_id": "trace_abc123"
        }
        ```
    """

    type: WebSocketMessageType = Field(
        default=WebSocketMessageType.RESPONSE, description="消息类型 (固定为response)"
    )
    request_id: str = Field(..., description="对应的请求ID")
    success: bool = Field(default=True, description="请求是否成功")
    data: Any = Field(None, description="响应数据负载")
    timestamp: int = Field(
        default_factory=lambda: int(datetime.utcnow().timestamp() * 1000),
        description="UTC毫秒级时间戳",
    )
    server_time: int = Field(
        default_factory=lambda: int(datetime.utcnow().timestamp() * 1000),
        description="服务器时间 (UTC毫秒)",
    )
    trace_id: Optional[str] = Field(None, description="追踪ID")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "response",
                "request_id": "req_1234567890",
                "success": True,
                "data": {
                    "symbol": "600519",
                    "fund_flow": {"main_inflow": 123.45, "retail_outflow": -67.89},
                },
                "timestamp": 1699267201500,
                "server_time": 1699267201500,
                "trace_id": "trace_abc123",
            }
        }


class WebSocketErrorMessage(BaseModel):
    """
    WebSocket错误消息格式

    服务器返回给客户端的错误响应

    Example:
        ```python
        {
            "type": "error",
            "request_id": "req_1234567890",
            "error_code": "INVALID_SYMBOL",
            "error_message": "股票代码不存在或格式不正确",
            "error_details": {
                "symbol": "INVALID",
                "hint": "请使用6位数字股票代码"
            },
            "timestamp": 1699267201500,
            "trace_id": "trace_abc123"
        }
        ```
    """

    type: WebSocketMessageType = Field(
        default=WebSocketMessageType.ERROR, description="消息类型 (固定为error)"
    )
    request_id: Optional[str] = Field(None, description="对应的请求ID (如果有)")
    error_code: str = Field(
        ..., description="错误代码 (如: INVALID_SYMBOL, AUTH_FAILED)"
    )
    error_message: str = Field(..., description="人类可读的错误描述")
    error_details: Optional[Dict[str, Any]] = Field(None, description="错误详细信息")
    timestamp: int = Field(
        default_factory=lambda: int(datetime.utcnow().timestamp() * 1000),
        description="UTC毫秒级时间戳",
    )
    trace_id: Optional[str] = Field(None, description="追踪ID")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "error",
                "request_id": "req_1234567890",
                "error_code": "INVALID_SYMBOL",
                "error_message": "股票代码不存在或格式不正确",
                "error_details": {"symbol": "INVALID", "hint": "请使用6位数字股票代码"},
                "timestamp": 1699267201500,
                "trace_id": "trace_abc123",
            }
        }


class WebSocketSubscribeMessage(BaseModel):
    """
    WebSocket房间订阅消息

    客户端订阅特定房间以接收实时数据

    Example:
        ```python
        {
            "type": "subscribe",
            "request_id": "sub_1234567890",
            "room": "market_600519",
            "user_id": "user_001",
            "timestamp": 1699267200000
        }
        ```
    """

    type: WebSocketMessageType = Field(
        default=WebSocketMessageType.SUBSCRIBE, description="消息类型 (固定为subscribe)"
    )
    request_id: str = Field(..., description="订阅请求ID")
    room: str = Field(..., description="房间名称 (如: market_600519, portfolio_001)")
    user_id: Optional[str] = Field(None, description="用户ID")
    timestamp: int = Field(
        default_factory=lambda: int(datetime.utcnow().timestamp() * 1000),
        description="UTC毫秒级时间戳",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "type": "subscribe",
                "request_id": "sub_1234567890",
                "room": "market_600519",
                "user_id": "user_001",
                "timestamp": 1699267200000,
            }
        }


class WebSocketNotificationMessage(BaseModel):
    """
    WebSocket服务器推送通知

    服务器主动推送给订阅房间的客户端

    Example:
        ```python
        {
            "type": "notification",
            "room": "market_600519",
            "event": "price_update",
            "data": {
                "symbol": "600519",
                "price": 1850.50,
                "change": 2.5
            },
            "timestamp": 1699267202000,
            "server_time": 1699267202000
        }
        ```
    """

    type: WebSocketMessageType = Field(
        default=WebSocketMessageType.NOTIFICATION,
        description="消息类型 (固定为notification)",
    )
    room: str = Field(..., description="推送目标房间")
    event: str = Field(..., description="事件类型 (如: price_update, alert)")
    data: Any = Field(..., description="推送数据负载")
    timestamp: int = Field(
        default_factory=lambda: int(datetime.utcnow().timestamp() * 1000),
        description="UTC毫秒级时间戳",
    )
    server_time: int = Field(
        default_factory=lambda: int(datetime.utcnow().timestamp() * 1000),
        description="服务器时间 (UTC毫秒)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "type": "notification",
                "room": "market_600519",
                "event": "price_update",
                "data": {"symbol": "600519", "price": 1850.50, "change": 2.5},
                "timestamp": 1699267202000,
                "server_time": 1699267202000,
            }
        }


class WebSocketHeartbeatMessage(BaseModel):
    """
    WebSocket心跳消息

    用于检测连接状态，防止超时断开

    客户端发送PING，服务器回复PONG

    Example (PING):
        ```python
        {
            "type": "ping",
            "timestamp": 1699267200000
        }
        ```

    Example (PONG):
        ```python
        {
            "type": "pong",
            "timestamp": 1699267200500,
            "server_time": 1699267200500
        }
        ```
    """

    type: WebSocketMessageType = Field(..., description="消息类型 (ping或pong)")
    timestamp: int = Field(
        default_factory=lambda: int(datetime.utcnow().timestamp() * 1000),
        description="UTC毫秒级时间戳",
    )
    server_time: Optional[int] = Field(None, description="服务器时间 (仅PONG)")

    class Config:
        json_schema_extra = {
            "examples": [
                {"type": "ping", "timestamp": 1699267200000},
                {
                    "type": "pong",
                    "timestamp": 1699267200500,
                    "server_time": 1699267200500,
                },
            ]
        }


# ==================== 常用错误代码 ====================


class WebSocketErrorCode(str, Enum):
    """WebSocket错误代码枚举"""

    # 认证相关
    AUTH_REQUIRED = "AUTH_REQUIRED"  # 需要认证
    AUTH_FAILED = "AUTH_FAILED"  # 认证失败
    AUTH_TOKEN_EXPIRED = "AUTH_TOKEN_EXPIRED"  # Token过期

    # 请求相关
    INVALID_MESSAGE_FORMAT = "INVALID_MESSAGE_FORMAT"  # 消息格式无效
    INVALID_ACTION = "INVALID_ACTION"  # 操作类型无效
    INVALID_SYMBOL = "INVALID_SYMBOL"  # 股票代码无效
    INVALID_PARAMETERS = "INVALID_PARAMETERS"  # 参数无效

    # 权限相关
    PERMISSION_DENIED = "PERMISSION_DENIED"  # 权限不足
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"  # 超过速率限制

    # 订阅相关
    ROOM_NOT_FOUND = "ROOM_NOT_FOUND"  # 房间不存在
    SUBSCRIPTION_FAILED = "SUBSCRIPTION_FAILED"  # 订阅失败
    ALREADY_SUBSCRIBED = "ALREADY_SUBSCRIBED"  # 已订阅

    # 服务器相关
    INTERNAL_ERROR = "INTERNAL_ERROR"  # 服务器内部错误
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"  # 服务不可用
    TIMEOUT = "TIMEOUT"  # 请求超时


# ==================== Helper Functions ====================


def create_request_message(
    request_id: str,
    action: str,
    payload: Dict[str, Any],
    user_id: Optional[str] = None,
    trace_id: Optional[str] = None,
) -> WebSocketRequestMessage:
    """创建请求消息"""
    return WebSocketRequestMessage(
        request_id=request_id,
        action=action,
        payload=payload,
        user_id=user_id,
        trace_id=trace_id,
    )


def create_response_message(
    request_id: str,
    data: Any,
    trace_id: Optional[str] = None,
) -> WebSocketResponseMessage:
    """创建响应消息"""
    return WebSocketResponseMessage(
        request_id=request_id, success=True, data=data, trace_id=trace_id
    )


def create_error_message(
    error_code: str,
    error_message: str,
    request_id: Optional[str] = None,
    error_details: Optional[Dict[str, Any]] = None,
    trace_id: Optional[str] = None,
) -> WebSocketErrorMessage:
    """创建错误消息"""
    return WebSocketErrorMessage(
        request_id=request_id,
        error_code=error_code,
        error_message=error_message,
        error_details=error_details,
        trace_id=trace_id,
    )


def create_ping_message() -> WebSocketHeartbeatMessage:
    """创建PING心跳消息"""
    return WebSocketHeartbeatMessage(type=WebSocketMessageType.PING)


def create_pong_message() -> WebSocketHeartbeatMessage:
    """创建PONG心跳响应"""
    return WebSocketHeartbeatMessage(
        type=WebSocketMessageType.PONG,
        server_time=int(datetime.utcnow().timestamp() * 1000),
    )
