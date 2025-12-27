"""Cache Module for MyStocks"""

from .multi_level import (
    MultiLevelCache,
    MemoryCache,
    CacheConfig,
    get_cache,
    init_cache,
    close_cache,
    generate_cache_key,
)

from .decorators import (
    cached,
    cached_sync,
    CachePolicy,
    CACHE_POLICIES,
    CacheInvalidator,
    get_invalidator,
    invalidate_stock_cache,
    invalidate_market_cache,
)

__all__ = [
    "MultiLevelCache",
    "MemoryCache",
    "CacheConfig",
    "get_cache",
    "init_cache",
    "close_cache",
    "generate_cache_key",
    "cached",
    "cached_sync",
    "CachePolicy",
    "CACHE_POLICIES",
    "CacheInvalidator",
    "get_invalidator",
    "invalidate_stock_cache",
    "invalidate_market_cache",
]
