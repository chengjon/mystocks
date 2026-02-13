"""
Redis Distributed Lock
======================

分布式锁服务，基于Redis实现。

功能:
1. 防止重复计算 (同一指标同一时间只计算一次)
2. 资源竞争控制 (限制并发任务数量)
3. 互斥访问 (关键资源独占)

Version: 1.0.0
Author: MyStocks Project
"""

import logging
import time
import uuid
from contextlib import contextmanager
from typing import Any, Dict, Optional

from app.core.config import settings
from app.core.redis_client import get_redis_client

logger = logging.getLogger(__name__)


class RedisLockService:
    """
    Redis分布式锁服务

    使用场景:
    - 防止重复计算: 同一指标计算任务互斥
    - 资源限流: 限制同时运行的后台任务数量
    - 数据更新保护: 防止并发修改
    """

    def __init__(self):
        self.redis = get_redis_client()
        self.prefix = settings.redis_lock_prefix
        self.default_timeout = settings.redis_lock_default_timeout

    def _make_key(self, resource: str) -> str:
        """生成锁键"""
        return f"{self.prefix}{resource}"

    # ========== 基础锁操作 ==========

    def acquire(
        self,
        resource: str,
        timeout: Optional[int] = None,
        blocking: bool = True,
        blocking_timeout: Optional[int] = None,
    ) -> Optional[str]:
        """
        获取锁

        Args:
            resource: 资源标识 (如 "indicator:calc:000001:MACD")
            timeout: 锁超时时间 (秒)，默认使用配置的default_timeout
            blocking: 是否阻塞等待
            blocking_timeout: 阻塞等待超时 (秒)，None表示无限等待

        Returns:
            锁标识符 (token)，获取失败返回None
        """
        lock_key = self._make_key(resource)
        timeout = timeout or self.default_timeout
        token = str(uuid.uuid4())  # 唯一锁标识符

        start_time = time.time()

        while True:
            try:
                # SETNX + EXPIRE (原子操作)
                acquired = self.redis.set(lock_key, token, nx=True, ex=timeout)  # 仅当键不存在时设置  # 自动过期时间

                if acquired:
                    logger.debug("Lock acquired: %(resource)s (token: {token[:8]}...)")
                    return token

                if not blocking:
                    return None

                # 检查阻塞超时
                if blocking_timeout is not None:
                    elapsed = time.time() - start_time
                    if elapsed >= blocking_timeout:
                        logger.warning("Lock acquisition timeout: %(resource)s")
                        return None

                # 短暂休眠后重试
                time.sleep(0.1)

            except Exception:
                logger.error("Failed to acquire lock %(resource)s: %(e)s")
                if not blocking:
                    return None
                time.sleep(0.1)

    def release(self, resource: str, token: str) -> bool:
        """
        释放锁

        Args:
            resource: 资源标识
            token: 锁标识符 (必须与获取时的token一致)

        Returns:
            bool: 是否释放成功
        """
        lock_key = self._make_key(resource)

        try:
            # Lua脚本确保原子性: 只释放自己的锁
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """

            result = self.redis.eval(lua_script, 1, lock_key, token)
            success = bool(result)

            if success:
                logger.debug("Lock released: %(resource)s")
            else:
                logger.warning("Lock release failed (wrong token or expired): %(resource)s")

            return success

        except Exception:
            logger.error("Failed to release lock %(resource)s: %(e)s")
            return False

    def extend(self, resource: str, token: str, additional_time: int = 30) -> bool:
        """
        延长锁超时时间

        Args:
            resource: 资源标识
            token: 锁标识符
            additional_time: 延长时间 (秒)

        Returns:
            bool: 是否延长成功
        """
        lock_key = self._make_key(resource)

        try:
            # Lua脚本确保只延长自己的锁
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("expire", KEYS[1], ARGV[2])
            else
                return 0
            end
            """

            result = self.redis.eval(lua_script, 1, lock_key, token, additional_time)
            success = bool(result)

            if success:
                logger.debug("Lock extended: %(resource)s (+%(additional_time)ss)")

            return success

        except Exception:
            logger.error("Failed to extend lock %(resource)s: %(e)s")
            return False

    # ========== 上下文管理器 ==========

    @contextmanager
    def lock(
        self,
        resource: str,
        timeout: Optional[int] = None,
        blocking: bool = True,
        blocking_timeout: Optional[int] = None,
    ):
        """
        锁上下文管理器

        使用示例:
        ```python
        with redis_lock.lock("my_resource"):
            # 临界区代码
            do_something()
        # 自动释放锁
        ```

        Args:
            resource: 资源标识
            timeout: 锁超时时间
            blocking: 是否阻塞等待
            blocking_timeout: 阻塞等待超时

        Yields:
            锁标识符
        """
        token = None
        try:
            token = self.acquire(resource, timeout, blocking, blocking_timeout)
            if token is None:
                raise RuntimeError(f"Failed to acquire lock: {resource}")
            yield token
        finally:
            if token:
                self.release(resource, token)

    # ========== 便捷方法 ==========

    def is_locked(self, resource: str) -> bool:
        """
        检查资源是否被锁定

        Args:
            resource: 资源标识

        Returns:
            bool: 是否被锁定
        """
        lock_key = self._make_key(resource)
        return self.redis.exists(lock_key) > 0

    def get_lock_info(self, resource: str) -> Optional[Dict[str, Any]]:
        """
        获取锁信息

        Args:
            resource: 资源标识

        Returns:
            锁信息字典，不存在返回None
        """
        lock_key = self._make_key(resource)
        try:
            token = self.redis.get(lock_key)
            if token:
                ttl = self.redis.ttl(lock_key)
                return {"resource": resource, "token": token, "remaining_ttl": ttl}
        except Exception:
            logger.error("Failed to get lock info %(resource)s: %(e)s")
        return None

    # ========== 预定义锁场景 ==========

    @contextmanager
    def indicator_calculation_lock(self, stock_code: str, indicator_code: str, params: Optional[Dict] = None):
        """
        指标计算锁 (防止重复计算)

        Args:
            stock_code: 股票代码
            indicator_code: 指标代码
            params: 计算参数 (可选)

        Yields:
            锁标识符
        """
        import hashlib
        import json

        # 生成唯一资源标识
        params_str = json.dumps(params or {}, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
        resource = f"indicator:calc:{stock_code}:{indicator_code}:{params_hash}"

        with self.lock(resource, timeout=300) as token:  # 5分钟超时
            yield token

    @contextmanager
    def batch_task_lock(self, task_id: str):
        """
        批量任务锁 (防止任务重复执行)

        Args:
            task_id: 任务ID

        Yields:
            锁标识符
        """
        resource = f"task:batch:{task_id}"

        with self.lock(resource, timeout=3600) as token:  # 1小时超时
            yield token

    @contextmanager
    def resource_update_lock(self, resource_type: str, resource_id: str):
        """
        资源更新锁 (防止并发修改)

        Args:
            resource_type: 资源类型 (如 "data_source", "indicator")
            resource_id: 资源ID

        Yields:
            锁标识符
        """
        resource = f"resource:update:{resource_type}:{resource_id}"

        with self.lock(resource, timeout=60) as token:  # 1分钟超时
            yield token


# 全局单例
redis_lock = RedisLockService()
