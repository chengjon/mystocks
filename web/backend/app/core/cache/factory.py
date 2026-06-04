"""Compatibility wrappers for the canonical cache manager lifecycle."""

from __future__ import annotations

from typing import Any

from app.core import cache_manager as canonical_cache_manager

CacheManager = canonical_cache_manager.CacheManager


def get_cache_manager(tdengine_manager: Any | None = None) -> CacheManager:
    """
    获取缓存管理器单例 (向后兼容)

    Args:
        tdengine_manager: TDengineManager 实例

    Returns:
        CacheManager 单例实例
    """
    provider = canonical_cache_manager._get_cache_lifecycle_provider()
    return provider.get_sync(tdengine_manager=tdengine_manager)


def reset_cache_manager() -> None:
    """重置缓存管理器（用于测试）"""
    canonical_cache_manager.reset_cache_manager()
