from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from threading import RLock
from typing import Any

logger = logging.getLogger(__name__)

_manager: CacheManager | None = None
_async_manager: AsyncCacheManager | None = None


def _safe_get_tdengine_manager() -> Any | None:
    try:
        from app.core.tdengine_manager import get_tdengine_manager

        return get_tdengine_manager()
    except Exception as error:
        logger.warning("Failed to initialize TDengine manager for cache manager: %s", error)
        return None


class CacheManager:
    """Sync compatibility cache manager used by most backend routes and tests."""

    def __init__(self, tdengine_manager: Any | None = None) -> None:
        self.tdengine = tdengine_manager if tdengine_manager is not None else _safe_get_tdengine_manager()
        self._lock = RLock()
        self._memory_cache: dict[str, dict[str, Any]] = {}
        self._cache_ttl: dict[str, datetime] = {}
        self._access_patterns: defaultdict[str, list[datetime]] = defaultdict(list)
        self._max_memory_entries = 10000
        self._tiered_ttl = {
            "tick_data": 30,
            "realtime_quote": 60,
            "minute_kline": 300,
            "fund_flow": 600,
            "etf": 1800,
            "dashboard": 3600,
            "default": 300,
        }
        self.reset_stats()

    def reset_stats(self) -> None:
        self._cache_stats = {
            "hits": 0,
            "misses": 0,
            "reads": 0,
            "writes": 0,
            "evictions": 0,
            "batch_operations": 0,
            "total_response_time": 0.0,
        }

    def get_cache_key(self, symbol: str, data_type: str, timeframe: str = "1d") -> str:
        return f"{data_type}:{symbol}:{timeframe}".lower()

    def _calculate_hit_rate(self) -> float:
        total_reads = self._cache_stats["reads"]
        if total_reads == 0:
            return 0.0
        return float(self._cache_stats["hits"]) / float(total_reads)

    def _get_tiered_ttl(self, data_type: str) -> int:
        return int(self._tiered_ttl.get(data_type.lower(), self._tiered_ttl["default"]))

    def _record_access_pattern(self, symbol: str, data_type: str) -> None:
        cache_prefix = f"{data_type}:{symbol}".lower()
        self._access_patterns[cache_prefix].append(datetime.now(timezone.utc))

    def _evict_memory_cache(self) -> None:
        if not self._memory_cache:
            return

        oldest_key = min(
            self._memory_cache.keys(),
            key=lambda key: self._cache_ttl.get(key, datetime.min.replace(tzinfo=timezone.utc)),
        )
        self._memory_cache.pop(oldest_key, None)
        self._cache_ttl.pop(oldest_key, None)
        self._cache_stats["evictions"] += 1

    def _is_cache_expired(self, cache_key: str) -> bool:
        expiry = self._cache_ttl.get(cache_key)
        if expiry is None:
            return True
        return datetime.now(timezone.utc) > expiry

    def _add_to_memory_cache(
        self,
        symbol: str,
        data_type: str,
        timeframe: str,
        cached_entry: dict[str, Any],
        ttl_seconds: int,
    ) -> None:
        cache_key = self.get_cache_key(symbol, data_type, timeframe)
        with self._lock:
            if len(self._memory_cache) >= self._max_memory_entries:
                self._evict_memory_cache()
            self._memory_cache[cache_key] = cached_entry
            self._cache_ttl[cache_key] = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)

    def _get_from_memory_cache(
        self,
        symbol: str,
        data_type: str,
        timeframe: str,
    ) -> dict[str, Any] | None:
        cache_key = self.get_cache_key(symbol, data_type, timeframe)
        with self._lock:
            if cache_key not in self._memory_cache:
                return None
            if self._is_cache_expired(cache_key):
                self._memory_cache.pop(cache_key, None)
                self._cache_ttl.pop(cache_key, None)
                return None
            return self._memory_cache[cache_key]

    def clear_memory_cache(self) -> int:
        with self._lock:
            deleted_count = len(self._memory_cache)
            self._memory_cache.clear()
            self._cache_ttl.clear()
            self._access_patterns.clear()
        return deleted_count

    def get_memory_cache_stats(self) -> dict[str, Any]:
        total_entries = len(self._memory_cache)
        usage_percentage = 0.0
        if self._max_memory_entries:
            usage_percentage = round((total_entries / self._max_memory_entries) * 100, 2)
        return {
            "total_entries": total_entries,
            "max_entries": self._max_memory_entries,
            "usage_percentage": usage_percentage,
        }

    def health_check(self) -> bool:
        if self.tdengine is None:
            return False
        health_check = getattr(self.tdengine, "health_check", None)
        if not callable(health_check):
            return False
        try:
            return bool(health_check())
        except Exception as error:
            logger.warning("Cache manager TDengine health check failed: %s", error)
            return False

    def fetch_from_cache(
        self,
        symbol: str,
        data_type: str,
        timeframe: str | None = None,
        days: int = 1,
    ) -> dict[str, Any] | None:
        start_time = datetime.now(timezone.utc)
        resolved_timeframe = timeframe or "1d"
        self._cache_stats["reads"] += 1

        cached_entry = self._get_from_memory_cache(symbol, data_type, resolved_timeframe)
        if cached_entry is not None:
            self._cache_stats["hits"] += 1
            self._record_access_pattern(symbol, data_type)
            self._cache_stats["total_response_time"] += (
                datetime.now(timezone.utc) - start_time
            ).total_seconds()
            return cached_entry

        tdengine_result = None
        read_cache = getattr(self.tdengine, "read_cache", None)
        if callable(read_cache):
            try:
                tdengine_result = read_cache(
                    symbol=symbol,
                    data_type=data_type,
                    timeframe=resolved_timeframe,
                    days=days,
                )
            except Exception as error:
                logger.warning("Failed to read cache from TDengine: %s", error)

        if isinstance(tdengine_result, dict):
            now = datetime.now(timezone.utc)
            cached_entry = {
                "data": tdengine_result,
                "source": "cache",
                "timestamp": now.isoformat(),
            }
            self._add_to_memory_cache(
                symbol=symbol,
                data_type=data_type,
                timeframe=resolved_timeframe,
                cached_entry=cached_entry,
                ttl_seconds=self._get_tiered_ttl(data_type),
            )
            self._cache_stats["hits"] += 1
            self._cache_stats["total_response_time"] += (
                datetime.now(timezone.utc) - start_time
            ).total_seconds()
            return cached_entry

        self._cache_stats["misses"] += 1
        self._cache_stats["total_response_time"] += (
            datetime.now(timezone.utc) - start_time
        ).total_seconds()
        return None

    def write_to_cache(
        self,
        symbol: str,
        data_type: str,
        timeframe: str,
        data: dict[str, Any] | None,
        ttl_days: int = 7,
        timestamp: datetime | None = None,
    ) -> bool:
        if data is None or not isinstance(data, dict):
            return False

        self._cache_stats["writes"] += 1
        now = timestamp or datetime.now(timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        enriched_data = dict(data)
        enriched_data.setdefault("_cached_at", now.isoformat())
        enriched_data.setdefault("_ttl_days", ttl_days)
        enriched_data.setdefault("_cache_version", "sync-compat")

        cached_entry = {
            "data": enriched_data,
            "source": "cache",
            "timestamp": now.isoformat(),
        }
        self._add_to_memory_cache(
            symbol=symbol,
            data_type=data_type,
            timeframe=timeframe,
            cached_entry=cached_entry,
            ttl_seconds=max(ttl_days * 24 * 3600, self._get_tiered_ttl(data_type)),
        )

        write_cache = getattr(self.tdengine, "write_cache", None)
        if callable(write_cache):
            try:
                write_cache(
                    symbol=symbol,
                    data_type=data_type,
                    timeframe=timeframe,
                    data=enriched_data,
                    timestamp=now,
                )
            except Exception as error:
                logger.warning("Failed to write cache to TDengine: %s", error)

        return True

    def batch_write(self, records: list[dict[str, Any]], ttl_days: int = 7) -> int:
        self._cache_stats["batch_operations"] += 1
        success_count = 0
        for record in records:
            symbol = record.get("symbol")
            data_type = record.get("data_type")
            timeframe = record.get("timeframe", "1d")
            data = record.get("data")
            if not symbol or not data_type:
                continue
            if self.write_to_cache(symbol=symbol, data_type=data_type, timeframe=timeframe, data=data, ttl_days=ttl_days):
                success_count += 1
        return success_count

    def batch_read(self, queries: list[dict[str, Any]]) -> dict[str, Any]:
        self._cache_stats["batch_operations"] += 1
        results: dict[str, Any] = {}
        for query in queries:
            symbol = query.get("symbol")
            data_type = query.get("data_type")
            timeframe = query.get("timeframe", "1d")
            if not symbol or not data_type:
                continue
            result_key = f"{symbol}:{data_type}"
            results[result_key] = self.fetch_from_cache(
                symbol=symbol,
                data_type=data_type,
                timeframe=timeframe,
                days=int(query.get("days", 1)),
            )
        return results

    def invalidate_cache(
        self,
        symbol: str | None = None,
        data_type: str | None = None,
    ) -> int:
        with self._lock:
            if symbol is None and data_type is None:
                return self.clear_memory_cache()

            keys_to_delete = []
            for cache_key in self._memory_cache:
                parts = cache_key.split(":")
                if len(parts) != 3:
                    continue
                current_type, current_symbol, _ = parts
                if symbol is not None and current_symbol != symbol.lower():
                    continue
                if data_type is not None and current_type != data_type.lower():
                    continue
                keys_to_delete.append(cache_key)

            for cache_key in keys_to_delete:
                self._memory_cache.pop(cache_key, None)
                self._cache_ttl.pop(cache_key, None)

            return len(keys_to_delete)

    def is_cache_valid(self, symbol: str, data_type: str, max_age_days: int = 7) -> bool:
        cached_entry = self.fetch_from_cache(symbol=symbol, data_type=data_type)
        if cached_entry is None:
            return False

        cached_at = cached_entry.get("data", {}).get("_cached_at")
        if not cached_at:
            return True

        cached_dt = datetime.fromisoformat(cached_at)
        if cached_dt.tzinfo is None:
            cached_dt = cached_dt.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) - cached_dt <= timedelta(days=max_age_days)

    def get_cache_stats(self) -> dict[str, Any]:
        avg_response_time = 0.0
        if self._cache_stats["reads"] > 0:
            avg_response_time = self._cache_stats["total_response_time"] / self._cache_stats["reads"]
        stats = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_reads": self._cache_stats["reads"],
            "total_writes": self._cache_stats["writes"],
            "cache_hits": self._cache_stats["hits"],
            "cache_misses": self._cache_stats["misses"],
            "evictions": self._cache_stats["evictions"],
            "batch_operations": self._cache_stats["batch_operations"],
            "hit_rate": self._calculate_hit_rate(),
            "hit_rate_percent": f"{self._calculate_hit_rate() * 100:.1f}%",
            "avg_response_time_ms": round(avg_response_time * 1000, 2),
            "memory_cache_stats": self.get_memory_cache_stats(),
        }

        get_td_stats = getattr(self.tdengine, "get_cache_stats", None)
        if callable(get_td_stats):
            try:
                td_stats = get_td_stats()
            except Exception as error:
                logger.warning("Failed to fetch TDengine cache stats: %s", error)
                td_stats = None
            if td_stats:
                stats["tdengine_stats"] = td_stats

        return stats

    def close(self) -> None:
        close_tdengine = getattr(self.tdengine, "close", None)
        if callable(close_tdengine):
            try:
                close_tdengine()
            except Exception as error:
                logger.warning("Failed to close TDengine manager from cache manager: %s", error)


class AsyncCacheManager:
    """Thin async adapter used by dashboard code paths."""

    def __init__(self, sync_manager: CacheManager, redis_cache: Any | None = None) -> None:
        self._sync = sync_manager
        self.redis_cache = redis_cache
        self.tdengine = sync_manager.tdengine

    async def fetch_from_cache(
        self,
        symbol: str,
        data_type: str,
        timeframe: str | None = None,
        days: int = 1,
    ) -> dict[str, Any] | None:
        return self._sync.fetch_from_cache(symbol=symbol, data_type=data_type, timeframe=timeframe, days=days)

    async def write_to_cache(
        self,
        symbol: str,
        data_type: str,
        timeframe: str,
        data: dict[str, Any] | None,
        ttl_days: int = 7,
        timestamp: datetime | None = None,
    ) -> bool:
        return self._sync.write_to_cache(
            symbol=symbol,
            data_type=data_type,
            timeframe=timeframe,
            data=data,
            ttl_days=ttl_days,
            timestamp=timestamp,
        )

    async def invalidate_cache(self, symbol: str | None = None, data_type: str | None = None) -> int:
        return self._sync.invalidate_cache(symbol=symbol, data_type=data_type)

    async def is_cache_valid(self, symbol: str, data_type: str, max_age_days: int = 7) -> bool:
        return self._sync.is_cache_valid(symbol=symbol, data_type=data_type, max_age_days=max_age_days)

    def get_cache_stats(self) -> dict[str, Any]:
        return self._sync.get_cache_stats()

    def health_check(self) -> dict[str, Any]:
        healthy = self._sync.health_check()
        return {
            "overall_healthy": healthy,
            "components": {
                "tdengine": {
                    "healthy": healthy,
                    "status": "OK" if healthy else "ERROR",
                }
            },
            "issues": [] if healthy else ["TDengine connection failed"],
        }

    def close(self) -> None:
        self._sync.close()


def get_cache_manager() -> CacheManager:
    global _manager
    if _manager is None:
        _manager = CacheManager()
    return _manager


def reset_cache_manager() -> None:
    global _manager, _async_manager
    if _async_manager is not None:
        _async_manager.close()
    elif _manager is not None:
        _manager.close()
    _async_manager = None
    _manager = None


async def get_cache_manager_async(
    tdengine_manager: Any | None = None,
    redis_cache: Any | None = None,
) -> AsyncCacheManager:
    global _manager, _async_manager
    if _manager is None:
        _manager = CacheManager(tdengine_manager=tdengine_manager)
    if _async_manager is None:
        _async_manager = AsyncCacheManager(_manager, redis_cache=redis_cache)
    return _async_manager
