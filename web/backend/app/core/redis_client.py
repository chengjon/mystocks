"""
Redis Client Manager
=====================

统一的Redis连接管理器，支持连接池、自动重连、错误处理。

Version: 1.0.0
Author: MyStocks Project
"""

import redis
import logging
from typing import Optional
from contextlib import contextmanager
from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisManager:
    """
    Redis连接管理器 (单例模式)

    功能:
    1. 连接池管理
    2. 自动重连
    3. 错误处理
    4. 健康检查
    """

    _instance: Optional["RedisManager"] = None
    _redis_client: Optional[redis.Redis] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._redis_client is None:
            self._initialize_client()

    def _initialize_client(self):
        """初始化Redis连接池"""
        try:
            self._redis_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password if settings.redis_password else None,
                max_connections=settings.redis_max_connections,
                socket_timeout=settings.redis_socket_timeout,
                socket_connect_timeout=settings.redis_socket_connect_timeout,
                decode_responses=settings.redis_decode_responses,
                health_check_interval=30,  # 健康检查间隔
                retry_on_timeout=True,  # 超时自动重试
                retry_on_error=[redis.ConnectionError, redis.TimeoutError],
            )
            # 测试连接
            self._redis_client.ping()
            logger.info(f"✅ Redis connected: {settings.redis_host}:{settings.redis_port}/{settings.redis_db}")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            self._redis_client = None

    @property
    def client(self) -> redis.Redis:
        """获取Redis客户端（自动重连）"""
        if self._redis_client is None:
            self._initialize_client()
        return self._redis_client

    @contextmanager
    def get_connection(self):
        """
        获取Redis连接的上下文管理器

        使用示例:
        ```python
        with redis_manager.get_connection() as conn:
            conn.set('key', 'value')
        ```
        """
        conn = self.client
        try:
            yield conn
        except Exception as e:
            logger.error(f"Redis operation failed: {e}")
            raise

    def health_check(self) -> bool:
        """
        健康检查

        Returns:
            bool: Redis是否可用
        """
        try:
            self.client.ping()
            return True
        except Exception as e:
            logger.warning(f"Redis health check failed: {e}")
            return False

    def close(self):
        """关闭Redis连接"""
        if self._redis_client:
            self._redis_client.close()
            self._redis_client = None
            logger.info("Redis connection closed")

    def flush_db(self, asynchronous: bool = False):
        """
        清空当前数据库（谨慎使用！）

        Args:
            asynchronous: 是否异步执行
        """
        try:
            self.client.flushdb(asynchronous=asynchronous)
            logger.warning(f"Redis DB {settings.redis_db} flushed")
        except Exception as e:
            logger.error(f"Failed to flush Redis DB: {e}")


# 全局单例实例
redis_manager = RedisManager()


def get_redis_client() -> redis.Redis:
    """
    获取Redis客户端的快捷函数

    Returns:
        redis.Redis: Redis客户端实例
    """
    return redis_manager.client
