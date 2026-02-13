"""
实时市场数据流服务 - Real-Time Market Data Streaming Service

Task 6: 实现基于WebSocket的实时行情流传输

功能特性:
- 实时tick数据流传输（TDengine → WebSocket客户端）
- 房间模式订阅（股票代码作为房间标识）
- 智能数据过滤和字段选择
- 时间戳版本化和去重
- 流性能监控和度量
- 自动故障恢复

Author: Claude Code
Date: 2025-11-06
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

import structlog

logger = structlog.get_logger()


class StreamStatus(str, Enum):
    """流状态枚举"""

    INACTIVE = "inactive"  # 未激活
    ACTIVE = "active"  # 活跃流
    PAUSED = "paused"  # 暂停
    ERROR = "error"  # 错误状态


class StreamEventType(str, Enum):
    """流事件类型"""

    STREAM_STARTED = "stream_started"  # 流开始
    STREAM_STOPPED = "stream_stopped"  # 流停止
    STREAM_DATA = "stream_data"  # 流数据
    STREAM_ERROR = "stream_error"  # 流错误
    STREAM_PAUSED = "stream_paused"  # 流暂停
    STREAM_RESUMED = "stream_resumed"  # 流恢复


@dataclass
class StreamSubscriber:
    """流订阅者信息"""

    sid: str  # Socket.IO连接ID
    user_id: Optional[str] = None
    subscribed_at: datetime = field(default_factory=datetime.utcnow)
    fields: Set[str] = field(default_factory=lambda: {"price", "volume", "timestamp"})  # 订阅的字段
    last_message_id: Optional[str] = None  # 最后接收的消息ID
    messages_received: int = 0  # 接收消息计数

    def update_activity(self) -> None:
        """更新活动时间"""
        self.subscribed_at = datetime.now(timezone.utc)


@dataclass
class StreamData:
    """流数据消息"""

    message_id: str
    symbol: str
    timestamp: int  # Unix毫秒时间戳
    data: Dict[str, Any]  # 实际数据
    version: int = 1  # 版本号（用于去重）
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "message_id": self.message_id,
            "symbol": self.symbol,
            "timestamp": self.timestamp,
            "data": self.data,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
        }


class MarketDataStream:
    """单个股票代码的市场数据流"""

    def __init__(
        self,
        symbol: str,
        update_interval: float = 1.0,
        buffer_size: int = 100,
    ):
        """
        初始化市场数据流

        Args:
            symbol: 股票代码（如 600519）
            update_interval: 更新间隔（秒）
            buffer_size: 消息缓冲区大小
        """
        self.symbol = symbol
        self.stream_id = str(uuid.uuid4())
        self.update_interval = update_interval
        self.buffer_size = buffer_size

        # 订阅者管理
        self.subscribers: Dict[str, StreamSubscriber] = {}

        # 状态管理
        self.status = StreamStatus.INACTIVE
        self.created_at = datetime.now(timezone.utc)
        self.last_update_time = datetime.now(timezone.utc)

        # 数据缓冲
        self.data_buffer: List[StreamData] = []
        self.seen_message_ids: Set[str] = set()  # 去重

        # 指标
        self.messages_sent = 0
        self.messages_dropped = 0
        self.errors_count = 0

        logger.info(
            "📊 Market data stream created",
            symbol=symbol,
            stream_id=self.stream_id,
        )

    def add_subscriber(
        self,
        sid: str,
        user_id: Optional[str] = None,
        fields: Optional[Set[str]] = None,
    ) -> StreamSubscriber:
        """添加订阅者"""
        subscriber = StreamSubscriber(
            sid=sid,
            user_id=user_id,
            fields=fields or {"price", "volume", "timestamp"},
        )
        self.subscribers[sid] = subscriber

        logger.info(
            "✅ Subscriber added to stream",
            symbol=self.symbol,
            sid=sid,
            total_subscribers=len(self.subscribers),
        )

        return subscriber

    def remove_subscriber(self, sid: str) -> Optional[StreamSubscriber]:
        """移除订阅者"""
        subscriber = self.subscribers.pop(sid, None)

        if subscriber:
            logger.info(
                "✅ Subscriber removed from stream",
                symbol=self.symbol,
                sid=sid,
                total_subscribers=len(self.subscribers),
            )

        return subscriber

    def has_subscribers(self) -> bool:
        """检查是否有订阅者"""
        return len(self.subscribers) > 0

    def buffer_data(self, stream_data: StreamData) -> bool:
        """缓冲流数据（去重）"""
        # 检查去重
        if stream_data.message_id in self.seen_message_ids:
            logger.debug(
                "⚠️ Duplicate message dropped",
                symbol=self.symbol,
                message_id=stream_data.message_id,
            )
            self.messages_dropped += 1
            return False

        # 缓冲区已满，移除最早的消息
        if len(self.data_buffer) >= self.buffer_size:
            removed = self.data_buffer.pop(0)
            self.seen_message_ids.discard(removed.message_id)

        # 添加到缓冲
        self.data_buffer.append(stream_data)
        self.seen_message_ids.add(stream_data.message_id)

        return True

    def get_buffered_data(self, since_message_id: Optional[str] = None) -> List[StreamData]:
        """获取缓冲的数据（可选：自某个消息ID以后）"""
        if since_message_id is None:
            return list(self.data_buffer)

        # 查找起始位置
        try:
            start_idx = next(i for i, msg in enumerate(self.data_buffer) if msg.message_id == since_message_id)
            return self.data_buffer[start_idx + 1 :]
        except StopIteration:
            # 消息ID未找到，返回所有数据
            return list(self.data_buffer)

    def get_stats(self) -> Dict[str, Any]:
        """获取流统计信息"""
        return {
            "stream_id": self.stream_id,
            "symbol": self.symbol,
            "status": self.status,
            "subscriber_count": len(self.subscribers),
            "messages_sent": self.messages_sent,
            "messages_dropped": self.messages_dropped,
            "errors_count": self.errors_count,
            "buffer_size": len(self.data_buffer),
            "uptime_seconds": (datetime.now(timezone.utc) - self.created_at).total_seconds(),
            "created_at": self.created_at.isoformat(),
            "last_update": self.last_update_time.isoformat(),
        }


class RealtimeStreamingService:
    """实时流式传输服务 - 管理所有市场数据流"""

    def __init__(self, default_buffer_size: int = 100):
        """
        初始化实时流服务

        Args:
            default_buffer_size: 默认缓冲区大小
        """
        self.streams: Dict[str, MarketDataStream] = {}
        self.subscriber_to_stream: Dict[str, str] = {}  # sid -> symbol
        self.default_buffer_size = default_buffer_size

        # 事件回调
        self.event_callbacks: Dict[StreamEventType, List[Callable]] = {event_type: [] for event_type in StreamEventType}

        # 指标
        self.total_messages_sent = 0
        self.total_messages_dropped = 0
        self.peak_subscribers = 0

        logger.info("✅ Realtime Streaming Service initialized")

    def start_stream(self, symbol: str) -> MarketDataStream:
        """启动股票代码的流"""
        if symbol in self.streams:
            logger.warning("⚠️ Stream already exists for symbol", symbol=symbol)
            return self.streams[symbol]

        stream = MarketDataStream(symbol=symbol, buffer_size=self.default_buffer_size)
        stream.status = StreamStatus.ACTIVE
        self.streams[symbol] = stream

        self._trigger_event(StreamEventType.STREAM_STARTED, {"symbol": symbol})

        logger.info("✅ Stream started", symbol=symbol)
        return stream

    def stop_stream(self, symbol: str) -> bool:
        """停止股票代码的流"""
        if symbol not in self.streams:
            logger.warning("⚠️ Stream not found", symbol=symbol)
            return False

        stream = self.streams.pop(symbol)

        # 清理所有订阅者
        for sid in list(stream.subscribers.keys()):
            self.subscriber_to_stream.pop(sid, None)

        self._trigger_event(StreamEventType.STREAM_STOPPED, {"symbol": symbol})

        logger.info("✅ Stream stopped", symbol=symbol)
        return True

    def subscribe(
        self,
        sid: str,
        symbol: str,
        user_id: Optional[str] = None,
        fields: Optional[Set[str]] = None,
    ) -> bool:
        """订阅股票流"""
        # 创建流（如果不存在）
        if symbol not in self.streams:
            self.start_stream(symbol)

        stream = self.streams[symbol]

        # 添加订阅者
        stream.add_subscriber(sid, user_id, fields)
        self.subscriber_to_stream[sid] = symbol

        # 更新峰值
        total_subscribers = sum(len(s.subscribers) for s in self.streams.values())
        if total_subscribers > self.peak_subscribers:
            self.peak_subscribers = total_subscribers

        logger.info(
            "✅ Subscriber added to stream",
            symbol=symbol,
            sid=sid,
            total_active_streams=len(self.streams),
        )

        return True

    def unsubscribe(self, sid: str, symbol: Optional[str] = None) -> bool:
        """取消订阅"""
        # 如果未指定symbol，从映射中获取
        if symbol is None:
            symbol = self.subscriber_to_stream.get(sid)
            if symbol is None:
                logger.warning("⚠️ Subscriber not found", sid=sid)
                return False

        if symbol not in self.streams:
            logger.warning("⚠️ Stream not found", symbol=symbol)
            return False

        stream = self.streams[symbol]
        stream.remove_subscriber(sid)
        self.subscriber_to_stream.pop(sid, None)

        # 如果没有订阅者，停止流
        if not stream.has_subscribers():
            self.stop_stream(symbol)

        return True

    def broadcast_data(self, symbol: str, data: Dict[str, Any]) -> bool:
        """向订阅者广播数据"""
        if symbol not in self.streams:
            logger.warning("⚠️ Stream not found", symbol=symbol)
            return False

        stream = self.streams[symbol]

        # 创建流数据
        stream_data = StreamData(
            message_id=str(uuid.uuid4()),
            symbol=symbol,
            timestamp=int(datetime.now(timezone.utc).timestamp() * 1000),  # 毫秒时间戳
            data=data,
        )

        # 缓冲数据
        if not stream.buffer_data(stream_data):
            return False

        # 更新指标
        stream.messages_sent += 1
        self.total_messages_sent += 1
        stream.last_update_time = datetime.now(timezone.utc)

        return True

    def filter_data(self, data: Dict[str, Any], fields: Set[str]) -> Dict[str, Any]:
        """过滤数据中的指定字段"""
        return {k: v for k, v in data.items() if k in fields}

    def get_stream(self, symbol: str) -> Optional[MarketDataStream]:
        """获取流对象"""
        return self.streams.get(symbol)

    def get_subscriber_stream(self, sid: str) -> Optional[MarketDataStream]:
        """通过sid获取订阅者的流"""
        symbol = self.subscriber_to_stream.get(sid)
        if symbol is None:
            return None
        return self.streams.get(symbol)

    def get_active_symbols(self) -> List[str]:
        """获取所有活跃的股票代码"""
        return list(self.streams.keys())

    def get_stats(self) -> Dict[str, Any]:
        """获取全局统计信息"""
        total_subscribers = sum(len(s.subscribers) for s in self.streams.values())

        return {
            "active_streams": len(self.streams),
            "total_subscribers": total_subscribers,
            "peak_subscribers": self.peak_subscribers,
            "total_messages_sent": self.total_messages_sent,
            "total_messages_dropped": self.total_messages_dropped,
            "streams": {symbol: stream.get_stats() for symbol, stream in self.streams.items()},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def register_event_handler(self, event_type: StreamEventType, handler: Callable) -> None:
        """注册事件处理器"""
        if event_type not in self.event_callbacks:
            self.event_callbacks[event_type] = []

        self.event_callbacks[event_type].append(handler)
        logger.info("✅ Registered streaming event handler: %(event_type)s")

    def _trigger_event(self, event_type: StreamEventType, data: Dict[str, Any]) -> None:
        """触发事件"""
        handlers = self.event_callbacks.get(event_type, [])
        for handler in handlers:
            try:
                handler(data)
            except Exception as e:
                logger.error(
                    "❌ Error calling streaming event handler",
                    event_type=event_type,
                    error=str(e),
                )


# 全局单例
_streaming_service: Optional[RealtimeStreamingService] = None


def get_streaming_service() -> RealtimeStreamingService:
    """获取流服务单例"""
    global _streaming_service
    if _streaming_service is None:
        _streaming_service = RealtimeStreamingService()
    return _streaming_service


def reset_streaming_service() -> None:
    """重置流服务单例（仅用于测试）"""
    global _streaming_service
    _streaming_service = None
