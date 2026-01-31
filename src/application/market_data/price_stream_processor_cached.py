"""
Price Stream Processor with Caching
带缓存的实时行情流处理器

在 Phase 12.3 的基础上集成 LRU 缓存性能优化。

Author: Claude Code
Date: 2026-01-09
Phase: 12.5 - Performance Optimization Integration
"""

import logging
from collections import defaultdict
from datetime import datetime
from typing import Dict

from src.application.market_data.price_stream_processor import PriceStreamProcessor
from src.domain.portfolio.service import PortfolioValuationService
from src.domain.shared.event_bus import IEventBus
from src.domain.market_data.streaming.price_changed_event import PriceChangedEvent
from src.services.performance_optimizer import LRUCache

logger = logging.getLogger(__name__)


class CachedPriceStreamProcessor(PriceStreamProcessor):
    """
    带缓存的实时行情流处理器

    在 PriceStreamProcessor 基础上增加：
    1. LRU 缓存：缓存投资组合快照，减少数据库查询
    2. 智能刷新：仅在数据变化时刷新缓存
    3. 缓存预热：在启动时预加载常用数据

    Args:
        event_bus: 事件总线
        valuation_service: 投资组合估值服务
        redis_client: Redis 客户端（可选）
        batch_size: 批处理大小
        batch_timeout: 批处理超时（秒）
        enable_cache: 是否启用缓存（默认启用）
        cache_max_size: 缓存最大条目数（默认1000）
        cache_ttl: 缓存过期时间（秒，默认300）
    """

    def __init__(
        self,
        event_bus: IEventBus,
        valuation_service: PortfolioValuationService,
        redis_client=None,
        batch_size: int = 100,
        batch_timeout: float = 0.1,
        enable_throttling: bool = True,
        enable_cache: bool = True,
        cache_max_size: int = 1000,
        cache_ttl: float = 300.0,
    ):
        # 调用父类初始化
        super().__init__(
            event_bus=event_bus,
            valuation_service=valuation_service,
            redis_client=redis_client,
            batch_size=batch_size,
            batch_timeout=batch_timeout,
            enable_throttling=enable_throttling,
        )

        # 初始化缓存
        self.enable_cache = enable_cache
        if enable_cache:
            self.portfolio_cache = LRUCache(max_size=cache_max_size, ttl=cache_ttl)
            logger.info("✅ Cache enabled: max_size=%(cache_max_size)s, ttl=%(cache_ttl)ss")
        else:
            self.portfolio_cache = None
            logger.info("⚠️ Cache disabled")

        # 扩展指标
        self.metrics.update(
            {
                "cache_hits": 0,
                "cache_misses": 0,
                "cache_stores": 0,
                "cache_evictions": 0,
            }
        )

    async def start(self) -> None:
        """启动处理器"""
        await super().start()

        # 预热缓存
        if self.enable_cache:
            await self._warmup_cache()

    async def _warmup_cache(self):
        """预热缓存：预加载所有投资组合快照"""
        logger.info("🔥 Warming up cache...")

        try:
            # 获取所有投资组合
            portfolios = self.valuation_service.portfolio_repo.find_all(limit=1000)

            for portfolio in portfolios:
                # 计算绩效
                performance = portfolio.calculate_performance()

                # 存入缓存
                cache_key = f"portfolio:{portfolio.id}"
                self.portfolio_cache.set(
                    cache_key, {"portfolio": portfolio, "performance": performance, "cached_at": datetime.now()}
                )

                self.metrics["cache_stores"] += 1

            logger.info("✅ Cache warmed up: {len(portfolios)} portfolios loaded")

        except Exception as e:
            logger.error("Failed to warm up cache: %(e)s")

    async def _flush_updates(self) -> None:
        """刷新更新队列（带缓存优化版本）"""
        if not self._update_queue:
            return

        # 获取所有更新
        updates = list(self._update_queue)
        self._update_queue.clear()
        self._last_flush = datetime.now()

        logger.debug("🔄 Flushing {len(updates)} price updates...")

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

        # 触发投资组合重新计算（带缓存优化）
        if portfolio_updates:
            for portfolio_id, prices in portfolio_updates.items():
                try:
                    # 如果启用缓存，先检查缓存
                    if self.enable_cache:
                        cache_key = f"portfolio:{portfolio_id}"
                        cached_data = self.portfolio_cache.get(cache_key)

                        if cached_data:
                            self.metrics["cache_hits"] += 1
                            # 使用缓存的投资组合进行更新
                            portfolio = cached_data["portfolio"]
                        else:
                            self.metrics["cache_misses"] += 1
                            # 从数据库加载
                            portfolio = self.valuation_service.portfolio_repo.find_by_id(portfolio_id)
                    else:
                        portfolio = self.valuation_service.portfolio_repo.find_by_id(portfolio_id)

                    if not portfolio:
                        logger.warning("⚠️ Portfolio not found: %(portfolio_id)s")
                        continue

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
                                # 更新缓存
                                if self.enable_cache:
                                    cache_key = f"portfolio:{portfolio_id}"
                                    updated_portfolio = self.valuation_service.portfolio_repo.find_by_id(portfolio_id)

                                    self.portfolio_cache.set(
                                        cache_key,
                                        {
                                            "portfolio": updated_portfolio,
                                            "performance": performance,
                                            "cached_at": datetime.now(),
                                        },
                                    )
                                    self.metrics["cache_stores"] += 1

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
        """获取处理器指标（包含缓存指标）"""
        base_metrics = super().get_metrics()

        if self.enable_cache:
            cache_stats = self.portfolio_cache.get_stats()
            cache_metrics = {
                "cache_hits": self.metrics["cache_hits"],
                "cache_misses": self.metrics["cache_misses"],
                "cache_stores": self.metrics["cache_stores"],
                "cache_hit_rate": (
                    self.metrics["cache_hits"] / (self.metrics["cache_hits"] + self.metrics["cache_misses"])
                    if (self.metrics["cache_hits"] + self.metrics["cache_misses"]) > 0
                    else 0
                ),
                "cache_size": cache_stats["size"],
                "cache_max_size": cache_stats["max_size"],
                "cache_ttl": cache_stats["ttl"],
            }
            base_metrics.update(cache_metrics)

        return base_metrics

    def clear_cache(self):
        """清空缓存"""
        if self.enable_cache and self.portfolio_cache:
            self.portfolio_cache.clear()
            logger.info("✅ Cache cleared")
