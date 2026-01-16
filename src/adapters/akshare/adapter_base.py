"""
AkShare适配器基础模块

提供抽象基类和通用工具函数，包括：
- API调用重试装饰器
- 适配器基类
- 通用数据标准化函数
"""

import logging
from typing import Callable, Any
import asyncio
from functools import wraps

logger = logging.getLogger(__name__)


def retry_api_call(max_retries: int = 3, delay: float = 1):
    """
    API调用重试装饰器

    Args:
        max_retries: 最大重试次数
        delay: 初始延迟时间（秒）

    Returns:
        装饰器函数
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        # 指数退避
                        await asyncio.sleep(delay * (2**attempt))
                        continue
            raise last_exception

        return wrapper

    return decorator


class BaseAkshareAdapter:
    """
    AkShare适配器基类

    提供通用的适配器功能，包括：
    - 日志记录
    - 重试机制
    - 错误处理
    """

    def __init__(self):
        """初始化适配器"""
        self.logger = logging.getLogger(self.__class__.__name__)

    def _standardize_columns(self, df, column_mapping: dict) -> None:
        """
        标准化DataFrame列名

        Args:
            df: pandas DataFrame
            column_mapping: 列名映射字典 {原列名: 新列名}
        """
        if df is None or df.empty:
            return
        df.rename(columns=column_mapping, inplace=True)

    def _add_timestamp(self, df) -> None:
        """添加查询时间戳"""
        if df is not None and not df.empty:
            df["query_timestamp"] = pd.Timestamp.now()

    async def _safe_api_call(self, api_func: Callable, *args, **kwargs) -> Any:
        """
        安全调用API函数，包含错误处理

        Args:
            api_func: API函数
            *args: 位置参数
            **kwargs: 关键字参数

        Returns:
            API返回结果
        """
        try:
            return api_func(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"API调用失败: {str(e)}", exc_info=True)
            raise


# 延迟导入pandas以避免循环依赖
def __getattr__(name: str):
    if name == "pd":
        import pandas as pd

        globals()[name] = pd
        return pd
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
