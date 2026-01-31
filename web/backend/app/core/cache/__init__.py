"""Cache Module for MyStocks"""

from .decorators import (
    CACHE_POLICIES,
    CacheInvalidator,
    CachePolicy,
    cached,
    cached_sync,
    get_invalidator,
    invalidate_market_cache,
    invalidate_stock_cache,
)
from .multi_level import (
    CacheConfig,
    MemoryCache,
    MultiLevelCache,
    close_cache,
    generate_cache_key,
    get_cache,
    init_cache,
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
