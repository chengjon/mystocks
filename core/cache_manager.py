#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CacheManager - 高性能内存缓存管理器

功能:
- LRU (Least Recently Used) 缓存
- TTL (Time To Live) 过期机制
- 线程安全
- 缓存统计和监控

用途:
- 缓存查询结果
- 缓存元数据（股票列表、交易日历等）
- 减少数据库查询压力

创建日期: 2025-10-25
版本: 1.0.0 (P3)
"""

import time
import threading
import logging
from typing import Any, Optional, Dict, Tuple, Callable
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class CacheStats:
    """缓存统计信息"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0
    expires: int = 0

    @property
    def hit_rate(self) -> float:
        """命中率"""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'hits': self.hits,
            'misses': self.misses,
            'sets': self.sets,
            'deletes': self.deletes,
            'evictions': self.evictions,
            'expires': self.expires,
            'hit_rate': f"{self.hit_rate:.2f}%",
            'total_requests': self.hits + self.misses
        }


@dataclass
class CacheEntry:
    """缓存条目"""
    value: Any
    expires_at: Optional[float] = None
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0

    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at

    def access(self) -> None:
        """记录访问"""
        self.last_accessed = time.time()
        self.access_count += 1


class LRUCache:
    """
    LRU (Least Recently Used) 缓存

    特性:
    - 线程安全
    - 支持 TTL 过期
    - 自动淘汰最少使用的条目
    - 完整的统计信息

    示例:
        ```python
        cache = LRUCache(max_size=1000, default_ttl=300)

        # 设置缓存
        cache.set('key1', 'value1')
        cache.set('key2', 'value2', ttl=60)  # 60秒后过期

        # 获取缓存
        value = cache.get('key1')

        # 查看统计
        stats = cache.get_stats()
        print(f"缓存命中率: {stats.hit_rate:.2f}%")
        ```
    """

    def __init__(self, max_size: int = 1000, default_ttl: Optional[int] = None):
        """
        初始化 LRU 缓存

        Args:
            max_size: 最大缓存条目数
            default_ttl: 默认TTL（秒），None表示永不过期
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._stats = CacheStats()

        logger.info(f"LRUCache initialized: max_size={max_size}, default_ttl={default_ttl}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取缓存值

        Args:
            key: 缓存键
            default: 默认值（缓存未命中时返回）

        Returns:
            缓存值或默认值
        """
        with self._lock:
            entry = self._cache.get(key)

            # 缓存未命中
            if entry is None:
                self._stats.misses += 1
                return default

            # 检查过期
            if entry.is_expired():
                self._stats.misses += 1
                self._stats.expires += 1
                del self._cache[key]
                logger.debug(f"Cache expired: {key}")
                return default

            # 缓存命中
            self._stats.hits += 1
            entry.access()

            # 移到末尾（最近使用）
            self._cache.move_to_end(key)

            return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
            ttl: TTL（秒），None使用默认TTL
        """
        with self._lock:
            # 计算过期时间
            expires_at = None
            ttl_to_use = ttl if ttl is not None else self.default_ttl
            if ttl_to_use is not None:
                expires_at = time.time() + ttl_to_use

            # 创建缓存条目
            entry = CacheEntry(value=value, expires_at=expires_at)

            # 如果键已存在，删除旧的
            if key in self._cache:
                del self._cache[key]

            # 添加新条目
            self._cache[key] = entry
            self._cache.move_to_end(key)
            self._stats.sets += 1

            # 检查是否超过最大容量
            while len(self._cache) > self.max_size:
                # 淘汰最老的条目（最少最近使用）
                evicted_key, _ = self._cache.popitem(last=False)
                self._stats.evictions += 1
                logger.debug(f"Cache evicted: {evicted_key} (size limit reached)")

    def delete(self, key: str) -> bool:
        """
        删除缓存条目

        Args:
            key: 缓存键

        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats.deletes += 1
                return True
            return False

    def clear(self) -> None:
        """清空所有缓存"""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            logger.info(f"Cache cleared: {count} entries removed")

    def cleanup_expired(self) -> int:
        """
        清理过期条目

        Returns:
            清理的条目数量
        """
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]

            for key in expired_keys:
                del self._cache[key]
                self._stats.expires += 1

            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired entries")

            return len(expired_keys)

    def get_stats(self) -> CacheStats:
        """获取缓存统计信息"""
        return self._stats

    def get_size(self) -> int:
        """获取当前缓存条目数量"""
        with self._lock:
            return len(self._cache)

    def get_or_set(
        self,
        key: str,
        factory: Callable[[], Any],
        ttl: Optional[int] = None
    ) -> Any:
        """
        获取缓存值，如果不存在则通过工厂函数创建

        Args:
            key: 缓存键
            factory: 工厂函数（用于创建值）
            ttl: TTL（秒）

        Returns:
            缓存值
        """
        value = self.get(key)
        if value is None:
            value = factory()
            self.set(key, value, ttl=ttl)
        return value


class CacheManager:
    """
    缓存管理器 - 管理多个命名缓存

    示例:
        ```python
        manager = CacheManager()

        # 创建专用缓存
        manager.create_cache('query_results', max_size=500, default_ttl=300)
        manager.create_cache('metadata', max_size=100, default_ttl=3600)

        # 使用缓存
        manager.set('query_results', 'q1', result_df)
        result = manager.get('query_results', 'q1')

        # 查看所有缓存统计
        stats = manager.get_all_stats()
        ```
    """

    def __init__(self):
        """初始化缓存管理器"""
        self._caches: Dict[str, LRUCache] = {}
        self._lock = threading.RLock()

        logger.info("CacheManager initialized")

    def create_cache(
        self,
        name: str,
        max_size: int = 1000,
        default_ttl: Optional[int] = None
    ) -> LRUCache:
        """
        创建命名缓存

        Args:
            name: 缓存名称
            max_size: 最大条目数
            default_ttl: 默认TTL（秒）

        Returns:
            创建的缓存实例
        """
        with self._lock:
            if name in self._caches:
                logger.warning(f"Cache '{name}' already exists, returning existing cache")
                return self._caches[name]

            cache = LRUCache(max_size=max_size, default_ttl=default_ttl)
            self._caches[name] = cache
            logger.info(f"Created cache: {name} (max_size={max_size}, default_ttl={default_ttl})")
            return cache

    def get_cache(self, name: str) -> Optional[LRUCache]:
        """获取命名缓存"""
        return self._caches.get(name)

    def get(self, cache_name: str, key: str, default: Any = None) -> Any:
        """从指定缓存获取值"""
        cache = self.get_cache(cache_name)
        if cache is None:
            logger.warning(f"Cache '{cache_name}' not found")
            return default
        return cache.get(key, default)

    def set(self, cache_name: str, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置指定缓存的值"""
        cache = self.get_cache(cache_name)
        if cache is None:
            logger.warning(f"Cache '{cache_name}' not found, creating with defaults")
            cache = self.create_cache(cache_name)
        cache.set(key, value, ttl=ttl)

    def delete(self, cache_name: str, key: str) -> bool:
        """删除指定缓存的值"""
        cache = self.get_cache(cache_name)
        if cache is None:
            return False
        return cache.delete(key)

    def clear_cache(self, cache_name: str) -> None:
        """清空指定缓存"""
        cache = self.get_cache(cache_name)
        if cache is not None:
            cache.clear()

    def clear_all(self) -> None:
        """清空所有缓存"""
        with self._lock:
            for cache in self._caches.values():
                cache.clear()
            logger.info("All caches cleared")

    def cleanup_all_expired(self) -> Dict[str, int]:
        """
        清理所有缓存的过期条目

        Returns:
            每个缓存清理的条目数量
        """
        result = {}
        with self._lock:
            for name, cache in self._caches.items():
                count = cache.cleanup_expired()
                if count > 0:
                    result[name] = count
        return result

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """获取所有缓存的统计信息"""
        stats = {}
        with self._lock:
            for name, cache in self._caches.items():
                stats[name] = {
                    **cache.get_stats().to_dict(),
                    'size': cache.get_size(),
                    'max_size': cache.max_size
                }
        return stats

    def list_caches(self) -> list[str]:
        """列出所有缓存名称"""
        with self._lock:
            return list(self._caches.keys())


# 全局缓存管理器实例
_global_cache_manager: Optional[CacheManager] = None
_global_lock = threading.Lock()


def get_cache_manager() -> CacheManager:
    """获取全局缓存管理器实例（单例模式）"""
    global _global_cache_manager

    if _global_cache_manager is None:
        with _global_lock:
            if _global_cache_manager is None:
                _global_cache_manager = CacheManager()

    return _global_cache_manager
