"""
缓存服务模块

提供内存缓存、Redis缓存、分布式缓存、缓存失效策略等功能
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum

logger = __import__("logging").getLogger(__name__)


class CacheType(Enum):
    """缓存类型"""

    MEMORY = "memory"
    REDIS = "redis"
    DISTRIBUTED = "distributed"
    HYBRID = "hybrid"


class CacheStrategy(Enum):
    """缓存策略"""

    LRU = "lru"
    TTL = "ttl"
    LFU = "lfu"
    NO_EVICTION = "no_eviction"
    WRITE_BACK = "write_back"
    WRITE_THROUGH = "write_through"


class CacheEntry:
    """缓存条目数据类"""

    key: str = ""
    value: Any = None
    data_type: str = ""
    created_at: Optional[datetime] = None
    last_accessed_at: Optional[datetime] = None
    access_count: int = 0
    size_bytes: int = 0
    ttl_seconds: int = 0

    def to_dict(self) -> Dict:
        return {
            "key": self.key,
            "data_type": self.data_type,
            "value": self.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_accessed_at": self.last_accessed_at.isoformat() if self.last_accessed_at else None,
            "access_count": self.access_count,
            "size_bytes": self.size_bytes,
            "ttl_seconds": self.ttl_seconds,
            "is_expired": (datetime.now() - self.last_accessed_at).total_seconds() > self.ttl_seconds
            if self.last_accessed_at
            else False,
        }


class CacheStats:
    """缓存统计数据类"""

    total_entries: int = 0
    total_hits: int = 0
    total_misses: int = 0
    total_evictions: int = 0
    hit_rate: float = 0.0
    miss_rate: float = 0.0
    eviction_rate: float = 0.0
    cache_size_bytes: int = 0
    cache_size_mb: float = 0.0
    average_ttl_seconds: float = 0.0
    generated_at: Optional[datetime] = None

    def to_dict(self) -> Dict:
        return {
            "total_entries": self.total_entries,
            "total_hits": self.total_hits,
            "total_misses": self.total_misses,
            "total_evictions": self.total_evictions,
            "hit_rate": f"{self.hit_rate:.2f}%",
            "miss_rate": f"{self.miss_rate:.2f}%",
            "eviction_rate": f"{self.eviction_rate:.2f}%",
            "cache_size_bytes": self.cache_size_bytes,
            "cache_size_mb": f"{self.cache_size_mb:.2f}",
            "average_ttl_seconds": f"{self.average_ttl_seconds:.2f}",
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
        }


class CacheService:
    """缓存服务"""

    def __init__(self, cache_type: CacheType = CacheType.MEMORY, redis_host: str = "localhost", redis_port: int = 6379):
        self.logger = logging.getLogger(__name__)
        self.cache_type = cache_type
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = 0
        self.memory_cache = {}  # key -> CacheEntry
        self.redis_pool = None
        self.max_cache_size = 10000
        self.default_ttl = 300
        self.max_entries = 10000

        self.stats = CacheStats()
        self.is_redis_connected = False

        logger.info(f"缓存服务初始化 (类型: {cache_type.value})")

    async def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值

        Args:
            key: 缓存键

        Returns:
            Any: 缓存值，未找到返回None
        """
        try:
            self._log_request_start("cache_get", {"key": key})

            if self.cache_type == CacheType.MEMORY:
                return self._get_memory_cache(key)
            elif self.cache_type == CacheType.REDIS:
                return await self._get_redis_cache(key)
            elif self.cache_type == CacheType.DISTRIBUTED:
                return await self._get_distributed_cache(key)
            else:
                self.logger.warning(f"不支持的缓存类型: {self.cache_type.value}")
                return None

        except Exception as e:
            self._log_request_error("cache_get", e)
            return None

    async def set(self, key: str, value: Any, ttl: int = None, data_type: str = "default") -> bool:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒）
            data_type: 数据类型

        Returns:
            bool: 是否设置成功
        """
        try:
            self._log_request_start("cache_set", {"key": key, "ttl": ttl, "data_type": data_type})

            if self.cache_type == CacheType.MEMORY:
                success = self._set_memory_cache(key, value, ttl, data_type)
            elif self.cache_type == CacheType.REDIS:
                success = await self._set_redis_cache(key, value, ttl, data_type)
            elif self.cache_type == CacheType.DISTRIBUTED:
                success = await self._set_distributed_cache(key, value, ttl, data_type)
            else:
                self.logger.warning(f"不支持的缓存类型: {self.cache_type.value}")
                return False

            if success:
                self._log_request_success("cache_set", {"key": key})

            return success

        except Exception as e:
            self._log_request_error("cache_set", e)
            return False

    async def delete(self, key: str) -> bool:
        """
        删除缓存值

        Args:
            key: 缓存键

        Returns:
            bool: 是否删除成功
        """
        try:
            self._log_request_start("cache_delete", {"key": key})

            if self.cache_type == CacheType.MEMORY:
                success = self._delete_memory_cache(key)
            elif self.cache_type == CacheType.REDIS:
                success = await self._delete_redis_cache(key)
            elif self.cache_type == CacheType.DISTRIBUTED:
                success = await self._delete_distributed_cache(key)
            else:
                self.logger.warning(f"不支持的缓存类型: {self.cache_type.value}")
                return False

            if success:
                self._log_request_success("cache_delete", {"key": key})

            return success

        except Exception as e:
            self._log_request_error("cache_delete", e)
            return False

    async def clear(self) -> bool:
        """
        清空所有缓存

        Returns:
            bool: 是否清空成功
        """
        try:
            self._log_request_start("cache_clear", {})

            if self.cache_type == CacheType.MEMORY:
                success = self._clear_memory_cache()
            elif self.cache_type == CacheType.REDIS:
                success = await self._clear_redis_cache()
            elif self.cache_type == CacheType.DISTRIBUTED:
                success = await self._clear_distributed_cache()
            else:
                self.logger.warning(f"不支持的缓存类型: {self.cache_type.value}")
                return False

            if success:
                self._log_request_success("cache_clear", {})
                self.stats.generated_at = datetime.now()

            return success

        except Exception as e:
            self._log_request_error("cache_clear", e)
            return False

    def _get_memory_cache(self, key: str) -> Optional[Any]:
        """获取内存缓存"""
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            entry.last_accessed_at = datetime.now()
            entry.access_count += 1
            self.stats.total_hits += 1
            self.logger.debug(f"命中内存缓存: {key}")
            return entry.value
        return None

    def _set_memory_cache(self, key: str, value: Any, ttl: int = None, data_type: str = "default") -> bool:
        """设置内存缓存"""
        try:
            entry = CacheEntry(
                key=key,
                value=value,
                data_type=data_type,
                created_at=datetime.now(),
                last_accessed_at=datetime.now(),
                access_count=0,
                ttl_seconds=ttl if ttl else self.default_ttl,
            )

            # 计算缓存大小
            import sys

            entry.size_bytes = sys.getsizeof(value)

            # 检查缓存大小
            if len(self.memory_cache) >= self.max_entries:
                self._evict_lru_entry()

            self.memory_cache[key] = entry
            self.stats.total_entries = len(self.memory_cache)
            self.stats.cache_size_bytes = sum(e.size_bytes for e in self.memory_cache.values())
            self.stats.cache_size_mb = self.stats.cache_size_bytes / (1024 * 1024)

            self.logger.debug(f"设置内存缓存: {key}")
            return True

        except Exception as e:
            self.logger.error(f"设置内存缓存失败: {key}: {e}")
            return False

    def _delete_memory_cache(self, key: str) -> bool:
        """删除内存缓存"""
        if key in self.memory_cache:
            del self.memory_cache[key]
            self.logger.debug(f"删除内存缓存: {key}")
            return True
        return False

    def _clear_memory_cache(self) -> bool:
        """清空内存缓存"""
        try:
            self.memory_cache.clear()
            self.stats.total_entries = 0
            self.stats.total_hits = 0
            self.stats.total_misses = 0
            self.stats.total_evictions = 0
            self.stats.cache_size_bytes = 0
            self.stats.cache_size_mb = 0.0

            self.logger.info("内存缓存已清空")
            return True

        except Exception as e:
            self.logger.error(f"清空内存缓存失败: {e}")
            return False

    def _evict_lru_entry(self):
        """淘汰最近最少使用的缓存条目"""
        try:
            if not self.memory_cache:
                return

            # 找到最少访问的条目
            lru_key = min(self.memory_cache.keys(), key=lambda k: self.memory_cache[k].access_count)

            del self.memory_cache[lru_key]
            self.stats.total_evictions += 1

            self.logger.debug(f"淘汰LRU缓存: {lru_key}")

        except Exception as e:
            self.logger.error(f"淘汰LRU缓存失败: {e}")

    async def _get_redis_cache(self, key: str) -> Optional[Any]:
        """获取Redis缓存"""
        try:
            if not self.is_redis_connected:
                await self._connect_redis()


            value = await self.redis_pool.get(key)

            if value:
                self.stats.total_hits += 1
                self.logger.debug(f"命中Redis缓存: {key}")
                return value.decode("utf-8")

            self.stats.total_misses += 1
            self.logger.debug(f"Redis缓存未命中: {key}")
            return None

        except Exception as e:
            self.logger.error(f"获取Redis缓存失败: {key}: {e}")
            return None

    async def _set_redis_cache(self, key: str, value: Any, ttl: int = None, data_type: str = "default") -> bool:
        """设置Redis缓存"""
        try:
            if not self.is_redis_connected:
                await self._connect_redis()


            serialized_value = str(value).encode("utf-8")

            if ttl:
                await self.redis_pool.setex(key, serialized_value, ex=ttl)
            else:
                await self.redis_pool.set(key, serialized_value)

            # 计算缓存大小
            entry_size = len(serialized_value)

            # 检查缓存大小
            if len(await self.redis_pool.dbsize()) > self.max_cache_size:
                await self._evict_random_redis_key()

            self.logger.debug(f"设置Redis缓存: {key}")
            return True

        except Exception as e:
            self.logger.error(f"设置Redis缓存失败: {key}: {e}")
            return False

    async def _delete_redis_cache(self, key: str) -> bool:
        """删除Redis缓存"""
        try:
            if not self.is_redis_connected:
                await self._connect_redis()


            await self.redis_pool.delete(key)

            self.logger.debug(f"删除Redis缓存: {key}")
            return True

        except Exception as e:
            self.logger.error(f"删除Redis缓存失败: {key}: {e}")
            return False

    async def _clear_redis_cache(self) -> bool:
        """清空Redis缓存"""
        try:
            if not self.is_redis_connected:
                await self._connect_redis()


            await self.redis_pool.flushdb()

            self.logger.info("Redis缓存已清空")
            return True

        except Exception as e:
            self.logger.error(f"清空Redis缓存失败: {e}")
            return False

    async def _connect_redis(self):
        """连接Redis"""
        try:
            import redis.asyncio as redis

            self.redis_pool = await redis.create_pool(
                host=self.redis_host, port=self.redis_port, db=self.redis_db, max_connections=10
            )

            self.is_redis_connected = True
            self.logger.info("Redis连接已建立")

        except Exception as e:
            self.logger.error(f"Redis连接失败: {e}")
            raise

    async def _evict_random_redis_key(self):
        """淘汰随机的Redis键"""
        try:

            keys = await self.redis_pool.keys("*")

            if keys:
                random_key = keys[len(keys) // 2]
                await self.redis_pool.delete(random_key)
                self.stats.total_evictions += 1

                self.logger.debug(f"淘汰Redis缓存: {random_key}")

        except Exception as e:
            self.logger.error(f"淘汰Redis缓存失败: {e}")

    async def _get_distributed_cache(self, key: str) -> Optional[Any]:
        """获取分布式缓存（预留）"""
        self.logger.warning("分布式缓存暂未实现")
        return None

    async def _set_distributed_cache(self, key: str, value: Any, ttl: int = None, data_type: str = "default") -> bool:
        """设置分布式缓存（预留）"""
        self.logger.warning("设置分布式缓存暂未实现")
        return False

    async def _delete_distributed_cache(self, key: str) -> bool:
        """删除分布式缓存（预留）"""
        self.logger.warning("删除分布式缓存暂未实现")
        return False

    async def _clear_distributed_cache(self) -> bool:
        """清空分布式缓存（预留）"""
        self.logger.warning("清空分布式缓存暂未实现")
        return False

    async def warm_up_cache(self, keys: List[str]) -> Dict:
        """
        预热缓存

        Args:
            keys: 需要预热的缓存键列表

        Returns:
            Dict: 预热结果
        """
        try:
            self._log_request_start("warm_up_cache", {"keys": len(keys)})

            warm_count = 0
            for key in keys:
                value = await self.get(key)
                if value:
                    warm_count += 1

            result = {"keys": keys, "warmed_keys": warm_count, "generated_at": datetime.now().isoformat()}

            self._log_request_success("warm_up_cache", result)
            return result

        except Exception as e:
            self._log_request_error("warm_up_cache", e)
            return {}

    async def get_stats(self) -> Dict:
        """
        获取缓存统计

        Returns:
            Dict: 缓存统计数据
        """
        try:
            # 计算命中率
            total_requests = self.stats.total_hits + self.stats.total_misses
            hit_rate = (self.stats.total_hits / total_requests * 100) if total_requests > 0 else 0

            # 计算淘汰率
            eviction_rate = (
                (self.stats.total_evictions / self.stats.total_entries * 100) if self.stats.total_entries > 0 else 0
            )

            # 计算平均TTL
            ttl_seconds_list = [entry.ttl_seconds for entry in self.memory_cache.values()]
            average_ttl = sum(ttl_seconds_list) / len(ttl_seconds_list) if ttl_seconds_list else 0

            # 更新统计数据
            self.stats.hit_rate = hit_rate
            self.stats.miss_rate = 100 - hit_rate
            self.stats.eviction_rate = eviction_rate
            self.stats.average_ttl_seconds = average_ttl
            self.stats.generated_at = datetime.now()

            return self.stats.to_dict()

        except Exception as e:
            self.logger.error(f"获取缓存统计失败: {e}")
            return {}

    def _log_request_start(self, method: str, params: Dict):
        """记录请求开始"""
        self.logger.info(f"开始{method}: {params}")

    def _log_request_success(self, method: str, result: Dict):
        """记录请求成功"""
        self.logger.info(f"{method}成功: {result}")

    def _log_request_error(self, method: str, error: Exception):
        """记录请求错误"""
        self.logger.error(f"{method}失败: {error}")
