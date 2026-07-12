"""P0 Task 3: 错误处理增强 - 熔断器和降级策略

遵循P0改进计划 Task 3: 错误处理增强
包含：
1. CircuitBreaker - 熔断器模式
2. FallbackStrategy - 降级策略
3. RetryPolicy - 重试政策
4. 装饰器 - @handle_errors, @with_circuit_breaker, @with_fallback
"""

import asyncio
import logging
import time
from enum import Enum
from functools import wraps
from typing import Any, Callable


logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """错误严重程度"""

    LOW = 1  # 低：可以忽略
    MEDIUM = 2  # 中：需要记录
    HIGH = 3  # 高：需要告警
    CRITICAL = 4  # 严重：需要立即处理


class ErrorCategory(Enum):
    """错误分类"""

    DATABASE = "database_error"
    NETWORK = "network_error"
    VALIDATION = "validation_error"
    TIMEOUT = "timeout_error"
    AUTHORIZATION = "authorization_error"
    RESOURCE = "resource_not_found"
    INTERNAL = "internal_server_error"


class CircuitBreakerState(Enum):
    """熔断器状态"""

    CLOSED = "closed"  # 正常，允许请求通过
    OPEN = "open"  # 故障，拒绝请求
    HALF_OPEN = "half_open"  # 恢复测试，允许部分请求通过


class CircuitBreaker:
    """熔断器模式 - 防止级联故障

    工作原理:
    1. CLOSED状态：正常工作，请求通过
    2. 失败次数达到阈值 -> OPEN状态
    3. OPEN状态：快速失败，不调用被保护的服务
    4. 经过超时时间 -> HALF_OPEN状态
    5. HALF_OPEN状态：尝试恢复，如果成功 -> CLOSED，失败 -> OPEN

    默认配置：
    - 失败阈值: 5次
    - 恢复超时: 60秒
    - 成功阈值: 2次（在HALF_OPEN状态下）
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        success_threshold: int = 2,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold

        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED

    def is_open(self) -> bool:
        """检查熔断器是否打开"""
        if self.state == CircuitBreakerState.OPEN:
            # 检查是否可以转入HALF_OPEN状态
            if self.last_failure_time:
                elapsed = time.time() - self.last_failure_time
                if elapsed >= self.recovery_timeout:
                    logger.info("🔄 Circuit breaker '{self.name}' transitioning to HALF_OPEN")
                    self.state = CircuitBreakerState.HALF_OPEN
                    self.success_count = 0
                    return False
            return True
        return False

    def record_failure(self):
        """记录一次失败"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == CircuitBreakerState.HALF_OPEN:
            # HALF_OPEN中失败，返回OPEN
            logger.warning("⚠️ Circuit breaker '{self.name}' reopening")
            self.state = CircuitBreakerState.OPEN
            self.failure_count = 0
        elif self.failure_count >= self.failure_threshold:
            # CLOSED中失败达到阈值，打开熔断器
            logger.error("🔴 Circuit breaker '{self.name}' opened (failures: {self.failure_count})")
            self.state = CircuitBreakerState.OPEN

    def record_success(self):
        """记录一次成功"""
        self.failure_count = 0

        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                # HALF_OPEN中成功达到阈值，关闭熔断器
                logger.info("✅ Circuit breaker '{self.name}' closed")
                self.state = CircuitBreakerState.CLOSED
                self.success_count = 0

    def get_status(self) -> dict:
        """获取熔断器状态"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure": self.last_failure_time,
        }


class FallbackStrategy:
    """降级策略 - 服务不可用时的备选方案

    支持：
    1. 使用缓存数据
    2. 使用Mock数据
    3. 使用默认值
    4. 调用备选服务
    """

    @staticmethod
    def with_cache(cache_key: str, cache_data: dict, cache_ttl: int = 3600):
        """降级到缓存数据

        Args:
            cache_key: 缓存键
            cache_data: 缓存字典
            cache_ttl: 缓存时间（秒）

        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
                except Exception as e:
                    logger.warning(
                        f"⚠️ Function {func.__name__} failed, falling back to cache",
                        exc_info=e,
                    )

                    # 从缓存中获取数据
                    if cache_key in cache_data:
                        cached_value = cache_data[cache_key]
                        if isinstance(cached_value, dict) and "timestamp" in cached_value:
                            age = time.time() - cached_value["timestamp"]
                            if age < cache_ttl:
                                logger.info("✅ Using cached data for %(cache_key)s (age: {int(age)}s)")
                                return cached_value.get("data")

                        logger.warning("⚠️ Cached data for %(cache_key)s is stale (age: {int(age)}s > %(cache_ttl)ss)")
                        return cached_value

                    # 缓存中没有数据，返回空
                    logger.error("❌ No cached data available for %(cache_key)s")
                    raise RuntimeError(f"Service failed and no cache available for {cache_key}")

            return wrapper

        return decorator

    @staticmethod
    def with_mock_data(mock_data: Any):
        """降级到Mock数据

        Args:
            mock_data: Mock数据

        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
                except Exception as e:
                    logger.warning(
                        f"⚠️ Function {func.__name__} failed, using mock data",
                        exc_info=e,
                    )
                    return mock_data

            return wrapper

        return decorator

    @staticmethod
    def with_default_value(default_value: Any):
        """降级到默认值

        Args:
            default_value: 默认值

        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
                except Exception as e:
                    logger.warning(
                        f"⚠️ Function {func.__name__} failed, returning default value",
                        exc_info=e,
                    )
                    return default_value

            return wrapper

        return decorator


class RetryPolicy:
    """重试政策"""

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
    ):
        """初始化重试政策

        Args:
            max_attempts: 最大尝试次数
            initial_delay: 初始延迟（秒）
            max_delay: 最大延迟（秒）
            backoff_factor: 延迟倍增因子
            jitter: 是否添加随机抖动

        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter

    def get_delay(self, attempt: int) -> float:
        """计算延迟时间（指数退避）

        Args:
            attempt: 当前尝试次数（从1开始）

        Returns:
            延迟时间（秒）

        """
        delay = min(self.initial_delay * (self.backoff_factor ** (attempt - 1)), self.max_delay)

        if self.jitter:
            import random

            delay *= 0.5 + random.random()

        return delay

    async def execute_async(self, func: Callable, *args, **kwargs) -> Any:
        """异步执行函数并重试

        Args:
            func: 要执行的函数
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            函数返回值

        Raises:
            最后一次尝试的异常

        """
        last_exception = None

        for attempt in range(1, self.max_attempts + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_attempts:
                    delay = self.get_delay(attempt)
                    logger.warning(
                        f"⚠️ Attempt {attempt}/{self.max_attempts} failed, retrying in {delay:.2f}s",
                        exc_info=e,
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error("❌ All {self.max_attempts} attempts failed", exc_info=e)

        raise last_exception

    def execute_sync(self, func: Callable, *args, **kwargs) -> Any:
        """同步执行函数并重试

        Args:
            func: 要执行的函数
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            函数返回值

        Raises:
            最后一次尝试的异常

        """
        last_exception = None

        for attempt in range(1, self.max_attempts + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_attempts:
                    delay = self.get_delay(attempt)
                    logger.warning(
                        f"⚠️ Attempt {attempt}/{self.max_attempts} failed, retrying in {delay:.2f}s",
                        exc_info=e,
                    )
                    time.sleep(delay)
                else:
                    logger.error("❌ All {self.max_attempts} attempts failed", exc_info=e)

        raise last_exception


# ==================== 装饰器 ====================


def with_circuit_breaker(circuit_breaker: CircuitBreaker):
    """应用熔断器装饰器

    使用示例:
    ```python
    cb = CircuitBreaker("fetch_data")

    @with_circuit_breaker(cb)
    async def fetch_data():
        return await external_api.get_data()
    ```
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if circuit_breaker.is_open():
                raise RuntimeError(f"Circuit breaker '{circuit_breaker.name}' is open")

            try:
                result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
                circuit_breaker.record_success()
                return result
            except Exception:
                circuit_breaker.record_failure()
                raise

        return wrapper

    return decorator


def with_retry(max_attempts: int = 3, initial_delay: float = 1.0):
    """应用重试装饰器

    使用示例:
    ```python
    @with_retry(max_attempts=3, initial_delay=1.0)
    async def fetch_data():
        return await external_api.get_data()
    ```
    """
    retry_policy = RetryPolicy(max_attempts=max_attempts, initial_delay=initial_delay)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if asyncio.iscoroutinefunction(func):
                return await retry_policy.execute_async(func, *args, **kwargs)
            return retry_policy.execute_sync(func, *args, **kwargs)

        return wrapper

    return decorator


# ==================== 应用导出 ====================

__all__ = [
    "CircuitBreaker",
    "CircuitBreakerState",
    "ErrorCategory",
    "ErrorSeverity",
    "FallbackStrategy",
    "RetryPolicy",
    "with_circuit_breaker",
    "with_retry",
]
