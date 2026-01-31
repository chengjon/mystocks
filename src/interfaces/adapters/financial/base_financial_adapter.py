"""
# 功能：基础财务适配器
# 作者：MyStocks Project
# 创建日期：2025-12-20
# 版本：1.0.0
# 说明：财务适配器的基础类和共享组件
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import pandas as pd
import sys
from datetime import datetime
from loguru import logger

from src.interfaces.data_source import IDataSource
from src.utils import symbol_utils


class BaseFinancialAdapter(IDataSource, ABC):
    """
    基础财务适配器抽象类

    提供财务数据适配器的通用功能和接口
    """

    def __init__(self):
        self._cache = {}
        self._data_sources = {}

        # 配置loguru
        logger.remove()  # 移除默认的日志处理器
        logger.add(
            sys.stdout,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
            level="INFO",
        )
        logger.add(
            "financial_adapter.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
            level="INFO",
            encoding="utf-8",
            rotation="10 MB",
        )

    def _get_cache_key(self, symbol: str, data_type: str, **kwargs) -> str:
        """生成缓存键"""
        key_parts = [symbol, data_type]
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")
        return "|".join(key_parts)

    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """从缓存获取数据"""
        return self._cache.get(cache_key)

    def _save_to_cache(self, cache_key: str, data: Any) -> None:
        """保存数据到缓存"""
        self._cache[cache_key] = data

    def _validate_symbol(self, symbol: str) -> bool:
        """验证股票代码格式"""
        return symbol_utils.is_valid_stock_code(symbol)

    def _validate_date_range(self, start_date: str, end_date: str) -> bool:
        """验证日期范围"""
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            return start <= end
        except ValueError:
            return False

    def _standardize_column_names(self, data: pd.DataFrame) -> pd.DataFrame:
        """标准化列名"""
        column_mapping = {
            "日期": "trade_date",
            "股票代码": "symbol",
            "开盘价": "open",
            "最高价": "high",
            "最低价": "low",
            "收盘价": "close",
            "成交量": "volume",
            "成交额": "amount",
        }
        return data.rename(columns=column_mapping)

    @abstractmethod
    def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取股票日线数据 - 抽象方法"""
        pass

    @abstractmethod
    def get_financial_report(self, symbol: str, report_type: str, period: str) -> Dict:
        """获取财务报告 - 抽象方法"""
        pass
