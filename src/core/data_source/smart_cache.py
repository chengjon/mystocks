"""
智能缓存模块 (SmartCache)

实现线程安全的 LRU + TTL 缓存，支持后台预刷新和软过期策略。
"""

import logging
import threading
import time
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class SmartCache:
    """
    智能缓存实现

    特性:
    - LRU 淘汰策略
    - TTL 过期机制
    - 预热刷新 (80% TTL 时触发)
    - 软过期策略 (过期后返回旧数据，同时后台刷新)
    - 线程安全 (使用 RLock)
    - 后台刷新线程池 (限制并发数)
    """

    def __init__(
        self,
        maxsize: int = 100,
        default_ttl: int = 3600,  # 默认 1 小时
        refresh_threshold: float = 0.8,  # 80% TTL 时预刷新
        soft_expiry: bool = True,  # 软过期策略
        max_refresh_workers: int = 5,  # 最大后台刷新线程数
    ):
        """
        初始化智能缓存

        Args:
            maxsize: 最大缓存条目数
            default_ttl: 默认 TTL (秒)
            refresh_threshold: 预刷新阈值 (0.0-1.0)
            soft_expiry: 是否启用软过期
            max_refresh_workers: 最大后台刷新线程数
        """
        self.cache = OrderedDict()
        self.maxsize = maxsize
        self.default_ttl = default_ttl
        self.refresh_threshold = refresh_threshold
        self.soft_expiry = soft_expiry

        # 线程安全
        self.lock = threading.RLock()

        # 后台刷新线程池
        self.refresh_executor = ThreadPoolExecutor(
            max_workers=max_refresh_workers,
            thread_name_prefix="smart_cache_refresh",
        )

        # 正在刷新的 key (防止重复刷新)
        self.refreshing = set()

        # 缓存统计
        self.hits = 0
        self.misses = 0
        self.refreshes = 0
        self.refresh_failures = 0

        logger.info(
            f"SmartCache initialized: maxsize={maxsize}, ttl={default_ttl}s, "
            f"refresh_threshold={refresh_threshold}, soft_expiry={soft_expiry}"
        )

    def get(self, key: Any) -> Optional[Any]:
        """
        获取缓存值

        Args:
            key: 缓存键

        Returns:
            缓存值，如果不存在或已过期则返回 None
        """
        with self.lock:
            if key not in self.cache:
                self.misses += 1
                return None

            entry = self.cache[key]
            current_time = time.time()

            # 检查是否过期
            is_expired = current_time > entry["expires_at"]

            # 检查是否需要预刷新
            needs_refresh = current_time > entry["refresh_at"]

            if is_expired:
                if self.soft_expiry and entry["value"] is not None:
                    # 软过期: 返回旧数据，同时后台刷新
                    logger.debug("Cache key %(key)s expired (soft expiry), returning stale data")
                    self._trigger_refresh(key, entry)
                    self.hits += 1
                    return entry["value"]
                else:
                    # 硬过期: 删除并返回 None
                    del self.cache[key]
                    self.misses += 1
                    return None

            if needs_refresh and key not in self.refreshing:
                # 预刷新: 返回当前数据，同时后台刷新
                logger.debug("Cache key %(key)s needs refresh, triggering background refresh")
                self._trigger_refresh(key, entry)
                self.hits += 1
                return entry["value"]

            # 命中: 返回数据
            self.hits += 1
            self.cache.move_to_end(key)
            return entry["value"]

    def set(
        self,
        key: Any,
        value: Any,
        ttl: Optional[int] = None,
        refresh_func: Optional[Callable] = None,
    ) -> None:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间 (秒)，None 表示使用默认值
            refresh_func: 刷新函数 (用于后台刷新)
        """
        with self.lock:
            current_time = time.time()
            ttl = ttl if ttl is not None else self.default_ttl

            # 计算过期时间和刷新时间
            expires_at = current_time + ttl
            refresh_at = current_time + (ttl * self.refresh_threshold)

            # 如果 key 已存在，保留原有的 refresh_func
            existing_entry = self.cache.get(key)
            if existing_entry and refresh_func is None:
                refresh_func = existing_entry.get("refresh_func")

            entry = {
                "value": value,
                "expires_at": expires_at,
                "refresh_at": refresh_at,
                "created_at": current_time,
                "ttl": ttl,
                "refresh_func": refresh_func,
            }

            # 更新缓存
            self.cache[key] = entry
            self.cache.move_to_end(key)

            # LRU 淘汰
            if len(self.cache) > self.maxsize:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                logger.debug("LRU evicted key: %(oldest_key)s")

            logger.debug("Cache set: key=%(key)s, ttl=%(ttl)ss, expires_at=%(expires_at)s")

    def _trigger_refresh(self, key: Any, entry: dict) -> None:
        """
        触发后台刷新

        Args:
            key: 缓存键
            entry: 缓存条目
        """
        refresh_func = entry.get("refresh_func")
        if not refresh_func:
            logger.debug("No refresh_func for key %(key)s, skipping refresh")
            return

        if key in self.refreshing:
            logger.debug("Key %(key)s is already being refreshed, skipping")
            return

        # 标记为正在刷新
        self.refreshing.add(key)

        # 提交后台刷新任务
        self.refresh_executor.submit(self._run_refresh, key, refresh_func)

    def _run_refresh(self, key: Any, refresh_func: Callable) -> None:
        """
        执行后台刷新

        Args:
            key: 缓存键
            refresh_func: 刷新函数
        """
        try:
            logger.debug("Running background refresh for key %(key)s")
            new_value = refresh_func()

            if new_value is not None:
                # 更新缓存 (保留原有的 TTL 和 refresh_func)
                with self.lock:
                    if key in self.cache:
                        old_entry = self.cache[key]
                        self.set(
                            key,
                            new_value,
                            ttl=old_entry["ttl"],
                            refresh_func=old_entry.get("refresh_func"),
                        )
                        self.refreshes += 1
                        logger.debug("Background refresh successful for key %(key)s")
            else:
                logger.warning("Background refresh returned None for key %(key)s")
                self.refresh_failures += 1

        except Exception as e:
            logger.error("Background refresh failed for key %(key)s: %(e)s")
            self.refresh_failures += 1
        finally:
            # 移除刷新标记
            self.refreshing.discard(key)

    def invalidate(self, key: Any) -> None:
        """
        使缓存失效

        Args:
            key: 缓存键
        """
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                logger.debug("Cache invalidated: key=%(key)s")

    def clear(self) -> None:
        """清空缓存"""
        with self.lock:
            self.cache.clear()
            logger.debug("Cache cleared")

    def cleanup_expired(self) -> int:
        """
        清理过期条目

        Returns:
            清理的条目数
        """
        with self.lock:
            current_time = time.time()
            expired_keys = [key for key, entry in self.cache.items() if current_time > entry["expires_at"]]

            for key in expired_keys:
                del self.cache[key]

            if expired_keys:
                logger.debug("Cleaned up {len(expired_keys)} expired entries")

            return len(expired_keys)

    def get_stats(self) -> dict:
        """
        获取缓存统计信息

        Returns:
            统计信息字典
        """
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = self.hits / total_requests if total_requests > 0 else 0

            return {
                "size": len(self.cache),
                "maxsize": self.maxsize,
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": hit_rate,
                "refreshes": self.refreshes,
                "refresh_failures": self.refresh_failures,
                "refreshing_count": len(self.refreshing),
            }

    def shutdown(self) -> None:
        """关闭缓存，清理后台线程"""
        logger.info("Shutting down SmartCache...")
        self.refresh_executor.shutdown(wait=True)
        logger.info("SmartCache shutdown complete")

    def __len__(self) -> int:
        """返回缓存大小"""
        return len(self.cache)

    def __contains__(self, key: Any) -> bool:
        """检查 key 是否存在"""
        return key in self.cache

    def __del__(self):
        """析构函数，确保线程池关闭"""
        try:
            self.shutdown()
        except Exception:
            pass
