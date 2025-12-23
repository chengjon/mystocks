"""
数据源调用日志记录模块
提供统一的数据源调用日志记录功能
"""

import logging
import time
from functools import wraps
from typing import Any, Callable, Dict


class DataSourceLogger:
    """数据源调用日志记录器"""

    def __init__(self, name: str = "DataSource"):
        """初始化日志记录器"""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # 避免重复添加处理器
        if not self.logger.handlers:
            # 创建控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)

            # 创建文件处理器
            file_handler = logging.FileHandler("data_source_calls.log")
            file_handler.setLevel(logging.INFO)

            # 创建格式器
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)

            # 添加处理器到logger
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)

    def log_call(
        self, adapter_type: str, method: str, params: Dict, result: Any, duration: float
    ):
        """记录数据源调用"""
        success = (
            result is not None
            and not isinstance(result, str)
            or (isinstance(result, str) and not result.startswith("Error"))
        )
        self.logger.info(
            f"Adapter Call: {adapter_type}.{method} "
            f"Params: {params} "
            f"Success: {success} "
            f"Duration: {duration:.3f}s"
        )

    def log_error(self, adapter_type: str, method: str, params: Dict, error: str):
        """记录数据源调用错误"""
        self.logger.error(
            f"Adapter Error: {adapter_type}.{method} Params: {params} Error: {error}"
        )


# 全局日志记录器实例
data_source_logger = DataSourceLogger()


def log_data_source_call(adapter_type: str):
    """数据源调用日志装饰器"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            # 记录调用参数
            params = {
                "args": args[1:] if len(args) > 1 else (),  # 排除self参数
                "kwargs": kwargs,
            }

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                # 记录成功的调用
                data_source_logger.log_call(
                    adapter_type=adapter_type,
                    method=func.__name__,
                    params=params,
                    result=result,
                    duration=duration,
                )

                return result
            except Exception as e:
                duration = time.time() - start_time

                # 记录错误
                data_source_logger.log_error(
                    adapter_type=adapter_type,
                    method=func.__name__,
                    params=params,
                    error=str(e),
                )

                raise e

        return wrapper

    return decorator


def log_data_source_method(adapter_type: str, method_name: str):
    """记录特定方法调用的装饰器"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            # 提取参数信息
            params = {}
            if func.__name__ == "get_data_from_adapter":
                if len(args) >= 3:
                    params = {
                        "adapter_type": args[1]
                        if len(args) > 1
                        else kwargs.get("adapter_type"),
                        "method": args[2] if len(args) > 2 else kwargs.get("method"),
                        "kwargs": kwargs,
                    }
            else:
                params = {"args": args[1:] if len(args) > 1 else (), "kwargs": kwargs}

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                # 根据结果类型判断成功与否
                success = True
                if isinstance(result, str) and (
                    result.startswith("Error") or result.startswith("失败")
                ):
                    success = False
                elif (
                    hasattr(result, "__len__")
                    and len(result) == 0
                    and method_name != "get_indicator_data"
                ):
                    success = False
                elif result is None:
                    success = False

                data_source_logger.logger.info(
                    f"DS Call: {adapter_type}.{method_name} "
                    f"Success: {success} "
                    f"Duration: {duration:.3f}s "
                    f"Params: {params if len(str(params)) < 200 else str(params)[:200] + '...'}"
                )

                return result
            except Exception as e:
                duration = time.time() - start_time
                data_source_logger.logger.error(
                    f"DS Error: {adapter_type}.{method_name} "
                    f"Duration: {duration:.3f}s "
                    f"Error: {str(e)} "
                    f"Params: {params if len(str(params)) < 200 else str(params)[:200] + '...'}"
                )
                raise e

        return wrapper

    return decorator
