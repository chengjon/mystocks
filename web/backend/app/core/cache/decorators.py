"""
Cache Decorators and Utilities for API Endpoints
Provides easy caching for high-frequency API endpoints
"""

import functools
import logging
from typing import Callable, Optional

from .multi_level import generate_cache_key, get_cache

logger = logging.getLogger(__name__)


class CachePolicy:
    """缓存策略配置"""

    def __init__(
        self,
        ttl: int = 300,
        memory_ttl: int = 60,
        cache_level: str = "both",
        vary_headers: Optional[list] = None,
        vary_query: Optional[list] = None,
    ):
        self.ttl = ttl
        self.memory_ttl = memory_ttl
        self.cache_level = cache_level
        self.vary_headers = vary_headers or []
        self.vary_query = vary_query or []


CACHE_POLICIES = {
    "market_overview": CachePolicy(ttl=30, memory_ttl=15, cache_level="both"),
    "stock_quote": CachePolicy(ttl=60, memory_ttl=30, cache_level="both"),
    "stock_history": CachePolicy(ttl=300, memory_ttl=60, cache_level="both"),
    "index_data": CachePolicy(ttl=30, memory_ttl=15, cache_level="both"),
    "fund_flow": CachePolicy(ttl=300, memory_ttl=60, cache_level="both"),
    "dragon_tiger": CachePolicy(ttl=300, memory_ttl=120, cache_level="both"),
    "announcement": CachePolicy(ttl=600, memory_ttl=300, cache_level="redis"),
    "user_portfolio": CachePolicy(ttl=60, memory_ttl=30, cache_level="memory"),
}


def cached(
    prefix: str,
    ttl: int = 300,
    memory_ttl: int = 60,
    cache_level: str = "both",
    key_builder: Optional[Callable] = None,
    unless: Optional[Callable] = None,
):
    """
    缓存装饰器

    Args:
        prefix: 缓存键前缀
        ttl: Redis缓存时间(秒)
        memory_ttl: 内存缓存时间(秒)
        cache_level: 缓存级别 ("memory", "redis", "both", "none")
        key_builder: 自定义键构建函数
        unless: 条件函数，返回True时不缓存
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if unless and unless(*args, **kwargs):
                return await func(*args, **kwargs)

            cache = get_cache()

            build_args = key_builder(*args, **kwargs) if key_builder else kwargs
            cache_key = generate_cache_key(prefix, **build_args)

            cached_value, found, level = await cache.get(cache_key)
            if found:
                logger.debug("Cache hit: %(cache_key)s (%(level)s)"")
                return cached_value

            result = await func(*args, **kwargs)

            if cache_level != "none":
                if cache_level == "memory":
                    await cache.set(cache_key, result, ttl=memory_ttl, memory_only=True)
                else:
                    await cache.set(cache_key, result, ttl=ttl)

                logger.debug("Cached: %(cache_key)s"")

            return result

        return wrapper

    return decorator


def cached_sync(
    prefix: str,
    ttl: int = 300,
    memory_ttl: int = 60,
    cache_level: str = "both",
):
    """同步缓存装饰器"""

    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache()
            cache_key = generate_cache_key(prefix, **kwargs)

            cached_value, found, level = cache.get(cache_key)
            if found:
                return cached_value

            result = func(*args, **kwargs)

            if cache_level != "none":
                if cache_level == "memory":
                    cache.set(cache_key, result, ttl=memory_ttl, memory_only=True)
                else:
                    cache.set(cache_key, result, ttl=ttl)

            return result

        return wrapper

    return decorator


class CacheInvalidator:
    """缓存失效管理器"""

    def __init__(self):
        self._patterns: dict[str, list[str]] = {}

    def register_pattern(self, cache_key: str, patterns: list[str]) -> None:
        """注册缓存键模式"""
        self._patterns[cache_key] = patterns

    async def invalidate(self, pattern: str) -> int:
        """失效匹配模式的所有缓存"""
        cache = get_cache()
        return await cache.delete_pattern(pattern)

    async def invalidate_related(self, cache_key: str) -> int:
        """失效相关缓存"""
        patterns = self._patterns.get(cache_key, [])
        count = 0
        for pattern in patterns:
            count += await self.invalidate(pattern)
        return count


_global_invalidator = CacheInvalidator()


def get_invalidator() -> CacheInvalidator:
    """获取全局缓存失效器"""
    return _global_invalidator


async def invalidate_stock_cache(stock_code: str) -> int:
    """失效股票相关缓存"""
    invalidator = get_invalidator()
    patterns = [
        f"stock:{stock_code}:*",
        f"quote:{stock_code}:*",
        f"history:{stock_code}:*",
    ]
    count = 0
    for pattern in patterns:
        count += await invalidator.invalidate(pattern)
    return count


async def invalidate_market_cache() -> int:
    """失效市场相关缓存"""
    invalidator = get_invalidator()
    patterns = ["market:overview:*", "index:*", "fund_flow:*"]
    count = 0
    for pattern in patterns:
        count += await invalidator.invalidate(pattern)
    return count


def create_cache_middleware(
    exclude_paths: list[str] = None,
    default_ttl: int = 60,
) -> Callable:
    """创建缓存中间件"""

    async def middleware(request, call_next):
        if exclude_paths and any(request.url.path.startswith(p) for p in exclude_paths):
            return await call_next(request)

        cache = get_cache()
        cache_key = generate_cache_key(
            "http",
            method=request.method,
            path=request.url.path,
            query=request.url.query,
        )

        cached_value, found, level = await cache.get(cache_key)
        if found:
            logger.debug("HTTP cache hit: %(cache_key)s"")
            return cached_value

        response = await call_next(request)

        if response.status_code == 200:
            await cache.set(cache_key, response, ttl=default_ttl)

        return response

    return middleware
