"""
统一错误处理工具
提供一致的错误处理策略和日志记录功能
"""

import logging
import time
from functools import wraps
from typing import Any, Callable

# 配置日志
logger = logging.getLogger(__name__)


class UnifiedErrorHandler:
    """
    统一错误处理器

    提供一致的错误处理策略，包括重试机制、日志记录和错误转换
    """

    @staticmethod
    def log_error(
        error: Exception, context: str = "", level: int = logging.ERROR
    ) -> None:
        """
        统一日志记录

        Args:
            error: 异常对象
            context: 错误上下文
            level: 日志级别
        """
        logger.log(
            level,
            f"错误发生 - 上下文: {context}, 错误: {str(error)}, 类型: {type(error).__name__}",
        )

    @staticmethod
    def safe_execute(
        func: Callable,
        context: str = "",
        default_return: Any = None,
        log_error: bool = True,
        reraise: bool = False,
    ) -> Any:
        """
        安全执行函数

        Args:
            func: 要执行的函数
            context: 执行上下文
            default_return: 默认返回值
            log_error: 是否记录错误
            reraise: 是否重新抛出异常

        Returns:
            函数返回值或默认返回值
        """
        try:
            return func()
        except Exception as e:
            if log_error:
                UnifiedErrorHandler.log_error(e, context)

            if reraise:
                raise

            return default_return

    @staticmethod
    def retry_on_failure(
        max_retries: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
        exceptions: tuple = (Exception,),
        context: str = "",
    ):
        """
        重试装饰器

        Args:
            max_retries: 最大重试次数
            delay: 初始延迟时间
            backoff: 延迟倍数
            exceptions: 需要重试的异常类型
            context: 执行上下文
        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                last_exception = None
                current_delay = delay

                for attempt in range(1, max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        UnifiedErrorHandler.log_error(
                            e, f"{context} - 第{attempt}次尝试失败"
                        )

                        if attempt < max_retries:
                            time.sleep(current_delay)
                            current_delay *= backoff
                        else:
                            UnifiedErrorHandler.log_error(
                                e, f"{context} - 所有重试均已失败"
                            )

                # 所有重试都失败，重新抛出最后一个异常
                raise last_exception

            return wrapper

        return decorator


# 便捷函数
def safe_execute(func: Callable, context: str = "", default_return: Any = None):
    """安全执行函数的便捷函数"""
    return UnifiedErrorHandler.safe_execute(func, context, default_return)


def retry_on_failure(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
    context: str = "",
):
    """重试装饰器的便捷函数"""
    return UnifiedErrorHandler.retry_on_failure(
        max_retries, delay, backoff, exceptions, context
    )


# 统一错误类型
class DataError(Exception):
    """数据相关错误"""

    pass


class ConnectionError(Exception):
    """连接相关错误"""

    pass


class ValidationError(Exception):
    """验证相关错误"""

    pass


class ProcessingError(Exception):
    """处理相关错误"""

    pass
