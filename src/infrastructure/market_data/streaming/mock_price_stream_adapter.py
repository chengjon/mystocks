"""
Mock Price Stream Adapter
模拟实时行情流适配器

用于测试和演示，模拟真实的实时行情数据流。
"""

import asyncio
import logging
import random
from datetime import datetime
from typing import Callable, List, Optional

from src.domain.market_data.streaming import IPriceStreamAdapter, PriceUpdate, StreamStatus

logger = logging.getLogger(__name__)


class MockPriceStreamAdapter(IPriceStreamAdapter):
    """
    模拟实时行情流适配器

    职责：
    - 模拟真实的实时行情数据流
    - 支持订阅多个股票代码
    - 自动生成模拟价格数据
    - 支持自动重连和心跳检测

    使用场景：
    - 单元测试
    - 集成测试
    - 开发环境演示
    """

    def __init__(
        self,
        update_interval: float = 1.0,
        price_volatility: float = 0.02,
        reconnect_interval: float = 5.0,
        heartbeat_interval: float = 30.0,
    ):
        """
        初始化 Mock 行情流适配器

        Args:
            update_interval: 价格更新间隔（秒）
            price_volatility: 价格波动率（0.0-1.0）
            reconnect_interval: 重连间隔（秒）
            heartbeat_interval: 心跳间隔（秒）
        """
        self.update_interval = update_interval
        self.price_volatility = price_volatility
        self.reconnect_interval = reconnect_interval
        self.heartbeat_interval = heartbeat_interval

        self._status = StreamStatus.DISCONNECTED
        self._subscribed_tickers: List[str] = []
        self._message_callbacks: List[Callable[[PriceUpdate], None]] = []
        self._current_prices: dict[str, float] = {}

        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._heartbeat_task: Optional[asyncio.Task] = None

        logger.info(
            f"✅ Mock Price Stream Adapter initialized (update_interval={update_interval}, price_volatility={price_volatility})"
        )

    async def connect(self) -> None:
        """连接到行情数据源"""
        if self._status == StreamStatus.CONNECTED:
            logger.warning("Already connected")
            return

        logger.info("🔌 Connecting to mock price stream...")
        self._status = StreamStatus.CONNECTING

        # 模拟连接延迟
        await asyncio.sleep(0.5)

        self._status = StreamStatus.CONNECTED
        logger.info("✅ Connected to mock price stream")

    async def disconnect(self) -> None:
        """断开连接"""
        if self._status == StreamStatus.DISCONNECTED:
            return

        logger.info("🔌 Disconnecting from mock price stream...")
        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass

        self._status = StreamStatus.DISCONNECTED
        logger.info("✅ Disconnected from mock price stream")

    async def subscribe(self, tickers: List[str]) -> None:
        """订阅股票代码"""
        if self._status != StreamStatus.CONNECTED:
            raise ConnectionError("Not connected")

        if not tickers:
            raise ValueError("Tickers list cannot be empty")

        logger.info("📊 Subscribing to {len(tickers)} tickers: {tickers[:5]}...")
        self._status = StreamStatus.SUBSCRIBING

        # 模拟订阅延迟
        await asyncio.sleep(0.2)

        # 初始化价格（首次订阅）
        for ticker in tickers:
            if ticker not in self._subscribed_tickers:
                self._subscribed_tickers.append(ticker)
                # 设置初始价格（随机值在 10-100 之间）
                self._current_prices[ticker] = round(random.uniform(10, 100), 2)

        self._status = StreamStatus.SUBSCRIBED
        logger.info("✅ Subscribed to {len(tickers)} tickers")

        # 启动价格更新任务
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._update_loop())
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

    async def unsubscribe(self, tickers: List[str]) -> None:
        """取消订阅股票代码"""
        if not tickers:
            return

        logger.info("📊 Unsubscribing from {len(tickers)} tickers: {tickers[:5]}...")

        for ticker in tickers:
            if ticker in self._subscribed_tickers:
                self._subscribed_tickers.remove(ticker)
                self._current_prices.pop(ticker, None)

        logger.info("✅ Unsubscribed from {len(tickers)} tickers")

    def on_message(self, callback: Callable[[PriceUpdate], None]) -> None:
        """注册消息回调函数"""
        if callback not in self._message_callbacks:
            self._message_callbacks.append(callback)
            logger.debug("✅ Registered message callback: {callback.__name__")

    def get_status(self) -> StreamStatus:
        """获取当前连接状态"""
        return self._status

    def get_subscribed_tickers(self) -> List[str]:
        """获取已订阅的股票代码列表"""
        return self._subscribed_tickers.copy()

    async def _update_loop(self):
        """价格更新循环"""
        logger.info("🔄 Starting price update loop...")

        while self._running and self._subscribed_tickers:
            try:
                # 为每个订阅的股票生成价格更新
                for ticker in self._subscribed_tickers:
                    old_price = self._current_prices[ticker]

                    # 生成新价格（随机波动）
                    price_change_pct = random.uniform(-self.price_volatility, self.price_volatility)
                    new_price = old_price * (1 + price_change_pct)
                    new_price = max(0.01, round(new_price, 2))  # 确保价格为正

                    self._current_prices[ticker] = new_price

                    # 创建价格更新
                    update = PriceUpdate(
                        symbol=ticker,
                        price=new_price,
                        timestamp=datetime.now(),
                        volume=random.randint(100, 10000),
                        bid_price=round(new_price * 0.999, 2),
                        ask_price=round(new_price * 1.001, 2),
                    )

                    # 调用所有回调函数
                    for callback in self._message_callbacks:
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(update)
                            else:
                                callback(update)
                        except Exception as e:
                            logger.error("Error in message callback: %(e)s")

                # 等待下一次更新
                await asyncio.sleep(self.update_interval)

            except asyncio.CancelledError:
                logger.info("🛑 Price update loop cancelled")
                break
            except Exception as e:
                logger.error("Error in price update loop: %(e)s")
                await asyncio.sleep(self.update_interval)

        logger.info("⏹️ Price update loop stopped")

    async def _heartbeat_loop(self):
        """心跳检测循环"""
        logger.info("💓 Starting heartbeat loop...")

        while self._running:
            try:
                await asyncio.sleep(self.heartbeat_interval)

                if self._status == StreamStatus.SUBSCRIBED:
                    logger.debug(
                        f"💓 Heartbeat: {len(self._subscribed_tickers)} tickers subscribed, "
                        f"status: {self._status.value}"
                    )

            except asyncio.CancelledError:
                logger.info("🛑 Heartbeat loop cancelled")
                break
            except Exception as e:
                logger.error("Error in heartbeat loop: %(e)s")

        logger.info("⏹️ Heartbeat loop stopped")

    async def start(self) -> None:
        """启动流（连接 + 开始接收消息）"""
        await self.connect()
        logger.info("✅ Mock price stream started")

    async def stop(self) -> None:
        """停止流（断开连接）"""
        await self.disconnect()
        logger.info("✅ Mock price stream stopped")
