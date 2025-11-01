"""
API缓存工具 - 减少数据库查询压力

解决问题：
- 高频API缺少缓存导致数据库压力大
- 提供灵活的缓存策略（Redis/内存）
- 支持TTL配置

使用方式：
    @cache_response("fund_flow", ttl=300)
    async def get_fund_flow(...):
        ...
"""

import hashlib
import json
from functools import wraps
from typing import Optional, Dict, Any, Callable
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# 内存缓存（简单实现，生产环境建议使用Redis）
_memory_cache: Dict[str, Dict[str, Any]] = {}


class CacheManager:
    """缓存管理器"""

    # 缓存配置：TTL（秒）
    CACHE_STRATEGY = {
        "stocks_basic": 3600,      # 1小时 - 股票基础信息
        "daily_kline": 1800,       # 30分钟 - 日线数据
        "fund_flow": 300,          # 5分钟 - 资金流向
        "etf_spot": 60,            # 1分钟 - ETF实时行情
        "chip_race": 300,          # 5分钟 - 竞价抢筹
        "lhb": 86400,              # 24小时 - 龙虎榜
        "wencai_results": 1800,    # 30分钟 - 问财查询结果
        "real_time_quotes": 10,    # 10秒 - 实时行情（非常短）
        "financial_report": 7200,  # 2小时 - 财务报表
    }

    @classmethod
    def get_ttl(cls, cache_type: str) -> int:
        """获取缓存TTL"""
        return cls.CACHE_STRATEGY.get(cache_type, 300)  # 默认5分钟

    @classmethod
    def generate_cache_key(cls, prefix: str, **kwargs) -> str:
        """生成缓存键"""
        # 将参数排序并序列化
        sorted_kwargs = sorted(kwargs.items())
        param_str = json.dumps(sorted_kwargs, sort_keys=True)
        param_hash = hashlib.md5(param_str.encode()).hexdigest()[:8]
        return f"api:{prefix}:{param_hash}"

    @classmethod
    def get_cache(cls, cache_key: str) -> Optional[Any]:
        """获取缓存数据"""
        if cache_key not in _memory_cache:
            return None

        cache_entry = _memory_cache[cache_key]
        expires_at = cache_entry.get("expires_at")

        # 检查是否过期
        if expires_at and datetime.now() > expires_at:
            del _memory_cache[cache_key]
            logger.debug(f"🗑️  Cache expired: {cache_key}")
            return None

        logger.debug(f"✅ Cache hit: {cache_key}")
        return cache_entry.get("data")

    @classmethod
    def set_cache(cls, cache_key: str, data: Any, ttl: int):
        """设置缓存数据"""
        expires_at = datetime.now() + timedelta(seconds=ttl)
        _memory_cache[cache_key] = {
            "data": data,
            "expires_at": expires_at,
            "created_at": datetime.now()
        }
        logger.debug(f"💾 Cache set: {cache_key} (TTL: {ttl}s)")

    @classmethod
    def clear_cache(cls, prefix: Optional[str] = None):
        """清除缓存"""
        if prefix:
            keys_to_delete = [k for k in _memory_cache.keys() if k.startswith(f"api:{prefix}:")]
            for key in keys_to_delete:
                del _memory_cache[key]
            logger.info(f"🗑️  Cleared cache: {prefix}* ({len(keys_to_delete)} keys)")
        else:
            _memory_cache.clear()
            logger.info("🗑️  Cleared all cache")

    @classmethod
    def get_cache_stats(cls) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_keys = len(_memory_cache)
        expired_keys = 0
        valid_keys = 0

        for cache_entry in _memory_cache.values():
            if datetime.now() > cache_entry.get("expires_at"):
                expired_keys += 1
            else:
                valid_keys += 1

        return {
            "total_keys": total_keys,
            "valid_keys": valid_keys,
            "expired_keys": expired_keys,
            "cache_types": list(set(k.split(":")[1] for k in _memory_cache.keys() if ":" in k))
        }


def cache_response(cache_type: str, ttl: Optional[int] = None, skip_cache: bool = False):
    """
    API响应缓存装饰器

    Args:
        cache_type: 缓存类型（用于生成缓存键前缀）
        ttl: 缓存有效期（秒），None则使用默认配置
        skip_cache: 是否跳过缓存（用于调试）

    Example:
        @cache_response("fund_flow", ttl=300)
        async def get_fund_flow(symbol: str, timeframe: str):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if skip_cache:
                return await func(*args, **kwargs)

            # 生成缓存键（排除 current_user 等敏感参数 + 依赖注入对象）
            cache_params = {k: v for k, v in kwargs.items() if k not in ['current_user', 'request', 'service']}
            cache_key = CacheManager.generate_cache_key(cache_type, **cache_params)

            # 尝试获取缓存
            cached_data = CacheManager.get_cache(cache_key)
            if cached_data is not None:
                return cached_data

            # 执行函数
            result = await func(*args, **kwargs)

            # 缓存结果（只缓存成功的响应）
            if result and isinstance(result, dict) and result.get("success") is not False:
                cache_ttl = ttl if ttl is not None else CacheManager.get_ttl(cache_type)
                CacheManager.set_cache(cache_key, result, cache_ttl)

            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            """同步函数包装器"""
            if skip_cache:
                return func(*args, **kwargs)

            cache_params = {k: v for k, v in kwargs.items() if k not in ['current_user', 'request', 'service']}
            cache_key = CacheManager.generate_cache_key(cache_type, **cache_params)

            cached_data = CacheManager.get_cache(cache_key)
            if cached_data is not None:
                return cached_data

            result = func(*args, **kwargs)

            if result and isinstance(result, dict) and result.get("success") is not False:
                cache_ttl = ttl if ttl is not None else CacheManager.get_ttl(cache_type)
                CacheManager.set_cache(cache_key, result, cache_ttl)

            return result

        # 根据函数类型返回对应的包装器
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# 便捷函数
def clear_api_cache(cache_type: Optional[str] = None):
    """清除API缓存"""
    CacheManager.clear_cache(cache_type)


def get_cache_stats() -> Dict[str, Any]:
    """获取缓存统计"""
    return CacheManager.get_cache_stats()
