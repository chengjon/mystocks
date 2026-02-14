from app.core.cache import CacheManager  # noqa: F401
from app.core.cache.stats_health import get_cache_manager_async as _get_async

_manager = None

def get_cache_manager():
    global _manager
    if _manager is None:
        _manager = CacheManager()
    return _manager

async def get_cache_manager_async():
    return await _get_async()
