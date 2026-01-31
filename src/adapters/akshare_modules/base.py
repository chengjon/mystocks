# pylint: disable=all
"""
AkShare适配器基础模块

提供API调用重试机制和通用工具函数
"""

import asyncio
import logging
from functools import wraps
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


def _retry_api_call(max_retries: int = 3, delay: float = 1):
    """
    API调用重试装饰器工厂函数

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

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        # 指数退避
                        import time
                        time.sleep(delay * (2**attempt))
                        continue
            raise last_exception

        # 根据函数是否是异步的来决定使用哪个包装器
        import inspect
        if inspect.iscoroutinefunction(func):
            return wrapper
        return sync_wrapper

    return decorator


class ColumnMapper:
    """列名映射器 - 中英文列名互转"""

    # 通用列名映射
    COLUMN_MAPPING = {
        # 英文 -> 中文
        "date": "日期",
        "time": "时间",
        "open": "开盘价",
        "high": "最高价",
        "low": "最低价",
        "close": "收盘价",
        "volume": "成交量",
        "amount": "成交额",
        "symbol": "股票代码",
        "name": "股票名称",
        # 中文 -> 英文
        "日期": "date",
        "股票代码": "symbol",
        "股票名称": "name",
        "开盘价": "open",
        "最高价": "high",
        "最低价": "low",
        "收盘价": "close",
        "涨跌幅": "change_percent",
        "成交量": "volume",
        "成交额": "amount",
    }

    @classmethod
    def to_english(cls, df) -> None:
        """将DataFrame的中文列名转换为英文列名（原地修改）"""
        if df is None or df.empty:
            return
        rename_dict = {}
        for col in df.columns:
            if col in cls.COLUMN_MAPPING:
                rename_dict[col] = cls.COLUMN_MAPPING[col]
        if rename_dict:
            df.rename(columns=rename_dict, inplace=True)

    @classmethod
    def to_chinese(cls, df) -> None:
        """将DataFrame的英文列名转换为中文列名（原地修改）"""
        if df is None or df.empty:
            return
        # 创建反向映射
        reverse_mapping = {v: k for k, v in cls.COLUMN_MAPPING.items() if k in df.columns}
        if reverse_mapping:
            df.rename(columns=reverse_mapping, inplace=True)


def get_column_mapper() -> ColumnMapper:
    """获取列映射器实例"""
    return ColumnMapper()
