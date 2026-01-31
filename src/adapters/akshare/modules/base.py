"""
Market Data Adapter - 基础模块和重试装饰器

提供统一的API调用重试机制和列名映射工具
"""

import asyncio
import functools
import logging
from typing import Callable, Optional, Dict, Any

logger = logging.getLogger(__name__)


# ============================================================================
# 重试装饰器
# ============================================================================


def retry_api_call(max_retries: int = 3, delay: int = 1):
    """
    API调用重试装饰器

    提供自动重试机制，处理网络错误和API限流

    Args:
        max_retries: 最大重试次数
        delay: 重试延迟（秒）

    Returns:
        装饰器函数

    Example:
        @retry_api_call(max_retries=3, delay=2)
        async def fetch_data():
            return await ak.stock_daily(symbol="600000")
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception: Optional[Exception] = None

            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning("[Retry] API调用失败 (尝试 {attempt + 1}/%(max_retries)s): %(e)s")

                    if attempt < max_retries - 1:
                        # 指数退避策略，避免同时重试导致限流
                        await asyncio.sleep(delay * (2**attempt))
                    else:
                        logger.error("[Retry] 所有重试失败: %(e)s")
                        break

            if last_exception:
                raise last_exception

        return wrapper

    return decorator


# ============================================================================
# 列名映射器
# ============================================================================


class ColumnMapper:
    """
    列名映射管理类

    提供统一的列名映射，处理不同数据源的列名差异
    支持列名标准化和反向映射
    """

    def __init__(self):
        """初始化列名映射器"""
        self._mappings: Dict[str, Dict[str, str]] = {}
        self._load_default_mappings()

    def _load_default_mappings(self):
        """加载默认的列名映射"""
        # 通用数据字段映射
        self._mappings.update(
            {
                "common": {
                    "symbol": ["代码", "symbol", "stock_code", "股票代码"],
                    "name": ["名称", "name", "stock_name", "股票名称"],
                    "price": ["最新价", "price", "close", "收盘价"],
                    "volume": ["成交量", "volume", "量"],
                    "amount": ["成交额", "amount", "成交金额"],
                    "change": ["涨跌幅", "change_percent", "涨跌"],
                    "change_amount": ["涨跌额", "change", "涨跌额"],
                    "date": ["日期", "date", "交易日期"],
                    "time": ["时间", "time", "timestamp"],
                },
                "market_data": {
                    "index_code": ["指数代码", "index_code", "指数"],
                    "index_name": ["指数名称", "index_name", "指数名称"],
                    "sector": ["行业", "sector", "行业名称"],
                    "total_market_value": ["总市值", "total_market_value", "市值"],
                    "turnover_rate": ["换手率", "turnover_rate", "换手率"],
                },
                "financial": {
                    "pe_ratio": ["市盈率", "pe", "pe_ratio", "市盈率"],
                    "pb_ratio": ["市净率", "pb", "pb_ratio", "市净率"],
                    "roe": ["净资产收益率", "roe", "净资产收益率"],
                    "roa": ["总资产报酬率", "roa", "总资产报酬率"],
                    "revenue": ["营业收入", "revenue", "营业总收入"],
                    "profit": ["净利润", "profit", "净利润"],
                },
            }
        )

    def register_mapping(self, category: str, mappings: Dict[str, str]):
        """
        注册新的列名映射

        Args:
            category: 映射类别（如"common", "market_data", "financial"）
            mappings: 列名映射字典
        """
        if category not in self._mappings:
            self._mappings[category] = {}

        self._mappings[category].update(mappings)
        logger.info("[ColumnMapper] 注册列名映射: %s, %s 项", category, len(mappings))

    def get_standard_name(self, category: str, raw_name: str) -> Optional[str]:
        """
        获取标准化的列名

        Args:
            category: 映射类别
            raw_name: 原始列名

        Returns:
            标准化列名，未找到返回None
        """
        if category not in self._mappings:
            logger.warning("[ColumnMapper] 未知的映射类别: %(category)s")
            return None

        for standard_name, raw_names in self._mappings[category].items():
            if raw_name in raw_names:
                return standard_name

        return None

    def standardize_dataframe(self, df: Any, category: str = "common") -> Any:
        """
        标准化DataFrame列名

        Args:
            df: 输入DataFrame
            category: 映射类别

        Returns:
            标准化后的DataFrame
        """
        if category not in self._mappings:
            logger.warning("[ColumnMapper] 未知的映射类别: %(category)s")
            return df

        try:
            import pandas as pd

            if not isinstance(df, pd.DataFrame):
                return df

            df = df.copy()

            # 创建重命名映射
            rename_dict = {}
            for standard_name, raw_names in self._mappings[category].items():
                for raw_name in raw_names:
                    if raw_name in df.columns:
                        rename_dict[raw_name] = standard_name

            # 执行重命名
            if rename_dict:
                df = df.rename(columns=rename_dict)
                logger.debug("[ColumnMapper] 标准化列名: %s 列", len(rename_dict))

            return df
        except Exception as e:
            logger.error("[ColumnMapper] 标准化失败: %s", e)
            return df

    def get_available_categories(self) -> list:
        """获取所有可用的映射类别"""
        return list(self._mappings.keys())

    def export_mappings(self) -> Dict[str, Dict[str, str]]:
        """
        导出所有列名映射

        Returns:
            映射字典
        """
        return self._mappings


# ============================================================================
# 导出函数
# ============================================================================


__all__ = [
    "retry_api_call",
    "ColumnMapper",
]

# 全局列名映射器实例（单例模式）
_global_column_mapper = None


def get_column_mapper() -> ColumnMapper:
    """
    获取全局列名映射器实例

    Returns:
        ColumnMapper 实例
    """
    global _global_column_mapper
    if _global_column_mapper is None:
        _global_column_mapper = ColumnMapper()
        logger.debug("[ColumnMapper] 创建全局列名映射器实例")
    return _global_column_mapper
