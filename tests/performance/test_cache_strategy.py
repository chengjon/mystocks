#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试缓存策略优化模块

提供测试过程中的缓存优化功能：
1. LRU 缓存实现
2. TTL 过期策略
3. 缓存预热
4. 缓存压缩
5. 缓存统计
"""

import time
import threading
import hashlib
import pickle
import zlib
from typing import Any, Dict, List, Optional, Callable, TypeVar
from dataclasses import dataclass
import logging


logger = logging.getLogger(__name__)


T = TypeVar("T")


@dataclass
class CacheStats:
    """缓存统计"""

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size: int = 0
    memory_kb: float = 0.0
    hit_rate: float = 0.0

    def to_dict(self) -> Dict:
        total = self.hits + self.misses
        self.hit_rate = self.hits / total * 100 if total > 0 else 0.0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "size": self.size,
            "memory_kb": round(self.memory_kb, 2),
            "hit_rate": round(self.hit_rate, 2),
        }


@dataclass
class CacheEntry:
    """缓存条目"""

    key: str
    value: Any
    created_at: float
    last_accessed: float
    access_count: int
    size: int
    ttl: Optional[int] = None
    compressed: bool = False

    def is_expired(self) -> bool:
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl

    def is_stale(self, max_idle_seconds: int = 3600) -> bool:
        return time.time() - self.last_accessed > max_idle_seconds


class LRUCache:
    """LRU 缓存实现"""

    def __init__(self, max_size: int = 1000, ttl_seconds: Optional[int] = None):
        self.max_size = max_size
        self.ttl = ttl_seconds
        self._cache: Dict[str, CacheEntry] = {}
        self._order: List[str] = []
        self._lock = threading.Lock()
        self._stats = CacheStats()

    def _hash_key(self, key: Any) -> str:
        """生成缓存键的哈希"""
        if isinstance(key, str):
            return key
        key_str = str(key)
        return hashlib.md5(key_str.encode()).hexdigest()

    def _evict_lru(self):
        """淘汰最久未使用的条目"""
        if not self._order:
            return

        while len(self._cache) >= self.max_size and self._order:
            lru_key = self._order.pop(0)
            if lru_key in self._cache:
                del self._cache[lru_key]
                self._stats.evictions += 1

    def _calculate_size(self, value: Any) -> int:
        """计算值的大小"""
        try:
            return len(pickle.dumps(value))
        except Exception:
            return len(str(value))

    def get(self, key: Any) -> Optional[Any]:
        """获取缓存值"""
        hashed_key = self._hash_key(key)

        with self._lock:
            if hashed_key in self._cache:
                entry = self._cache[hashed_key]

                if entry.is_expired():
                    del self._cache[hashed_key]
                    self._stats.misses += 1
                    return None

                # 更新访问顺序
                if hashed_key in self._order:
                    self._order.remove(hashed_key)
                self._order.append(hashed_key)
                entry.last_accessed = time.time()
                entry.access_count += 1

                self._stats.hits += 1
                return entry.value

            self._stats.misses += 1
            return None

    def set(self, key: Any, value: Any, ttl: Optional[int] = None):
        """设置缓存值"""
        hashed_key = self._hash_key(key)
        ttl = ttl or self.ttl

        with self._lock:
            size = self._calculate_size(value)

            # 如果已存在，更新值
            if hashed_key in self._cache:
                entry = self._cache[hashed_key]
                entry.value = value
                entry.created_at = time.time()
                entry.last_accessed = time.time()
                entry.size = size
                entry.ttl = ttl

                # 更新访问顺序
                if hashed_key in self._order:
                    self._order.remove(hashed_key)
                self._order.append(hashed_key)
                return

            # 淘汰 LRU 条目
            self._evict_lru()

            # 添加新条目
            self._cache[hashed_key] = CacheEntry(
                key=hashed_key,
                value=value,
                created_at=time.time(),
                last_accessed=time.time(),
                access_count=0,
                size=size,
                ttl=ttl,
            )
            self._order.append(hashed_key)
            self._stats.size = len(self._cache)

    def delete(self, key: Any) -> bool:
        """删除缓存条目"""
        hashed_key = self._hash_key(key)

        with self._lock:
            if hashed_key in self._cache:
                del self._cache[hashed_key]
                if hashed_key in self._order:
                    self._order.remove(hashed_key)
                self._stats.size = len(self._cache)
                return True
            return False

    def clear(self):
        """清空缓存"""
        with self._lock:
            self._cache.clear()
            self._order.clear()
            self._stats = CacheStats()

    def get_stats(self) -> CacheStats:
        """获取统计信息"""
        with self._lock:
            total = self._stats.hits + self._stats.misses
            if total > 0:
                self._stats.hit_rate = self._stats.hits / total * 100

            # 计算内存使用
            self._stats.memory_kb = sum(e.size for e in self._cache.values()) / 1024
            self._stats.size = len(self._cache)

            return self._stats

    def cleanup_expired(self) -> int:
        """清理过期条目"""
        removed = 0
        with self._lock:
            expired_keys = [k for k, v in self._cache.items() if v.is_expired()]
            for key in expired_keys:
                del self._cache[key]
                if key in self._order:
                    self._order.remove(key)
                removed += 1

            self._stats.size = len(self._cache)
        return removed


class CompressedCache:
    """压缩缓存"""

    def __init__(self, cache: Optional[LRUCache] = None, compression_level: int = 6):
        self.cache = cache or LRUCache(max_size=500)
        self.compression_level = compression_level

    def get(self, key: Any) -> Optional[Any]:
        """获取并解压"""
        compressed = self.cache.get(key)
        if compressed is None:
            return None

        try:
            return pickle.loads(zlib.decompress(compressed))
        except Exception:
            return None

    def set(self, key: Any, value: Any, ttl: Optional[int] = None):
        """压缩并缓存"""
        try:
            compressed = zlib.compress(pickle.dumps(value), self.compression_level)
            self.cache.set(key, compressed, ttl)
        except Exception:
            self.cache.set(key, value, ttl)

    def get_stats(self) -> Dict:
        """获取统计"""
        return self.cache.get_stats().to_dict()


class CacheWarmer:
    """缓存预热器"""

    def __init__(self, cache: LRUCache):
        self.cache = cache
        self._warm_data: Dict[str, Any] = {}

    def add_warmup_task(self, key: str, generator: Callable[[], Any]):
        """添加预热任务"""
        self._warm_data[key] = generator

    def warmup(self, keys: Optional[List[str]] = None) -> Dict[str, Any]:
        """执行预热"""
        keys = keys or list(self._warm_data.keys())
        results = {}

        for key in keys:
            if key in self._warm_data:
                try:
                    results[key] = self._warm_data[key]()
                except Exception as e:
                    results[key] = f"Error: {e}"

        # 缓存预热结果
        for key, value in results.items():
            if not isinstance(value, str):
                self.cache.set(key, value)

        return results


class TestCacheStrategy:
    """测试缓存策略"""

    def __init__(self):
        self.test_data_cache = LRUCache(max_size=100, ttl_seconds=3600)
        self.result_cache = LRUCache(max_size=500, ttl_seconds=1800)
        self.query_cache = LRUCache(max_size=200, ttl_seconds=900)

    def cache_test_data(self, test_id: str, data: Any) -> None:
        """缓存测试数据"""
        self.test_data_cache.set(f"data_{test_id}", data)

    def get_test_data(self, test_id: str) -> Optional[Any]:
        """获取测试数据"""
        return self.test_data_cache.get(f"data_{test_id}")

    def cache_result(self, test_id: str, result: Any) -> None:
        """缓存测试结果"""
        self.result_cache.set(f"result_{test_id}", result)

    def get_result(self, test_id: str) -> Optional[Any]:
        """获取测试结果"""
        return self.result_cache.get(f"result_{test_id}")

    def cache_query(self, query_key: str, result: Any) -> None:
        """缓存查询结果"""
        self.query_cache.set(query_key, result)

    def get_query(self, query_key: str) -> Optional[Any]:
        """获取查询结果"""
        return self.query_cache.get(query_key)

    def get_all_stats(self) -> Dict[str, Dict]:
        """获取所有缓存统计"""
        return {
            "test_data": self.test_data_cache.get_stats().to_dict(),
            "results": self.result_cache.get_stats().to_dict(),
            "queries": self.query_cache.get_stats().to_dict(),
        }

    def cleanup_all(self) -> Dict[str, int]:
        """清理所有缓存"""
        return {
            "test_data": self.test_data_cache.cleanup_expired(),
            "results": self.result_cache.cleanup_expired(),
            "queries": self.query_cache.cleanup_expired(),
        }

    def clear_all(self):
        """清空所有缓存"""
        self.test_data_cache.clear()
        self.result_cache.clear()
        self.query_cache.clear()


if __name__ == "__main__":
    print("=== Test Cache Strategy Demo ===")

    # 创建缓存策略
    strategy = TestCacheStrategy()

    # 缓存测试数据
    print("\nCaching test data...")
    for i in range(10):
        data = {"id": i, "values": list(range(100)), "name": f"test_{i}"}
        strategy.cache_test_data(str(i), data)

    # 获取测试数据
    print("Retrieving test data...")
    for i in range(10):
        result = strategy.get_test_data(str(i))
        if result:
            print(f"  Hit: test_{i} - {result['name']}")

    # 缓存测试结果
    print("\nCaching results...")
    for i in range(10):
        strategy.cache_result(str(i), {"passed": i % 2 == 0, "time": i * 0.1})

    # 获取结果
    print("Retrieving results...")
    for i in range(10):
        result = strategy.get_result(str(i))
        if result:
            strategy.get_result(str(i))  # 再次获取以增加命中

    # 获取统计
    print("\nCache Statistics:")
    stats = strategy.get_all_stats()
    for cache_name, cache_stats in stats.items():
        print(f"  {cache_name}:")
        for key, value in cache_stats.items():
            print(f"    {key}: {value}")

    # 清理
    print("\nCleaning up expired entries...")
    cleaned = strategy.cleanup_all()
    print(f"  Cleaned: {cleaned}")

    print("\n✅ Cache strategy demo complete!")
