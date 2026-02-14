"""缓存管理器包"""
from .core import CacheCoreInit
from .fetch_write import CacheFetchWriteMixin
from .batch_ops import CacheBatchMixin
from .stats_health import CacheStatsHealthMixin


class CacheManager(CacheCoreInit, CacheFetchWriteMixin, CacheBatchMixin, CacheStatsHealthMixin):
    """缓存管理器"""
    pass


__all__ = ["CacheManager"]
