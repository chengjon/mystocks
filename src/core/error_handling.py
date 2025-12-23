"""
Comprehensive Error Handling and Recovery Mechanisms
综合错误处理和恢复机制

创建日期: 2025-11-26
版本: 1.0.0
"""

import asyncio
import logging
import time
import traceback
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, Optional

import pandas as pd

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """错误严重程度枚举"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """错误分类枚举"""

    DATABASE = "database"
    NETWORK = "network"
    VALIDATION = "validation"
    SYSTEM = "system"
    BUSINESS = "business"
    TIMEOUT = "timeout"
    RESOURCE = "resource"


class RetryableError(Exception):
    """可重试错误基类"""

    def __init__(
        self,
        message: str,
        category: ErrorCategory,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    ):
        super().__init__(message)
        self.category = category
        self.severity = severity
        self.retry_count = 0


class NonRetryableError(Exception):
    """不可重试错误基类"""

    def __init__(
        self,
        message: str,
        category: ErrorCategory,
        severity: ErrorSeverity = ErrorSeverity.HIGH,
    ):
        super().__init__(message)
        self.category = category
        self.severity = severity


class DatabaseConnectionError(RetryableError):
    """数据库连接错误"""

    def __init__(self, message: str):
        super().__init__(message, ErrorCategory.DATABASE, ErrorSeverity.HIGH)


class DatabaseQueryError(RetryableError):
    """数据库查询错误"""

    def __init__(self, message: str):
        super().__init__(message, ErrorCategory.DATABASE, ErrorSeverity.MEDIUM)


class NetworkTimeoutError(RetryableError):
    """网络超时错误"""

    def __init__(self, message: str):
        super().__init__(message, ErrorCategory.TIMEOUT, ErrorSeverity.MEDIUM)


class ValidationError(NonRetryableError):
    """数据验证错误"""

    def __init__(self, message: str):
        super().__init__(message, ErrorCategory.VALIDATION, ErrorSeverity.MEDIUM)


class ResourceExhaustionError(RetryableError):
    """资源耗尽错误"""

    def __init__(self, message: str):
        super().__init__(message, ErrorCategory.RESOURCE, ErrorSeverity.HIGH)


class ErrorRecoveryStrategy:
    """错误恢复策略"""

    @staticmethod
    def exponential_backoff(
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
    ) -> Callable[[int], float]:
        """指数退避策略"""

        def delay_func(attempt: int) -> float:
            delay = min(base_delay * (backoff_factor**attempt), max_delay)
            if jitter:
                delay *= 0.5 + (hash(attempt) % 100) / 200.0  # 添加抖动
            return delay

        return delay_func

    @staticmethod
    def linear_backoff(
        base_delay: float = 1.0, increment: float = 0.5, max_delay: float = 10.0
    ) -> Callable[[int], float]:
        """线性退避策略"""

        def delay_func(attempt: int) -> float:
            delay = min(base_delay + increment * attempt, max_delay)
            return delay

        return delay_func


class ErrorHandler:
    """错误处理器"""

    def __init__(self, enable_logging: bool = True, enable_metrics: bool = True):
        self.enable_logging = enable_logging
        self.enable_metrics = enable_metrics
        self.error_stats: Dict[str, Dict[str, int]] = {}

    def log_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        attempt: Optional[int] = None,
    ) -> None:
        """记录错误"""
        if not self.enable_logging:
            return

        error_type = type(error).__name__
        timestamp = datetime.now().isoformat()

        # 更新错误统计
        if error_type not in self.error_stats:
            self.error_stats[error_type] = {
                "total": 0,
                ErrorSeverity.LOW.value: 0,
                ErrorSeverity.MEDIUM.value: 0,
                ErrorSeverity.HIGH.value: 0,
                ErrorSeverity.CRITICAL.value: 0,
            }

        self.error_stats[error_type]["total"] += 1

        # 记录严重程度
        if hasattr(error, "severity"):
            self.error_stats[error_type][error.severity.value] += 1
            severity = error.severity.value
        else:
            severity = ErrorSeverity.MEDIUM.value
            self.error_stats[error_type][ErrorSeverity.MEDIUM.value] += 1

        # 记录分类
        category = getattr(error, "category", "unknown")

        log_message = (
            f"[{timestamp}] ERROR [{severity}] [{category}] {error_type}: {str(error)}"
        )

        if attempt is not None:
            log_message += f" (attempt {attempt})"

        if context:
            log_message += f" | Context: {context}"

        # 记录堆栈跟踪
        if severity in [ErrorSeverity.HIGH.value, ErrorSeverity.CRITICAL.value]:
            log_message += f"\nStack trace:\n{traceback.format_exc()}"

        logger.error(log_message)

    def get_error_stats(self) -> Dict[str, Any]:
        """获取错误统计"""
        return {
            "timestamp": datetime.now().isoformat(),
            "error_stats": self.error_stats.copy(),
            "total_errors": sum(stats["total"] for stats in self.error_stats.values()),
        }

    def reset_stats(self) -> None:
        """重置错误统计"""
        self.error_stats.clear()


# 全局错误处理器实例
_global_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """获取全局错误处理器实例"""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()
    return _global_error_handler


def handle_errors(
    max_attempts: int = 3,
    delay_strategy: Optional[Callable[[int], float]] = None,
    retry_on: Optional[tuple] = None,
    fallback_value: Any = None,
    catch_exceptions: tuple = (Exception,),
    reraise: bool = False,
    context: Optional[Dict[str, Any]] = None,
):
    """
    错误处理装饰器

    Args:
        max_attempts: 最大重试次数
        delay_strategy: 延迟策略函数
        retry_on: 指定重试的异常类型
        fallback_value: 失败时的回退值
        catch_exceptions: 捕获的异常类型
        reraise: 是否重新抛出异常
        context: 错误上下文信息
    """
    if delay_strategy is None:
        delay_strategy = ErrorRecoveryStrategy.exponential_backoff()

    if retry_on is None:
        retry_on = (RetryableError,)

    def decorator(func):
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            error_handler = get_error_handler()
            last_error = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except catch_exceptions as e:
                    last_error = e

                    # 记录错误
                    error_handler.log_error(e, context, attempt + 1)

                    # 检查是否应该重试
                    if attempt < max_attempts - 1 and isinstance(e, retry_on):
                        # 计算延迟
                        delay = delay_strategy(attempt)
                        logger.warning(
                            f"Retrying {func.__name__} in {delay:.2f}s (attempt {attempt + 1}/{max_attempts})"
                        )
                        time.sleep(delay)
                        continue
                    else:
                        # 不重试，使用回退值或抛出异常
                        if fallback_value is not None:
                            logger.warning(f"Using fallback value for {func.__name__}")
                            return fallback_value
                        elif reraise:
                            raise
                        else:
                            logger.error(
                                f"Failed to execute {func.__name__} after {max_attempts} attempts"
                            )
                            return None

            return None

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            error_handler = get_error_handler()
            last_error = None

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except catch_exceptions as e:
                    last_error = e

                    # 记录错误
                    error_handler.log_error(e, context, attempt + 1)

                    # 检查是否应该重试
                    if attempt < max_attempts - 1 and isinstance(e, retry_on):
                        # 计算延迟
                        delay = delay_strategy(attempt)
                        logger.warning(
                            f"Retrying {func.__name__} in {delay:.2f}s (attempt {attempt + 1}/{max_attempts})"
                        )
                        await asyncio.sleep(delay)
                        continue
                    else:
                        # 不重试，使用回退值或抛出异常
                        if fallback_value is not None:
                            logger.warning(f"Using fallback value for {func.__name__}")
                            return fallback_value
                        elif reraise:
                            raise
                        else:
                            logger.error(
                                f"Failed to execute {func.__name__} after {max_attempts} attempts"
                            )
                            return None

            return None

        # 根据函数是否是协程返回相应的包装器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class CircuitBreaker:
    """熔断器"""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = Exception,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.state == "OPEN":
                if self._should_attempt_reset():
                    self.state = "HALF_OPEN"
                else:
                    raise Exception("Circuit breaker is OPEN")

            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure()
                raise e

        return wrapper

    def _should_attempt_reset(self) -> bool:
        return (
            self.last_failure_time
            and time.time() - self.last_failure_time >= self.recovery_timeout
        )

    def _on_success(self) -> None:
        self.failure_count = 0
        self.state = "CLOSED"

    def _on_failure(self) -> None:
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


def validate_dataframe(
    df: pd.DataFrame,
    required_columns: Optional[list] = None,
    min_rows: int = 0,
    max_empty_ratio: float = 0.5,
) -> bool:
    """
    验证DataFrame

    Args:
        df: 要验证的DataFrame
        required_columns: 必需的列
        min_rows: 最小行数
        max_empty_ratio: 最大空值比例

    Returns:
        bool: 验证是否通过
    """
    if df is None or df.empty:
        if min_rows > 0:
            raise ValidationError("DataFrame为空或为None")
        return True

    # 检查行数
    if len(df) < min_rows:
        raise ValidationError(f"DataFrame行数({len(df)})小于最小要求({min_rows})")

    # 检查必需列
    if required_columns:
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValidationError(f"DataFrame缺少必需列: {missing_columns}")

    # 检查空值比例
    if max_empty_ratio < 1.0:
        total_cells = len(df) * len(df.columns)
        empty_cells = df.isnull().sum().sum()
        empty_ratio = empty_cells / total_cells if total_cells > 0 else 1.0

        if empty_ratio > max_empty_ratio:
            raise ValidationError(
                f"DataFrame空值比例({empty_ratio:.2f})超过限制({max_empty_ratio:.2f})"
            )

    return True


def safe_execute(
    func: Callable, *args, default_return: Any = None, log_errors: bool = True, **kwargs
) -> Any:
    """
    安全执行函数

    Args:
        func: 要执行的函数
        *args: 位置参数
        default_return: 默认返回值
        log_errors: 是否记录错误
        **kwargs: 关键字参数

    Returns:
        Any: 函数结果或默认返回值
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_errors:
            error_handler = get_error_handler()
            error_handler.log_error(
                e, {"function": func.__name__, "args": args, "kwargs": kwargs}
            )
        return default_return


if __name__ == "__main__":
    print("测试错误处理系统...")

    # 测试错误处理器
    handler = get_error_handler()

    # 测试重试机制
    @handle_errors(max_attempts=3, fallback_value="fallback")
    def test_retry_function(should_fail: bool = True):
        if should_fail:
            raise RetryableError("测试错误", ErrorCategory.DATABASE)
        return "success"

    # 第一次调用失败，使用回退值
    result = test_retry_function(True)
    print(f"重试测试结果: {result}")

    # 第二次调用成功
    result = test_retry_function(False)
    print(f"成功测试结果: {result}")

    # 显示错误统计
    stats = handler.get_error_stats()
    print(f"\n错误统计: {stats}")

    print("\n错误处理系统基础功能已实现")
    print("主要功能:")
    print("  - 错误分类和严重程度")
    print("  - 指数退避和线性退避策略")
    print("  - 重试机制和回退值")
    print("  - 熔断器模式")
    print("  - DataFrame验证")
    print("  - 错误统计和监控")
    print("  - 安全执行包装器")
