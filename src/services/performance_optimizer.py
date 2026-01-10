"""
性能优化模块
Performance Optimization Module

提供持仓市值计算的性能优化：
1. LRU 缓存
2. 批量更新
3. 增量计算
4. 异步处理

Author: Claude Code
Date: 2026-01-09
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import structlog
import asyncio
from functools import lru_cache
from collections import OrderedDict
import hashlib
import json

logger = structlog.get_logger()


class LRUCache:
    """LRU 缓存实现"""

    def __init__(self, max_size: int = 1000, ttl: float = 300.0):
        """
        初始化 LRU 缓存

        Args:
            max_size: 最大缓存条目数
            ttl: 缓存过期时间（秒）
        """
        self.max_size = max_size
        self.ttl = ttl
        self.cache: OrderedDict = OrderedDict()
        self.timestamps: Dict[str, datetime] = {}

    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if key not in self.cache:
            return None

        if self._is_expired(key):
            self._remove(key)
            return None

        self.cache.move_to_end(key)
        return self.cache[key]

    def set(self, key: str, value: Any) -> None:
        """设置缓存值"""
        if key in self.cache:
            self.cache.move_to_end(key)

        self.cache[key] = value
        self.timestamps[key] = datetime.now()

        if len(self.cache) > self.max_size:
            oldest = next(iter(self.cache))
            self._remove(oldest)

    def _is_expired(self, key: str) -> bool:
        """检查是否过期"""
        if key not in self.timestamps:
            return True
        return (datetime.now() - self.timestamps[key]).total_seconds() > self.ttl

    def _remove(self, key: str) -> None:
        """移除缓存条目"""
        self.cache.pop(key, None)
        self.timestamps.pop(key, None)

    def clear(self) -> None:
        """清空缓存"""
        self.cache.clear()
        self.timestamps.clear()

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "ttl": self.ttl,
            "hit_rate": getattr(self, "_hit_count", 0) / max(getattr(self, "_access_count", 1), 1),
        }


class BatchProcessor:
    """批量处理器"""

    def __init__(
        self,
        max_batch_size: int = 100,
        flush_interval: float = 0.05,
        processor: Optional[Callable] = None,
    ):
        """
        初始化批量处理器

        Args:
            max_batch_size: 最大批量大小
            flush_interval: 刷新间隔（秒）
            processor: 处理函数
        """
        self.max_batch_size = max_batch_size
        self.flush_interval = flush_interval
        self.processor = processor

        self.batch: List[Any] = []
        self._lock = asyncio.Lock()
        self._flush_task: Optional[asyncio.Task] = None
        self._last_flush = datetime.now()

        self.metrics = {
            "total_batches": 0,
            "total_items": 0,
        }

    async def add(self, item: Any) -> None:
        """添加项目到批次"""
        async with self._lock:
            self.batch.append(item)

            if len(self.batch) >= self.max_batch_size:
                await self._flush()

            elif not self._flush_task or self._flush_task.done():
                self._flush_task = asyncio.create_task(self._scheduled_flush())

    async def _scheduled_flush(self) -> None:
        """定时刷新"""
        await asyncio.sleep(self.flush_interval)
        async with self._lock:
            if self.batch:
                await self._flush()

    async def _flush(self) -> None:
        """刷新批次"""
        if not self.batch:
            return

        items = list(self.batch)
        self.batch.clear()
        self._last_flush = datetime.now()

        if self.processor:
            if asyncio.iscoroutinefunction(self.processor):
                await self.processor(items)
            else:
                self.processor(items)

        self.metrics["total_batches"] += 1
        self.metrics["total_items"] += len(items)

    async def flush(self) -> None:
        """手动刷新"""
        async with self._lock:
            await self._flush()

    def get_metrics(self) -> Dict[str, Any]:
        """获取指标"""
        return {
            **self.metrics,
            "pending_items": len(self.batch),
            "last_flush": self._last_flush.isoformat(),
        }


class IncrementalCalculator:
    """增量计算器"""

    def __init__(self, initial_value: float = 0.0):
        """初始化增量计算器"""
        self.value = initial_value
        self.history: List[float] = []
        self.max_history = 100

    def add_delta(self, delta: float) -> float:
        """添加增量并返回新值"""
        self.value += delta
        self.history.append(self.value)

        if len(self.history) > self.max_history:
            self.history.pop(0)

        return self.value

    def set_value(self, value: float) -> float:
        """设置值并计算增量"""
        delta = value - self.value
        self.value = value
        self.history.append(value)

        if len(self.history) > self.max_history:
            self.history.pop(0)

        return delta

    def get_value(self) -> float:
        """获取当前值"""
        return self.value

    def get_change(self) -> float:
        """获取变化量"""
        if len(self.history) < 2:
            return 0.0
        return self.history[-1] - self.history[-2]

    def get_rate_of_change(self, window: int = 5) -> float:
        """获取变化率"""
        if len(self.history) < window + 1:
            return 0.0
        return (self.history[-1] - self.history[-window - 1]) / window


class CacheKeyGenerator:
    """缓存键生成器"""

    @staticmethod
    def generate(params: Dict[str, Any]) -> str:
        """生成缓存键"""
        sorted_params = sorted(params.items())
        key_string = json.dumps(sorted_params, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()

    @staticmethod
    def position_key(symbol: str, quantity: int, avg_price: float) -> str:
        """生成持仓缓存键"""
        return f"position:{symbol}:{quantity}:{avg_price:.2f}"

    @staticmethod
    def market_key(symbol: str, price_type: str = "latest") -> str:
        """生成市场价格缓存键"""
        return f"market:{symbol}:{price_type}"

    @staticmethod
    def portfolio_key(portfolio_id: str) -> str:
        """生成组合缓存键"""
        return f"portfolio:{portfolio_id}"


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self, window_size: int = 100):
        """初始化性能监控器"""
        self.window_size = window_size
        self.latencies: List[float] = []
        self.operation_counts: Dict[str, int] = {}
        self.error_counts: Dict[str, int] = {}

    def record_latency(self, operation: str, latency: float) -> None:
        """记录延迟"""
        self.latencies.append(latency)

        if len(self.latencies) > self.window_size:
            self.latencies.pop(0)

        if operation not in self.operation_counts:
            self.operation_counts[operation] = 0
        self.operation_counts[operation] += 1

    def record_error(self, operation: str, error: Exception) -> None:
        """记录错误"""
        if operation not in self.error_counts:
            self.error_counts[operation] = 0
        self.error_counts[operation] += 1

        logger.warning(f"Operation {operation} failed", error=str(error), count=self.error_counts[operation])

    def get_avg_latency(self) -> float:
        """获取平均延迟"""
        if not self.latencies:
            return 0.0
        return sum(self.latencies) / len(self.latencies)

    def get_percentile_latency(self, percentile: float = 95) -> float:
        """获取百分位延迟"""
        if not self.latencies:
            return 0.0
        sorted_latencies = sorted(self.latencies)
        index = int(len(sorted_latencies) * percentile / 100)
        return sorted_latencies[min(index, len(sorted_latencies) - 1)]

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "avg_latency_ms": self.get_avg_latency() * 1000,
            "p95_latency_ms": self.get_percentile_latency() * 1000,
            "p99_latency_ms": self.get_percentile_latency(99) * 1000,
            "operation_counts": self.operation_counts,
            "error_counts": self.error_counts,
            "total_operations": sum(self.operation_counts.values()),
            "total_errors": sum(self.error_counts.values()),
        }


_global_cache: Optional[LRUCache] = None
_global_batch_processor: Optional[BatchProcessor] = None
_global_performance_monitor: Optional[PerformanceMonitor] = None


def get_cache() -> LRUCache:
    """获取全局缓存实例"""
    global _global_cache
    if _global_cache is None:
        _global_cache = LRUCache(max_size=10000, ttl=60.0)
    return _global_cache


def get_batch_processor() -> BatchProcessor:
    """获取全局批量处理器实例"""
    global _global_batch_processor
    if _global_batch_processor is None:
        _global_batch_processor = BatchProcessor(max_batch_size=500, flush_interval=0.02)
    return _global_batch_processor


def get_performance_monitor() -> PerformanceMonitor:
    """获取全局性能监控器实例"""
    global _global_performance_monitor
    if _global_performance_monitor is None:
        _global_performance_monitor = PerformanceMonitor(window_size=200)
    return _global_performance_monitor
