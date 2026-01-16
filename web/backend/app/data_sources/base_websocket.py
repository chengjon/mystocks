"""
WebSocket Adapter Interface - WebSocket适配器接口

定义WebSocket数据源的标准接口，包括：
- 连接管理
- 订阅/取消订阅
- 消息处理
- 自动重连

作者: Claude Code (Sisyphus)
日期: 2026-01-14
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable, Protocol
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


class WebSocketCapability(Protocol):
    """
    WebSocket能力协议

    定义WebSocket适配器必须实现的方法
    """

    async def connect(self) -> bool:
        """建立WebSocket连接"""
        ...

    async def disconnect(self) -> None:
        """断开WebSocket连接"""
        ...

    async def subscribe(self, symbols: List[str]) -> bool:
        """订阅股票数据"""
        ...

    async def unsubscribe(self, symbols: List[str]) -> bool:
        """取消订阅股票数据"""
        ...

    async def on_message(self, handler: Callable[[Dict[str, Any]], None]) -> None:
        """设置消息处理器"""
        ...

    def is_connected(self) -> bool:
        """检查连接状态"""
        ...


@dataclass
class WebSocketConfig:
    """WebSocket配置"""

    url: str
    heartbeat_interval: float = 30.0
    reconnect_attempts: int = 5
    reconnect_delay: float = 2.0
    connection_timeout: float = 10.0
    ping_timeout: float = 5.0

    # 认证相关
    api_key: Optional[str] = None
    api_secret: Optional[str] = None

    # 代理设置
    proxy_url: Optional[str] = None

    # 自定义头信息
    headers: Optional[Dict[str, str]] = None


class BaseWebSocketAdapter(ABC):
    """
    WebSocket适配器基类

    提供WebSocket连接的基本功能和生命周期管理
    """

    def __init__(self, config: WebSocketConfig):
        """
        初始化WebSocket适配器

        Args:
            config: WebSocket配置
        """
        self.config = config
        self.websocket = None
        self.is_running = False
        self.message_handlers: List[Callable[[Dict[str, Any]], None]] = []
        self.subscribed_symbols: set = set()

        # 连接状态
        self.last_heartbeat = datetime.now()
        self.connection_attempts = 0
        self.reconnect_task: Optional[asyncio.Task] = None

        logger.info(f"✅ {self.__class__.__name__} initialized with {config.url}")

    @abstractmethod
    async def connect(self) -> bool:
        """
        建立WebSocket连接

        Returns:
            是否连接成功
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """断开WebSocket连接"""
        pass

    @abstractmethod
    async def _send_subscription_message(self, symbols: List[str], action: str) -> bool:
        """
        发送订阅/取消订阅消息

        Args:
            symbols: 股票代码列表
            action: 动作 ('subscribe' 或 'unsubscribe')

        Returns:
            是否发送成功
        """
        pass

    async def subscribe(self, symbols: List[str]) -> bool:
        """
        订阅股票数据

        Args:
            symbols: 股票代码列表

        Returns:
            是否订阅成功
        """
        try:
            if not self.is_connected():
                logger.warning("WebSocket not connected, attempting to connect...")
                if not await self.connect():
                    return False

            # 发送订阅消息
            success = await self._send_subscription_message(symbols, "subscribe")
            if success:
                self.subscribed_symbols.update(symbols)
                logger.info(f"Subscribed to symbols: {symbols}")
                return True
            else:
                logger.error(f"Failed to subscribe to symbols: {symbols}")
                return False

        except Exception as e:
            logger.error(f"Error subscribing to symbols {symbols}: {e}")
            return False

    async def unsubscribe(self, symbols: List[str]) -> bool:
        """
        取消订阅股票数据

        Args:
            symbols: 股票代码列表

        Returns:
            是否取消订阅成功
        """
        try:
            if not self.is_connected():
                logger.warning("WebSocket not connected")
                return False

            # 发送取消订阅消息
            success = await self._send_subscription_message(symbols, "unsubscribe")
            if success:
                self.subscribed_symbols.difference_update(symbols)
                logger.info(f"Unsubscribed from symbols: {symbols}")
                return True
            else:
                logger.error(f"Failed to unsubscribe from symbols: {symbols}")
                return False

        except Exception as e:
            logger.error(f"Error unsubscribing from symbols {symbols}: {e}")
            return False

    def on_message(self, handler: Callable[[Dict[str, Any]], None]) -> None:
        """
        添加消息处理器

        Args:
            handler: 消息处理函数
        """
        self.message_handlers.append(handler)
        logger.debug(f"Added message handler: {handler.__name__}")

    async def _handle_message(self, message: Dict[str, Any]) -> None:
        """
        处理接收到的消息

        Args:
            message: 消息数据
        """
        try:
            # 更新心跳时间
            self.last_heartbeat = datetime.now()

            # 调用所有消息处理器
            for handler in self.message_handlers:
                try:
                    await handler(message)
                except Exception as e:
                    logger.error(f"Error in message handler {handler.__name__}: {e}")

        except Exception as e:
            logger.error(f"Error handling message: {e}")

    def is_connected(self) -> bool:
        """
        检查连接状态

        Returns:
            是否已连接
        """
        return self.websocket is not None and self.is_running

    async def _start_heartbeat(self) -> None:
        """启动心跳监控"""
        while self.is_running:
            try:
                await asyncio.sleep(self.config.heartbeat_interval)

                if not self.is_connected():
                    continue

                # 检查最后心跳时间
                time_since_heartbeat = (
                    datetime.now() - self.last_heartbeat
                ).total_seconds()
                if time_since_heartbeat > self.config.heartbeat_interval * 2:
                    logger.warning(
                        f"No heartbeat received for {time_since_heartbeat:.1f}s, attempting reconnect"
                    )
                    await self._reconnect()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat monitor: {e}")

    async def _reconnect(self) -> None:
        """重连逻辑"""
        if self.reconnect_task and not self.reconnect_task.done():
            return  # 重连已在进行中

        self.reconnect_task = asyncio.create_task(self._perform_reconnect())

    async def _perform_reconnect(self) -> None:
        """执行重连"""
        for attempt in range(self.config.reconnect_attempts):
            try:
                logger.info(
                    f"Reconnection attempt {attempt + 1}/{self.config.reconnect_attempts}"
                )

                # 断开现有连接
                if self.is_connected():
                    await self.disconnect()

                # 等待延迟
                await asyncio.sleep(self.config.reconnect_delay * (attempt + 1))

                # 重新连接
                if await self.connect():
                    logger.info("Reconnection successful")

                    # 重新订阅
                    if self.subscribed_symbols:
                        await self.subscribe(list(self.subscribed_symbols))

                    return

            except Exception as e:
                logger.error(f"Reconnection attempt {attempt + 1} failed: {e}")

        logger.error("All reconnection attempts failed")

    async def close(self) -> None:
        """关闭适配器"""
        logger.info(f"Closing {self.__class__.__name__}...")

        self.is_running = False

        # 取消重连任务
        if self.reconnect_task and not self.reconnect_task.done():
            self.reconnect_task.cancel()

        # 断开连接
        if self.is_connected():
            await self.disconnect()

        logger.info(f"✅ {self.__class__.__name__} closed")


class SinaFinanceWebSocketAdapter(BaseWebSocketAdapter):
    """
    新浪财经WebSocket适配器

    连接新浪财经的实时数据WebSocket服务
    """

    def __init__(self):
        config = WebSocketConfig(
            url="wss://websocket.sina.com.cn/market",
            heartbeat_interval=30.0,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Origin": "https://finance.sina.com.cn",
            },
        )
        super().__init__(config)

    async def connect(self) -> bool:
        """连接新浪财经WebSocket"""
        try:
            # 这里实现实际的WebSocket连接逻辑
            # 使用websockets库或其他WebSocket客户端
            logger.info("Connecting to Sina Finance WebSocket...")

            # 模拟连接过程
            await asyncio.sleep(0.1)  # 模拟连接延迟

            self.websocket = "mock_connection"  # 模拟连接对象
            self.is_running = True

            # 启动心跳监控
            asyncio.create_task(self._start_heartbeat())

            logger.info("✅ Connected to Sina Finance WebSocket")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Sina Finance WebSocket: {e}")
            return False

    async def disconnect(self) -> None:
        """断开新浪财经WebSocket连接"""
        try:
            if self.websocket:
                # 关闭WebSocket连接
                logger.info("Disconnecting from Sina Finance WebSocket...")
                self.websocket = None
                self.is_running = False
                logger.info("✅ Disconnected from Sina Finance WebSocket")

        except Exception as e:
            logger.error(f"Error disconnecting from Sina Finance WebSocket: {e}")

    async def _send_subscription_message(self, symbols: List[str], action: str) -> bool:
        """发送订阅消息"""
        try:
            if not self.is_connected():
                return False

            # 构造订阅消息
            message = {
                "type": action,
                "symbols": symbols,
                "timestamp": datetime.now().isoformat(),
            }

            # 发送消息（模拟）
            logger.debug(f"Sending {action} message for symbols: {symbols}")

            # 这里应该实际发送WebSocket消息
            # await self.websocket.send(json.dumps(message))

            return True

        except Exception as e:
            logger.error(f"Error sending {action} message: {e}")
            return False
