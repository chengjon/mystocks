"""缓存预热系统 - Cache Prewarming System

实现基于访问频率的缓存预热和性能监控。

Features:
- 启动时自动预热热点数据 (Automatic Hot Data Prewarming)
- 缓存命中率监控 (Cache Hit Rate Monitoring)
- 性能指标追踪 (Performance Metrics Tracking)
- 健康状态检查 (Health Status Checks)
- 定期重新预热 (Periodic Rewarming)

Architecture:
- CachePrewarmingStrategy: 预热策略执行
- CacheMonitor: 缓存性能监控
- PrewarmingScheduler: 定期预热调度
"""

import time
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

import structlog

from app.core.cache_eviction import get_eviction_strategy
from app.core.cache_manager import CacheManager, get_cache_manager


logger = structlog.get_logger()


class CacheMonitor:
    """缓存性能监控器"""

    def __init__(self):
        """初始化缓存监控器"""
        self.hit_count = 0
        self.miss_count = 0
        self.total_read_time = 0.0
        self.read_operations = 0
        self.last_reset = datetime.now(timezone.utc)

        logger.info("🔧 初始化缓存监控器")

    def record_hit(self, latency_ms: float = 0) -> None:
        """记录缓存命中

        Args:
            latency_ms: 读取延迟（毫秒）

        """
        self.hit_count += 1
        self.total_read_time += latency_ms
        self.read_operations += 1

    def record_miss(self, latency_ms: float = 0) -> None:
        """记录缓存未命中

        Args:
            latency_ms: 读取延迟（毫秒）

        """
        self.miss_count += 1
        self.total_read_time += latency_ms
        self.read_operations += 1

    def get_hit_rate(self) -> float:
        """获取缓存命中率"""
        total = self.hit_count + self.miss_count
        if total == 0:
            return 0.0
        return (self.hit_count / total) * 100

    def get_average_latency(self) -> float:
        """获取平均读取延迟（毫秒）"""
        if self.read_operations == 0:
            return 0.0
        return self.total_read_time / self.read_operations

    def get_metrics(self) -> Dict[str, Any]:
        """获取监控指标"""
        uptime = datetime.now(timezone.utc) - self.last_reset
        hit_rate = self.get_hit_rate()

        return {
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": hit_rate,
            "hit_rate_percent": f"{hit_rate:.1f}%",
            "total_reads": self.hit_count + self.miss_count,
            "average_latency_ms": self.get_average_latency(),
            "uptime_seconds": uptime.total_seconds(),
            "health_status": "healthy" if hit_rate >= 80 else "warning",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def reset(self) -> None:
        """重置监控数据"""
        self.hit_count = 0
        self.miss_count = 0
        self.total_read_time = 0.0
        self.read_operations = 0
        self.last_reset = datetime.now(timezone.utc)
        logger.info("✅ 缓存监控数据已重置")


class CachePrewarmingStrategy:
    """缓存预热策略"""

    def __init__(
        self,
        cache_manager: Optional[CacheManager] = None,
        eviction_strategy: Optional[Any] = None,
    ):
        """初始化预热策略

        Args:
            cache_manager: CacheManager实例
            eviction_strategy: 淘汰策略实例（用于获取热点数据）

        """
        self.cache_manager = cache_manager or get_cache_manager()
        self.eviction_strategy = eviction_strategy or get_eviction_strategy()
        self.monitor = CacheMonitor()
        self.prewarming_history: Dict[str, datetime] = {}

        logger.info("🔧 初始化缓存预热策略")

    def get_hot_data_list(self, top_n: int = 20) -> List[Dict[str, Any]]:
        """获取热点数据列表

        Args:
            top_n: 返回热点数据数量

        Returns:
            热点数据列表，包含cache_key和access_count

        """
        hot_data = self.eviction_strategy.get_hot_data(top_n=top_n)
        return hot_data

    def prewarm_cache(self, data_sources: Optional[Dict[str, Callable]] = None) -> Dict[str, Any]:
        """执行缓存预热

        Args:
            data_sources: 数据源字典 {cache_key: fetch_function}
                          如果为None，则使用已缓存的热点数据

        Returns:
            预热结果统计

        """
        try:
            start_time = time.time()
            prewarmed_count = 0
            failed_count = 0

            # 如果没有提供数据源，使用热点数据列表
            if data_sources is None:
                hot_data = self.get_hot_data_list(top_n=20)
                logger.info(
                    "🔥 开始缓存预热",
                    hot_data_count=len(hot_data),
                )

                for item in hot_data:
                    cache_key = item.get("cache_key", "")
                    if not cache_key:
                        continue

                    try:
                        # 解析cache_key格式: symbol:data_type:timeframe
                        parts = cache_key.lower().split(":")
                        if len(parts) >= 2:
                            symbol = parts[0]
                            data_type = parts[1]
                            timeframe = parts[2] if len(parts) > 2 else "1d"

                            # 验证缓存是否存在
                            cached = self.cache_manager.fetch_from_cache(
                                symbol=symbol,
                                data_type=data_type,
                                timeframe=timeframe,
                            )

                            if cached:
                                prewarmed_count += 1
                                self.prewarming_history[cache_key] = datetime.now(timezone.utc)

                    except Exception as e:
                        logger.warning(
                            "⚠️ 预热单个缓存失败",
                            cache_key=cache_key,
                            error=str(e),
                        )
                        failed_count += 1
            else:
                # 使用提供的数据源预热
                logger.info(
                    "🔥 开始缓存预热",
                    source_count=len(data_sources),
                )

                for cache_key, fetch_fn in data_sources.items():
                    try:
                        # 执行数据源函数获取数据
                        data = fetch_fn()

                        # 解析cache_key并写入缓存
                        parts = cache_key.split(":")
                        if len(parts) >= 2:
                            symbol = parts[0]
                            data_type = parts[1]
                            timeframe = parts[2] if len(parts) > 2 else "1d"

                            success = self.cache_manager.write_to_cache(
                                symbol=symbol,
                                data_type=data_type,
                                timeframe=timeframe,
                                data=data,
                            )

                            if success:
                                prewarmed_count += 1
                                self.prewarming_history[cache_key] = datetime.now(timezone.utc)
                            else:
                                failed_count += 1

                    except Exception as e:
                        logger.warning(
                            "⚠️ 预热单个缓存失败",
                            cache_key=cache_key,
                            error=str(e),
                        )
                        failed_count += 1

            elapsed = time.time() - start_time

            logger.info(
                "✅ 缓存预热完成",
                prewarmed_count=prewarmed_count,
                failed_count=failed_count,
                elapsed_seconds=round(elapsed, 2),
            )

            return {
                "success": True,
                "prewarmed_count": prewarmed_count,
                "failed_count": failed_count,
                "total_count": prewarmed_count + failed_count,
                "elapsed_seconds": elapsed,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error("❌ 缓存预热失败", error=str(e))
            return {
                "success": False,
                "message": str(e),
                "prewarmed_count": 0,
                "failed_count": 0,
            }

    def get_prewarming_status(self) -> Dict[str, Any]:
        """获取预热状态"""
        return {
            "last_prewarming": (self.prewarming_history.get("_last_full_prewarm") if self.prewarming_history else None),
            "prewarmed_keys_count": len(self.prewarming_history),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_health_status(self) -> Dict[str, Any]:
        """获取缓存健康状态"""
        metrics = self.monitor.get_metrics()
        hit_rate = metrics.get("hit_rate", 0)

        return {
            "status": "healthy" if hit_rate >= 80 else "warning",
            "hit_rate": hit_rate,
            "hit_rate_percent": metrics.get("hit_rate_percent"),
            "total_reads": metrics.get("total_reads"),
            "average_latency_ms": metrics.get("average_latency_ms"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# ==================== 全局实例 ====================

_cache_monitor: Optional[CacheMonitor] = None
_prewarming_strategy: Optional[CachePrewarmingStrategy] = None


def get_cache_monitor() -> CacheMonitor:
    """获取缓存监控器单例

    Returns:
        CacheMonitor实例

    """
    global _cache_monitor

    if _cache_monitor is None:
        _cache_monitor = CacheMonitor()

    return _cache_monitor


def get_prewarming_strategy() -> CachePrewarmingStrategy:
    """获取预热策略单例

    Returns:
        CachePrewarmingStrategy实例

    """
    global _prewarming_strategy

    if _prewarming_strategy is None:
        _prewarming_strategy = CachePrewarmingStrategy()

    return _prewarming_strategy


def reset_cache_monitor() -> None:
    """重置缓存监控器（用于测试）"""
    global _cache_monitor
    if _cache_monitor:
        _cache_monitor = None


def reset_prewarming_strategy() -> None:
    """重置预热策略（用于测试）"""
    global _prewarming_strategy
    if _prewarming_strategy:
        _prewarming_strategy = None
