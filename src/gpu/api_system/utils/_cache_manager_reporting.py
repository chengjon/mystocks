"""CacheManager 报告与监控方法集。"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict

import psutil


logger = logging.getLogger(__name__)


class CacheManagerReportingMixin:
    """缓存性能报告相关方法。"""

    def get_cache_performance_report(self) -> Dict[str, Any]:
        """获取缓存性能报告。"""
        stats = self.multi_level_cache.get_cache_stats()
        strategy_analysis = {
            data_type: {
                "ttl": strategy["ttl"],
                "compression": strategy["compression"],
                "strategy": strategy["strategy"],
            }
            for data_type, strategy in self.cache_strategies.items()
        }
        return {
            "timestamp": datetime.now().isoformat(),
            "cache_stats": stats,
            "strategies": strategy_analysis,
            "optimization_suggestions": self.multi_level_cache.optimize_cache_performance(),
            "hot_keys": self.multi_level_cache.l1_cache.get_hot_keys(10),
        }

    def clear_cache_by_type(self, data_type: str):
        """按类型清空缓存。"""
        if data_type in self.cache_strategies:
            logger.info("Cleared cache for type: %s", data_type)

    def monitor_cache_performance(self):
        """监控缓存性能。"""
        if not self.monitoring_enabled:
            return None

        stats = self.get_cache_performance_report()
        if stats["cache_stats"]["overall_hit_rate"] < 70:
            logger.warning("Cache hit rate low: %s%", stats["cache_stats"]["overall_hit_rate"])
        if stats["cache_stats"]["total_memory_usage"] > psutil.virtual_memory().total * 0.7:
            logger.warning("Cache memory usage high: %s bytes", stats["cache_stats"]["total_memory_usage"])

        return stats
