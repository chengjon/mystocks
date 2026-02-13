"""
Unified Stream Manager - 统一流管理器

提供实时数据流的统一管理，包括：
- WebSocket连接管理
- 数据源适配器路由
- 事件总线广播
- 订阅生命周期管理

作者: Claude Code (Sisyphus)
日期: 2026-01-14
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

from src.core.unified_manager import MyStocksUnifiedManager

logger = logging.getLogger(__name__)


class StreamStatus(str, Enum):
    """流状态枚举"""

    INACTIVE = "inactive"  # 未激活
    CONNECTING = "connecting"  # 连接中
    ACTIVE = "active"  # 活跃
    ERROR = "error"  # 错误
    CLOSED = "closed"  # 已关闭


@dataclass
class StreamSubscription:
    """流订阅信息"""

    symbol: str
    subscribers: Set[str] = field(default_factory=set)
    status: StreamStatus = StreamStatus.INACTIVE
    adapter_name: Optional[str] = None
    last_update: Optional[datetime] = None
    error_count: int = 0


class StreamManager:
    """
    Unified Stream Manager - 统一流管理器

    核心功能：
    1. 实时数据流订阅管理
    2. 数据源适配器自动路由
    3. WebSocket连接生命周期管理
    4. 事件总线集成

    设计理念：
    - 事件驱动架构：从"拉取"转向"推送"
    - 统一抽象：隐藏底层数据源差异
    - 高可用性：自动故障转移和重连
    """

    def __init__(self, unified_manager: Optional[MyStocksUnifiedManager] = None):
        """
        初始化流管理器

        Args:
            unified_manager: 统一数据管理器实例
        """
        self.unified_manager = unified_manager or MyStocksUnifiedManager()

        self.subscriptions: Dict[str, StreamSubscription] = {}
        self.active_streams: Dict[str, Any] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.websocket_adapters: Dict[str, Any] = {}
        self.reconnect_tasks: Dict[str, asyncio.Task] = {}

        self.max_reconnect_attempts = 5
        self.reconnect_delay = 2.0
        self.heartbeat_interval = 30.0

        logger.info("✅ Unified Stream Manager initialized")

    async def subscribe(self, symbols: List[str], subscriber_id: str = "default") -> Dict[str, bool]:
        """
        订阅股票实时数据流

        Args:
            symbols: 股票代码列表
            subscriber_id: 订阅者ID

        Returns:
            订阅结果字典 {symbol: success}
        """
        results = {}

        for symbol in symbols:
            try:
                if symbol in self.subscriptions:
                    subscription = self.subscriptions[symbol]
                    subscription.subscribers.add(subscriber_id)
                    results[symbol] = True
                    logger.debug("Added subscriber %(subscriber_id)s to existing stream %(symbol)s")
                    continue

                subscription = StreamSubscription(symbol=symbol)
                subscription.subscribers.add(subscriber_id)

                adapter_name = await self._resolve_adapter(symbol)
                if not adapter_name:
                    logger.warning("No adapter found for symbol %(symbol)s")
                    subscription.status = StreamStatus.ERROR
                    results[symbol] = False
                    continue

                subscription.adapter_name = adapter_name
                self.subscriptions[symbol] = subscription

                success = await self._start_stream(symbol)
                results[symbol] = success

                if success:
                    logger.info("Successfully subscribed to %(symbol)s via %(adapter_name)s")
                else:
                    logger.error("Failed to start stream for %(symbol)s")

            except Exception:
                logger.error("Error subscribing to %(symbol)s: %(e)s")
                results[symbol] = False

        return results

    async def unsubscribe(self, symbols: List[str], subscriber_id: str = "default") -> Dict[str, bool]:
        """
        取消订阅

        Args:
            symbols: 股票代码列表
            subscriber_id: 订阅者ID

        Returns:
            取消订阅结果字典 {symbol: success}
        """
        results = {}

        for symbol in symbols:
            try:
                if symbol not in self.subscriptions:
                    results[symbol] = True
                    continue

                subscription = self.subscriptions[symbol]
                subscription.subscribers.discard(subscriber_id)

                if not subscription.subscribers:
                    await self._stop_stream(symbol)
                    del self.subscriptions[symbol]
                    logger.info("Stopped stream for %(symbol)s - no more subscribers")

                results[symbol] = True

            except Exception:
                logger.error("Error unsubscribing from %(symbol)s: %(e)s")
                results[symbol] = False

        return results

    async def get_stream_status(self, symbol: str) -> Optional[StreamSubscription]:
        """
        获取流状态

        Args:
            symbol: 股票代码

        Returns:
            流订阅信息，如果不存在返回None
        """
        return self.subscriptions.get(symbol)

    async def get_active_streams(self) -> List[str]:
        """
        获取所有活跃的流

        Returns:
            活跃流符号列表
        """
        return [symbol for symbol, sub in self.subscriptions.items() if sub.status == StreamStatus.ACTIVE]

    def add_event_handler(self, event_type: str, handler: Callable) -> None:
        """
        添加事件处理器

        Args:
            event_type: 事件类型 (e.g., "market.tick", "market.bar")
            handler: 事件处理函数
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        logger.debug("Added event handler for %(event_type)s")

    async def _resolve_adapter(self, symbol: str) -> Optional[str]:
        """
        解析股票代码对应的适配器

        Args:
            symbol: 股票代码

        Returns:
            适配器名称，如果找不到返回None
        """
        try:
            if symbol.startswith(("6", "000", "001", "002", "300")):
                return "sina_finance"
            elif symbol.startswith(("HK", "hk")):
                return "hkex"
            elif symbol.startswith(("US", "us")):
                return "yahoo_finance"
            else:
                return "sina_finance"

        except Exception:
            logger.error("Error resolving adapter for %(symbol)s: %(e)s")
            return None

    async def _start_stream(self, symbol: str) -> bool:
        """
        启动数据流

        Args:
            symbol: 股票代码

        Returns:
            是否成功启动
        """
        try:
            subscription = self.subscriptions[symbol]
            adapter_name = subscription.adapter_name

            adapter = await self._get_websocket_adapter(adapter_name)
            if not adapter:
                logger.error("No WebSocket adapter available for %(adapter_name)s")
                return False

            success = await adapter.connect()
            if not success:
                logger.error("Failed to connect WebSocket for %(adapter_name)s")
                return False

            success = await adapter.subscribe([symbol])
            if not success:
                logger.error("Failed to subscribe %(symbol)s via %(adapter_name)s")
                return False

            await adapter.on_message(self._handle_stream_message)

            subscription.status = StreamStatus.ACTIVE
            subscription.last_update = datetime.now()

            asyncio.create_task(self._heartbeat_monitor(symbol))

            logger.info("Stream started for %(symbol)s via %(adapter_name)s")
            return True

        except Exception:
            logger.error("Error starting stream for %(symbol)s: %(e)s")
            subscription.status = StreamStatus.ERROR
            return False

    async def _stop_stream(self, symbol: str) -> None:
        """
        停止数据流

        Args:
            symbol: 股票代码
        """
        try:
            if symbol in self.active_streams:
                adapter = self.active_streams[symbol]
                await adapter.disconnect()
                del self.active_streams[symbol]

            if symbol in self.reconnect_tasks:
                self.reconnect_tasks[symbol].cancel()
                del self.reconnect_tasks[symbol]

            logger.info("Stream stopped for %(symbol)s")

        except Exception:
            logger.error("Error stopping stream for %(symbol)s: %(e)s")

    async def _get_websocket_adapter(self, adapter_name: str) -> Optional[Any]:
        """
        获取WebSocket适配器实例

        Args:
            adapter_name: 适配器名称

        Returns:
            WebSocket适配器实例
        """
        logger.warning("WebSocket adapter %(adapter_name)s not implemented yet")
        return None

    async def _handle_stream_message(self, message: Dict[str, Any]) -> None:
        """
        处理流消息

        Args:
            message: 消息数据
        """
        try:
            msg_type = message.get("type", "unknown")
            symbol = message.get("symbol", "")
            data = message.get("data", {})

            event_type = f"market.{msg_type}"
            await self._trigger_event(
                event_type,
                {"symbol": symbol, "data": data, "timestamp": datetime.now()},
            )

            if symbol in self.subscriptions:
                self.subscriptions[symbol].last_update = datetime.now()

        except Exception:
            logger.error("Error handling stream message: %(e)s")

    async def _trigger_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        触发事件

        Args:
            event_type: 事件类型
            data: 事件数据
        """
        try:
            if event_type in self.event_handlers:
                handlers = self.event_handlers[event_type]
                tasks = [handler(data) for handler in handlers]
                await asyncio.gather(*tasks, return_exceptions=True)

        except Exception:
            logger.error("Error triggering event %(event_type)s: %(e)s")

    async def _heartbeat_monitor(self, symbol: str) -> None:
        """
        心跳监控

        Args:
            symbol: 股票代码
        """
        while symbol in self.subscriptions:
            try:
                await asyncio.sleep(self.heartbeat_interval)

                subscription = self.subscriptions[symbol]
                if subscription.status != StreamStatus.ACTIVE:
                    continue

                if subscription.last_update:
                    time_since_update = (datetime.now() - subscription.last_update).total_seconds()
                    if time_since_update > self.heartbeat_interval * 2:
                        logger.warning("No data received for %(symbol)s in {time_since_update:.1f}s")

            except asyncio.CancelledError:
                break
            except Exception:
                logger.error("Error in heartbeat monitor for %(symbol)s: %(e)s")

    async def shutdown(self) -> None:
        """关闭管理器"""
        logger.info("Shutting down Stream Manager...")

        symbols = list(self.subscriptions.keys())
        await asyncio.gather(*[self._stop_stream(symbol) for symbol in symbols])

        for task in self.reconnect_tasks.values():
            task.cancel()

        logger.info("✅ Stream Manager shutdown complete")
