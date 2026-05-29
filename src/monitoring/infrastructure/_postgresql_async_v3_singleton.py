"""MonitoringPostgreSQLAccess 单例 helper。"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from src.monitoring.infrastructure.postgresql_async_v3 import MonitoringPostgreSQLAccess


logger = logging.getLogger(__name__)

PostgresAsyncProvider = Callable[[], "MonitoringPostgreSQLAccess"]

_postgres_async_instance: Optional["MonitoringPostgreSQLAccess"] = None
_postgres_async_provider: Optional[PostgresAsyncProvider] = None


def set_postgres_async_provider(provider: PostgresAsyncProvider) -> None:
    """Install an explicit PostgreSQL async access provider."""
    global _postgres_async_provider
    _postgres_async_provider = provider


def reset_postgres_async_provider() -> None:
    """Clear explicit provider and cached singleton state."""
    global _postgres_async_instance, _postgres_async_provider
    _postgres_async_provider = None
    _postgres_async_instance = None


def get_postgres_async() -> "MonitoringPostgreSQLAccess":
    """获取全局单例实例。"""
    global _postgres_async_instance
    if _postgres_async_provider is not None:
        return _postgres_async_provider()
    if _postgres_async_instance is None:
        from src.monitoring.infrastructure.postgresql_async_v3 import MonitoringPostgreSQLAccess

        _postgres_async_instance = MonitoringPostgreSQLAccess()
    return _postgres_async_instance


async def initialize_postgres_async() -> bool:
    """初始化全局单例。"""
    instance = get_postgres_async()
    try:
        await instance.initialize()
        return True
    except Exception as exc:
        logger.error("❌ 异步数据库初始化失败: %s", exc)
        return False


async def close_postgres_async():
    """关闭全局单例。"""
    instance = get_postgres_async()
    await instance.close()
    logger.info("✅ 异步数据库连接已关闭")
