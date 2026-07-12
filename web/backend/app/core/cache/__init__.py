"""缓存管理器包"""
from .batch_ops import CacheBatchMixin
from .core import CacheCoreInit
from .fetch_write import CacheFetchWriteMixin
from .stats_health import CacheStatsHealthMixin


class CacheManager(CacheCoreInit, CacheFetchWriteMixin, CacheBatchMixin, CacheStatsHealthMixin):
    """缓存管理器"""



__all__ = ["CacheManager"]
