"""缓存管理器子模块"""

import logging
import time
from collections import OrderedDict
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)

from .manager import CacheManager

def get_cache_manager(
    tdengine_manager: Optional[TDengineManager] = None,
) -> CacheManager:
    """
    获取缓存管理器单例 (向后兼容)

    注意: 此方法不支持Redis注入。如需Redis支持，请使用 get_cache_manager_async()

    Args:
        tdengine_manager: TDengineManager 实例

    Returns:
        CacheManager 单例实例
    """
    global _cache_manager

    if _cache_manager is None:
        _cache_manager = CacheManager(tdengine_manager)
        logger.warning("⚠️ 使用同步缓存管理器，Redis功能不可用。如需Redis支持，请使用 get_cache_manager_async()")

    return _cache_manager


def reset_cache_manager() -> None:
    """重置缓存管理器（用于测试）"""
    global _cache_manager
    if _cache_manager:
        _cache_manager.close()
    _cache_manager = None
