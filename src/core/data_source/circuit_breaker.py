"""
熔断器模块 (CircuitBreaker)

实现线程安全的熔断器模式，保护系统免受级联故障影响。
"""

import threading
import time
import logging
from enum import Enum
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """熔断器状态"""

    CLOSED = "CLOSED"  # 正常状态，允许请求通过
    OPEN = "OPEN"  # 熔断状态，拒绝请求
    HALF_OPEN = "HALF_OPEN"  # 半开状态，允许试探请求


class CircuitBreakerOpenError(Exception):
    """熔断器开启异常"""

    pass


class CircuitBreaker:
    """
    熔断器实现

    特性:
    - 三态熔断器 (CLOSED, OPEN, HALF_OPEN)
    - 线程安全 (使用 Lock)
    - 自动恢复 (超时后进入半开状态)
    - 可配置阈值和超时
    """

    def __init__(
        self,
        failure_threshold: int = 5,  # 连续失败次数阈值
        recovery_timeout: int = 60,  # 恢复超时时间 (秒)
        expected_exception: Exception = Exception,  # 预期的异常类型
        name: str = "default",  # 熔断器名称
    ):
        """
        初始化熔断器

        Args:
            failure_threshold: 连续失败次数阈值
            recovery_timeout: 恢复超时时间 (秒)
            expected_exception: 预期的异常类型
            name: 熔断器名称
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.name = name

        # 熔断器状态
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.opened_at = None

        # 线程安全
        self.lock = threading.Lock()

        # 统计信息
        self.total_calls = 0
        self.total_failures = 0
        self.total_successes = 0

        logger.info(
            f"CircuitBreaker '{name}' initialized: "
            f"failure_threshold={failure_threshold}, "
            f"recovery_timeout={recovery_timeout}s"
        )

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        执行函数调用，带熔断保护

        Args:
            func: 要执行的函数
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            函数返回值

        Raises:
            CircuitBreakerOpenError: 熔断器开启时抛出
        """
        self.total_calls += 1

        # 检查熔断器状态
        if not self._can_attempt():
            remaining_time = self._get_remaining_time()
            logger.warning(
                f"CircuitBreaker '{self.name}' is OPEN, " f"rejecting call ({remaining_time:.1f}s remaining)"
            )
            raise CircuitBreakerOpenError(
                f"CircuitBreaker '{self.name}' is OPEN. " f"Retry after {remaining_time:.1f} seconds"
            )

        # 执行函数调用
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e

    def _can_attempt(self) -> bool:
        """
        检查是否可以尝试调用

        Returns:
            True 如果可以尝试，否则 False
        """
        with self.lock:
            # CLOSED 状态: 允许调用
            if self.state == CircuitState.CLOSED:
                return True

            # OPEN 状态: 检查是否超时
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    # 超时，进入 HALF_OPEN 状态
                    logger.info(f"CircuitBreaker '{self.name}' timeout reached, " "transitioning to HALF_OPEN")
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                    return True
                else:
                    return False

            # HALF_OPEN 状态: 允许试探
            return True

    def _should_attempt_reset(self) -> bool:
        """
        检查是否应该尝试重置

        Returns:
            True 如果超时，否则 False
        """
        if self.opened_at is None:
            return False

        current_time = time.time()
        return current_time - self.opened_at >= self.recovery_timeout

    def _get_remaining_time(self) -> float:
        """
        获取剩余超时时间

        Returns:
            剩余时间 (秒)
        """
        if self.opened_at is None:
            return 0.0

        current_time = time.time()
        elapsed = current_time - self.opened_at
        remaining = self.recovery_timeout - elapsed

        return max(0.0, remaining)

    def _on_success(self) -> None:
        """处理成功调用"""
        with self.lock:
            self.total_successes += 1
            self.last_failure_time = None

            if self.state == CircuitState.CLOSED:
                # CLOSED 状态: 重置失败计数
                self.failure_count = 0

            elif self.state == CircuitState.HALF_OPEN:
                # HALF_OPEN 状态: 累计成功次数
                self.success_count += 1

                # 如果连续成功次数达到阈值，回到 CLOSED 状态
                if self.success_count >= 2:  # 连续 2 次成功
                    logger.info(f"CircuitBreaker '{self.name}' recovered, " "transitioning to CLOSED")
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    self.success_count = 0
                    self.opened_at = None

    def _on_failure(self) -> None:
        """处理失败调用"""
        with self.lock:
            self.total_failures += 1
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.state == CircuitState.CLOSED:
                # CLOSED 状态: 检查是否达到阈值
                if self.failure_count >= self.failure_threshold:
                    logger.warning(
                        f"CircuitBreaker '{self.name}' failure threshold reached "
                        f"({self.failure_count}/{self.failure_threshold}), "
                        "transitioning to OPEN"
                    )
                    self.state = CircuitState.OPEN
                    self.opened_at = time.time()

            elif self.state == CircuitState.HALF_OPEN:
                # HALF_OPEN 状态: 失败直接回到 OPEN 状态
                logger.warning(
                    f"CircuitBreaker '{self.name}' test call failed in " "HALF_OPEN state, transitioning back to OPEN"
                )
                self.state = CircuitState.OPEN
                self.opened_at = time.time()
                self.success_count = 0

    def reset(self) -> None:
        """手动重置熔断器"""
        with self.lock:
            logger.info(f"CircuitBreaker '{self.name}' manually reset")
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.last_failure_time = None
            self.opened_at = None

    def get_state(self) -> CircuitState:
        """
        获取当前状态

        Returns:
            当前熔断器状态
        """
        with self.lock:
            # 检查是否需要自动转换状态
            if self.state == CircuitState.OPEN and self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0

            return self.state

    def get_stats(self) -> dict:
        """
        获取统计信息

        Returns:
            统计信息字典
        """
        with self.lock:
            total_requests = self.total_calls
            success_rate = self.total_successes / total_requests if total_requests > 0 else 0

            return {
                "name": self.name,
                "state": self.get_state().value,
                "failure_count": self.failure_count,
                "success_count": self.success_count,
                "total_calls": self.total_calls,
                "total_successes": self.total_successes,
                "total_failures": self.total_failures,
                "success_rate": success_rate,
                "failure_threshold": self.failure_threshold,
                "recovery_timeout": self.recovery_timeout,
                "last_failure_time": self.last_failure_time,
                "opened_at": self.opened_at,
                "remaining_time": self._get_remaining_time(),
            }

    def __str__(self) -> str:
        """字符串表示"""
        return (
            f"CircuitBreaker(name='{self.name}', "
            f"state={self.get_state().value}, "
            f"failures={self.failure_count}/{self.failure_threshold})"
        )
