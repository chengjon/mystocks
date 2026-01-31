"""
Price Stream Processor
实时行情流处理器

负责：
1. 接收 PriceUpdate 数据
2. 转换为 PriceChangedEvent 领域事件
3. 发布到 Redis 事件总线
4. 触发投资组合重新计算
"""

import asyncio
import logging
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Set

from redis import Redis

from src.domain.market_data.streaming import IPriceStreamAdapter, PriceChangedEvent, PriceUpdate
from src.domain.portfolio.service import PortfolioValuationService
from src.domain.shared.event_bus import IEventBus
from src.infrastructure.cache.redis_lock import RedisDistributedLock

logger = logging.getLogger(__name__)


class PriceStreamProcessor:
    """
    实时行情流处理器

    职责：
    - 接收实时行情数据
    - 发布价格变更事件到事件总线
    - 触发投资组合重新计算
    - 提供批处理和节流优化
    - 集成分布式锁保证并发安全

    Args:
        event_bus: 事件总线（RedisEventBus）
        redis_client: Redis 客户端（用于分布式锁）
        batch_size: 批处理大小
        batch_timeout: 批处理超时（秒）
        enable_throttling: 是否启用节流
    """

    def __init__(
        self,
        event_bus: IEventBus,
        valuation_service: PortfolioValuationService,
        redis_client: Optional[Redis] = None,
        batch_size: int = 100,
        batch_timeout: float = 0.1,
        enable_throttling: bool = True,
    ):
        self.event_bus = event_bus
        self.valuation_service = valuation_service
        self.redis_client = redis_client
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.enable_throttling = enable_throttling

        self._stream_adapters: List[IPriceStreamAdapter] = []
        self._price_cache: Dict[str, float] = {}
        self._update_queue: List[PriceUpdate] = []
        self._last_flush: datetime = datetime.now()

        self._portfolio_symbols: Dict[str, Set[str]] = {}  # portfolio_id -> set of symbols
        self._lock_manager: Optional[RedisDistributedLock] = None

        self._running = False
        self._processing_task: Optional[asyncio.Task] = None

        if redis_client:
            self._lock_manager = RedisDistributedLock(redis_client)

        self.metrics = {
            "total_updates": 0,
            "events_published": 0,
            "batches_processed": 0,
            "portfolio_revaluations": 0,
            "last_update_time": None,
        }

        logger.info(
            f"✅ Price Stream Processor initialized (batch_size={batch_size}, batch_timeout={batch_timeout}, throttling={enable_throttling})"
        )

    async def start(self) -> None:
        """启动处理器"""
        if self._running:
            logger.warning("Price Stream Processor already running")
            return

        logger.info("🚀 Starting Price Stream Processor...")
        self._running = True

        # 为所有适配器注册回调
        for adapter in self._stream_adapters:
            adapter.on_message(self._on_price_update)

        # 启动批处理任务
        self._processing_task = asyncio.create_task(self._batch_processing_loop())

        logger.info("✅ Price Stream Processor started")

    async def stop(self) -> None:
        """停止处理器"""
        if not self._running:
            return

        logger.info("🛑 Stopping Price Stream Processor...")
        self._running = False

        # 刷新剩余更新
        if self._update_queue:
            await self._flush_updates()

        # 停止处理任务
        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass

        # 停止所有适配器
        for adapter in self._stream_adapters:
            await adapter.stop()

        logger.info("✅ Price Stream Processor stopped")

    def add_stream_adapter(self, adapter: IPriceStreamAdapter) -> None:
        """添加行情流适配器"""
        self._stream_adapters.append(adapter)
        logger.info("✅ Added stream adapter: {adapter.__class__.__name__")

    def register_portfolio_symbols(self, portfolio_id: str, symbols: Set[str]) -> None:
        """
        注册投资组合的股票代码

        Args:
            portfolio_id: 投资组合ID
            symbols: 股票代码集合
        """
        self._portfolio_symbols[portfolio_id] = symbols
        logger.info("✅ Registered portfolio %(portfolio_id)s with {len(symbols)} symbols")

    def unregister_portfolio_symbols(self, portfolio_id: str) -> None:
        """
        注销投资组合

        Args:
            portfolio_id: 投资组合ID
        """
        if portfolio_id in self._portfolio_symbols:
            symbols = self._portfolio_symbols.pop(portfolio_id)
            logger.info("✅ Unregistered portfolio %(portfolio_id)s with {len(symbols)} symbols")

    def _on_price_update(self, update: PriceUpdate) -> None:
        """
        处理价格更新（同步回调）

        Args:
            update: 价格更新对象
        """
        self.metrics["total_updates"] += 1
        self.metrics["last_update_time"] = datetime.now()

        # 添加到批处理队列
        self._update_queue.append(update)

        # 如果不启用批处理，立即刷新
        if not self.enable_throttling:
            asyncio.create_task(self._flush_updates())

    async def _batch_processing_loop(self) -> None:
        """批处理循环"""
        logger.info("🔄 Starting batch processing loop...")

        while self._running:
            try:
                await asyncio.sleep(self.batch_timeout)

                # 检查是否需要刷新
                if self._update_queue:
                    should_flush = len(self._update_queue) >= self.batch_size
                    time_since_flush = (datetime.now() - self._last_flush).total_seconds()
                    should_flush = should_flush or time_since_flush >= self.batch_timeout

                    if should_flush:
                        await self._flush_updates()

            except asyncio.CancelledError:
                logger.info("🛑 Batch processing loop cancelled")
                break
            except Exception as e:
                logger.error("Error in batch processing loop: %s", e)

        logger.info("⏹️ Batch processing loop stopped")

    async def _flush_updates(self) -> None:
        """刷新更新队列"""
        if not self._update_queue:
            return

        # 获取所有更新
        updates = list(self._update_queue)
        self._update_queue.clear()
        self._last_flush = datetime.now()

        logger.debug("🔄 Flushing %s price updates...", len(updates))

        # 按投资组合分组
        portfolio_updates: Dict[str, Dict[str, float]] = defaultdict(dict)
        all_prices: Dict[str, float] = {}

        for update in updates:
            # 记录所有价格
            all_prices[update.symbol] = update.price

            # 按投资组合分组
            for portfolio_id, symbols in self._portfolio_symbols.items():
                if update.symbol in symbols:
                    portfolio_updates[portfolio_id][update.symbol] = update.price

        # 发布价格变更事件
        if all_prices:
            events = PriceChangedEvent.create_batch(all_prices, self._price_cache)
            for event in events:
                try:
                    self.event_bus.publish(event)
                    self.metrics["events_published"] += 1
                except Exception as e:
                    logger.error("Failed to publish PriceChangedEvent: %(e)s")

            # 更新价格缓存
            self._price_cache.update(all_prices)

        # 触发投资组合重新计算
        if portfolio_updates:
            for portfolio_id, prices in portfolio_updates.items():
                try:
                    # 如果有分布式锁，先获取锁
                    identifier = None
                    if self._lock_manager:
                        lock_name = f"portfolio:revaluate:{portfolio_id}"
                        identifier = self._lock_manager.acquire(lock_name, expire_seconds=5, wait_timeout=1)

                    if identifier or not self._lock_manager:
                        try:
                            # 调用 PortfolioValuationService 重新计算
                            performance = self.valuation_service.revaluate_portfolio(
                                portfolio_id=portfolio_id, prices=prices, force_save=True
                            )

                            if performance:
                                logger.info(
                                    f"📊 Revaluated portfolio {portfolio_id}: {len(prices)} symbols, "
                                    f"holdings_value={performance.holdings_value:.2f}, return={performance.total_return:.2f}%"
                                )
                                self.metrics["portfolio_revaluations"] += 1
                            else:
                                logger.warning("⚠️ Failed to revaluate portfolio %(portfolio_id)s")

                        finally:
                            if identifier and self._lock_manager:
                                self._lock_manager.release(lock_name, identifier)
                    else:
                        logger.warning("⚠️ Could not acquire lock for portfolio %(portfolio_id)s")

                except Exception as e:
                    logger.error("Failed to revaluate portfolio %(portfolio_id)s: %(e)s")

        self.metrics["batches_processed"] += 1
        logger.debug("✅ Flushed {len(updates)} price updates")

    def get_metrics(self) -> dict:
        """获取处理器指标"""
        return {
            **self.metrics,
            "queue_size": len(self._update_queue),
            "cached_symbols": len(self._price_cache),
            "registered_portfolios": len(self._portfolio_symbols),
            "stream_adapters": len(self._stream_adapters),
        }
