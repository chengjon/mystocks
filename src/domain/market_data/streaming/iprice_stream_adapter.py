"""
Price Stream Adapter Interface
实时行情流适配器接口

定义实时行情数据流的抽象接口，支持多种行情数据源。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class StreamStatus(str, Enum):
    """流状态"""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    SUBSCRIBING = "subscribing"
    SUBSCRIBED = "subscribed"
    ERROR = "error"
    RECONNECTING = "reconnecting"


@dataclass(frozen=True)
class PriceUpdate:
    """
    价格更新数据

    Attributes:
        symbol: 股票代码
        price: 最新价格
        volume: 成交量（可选）
        timestamp: 时间戳
        bid_price: 买一价（可选）
        ask_price: 卖一价（可选）
        extra: 额外数据（可选）
    """

    symbol: str
    price: float
    timestamp: datetime
    volume: Optional[int] = None
    bid_price: Optional[float] = None
    ask_price: Optional[float] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """验证价格更新数据"""
        if self.price <= 0:
            raise ValueError(f"Price must be positive: {self.price}")

        if self.bid_price is not None and self.bid_price <= 0:
            raise ValueError(f"Bid price must be positive: {self.bid_price}")

        if self.ask_price is not None and self.ask_price <= 0:
            raise ValueError(f"Ask price must be positive: {self.ask_price}")

        if self.volume is not None and self.volume < 0:
            raise ValueError(f"Volume cannot be negative: {self.volume}")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "symbol": self.symbol,
            "price": self.price,
            "timestamp": self.timestamp.isoformat(),
            "volume": self.volume,
            "bid_price": self.bid_price,
            "ask_price": self.ask_price,
            "extra": self.extra,
        }


class IPriceStreamAdapter(ABC):
    """
    实时行情流适配器接口

    职责：
    - 定义实时行情数据流的抽象接口
    - 支持订阅多个股票代码
    - 处理连接状态管理
    - 提供自动重连机制
    - 支持心跳检测

    使用场景：
    - WebSocket 行情流
    - HTTP Server-Sent Events (SSE)
    - 消息队列（Kafka/RabbitMQ）
    - 其他实时数据源
    """

    @abstractmethod
    async def connect(self) -> None:
        """
        连接到行情数据源

        Raises:
            ConnectionError: 连接失败
        """

    @abstractmethod
    async def disconnect(self) -> None:
        """
        断开连接
        """

    @abstractmethod
    async def subscribe(self, tickers: List[str]) -> None:
        """
        订阅股票代码

        Args:
            tickers: 股票代码列表

        Raises:
            ValueError: 股票代码格式错误
            ConnectionError: 未连接
        """

    @abstractmethod
    async def unsubscribe(self, tickers: List[str]) -> None:
        """
        取消订阅股票代码

        Args:
            tickers: 股票代码列表
        """

    @abstractmethod
    def on_message(self, callback: Callable[[PriceUpdate], None]) -> None:
        """
        注册消息回调函数

        Args:
            callback: 回调函数，接收 PriceUpdate 对象
        """

    @abstractmethod
    def get_status(self) -> StreamStatus:
        """
        获取当前连接状态

        Returns:
            StreamStatus: 流状态
        """

    @abstractmethod
    def get_subscribed_tickers(self) -> List[str]:
        """
        获取已订阅的股票代码列表

        Returns:
            List[str]: 股票代码列表
        """

    async def start(self) -> None:
        """
        启动流（连接 + 开始接收消息）

        默认实现：先连接，然后等待消息
        """
        await self.connect()

    async def stop(self) -> None:
        """
        停止流（断开连接）

        默认实现：断开连接
        """
        await self.disconnect()

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.stop()
