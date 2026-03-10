"""MonitoringPostgreSQLAccess 单例 helper。"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from src.monitoring.infrastructure.postgresql_async_v3 import MonitoringPostgreSQLAccess


logger = logging.getLogger(__name__)

_postgres_async_instance: Optional["MonitoringPostgreSQLAccess"] = None


def get_postgres_async() -> "MonitoringPostgreSQLAccess":
    """获取全局单例实例。"""
    global _postgres_async_instance
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
    except Exception:
        logger.error("❌ 异步数据库初始化失败: %(e)s")
        return False


async def close_postgres_async():
    """关闭全局单例。"""
    instance = get_postgres_async()
    await instance.close()
    logger.info("✅ 异步数据库连接已关闭")
