"""
Multi-Level Cache Manager for MyStocks
Implements L1 (memory) and L2 (Redis) caching with circuit breaker protection
"""

import asyncio
import hashlib
import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Optional, Callable

import redis.asyncio as redis
from prometheus_client import Counter, Gauge, Histogram

logger = logging.getLogger(__name__)

CACHE_HITS = Counter(
    "cache_hits_total",
    "缓存命中总数",
    ["level"],
)

CACHE_MISSES = Counter(
    "cache_misses_total",
    "缓存未命中总数",
    ["level"],
)

CACHE_EVICTIONS = Counter(
    "cache_evictions_total",
    "缓存逐出总数",
    ["level"],
)

CACHE_SIZE = Gauge(
    "cache_size_bytes",
    "缓存大小(字节)",
    ["level"],
)

CACHE_OPERATION_LATENCY = Histogram(
    "cache_operation_duration_seconds",
    "缓存操作延迟(秒)",
    ["operation", "level"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
)


@dataclass
class CacheConfig:
    """缓存配置"""

    memory_max_size: int = 10000
    memory_ttl: int = 60
    redis_ttl: int = 300
    redis_key_prefix: str = "mystocks:cache:"
    circuit_breaker_timeout: float = 5.0


@dataclass
class CacheEntry:
    """缓存条目"""

    value: Any
    created_at: float
    expires_at: float
    access_count: int = 0
    last_accessed: float = 0.0


class MemoryCache:
    """L1 应用内存缓存"""

    def __init__(self, max_size: int = 10000, default_ttl: int = 60):
        self._data: dict[str, CacheEntry] = {}
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._lock = asyncio.Lock()
        self._stats_hits = 0
        self._stats_misses = 0

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        async with self._lock:
            if key not in self._data:
                self._stats_misses += 1
                return None

            entry = self._data[key]
            if time.time() > entry.expires_at:
                del self._data[key]
                self._stats_misses += 1
                CACHE_MISSES.labels(level="memory").inc()
                return None

            entry.access_count += 1
            entry.last_accessed = time.time()
            self._stats_hits += 1
            CACHE_HITS.labels(level="memory").inc()
            return entry.value

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存值"""
        ttl = ttl or self._default_ttl
        now = time.time()

        async with self._lock:
            if key in self._data:
                entry = self._data[key]
                entry.value = value
                entry.created_at = now
                entry.expires_at = now + ttl
                entry.access_count = 0
            else:
                self._data[key] = CacheEntry(
                    value=value,
                    created_at=now,
                    expires_at=now + ttl,
                )

            if len(self._data) > self._max_size:
                self._evict_lru()

    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        async with self._lock:
            if key in self._data:
                del self._data[key]
                CACHE_EVICTIONS.labels(level="memory").inc()
                return True
            return False

    async def clear(self) -> None:
        """清空缓存"""
        async with self._lock:
            self._data.clear()

    def _evict_lru(self) -> None:
        """LRU逐出策略"""
        if not self._data:
            return

        oldest_access = min((entry.last_accessed or entry.created_at for entry in self._data.values()), default=0)

        keys_to_remove = [
            key for key, entry in self._data.items() if entry.last_accessed == 0 or entry.last_accessed == oldest_access
        ]

        for key in keys_to_remove[:10]:
            del self._data[key]
            CACHE_EVICTIONS.labels(level="memory").inc()

    def get_stats(self) -> dict:
        """获取缓存统计"""
        return {
            "hits": self._stats_hits,
            "misses": self._stats_misses,
            "size": len(self._data),
            "max_size": self._max_size,
            "hit_rate": (
                self._stats_hits / (self._stats_hits + self._stats_misses)
                if (self._stats_hits + self._stats_misses) > 0
                else 0
            ),
        }


class CircuitBreaker:
    """Redis连接熔断器"""

    def __init__(self, timeout: float = 5.0, failure_threshold: int = 5):
        self._timeout = timeout
        self._failure_threshold = failure_threshold
        self._failure_count = 0
        self._last_failure_time: Optional[float] = None
        self._circuit_open = False
        self._lock = asyncio.Lock()

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """执行函数，带熔断保护"""
        async with self._lock:
            if self._circuit_open:
                if time.time() - self._last_failure_time > self._timeout:
                    self._circuit_open = False
                    self._failure_count = 0
                else:
                    raise RuntimeError("Circuit breaker is open")

        try:
            result = await func(*args, **kwargs)
            self._failure_count = 0
            return result
        except Exception:
            self._failure_count += 1
            self._last_failure_time = time.time()

            if self._failure_count >= self._failure_threshold:
                self._circuit_open = True
                logger.warning(f"Circuit breaker opened after {self._failure_count} failures")

            raise

    def get_state(self) -> dict:
        """获取熔断器状态"""
        return {
            "open": self._circuit_open,
            "failure_count": self._failure_count,
            "last_failure_time": self._last_failure_time,
        }


class MultiLevelCache:
    """多级缓存管理器 (L1: Memory, L2: Redis)"""

    def __init__(self, config: Optional[CacheConfig] = None):
        self._config = config or CacheConfig()
        self._memory_cache = MemoryCache(
            max_size=self._config.memory_max_size,
            default_ttl=self._config.memory_ttl,
        )
        self._redis: Optional[redis.Redis] = None
        self._redis_connected = False
        self._circuit_breaker = CircuitBreaker(
            timeout=self._config.circuit_breaker_timeout,
        )
        self._lock = asyncio.Lock()

    async def initialize(self, redis_url: str = "redis://localhost:6379") -> None:
        """初始化Redis连接"""
        async with self._lock:
            if self._redis is not None:
                return

            try:
                self._redis = redis.from_url(redis_url, decode_responses=True)
                await self._redis.ping()
                self._redis_connected = True
                logger.info("Redis connection established")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}")
                self._redis_connected = False
                self._redis = None

    async def close(self) -> None:
        """关闭Redis连接"""
        async with self._lock:
            if self._redis:
                await self._redis.close()
                self._redis = None
                self._redis_connected = False

    async def get(self, key: str) -> tuple[Optional[Any], bool, str]:
        """
        获取缓存值
        Returns: (value, found, cache_level)
        """
        start_time = time.perf_counter()

        try:
            memory_result = await self._memory_cache.get(key)
            if memory_result is not None:
                CACHE_OPERATION_LATENCY.labels(operation="get", level="memory").observe(
                    time.perf_counter() - start_time
                )
                return memory_result, True, "memory"

            if not self._redis_connected or self._redis is None:
                CACHE_MISSES.labels(level="memory").inc()
                return None, False, "none"

            redis_value = await self._get_redis(key)
            if redis_value is not None:
                await self._memory_cache.set(key, redis_value)
                CACHE_HITS.labels(level="redis").inc()
                CACHE_OPERATION_LATENCY.labels(operation="get", level="redis").observe(time.perf_counter() - start_time)
                return redis_value, True, "redis"

            CACHE_MISSES.labels(level="redis").inc()
            return None, False, "none"

        except Exception as e:
            logger.error(f"Cache get error: {e}")
            CACHE_MISSES.labels(level="error").inc()
            return None, False, "none"

    async def _get_redis(self, key: str) -> Optional[Any]:
        """从Redis获取缓存值"""
        try:
            value = await self._circuit_breaker.call(self._redis.get, self._config.redis_key_prefix + key)
            if value:
                return json.loads(value)
        except RuntimeError:
            pass
        except json.JSONDecodeError:
            logger.warning(f"Failed to decode cached value for key: {key}")
        except Exception as e:
            logger.error(f"Redis get error: {e}")
        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        memory_only: bool = False,
    ) -> None:
        """设置缓存值"""
        start_time = time.perf_counter()
        ttl = ttl or self._config.redis_ttl

        await self._memory_cache.set(key, value, self._config.memory_ttl)
        CACHE_HITS.labels(level="memory").inc()

        if not memory_only and self._redis_connected and self._redis:
            try:
                serialized = json.dumps(value, default=str)
                await self._circuit_breaker.call(
                    self._redis.setex,
                    self._config.redis_key_prefix + key,
                    ttl,
                    serialized,
                )
                CACHE_OPERATION_LATENCY.labels(operation="set", level="redis").observe(time.perf_counter() - start_time)
            except RuntimeError:
                pass
            except Exception as e:
                logger.error(f"Redis set error: {e}")

    async def delete(self, key: str) -> None:
        """删除缓存值"""
        await self._memory_cache.delete(key)

        if self._redis_connected and self._redis:
            try:
                await self._circuit_breaker.call(self._redis.delete, self._config.redis_key_prefix + key)
                CACHE_EVICTIONS.labels(level="redis").inc()
            except RuntimeError:
                pass
            except Exception as e:
                logger.error(f"Redis delete error: {e}")

    async def delete_pattern(self, pattern: str) -> int:
        """删除匹配模式的所有缓存键"""
        count = 0

        keys = [k for k in self._memory_cache._data.keys() if pattern in k]
        for key in keys:
            if await self._memory_cache.delete(key):
                count += 1

        if self._redis_connected and self._redis:
            try:
                redis_pattern = self._config.redis_key_prefix + pattern
                matching_keys = await self._circuit_breaker.call(self._redis.keys, redis_pattern)
                if matching_keys:
                    count += await self._circuit_breaker.call(self._redis.delete, *matching_keys)
                    CACHE_EVICTIONS.labels(level="redis").inc(len(matching_keys))
            except RuntimeError:
                pass
            except Exception as e:
                logger.error(f"Redis delete pattern error: {e}")

        return count

    async def clear(self) -> None:
        """清空所有缓存"""
        await self._memory_cache.clear()

        if self._redis_connected and self._redis:
            try:
                keys = await self._circuit_breaker.call(self._redis.keys, self._config.redis_key_prefix + "*")
                if keys:
                    await self._circuit_breaker.call(self._redis.delete, *keys)
                    CACHE_EVICTIONS.labels(level="redis").inc(len(keys))
            except RuntimeError:
                pass
            except Exception as e:
                logger.error(f"Redis clear error: {e}")

    def get_stats(self) -> dict:
        """获取缓存统计"""
        memory_stats = self._memory_cache.get_stats()
        return {
            "memory": memory_stats,
            "redis": {
                "connected": self._redis_connected,
                "circuit_breaker": self._circuit_breaker.get_state(),
            },
            "total_hits": memory_stats["hits"],
            "total_misses": memory_stats["misses"],
            "overall_hit_rate": memory_stats["hit_rate"],
        }


_global_cache: Optional[MultiLevelCache] = None


def get_cache() -> MultiLevelCache:
    """获取全局缓存实例"""
    global _global_cache
    if _global_cache is None:
        _global_cache = MultiLevelCache()
    return _global_cache


async def init_cache(redis_url: str = "redis://localhost:6379") -> None:
    """初始化全局缓存"""
    cache = get_cache()
    await cache.initialize(redis_url)


async def close_cache() -> None:
    """关闭全局缓存"""
    global _global_cache
    if _global_cache:
        await _global_cache.close()
        _global_cache = None


def generate_cache_key(prefix: str, **kwargs) -> str:
    """生成缓存键"""
    sorted_kwargs = sorted(kwargs.items())
    key_str = prefix + ":" + ":".join(f"{k}={v}" for k, v in sorted_kwargs)
    return hashlib.md5(key_str.encode(), usedforsecurity=False).hexdigest()
