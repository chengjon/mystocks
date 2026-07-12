"""指标 API 运行时支持组件。
"""

import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from functools import wraps
from typing import Dict, List, Optional

from app.core.exceptions import BusinessException


class IndicatorCache:
    """技术指标计算结果缓存"""

    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.cache: Dict[str, Dict] = {}
        self.max_size = max_size
        self.ttl = ttl
        self.access_times: Dict[str, datetime] = {}

    def _generate_cache_key(self, symbol: str, start_date: str, end_date: str, indicators: List[Dict]) -> str:
        cache_data = {
            "symbol": symbol,
            "start_date": start_date,
            "end_date": end_date,
            "indicators": sorted(indicators, key=lambda item: item["abbreviation"]),
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()

    def get(self, cache_key: str) -> Optional[Dict]:
        if cache_key not in self.cache:
            return None

        cache_entry = self.cache[cache_key]
        if (datetime.now(timezone.utc) - cache_entry["timestamp"]).seconds > self.ttl:
            self.remove(cache_key)
            return None

        self.access_times[cache_key] = datetime.now(timezone.utc)
        return cache_entry["data"]

    def set(self, cache_key: str, data: Dict) -> None:
        if len(self.cache) >= self.max_size:
            self._cleanup_old_entries()

        self.cache[cache_key] = {"data": data, "timestamp": datetime.now(timezone.utc)}
        self.access_times[cache_key] = datetime.now(timezone.utc)

    def remove(self, cache_key: str) -> None:
        self.cache.pop(cache_key, None)
        self.access_times.pop(cache_key, None)

    def _cleanup_old_entries(self) -> None:
        if not self.access_times:
            return

        oldest_key = min(self.access_times.keys(), key=lambda key: self.access_times[key])
        self.remove(oldest_key)

    def clear(self) -> None:
        self.cache.clear()
        self.access_times.clear()

    def get_stats(self) -> Dict:
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "ttl": self.ttl,
            "hit_rate": getattr(self, "_hit_count", 0) / max(getattr(self, "_total_requests", 1), 1),
        }


class RateLimiter:
    """技术指标 API 速率限制器"""

    def __init__(self):
        self.requests = defaultdict(list)

    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        now = datetime.now(timezone.utc)
        self.requests[key] = [request_time for request_time in self.requests[key] if (now - request_time).seconds < window]

        if len(self.requests[key]) >= limit:
            return False

        self.requests[key].append(now)
        return True


rate_limiter = RateLimiter()
indicator_cache = IndicatorCache()


def rate_limit(limit: int, window: int):
    """速率限制装饰器。"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = None
            for arg in args:
                if hasattr(arg, "id"):
                    current_user = arg
                    break

            if not current_user:
                for value in kwargs.values():
                    if hasattr(value, "id"):
                        current_user = value
                        break

            user_key = f"indicators_user_{current_user.id}" if current_user else "indicators_anonymous"

            if not rate_limiter.is_allowed(user_key, limit, window):
                raise BusinessException(
                    detail=f"技术指标计算请求过于频繁，请在{window}秒后重试",
                    status_code=429,
                    error_code="RATE_LIMIT_EXCEEDED",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator
