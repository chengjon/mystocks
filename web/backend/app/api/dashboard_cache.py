"""
仪表盘三级缓存辅助函数
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Any, Dict, Optional

from app.core.cache_manager import CacheManager

logger = logging.getLogger(__name__)


def generate_cache_key(user_id: int, trade_date: Optional[date]) -> str:
    """生成缓存键"""
    date_str = (trade_date or date.today()).isoformat()
    return f"dashboard_user_{user_id}_{date_str}"


async def try_get_cached_dashboard(
    cache_manager: CacheManager,
    user_id: int,
    trade_date: Optional[date],
) -> tuple[Optional[Dict[str, Any]], bool]:
    """尝试从三级缓存获取仪表盘数据"""
    try:
        cache_key = generate_cache_key(user_id, trade_date)
        cached_data = await cache_manager.fetch_from_cache(
            symbol=f"user_{user_id}",
            data_type="dashboard",
            timeframe="1d",
        )

        if cached_data and isinstance(cached_data, dict):
            logger.info("✅ 三级缓存命中: %s", cache_key)
            return cached_data, True

        logger.debug("⚠️ 三级缓存未命中: %s", cache_key)
        return None, False
    except Exception as error:
        logger.warning("三级缓存读取失败，将继续获取新数据: %s", error)
        return None, False


async def cache_dashboard_data(
    cache_manager: CacheManager,
    user_id: int,
    trade_date: Optional[date],
    dashboard_data: Dict[str, Any],
    ttl_hours: int = 24,
) -> bool:
    """将仪表盘数据写入三级缓存"""
    try:
        cache_key = generate_cache_key(user_id, trade_date)
        cache_entry = {
            "dashboard_data": dashboard_data,
            "user_id": user_id,
            "trade_date": (trade_date or date.today()).isoformat(),
            "cached_at": datetime.now().isoformat(),
            "ttl_hours": ttl_hours,
        }

        success = await cache_manager.write_to_cache(
            symbol=f"user_{user_id}",
            data_type="dashboard",
            timeframe="1d",
            data=cache_entry,
            ttl_days=(ttl_hours + 23) // 24,
            timestamp=datetime.now(),
        )

        success_bool = bool(success)
        if success_bool:
            logger.info("✅ 三级缓存写入成功: %s", cache_key)
        else:
            logger.warning("⚠️ 三级缓存写入失败: %s", cache_key)

        return success_bool
    except Exception as error:
        logger.warning("三级缓存写入异常: %s", error)
        return False
