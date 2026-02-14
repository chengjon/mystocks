"""缓存管理器子模块"""

import logging
import time
from collections import OrderedDict
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Union

import pandas as pd

logger = logging.getLogger(__name__)


class CacheStatsHealthMixin:
    """缓存统计、内存管理、健康检查"""

    async def is_cache_valid(self, symbol: str, data_type: str, max_age_days: int = 7) -> bool:
        """
        检查三级缓存的有效性

        Args:
            symbol: 股票代码
            data_type: 数据类型
            max_age_days: 最大缓存年龄 (天)

        Returns:
            True 如果缓存有效且未过期，False 否则
        """
        try:
            # 优先检查L1内存缓存
            cache_data = self._get_from_memory_cache(symbol, data_type, "1d")
            if cache_data:
                # 检查时间戳
                if "_cached_at" in cache_data.get("data", {}):
                    cached_at_str = cache_data["data"]["_cached_at"]
                    cached_at = datetime.fromisoformat(cached_at_str)
                    if cached_at.tzinfo is None:
                        cached_at = cached_at.replace(tzinfo=timezone.utc)
                    age = datetime.now(timezone.utc) - cached_at
                    is_valid = age <= timedelta(days=max_age_days)

                    logger.debug(
                        "L1缓存有效性检查",
                        symbol=symbol,
                        data_type=data_type,
                        age_days=age.days,
                        valid=is_valid,
                    )
                    return is_valid
                return True

            # 检查L2 Redis缓存
            if self._redis_available and self.redis_cache:
                cache_key = self.get_cache_key(symbol, data_type, "1d")
                redis_result, found, _ = await self.redis_cache.get(cache_key)
                if found and redis_result:
                    if "_cached_at" in redis_result.get("data", {}):
                        cached_at_str = redis_result["data"]["_cached_at"]
                        cached_at = datetime.fromisoformat(cached_at_str)
                        if cached_at.tzinfo is None:
                            cached_at = cached_at.replace(tzinfo=timezone.utc)
                        age = datetime.now(timezone.utc) - cached_at
                        is_valid = age <= timedelta(days=max_age_days)

                        logger.debug(
                            "L2缓存有效性检查",
                            symbol=symbol,
                            data_type=data_type,
                            age_days=age.days,
                            valid=is_valid,
                        )
                        return is_valid
                    return True

            # 检查L3 TDengine缓存
            if self.tdengine is not None:
                cache_data = await self._write_to_tdengine(
                    symbol=symbol,
                    data_type=data_type,
                    timeframe="1d",
                    data={},  # 读取模式
                    timestamp=None,
                )
                if cache_data and "_cached_at" in cache_data.get("data", {}):
                    cached_at_str = cache_data["data"]["_cached_at"]
                    cached_at = datetime.fromisoformat(cached_at_str)
                    if cached_at.tzinfo is None:
                        cached_at = cached_at.replace(tzinfo=timezone.utc)
                    age = datetime.now(timezone.utc) - cached_at
                    is_valid = age <= timedelta(days=max_age_days)

                    logger.debug(
                        "L3缓存有效性检查",
                        symbol=symbol,
                        data_type=data_type,
                        age_days=age.days,
                        valid=is_valid,
                    )
                    return is_valid

            return False

        except Exception as e:
            logger.error(
                "❌ 三级缓存有效性检查失败",
                symbol=symbol,
                data_type=data_type,
                error=str(e),
            )
            return False

            # 检查时间戳
            if "_cached_at" in cache_data.get("data", {}):
                cached_at_str = cache_data["data"]["_cached_at"]
                cached_at = datetime.fromisoformat(cached_at_str)
                age = datetime.now(timezone.utc) - cached_at
                is_valid = age <= timedelta(days=max_age_days)

                logger.debug(
                    "缓存有效性检查",
                    symbol=symbol,
                    data_type=data_type,
                    age_days=age.days,
                    valid=is_valid,
                )
                return is_valid

            return True

        except Exception as e:
            logger.error(
                "❌ 缓存有效性检查失败",
                symbol=symbol,
                error=str(e),
            )
            return False

    def get_cache_key(self, symbol: str, data_type: str, timeframe: str = "1d") -> str:
        """
        生成缓存键

        Args:
            symbol: 股票代码
            data_type: 数据类型
            timeframe: 时间维度

        Returns:
            缓存键字符串
        """
        return f"{data_type}:{symbol}:{timeframe}".lower()

    # ==================== 统计与监控 ====================

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息 (增强版)

        Returns:
            统计信息字典
        """
        hit_rate = self._calculate_hit_rate()
        avg_response_time = self._cache_stats["total_response_time"] / max(self._cache_stats["reads"], 1)

        stats = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_reads": self._cache_stats["reads"],
            "total_writes": self._cache_stats["writes"],
            "cache_hits": self._cache_stats["hits"],
            "cache_misses": self._cache_stats["misses"],
            "evictions": self._cache_stats["evictions"],
            "batch_operations": self._cache_stats["batch_operations"],
            "hit_rate": hit_rate,
            "hit_rate_percent": f"{hit_rate * 100:.1f}%",
            "avg_response_time_ms": round(avg_response_time * 1000, 2),
            "memory_cache_stats": self.get_memory_cache_stats(),
        }

        # 添加响应时间分布统计
        if "response_time_distribution" in self._cache_stats:
            stats["response_time_distribution"] = self._cache_stats["response_time_distribution"]

        # 从 TDengine 获取额外统计
        try:
            if self.tdengine is not None:
                tdengine_stats = self.tdengine.get_cache_stats()
                if tdengine_stats:
                    stats["tdengine_stats"] = tdengine_stats
        except Exception as e:
            logger.warning("无法获取 TDengine 统计", error=str(e))

        return stats

    def reset_stats(self) -> None:
        """重置统计计数器"""
        self._cache_stats = {
            "hits": 0,
            "misses": 0,
            "reads": 0,
            "writes": 0,
        }
        logger.info("✅ 统计计数器已重置")

    def _calculate_hit_rate(self) -> float:
        """计算缓存命中率"""
        total_reads: int = self._cache_stats["reads"]
        if total_reads == 0:
            return 0.0
        hits: int = self._cache_stats["hits"]
        return float(hits) / float(total_reads)

    # ==================== 内存缓存层 (替代Redis) ====================

    def _get_from_memory_cache(self, symbol: str, data_type: str, timeframe: Optional[str]) -> Optional[Dict[str, Any]]:
        """从内存缓存读取数据"""
        cache_key = self.get_cache_key(symbol, data_type, timeframe or "1d")

        with self._cache_lock:
            if cache_key in self._memory_cache:
                # 检查TTL
                if self._is_cache_expired(cache_key):
                    del self._memory_cache[cache_key]
                    del self._cache_ttl[cache_key]
                    return None

                # 更新访问统计
                self._access_patterns[cache_key].append(datetime.now(timezone.utc))
                result: Optional[Dict[str, Any]] = self._memory_cache[cache_key]
                return result

        return None

    def _add_to_memory_cache(
        self,
        symbol: str,
        data_type: str,
        timeframe: str,
        data: Dict[str, Any],
    ) -> None:
        """写入数据到内存缓存"""
        cache_key = self.get_cache_key(symbol, data_type, timeframe)

        with self._cache_lock:
            # 检查缓存大小限制
            if len(self._memory_cache) >= self._max_memory_entries:
                self._evict_memory_cache()

            # 计算TTL
            ttl_seconds = self._get_tiered_ttl(data_type)

            self._memory_cache[cache_key] = data
            self._cache_ttl[cache_key] = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
            self._access_patterns[cache_key].append(datetime.now(timezone.utc))

    def _is_cache_expired(self, cache_key: str) -> bool:
        """检查缓存是否过期"""
        if cache_key not in self._cache_ttl:
            return True

        return datetime.now(timezone.utc) > self._cache_ttl[cache_key]

    def _get_tiered_ttl(self, data_type: str) -> int:
        """获取分层TTL"""
        return self._tiered_ttl.get(data_type, self._tiered_ttl["default"])

    def _evict_memory_cache(self) -> None:
        """内存缓存淘汰策略 (LRU + 基于访问频率)"""
        if not self._memory_cache:
            return

        # 简单LRU策略：删除访问频率最低的条目
        lru_key = None
        min_access = float("inf")

        for key, access_times in self._access_patterns.items():
            access_freq = len(access_times)
            if access_freq < min_access:
                min_access = access_freq
                lru_key = key

        if lru_key and lru_key in self._memory_cache:
            del self._memory_cache[lru_key]
            del self._cache_ttl[lru_key]
            del self._access_patterns[lru_key]
            self._cache_stats["evictions"] += 1

    def _record_access_pattern(self, symbol: str, data_type: str) -> None:
        """记录访问模式"""
        cache_key = self.get_cache_key(symbol, data_type)
        with self._cache_lock:
            self._access_patterns[cache_key].append(datetime.now(timezone.utc))

    async def _write_to_tdengine(
        self,
        symbol: str,
        data_type: str,
        timeframe: str,
        data: Dict[str, Any],
        timestamp: Optional[datetime] = None,
    ) -> bool:
        """异步写入TDengine"""
        try:
            # 使用线程池执行TDengine写入，避免阻塞
            tdengine = self.tdengine
            if tdengine is None:
                return False

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: tdengine.write_cache(
                    symbol=symbol,
                    data_type=data_type,
                    timeframe=timeframe,
                    data=data,
                    timestamp=timestamp,
                ),
            )
            return result
        except Exception:
            logger.warning("TDengine异步写入失败: %(e)s")
            return False

    def _update_performance_stats(self, response_time: float, hit: bool) -> None:
        """更新性能统计"""
        self._cache_stats["total_response_time"] += response_time

        # 记录响应时间分布
        if hit:
            cache_level = "memory" if response_time < 0.001 else "tdengine"
        else:
            cache_level = "miss"

        if "response_time_distribution" not in self._cache_stats:
            self._cache_stats["response_time_distribution"] = {}

        response_time_dist: Dict[str, int] = self._cache_stats["response_time_distribution"]
        response_time_dist[cache_level] = response_time_dist.get(cache_level, 0) + 1

    def get_memory_cache_stats(self) -> Dict[str, Any]:
        """获取内存缓存统计"""
        with self._cache_lock:
            total_entries = len(self._memory_cache)
            total_size_mb = sum(len(str(data)) for data in self._memory_cache.values()) / (1024 * 1024)  # 估算大小

            # 计算各数据类型的分布
            type_distribution: defaultdict[str, int] = defaultdict(int)
            for cache_key in self._memory_cache.keys():
                parts = cache_key.split(":")
                if len(parts) >= 2:
                    data_type = parts[0]
                    type_distribution[data_type] += 1

            return {
                "total_entries": total_entries,
                "max_entries": self._max_memory_entries,
                "usage_percentage": (total_entries / self._max_memory_entries) * 100,
                "estimated_size_mb": round(total_size_mb, 2),
                "type_distribution": dict(type_distribution),
                "evictions": self._cache_stats["evictions"],
                "default_ttl_seconds": self._default_ttl,
                "tiered_ttl": self._tiered_ttl,
            }

    def clear_memory_cache(self) -> int:
        """清空内存缓存"""
        with self._cache_lock:
            count = len(self._memory_cache)
            self._memory_cache.clear()
            self._cache_ttl.clear()
            self._access_patterns.clear()
            return count

    # ==================== 三级缓存辅助方法 ====================

    async def _async_tdengine_clear(self, symbol: str, data_type: str) -> None:
        """异步清理TDengine特定缓存"""
        try:
            if self.tdengine is not None:
                # 这里需要实现TDengine的精确删除方法
                # 暂时使用clear_expired_cache作为替代
                await asyncio.get_event_loop().run_in_executor(None, lambda: self.tdengine.clear_expired_cache(days=0))
                logger.info("🗑️ L3 TDengine缓存清理完成", symbol=symbol, data_type=data_type)
        except Exception as e:
            logger.warning("L3 TDengine缓存清理失败", symbol=symbol, data_type=data_type, error=str(e))

    async def _async_tdengine_clear_symbol(self, symbol: str) -> None:
        """异步清理TDengine特定符号的所有缓存"""
        try:
            if self.tdengine is not None:
                await asyncio.get_event_loop().run_in_executor(None, lambda: self.tdengine.clear_expired_cache(days=0))
                logger.info("🗑️ L3 TDengine符号缓存清理完成", symbol=symbol)
        except Exception as e:
            logger.warning("L3 TDengine符号缓存清理失败", symbol=symbol, error=str(e))

    async def _async_tdengine_clear_all(self) -> None:
        """异步清理所有TDengine缓存"""
        try:
            if self.tdengine is not None:
                await asyncio.get_event_loop().run_in_executor(None, lambda: self.tdengine.clear_expired_cache(days=0))
                logger.warning("🗑️ L3 TDengine全部缓存清理完成")
        except Exception as e:
            logger.warning("L3 TDengine全部缓存清理失败", error=str(e))

    def optimize_memory_cache(self) -> Dict[str, Any]:
        """优化内存缓存"""
        with self._cache_lock:
            # 清理过期条目
            expired_count = 0
            now = datetime.now(timezone.utc)

            expired_keys = [key for key, expire_time in self._cache_ttl.items() if now > expire_time]

            for key in expired_keys:
                if key in self._memory_cache:
                    del self._memory_cache[key]
                del self._cache_ttl[key]
                if key in self._access_patterns:
                    del self._access_patterns[key]
                expired_count += 1

            # 记录优化结果
            stats_before = self.get_memory_cache_stats()

            return {
                "expired_entries_removed": expired_count,
                "entries_after_cleanup": len(self._memory_cache),
                "cache_usage_after": stats_before["usage_percentage"],
                "memory_freed_mb": 0,  # 简化实现
            }

    # ==================== 生命周期 ====================

    def health_check(self) -> Dict[str, Any]:
        """
        健康检查 (增强版)

        Returns:
            健康状态字典
        """
        health_status: Dict[str, Any] = {
            "overall_healthy": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "components": {},
            "performance_metrics": {},
            "issues": [],
        }

        try:
            # 检查 TDengine 连接
            tdengine_healthy = self.tdengine.health_check() if self.tdengine is not None else False
            components: Dict[str, Any] = health_status["components"]
            components["tdengine"] = {
                "healthy": tdengine_healthy,
                "status": "OK" if tdengine_healthy else "ERROR",
            }

            if not tdengine_healthy:
                health_status["overall_healthy"] = False
                health_status["issues"].append("TDengine connection failed")

            # 检查内存缓存
            memory_stats = self.get_memory_cache_stats()
            memory_healthy = (
                memory_stats["usage_percentage"] < 95 and len(self._memory_cache) < self._max_memory_entries
            )

            components["memory_cache"] = {
                "healthy": memory_healthy,
                "status": "OK" if memory_healthy else "WARNING",
                "usage_percentage": memory_stats["usage_percentage"],
                "total_entries": memory_stats["total_entries"],
            }

            if not memory_healthy:
                issues: List[str] = health_status["issues"]
                issues.append("Memory cache usage high")

            # 性能指标
            hit_rate = self._calculate_hit_rate()
            avg_response_time = self._cache_stats["total_response_time"] / max(self._cache_stats["reads"], 1)

            performance_healthy = hit_rate > 0.5 and avg_response_time < 1.0  # 命中率应该大于50%  # 平均响应时间小于1秒

            performance_metrics: Dict[str, Any] = {
                "hit_rate": hit_rate,
                "avg_response_time_ms": round(avg_response_time * 1000, 2),
                "performance_healthy": performance_healthy,
            }
            health_status["performance_metrics"] = performance_metrics

            if not performance_healthy:
                health_status["overall_healthy"] = False
                issues = health_status["issues"]
                if hit_rate < 0.5:
                    issues.append("Cache hit rate too low")
                if avg_response_time > 1.0:
                    issues.append("Response time too slow")

            logger.info(
                "🔍 缓存系统健康检查完成",
                overall_healthy=health_status["overall_healthy"],
                issues=len(health_status.get("issues", [])),
            )

            return health_status

        except Exception as e:
            logger.error("❌ 缓存系统健康检查失败", error=str(e))
            health_status["overall_healthy"] = False
            error_issues: List[str] = health_status["issues"]
            error_issues.append(f"Health check error: {str(e)}")
            return health_status

    def close(self) -> None:
        """关闭缓存管理器"""
        try:
            if self.tdengine is not None:
                self.tdengine.close()
            logger.info("✅ 缓存管理器已关闭")
        except Exception as e:
            logger.warning("关闭缓存管理器时出错", error=str(e))


# ==================== 全局单例管理 ====================

_cache_manager: Optional['CacheManager'] = None
REDIS_CACHE_AVAILABLE = False


async def get_cache_manager_async(
    tdengine_manager: Optional[Any] = None,
    redis_cache: Optional[Any] = None,
) -> 'CacheManager':
    """
    获取异步缓存管理器单例 (支持Redis注入)

    Args:
        tdengine_manager: TDengineManager 实例
        redis_cache: Redis多级缓存服务实例

    Returns:
        CacheManager 单例实例
    """
    global _cache_manager

    if _cache_manager is None:
        _cache_manager = CacheManager(tdengine_manager, redis_cache)

        # 如果提供了Redis缓存，初始化连接
        if redis_cache and REDIS_CACHE_AVAILABLE:
            try:
                # Redis缓存已在外部初始化，这里只需要验证
                if not hasattr(redis_cache, "_redis_connected") or not redis_cache._redis_connected:
                    await redis_cache.initialize()
                _cache_manager._redis_available = True
                logger.info("✅ Redis缓存服务已注入到缓存管理器")
            except Exception as e:
                logger.warning("⚠️ Redis缓存初始化失败，将降级为L1+L3模式", error=str(e))
                _cache_manager._redis_available = False

        # 执行健康检查
        try:
            health = _cache_manager.health_check()
            if not health.get("overall_healthy"):
                logger.warning("⚠️ 缓存管理器健康检查失败", issues=health.get("issues", []))
        except Exception as e:
            logger.warning("⚠️ 缓存管理器健康检查异常", error=str(e))

    return _cache_manager


