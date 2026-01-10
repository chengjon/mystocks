"""
Distributed Lock implementation using Redis
分布式锁实现，用于解决并发冲突
"""
import time
import uuid
import logging
from typing import Optional
import redis

logger = logging.getLogger(__name__)

class RedisDistributedLock:
    """
    基于 Redis 的分布式锁
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def acquire(self, lock_name: str, expire_seconds: int = 10, wait_timeout: int = 5) -> Optional[str]:
        """
        获取锁
        
        Args:
            lock_name: 锁名称
            expire_seconds: 过期时间（秒），防止进程崩溃导致死锁
            wait_timeout: 等待超时时间（秒）
            
        Returns:
            lock_token: 成功返回唯一标识符（用于释放锁），失败返回 None
        """
        identifier = str(uuid.uuid4())
        lock_key = f"lock:{lock_name}"
        end_time = time.time() + wait_timeout
        
        while time.time() < end_time:
            # SET NX PX: 只有不存在时设置，并带有过期毫秒数 (原子操作)
            if self.redis.set(lock_key, identifier, nx=True, ex=expire_seconds):
                logger.debug(f"Acquired lock: {lock_name}")
                return identifier
            
            time.sleep(0.1) # 短暂重试间隔
            
        logger.warning(f"Timeout waiting for lock: {lock_name}")
        return None

    def release(self, lock_name: str, identifier: str) -> bool:
        """
        释放锁（使用 Lua 脚本确保原子性，只有持有者能释放）
        """
        lock_key = f"lock:{lock_name}"
        
        # Lua 脚本：只有当当前值等于 identifier 时才删除
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        
        result = self.redis.eval(lua_script, 1, lock_key, identifier)
        success = bool(result)
        
        if success:
            logger.debug(f"Released lock: {lock_name}")
        else:
            logger.warning(f"Failed to release lock: {lock_name} (Identifier mismatch or lock expired)")
            
        return success

    def __enter__(self):
        # 这种方式需要预先设置好参数，这里建议使用 context manager factory
        raise NotImplementedError("Use context_lock() instead")

class DistributedLockContext:
    """
    锁的上下文管理器
    """
    def __init__(self, lock_manager: RedisDistributedLock, name: str, expire: int = 10):
        self.lock_manager = lock_manager
        self.name = name
        self.expire = expire
        self.token = None

    def __enter__(self):
        self.token = self.lock_manager.acquire(self.name, self.expire)
        if not self.token:
            raise RuntimeError(f"Could not acquire lock: {self.name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.token:
            self.lock_manager.release(self.name, self.token)
