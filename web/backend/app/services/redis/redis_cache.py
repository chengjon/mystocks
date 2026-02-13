"""
Redis L2 Cache Service
=======================

高性能分布式缓存服务 (L2: Redis)

功能:
1. 指标计算结果缓存
2. API响应缓存
3. 数据查询缓存
4. 自动过期和清理

Version: 1.0.0
Author: MyStocks Project
"""

import json
import logging
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.core.redis_client import get_redis_client

logger = logging.getLogger(__name__)


class RedisCacheService:
    """
    Redis缓存服务 (L2分布式缓存)

    三级缓存架构:
    - L1: 应用内存 (LRU Cache)
    - L2: Redis (分布式共享缓存) ← 本服务
    - L3: 磁盘/数据库 (持久化)
    """

    def __init__(self):
        self.redis = get_redis_client()
        self.prefix = settings.redis_cache_prefix
        self.default_ttl = settings.redis_cache_ttl

    def _make_key(self, key: str) -> str:
        """生成带前缀的缓存键"""
        return f"{self.prefix}{key}"

    # ========== 基础缓存操作 ==========

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        设置缓存

        Args:
            key: 缓存键
            value: 缓存值 (自动序列化)
            ttl: 过期时间 (秒)，默认使用配置的default_ttl

        Returns:
            bool: 是否设置成功
        """
        try:
            cache_key = self._make_key(key)
            ttl = ttl or self.default_ttl

            # 自动序列化 (Security: Use JSON only, avoid pickle)
            serialized = json.dumps(value, default=str)

            self.redis.setex(cache_key, ttl, serialized)
            logger.debug("Cache set: %(key)s (TTL: %(ttl)ss)")
            return True

        except Exception:
            logger.error("Failed to set cache %(key)s: %(e)s")
            return False

    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存

        Args:
            key: 缓存键

        Returns:
            缓存值 (自动反序列化)，不存在返回None
        """
        try:
            cache_key = self._make_key(key)
            cached = self.redis.get(cache_key)

            if cached is None:
                return None

            # 尝试JSON反序列化
            try:
                return json.loads(cached)
            except (json.JSONDecodeError, UnicodeDecodeError):
                return cached.decode("utf-8")

        except Exception:
            logger.error("Failed to get cache %(key)s: %(e)s")
            return None

    def delete(self, key: str) -> bool:
        """
        删除缓存

        Args:
            key: 缓存键

        Returns:
            bool: 是否删除成功
        """
        try:
            cache_key = self._make_key(key)
            self.redis.delete(cache_key)
            logger.debug("Cache deleted: %(key)s")
            return True
        except Exception:
            logger.error("Failed to delete cache %(key)s: %(e)s")
            return False

    def exists(self, key: str) -> bool:
        """
        检查缓存是否存在

        Args:
            key: 缓存键

        Returns:
            bool: 缓存是否存在
        """
        try:
            cache_key = self._make_key(key)
            return self.redis.exists(cache_key) > 0
        except Exception:
            logger.error("Failed to check cache %(key)s: %(e)s")
            return False

    def expire(self, key: str, ttl: int) -> bool:
        """
        设置缓存过期时间

        Args:
            key: 缓存键
            ttl: 过期时间 (秒)

        Returns:
            bool: 是否设置成功
        """
        try:
            cache_key = self._make_key(key)
            return self.redis.expire(cache_key, ttl)
        except Exception:
            logger.error("Failed to set expiry for %(key)s: %(e)s")
            return False

    # ========== 批量操作 ==========

    def mget(self, keys: List[str]) -> Dict[str, Any]:
        """
        批量获取缓存

        Args:
            keys: 缓存键列表

        Returns:
            Dict[str, Any]: 键值对字典
        """
        result = {}
        try:
            cache_keys = [self._make_key(k) for k in keys]
            values = self.redis.mget(cache_keys)

            for key, value in zip(keys, values):
                if value is not None:
                    try:
                        result[key] = json.loads(value)
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        result[key] = value.decode("utf-8")

        except Exception:
            logger.error("Failed to mget cache: %(e)s")

        return result

    def mset(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        批量设置缓存

        Args:
            mapping: 键值对字典
            ttl: 统一的过期时间 (秒)

        Returns:
            bool: 是否设置成功
        """
        try:
            ttl = ttl or self.default_ttl
            pipe = self.redis.pipeline()

            for key, value in mapping.items():
                cache_key = self._make_key(key)
                serialized = json.dumps(value, default=str)
                pipe.setex(cache_key, ttl, serialized)

            pipe.execute()
            logger.debug("Batch cache set: {len(mapping)} keys (TTL: %(ttl)ss)")
            return True

        except Exception:
            logger.error("Failed to mset cache: %(e)s")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """
        删除匹配模式的所有缓存

        Args:
            pattern: 键模式 (支持*通配符)

        Returns:
            int: 删除的缓存数量
        """
        try:
            cache_pattern = self._make_key(pattern)
            keys = self.redis.keys(cache_pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except Exception:
            logger.error("Failed to delete pattern %(pattern)s: %(e)s")
            return 0

    # ========== 指标缓存专用方法 ==========

    def cache_indicator_result(
        self, stock_code: str, indicator_code: str, params: Dict[str, Any], result: Dict[str, Any], ttl: int = 3600
    ) -> bool:
        """
        缓存指标计算结果

        Args:
            stock_code: 股票代码
            indicator_code: 指标代码
            params: 计算参数
            result: 计算结果
            ttl: 过期时间 (默认1小时)

        Returns:
            bool: 是否缓存成功
        """
        # 生成唯一键: indicator:{stock_code}:{indicator_code}:{params_hash}
        import hashlib

        params_str = json.dumps(params, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]

        key = f"indicator:{stock_code}:{indicator_code}:{params_hash}"
        return self.set(key, result, ttl)

    def get_cached_indicator_result(
        self, stock_code: str, indicator_code: str, params: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        获取缓存的指标计算结果

        Args:
            stock_code: 股票代码
            indicator_code: 指标代码
            params: 计算参数

        Returns:
            缓存的计算结果，不存在返回None
        """
        import hashlib

        params_str = json.dumps(params, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]

        key = f"indicator:{stock_code}:{indicator_code}:{params_hash}"
        return self.get(key)

    # ========== API响应缓存 ==========

    def cache_api_response(
        self,
        endpoint: str,
        params: Dict[str, Any],
        response: Any,
        ttl: int = 300,  # 默认5分钟
    ) -> bool:
        """
        缓存API响应

        Args:
            endpoint: API端点路径
            params: 请求参数
            response: 响应数据
            ttl: 过期时间 (默认5分钟)

        Returns:
            bool: 是否缓存成功
        """
        import hashlib

        params_str = json.dumps(params, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]

        key = f"api:{endpoint}:{params_hash}"
        return self.set(key, response, ttl)

    def get_cached_api_response(self, endpoint: str, params: Dict[str, Any]) -> Optional[Any]:
        """
        获取缓存的API响应

        Args:
            endpoint: API端点路径
            params: 请求参数

        Returns:
            缓存的响应数据，不存在返回None
        """
        import hashlib

        params_str = json.dumps(params, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]

        key = f"api:{endpoint}:{params_hash}"
        return self.get(key)

    # ========== 统计信息 ==========

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息

        Returns:
            Dict: 包含键数量、内存使用等信息
        """
        try:
            info = self.redis.info("stats")
            return {
                "total_keys": info.get("keyspace", 0),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": info.get("keyspace_hits", 0)
                / max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1),
            }
        except Exception:
            logger.error("Failed to get cache stats: %(e)s")
            return {}


# 全局单例
redis_cache = RedisCacheService()
