"""
# 功能：统一数据源接口定义，所有数据源适配器必须实现此接口
# 作者：JohnC (ninjas@sina.com) & Claude
# 创建日期：2025-10-16
# 版本：2.1.0
# 依赖：详见requirements.txt或文件导入部分
# 注意事项：
#   本文件是MyStocks v2.1核心组件，遵循5-tier数据分类架构
# 版权：MyStocks Project © 2025
"""

import abc
import pandas as pd
from typing import Dict, List, Optional, Any


class IDataSource(abc.ABC):
    """统一数据接口：定义所有数据源必须实现的方法"""

    @abc.abstractmethod
    def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取股票日线数据

        Args:
            symbol: 股票代码
            start_date: 开始日期，格式：YYYY-MM-DD
            end_date: 结束日期，格式：YYYY-MM-DD

        Returns:
            DataFrame: 包含股票日线数据的DataFrame
                列包括: date, open, high, low, close, volume
        """
        pass

    @abc.abstractmethod
    def get_index_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取指数日线数据

        Args:
            symbol: 指数代码
            start_date: 开始日期，格式：YYYY-MM-DD
            end_date: 结束日期，格式：YYYY-MM-DD

        Returns:
            DataFrame: 包含指数日线数据的DataFrame
                列包括: date, open, high, low, close, volume
        """
        pass

    @abc.abstractmethod
    def get_stock_basic(self, symbol: str) -> Dict[str, Any]:
        """
        获取股票基本信息

        Args:
            symbol: 股票代码

        Returns:
            Dict[str, Any]: 包含股票基本信息的字典
                键包括: symbol, name, industry, market, list_date等
        """
        pass

    @abc.abstractmethod
    def get_index_components(self, symbol: str) -> List[str]:
        """
        获取指数成分股

        Args:
            symbol: 指数代码

        Returns:
            List[str]: 包含指数成分股代码的列表
        """
        pass

    @abc.abstractmethod
    def get_real_time_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        获取实时数据

        Args:
            symbol: 股票代码

        Returns:
            Optional[Dict[str, Any]]: 实时数据字典或None
                键包括: symbol, price, volume, timestamp等
        """
        pass

    @abc.abstractmethod
    def get_market_calendar(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取交易日历

        Args:
            start_date: 开始日期，格式：YYYY-MM-DD
            end_date: 结束日期，格式：YYYY-MM-DD

        Returns:
            pd.DataFrame: 交易日历数据
                列包括: date, is_trading_day, market
        """
        pass

    @abc.abstractmethod
    def get_financial_data(self, symbol: str, period: str = "annual") -> pd.DataFrame:
        """
        获取财务数据

        Args:
            symbol: 股票代码
            period: 报告期间，"annual"或"quarterly"

        Returns:
            pd.DataFrame: 财务数据
                列包括: symbol, end_date, revenue, net_profit等
        """
        pass

    @abc.abstractmethod
    def get_news_data(self, symbol: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取新闻数据

        Args:
            symbol: 股票代码，为None时获取市场新闻
            limit: 返回数量限制

        Returns:
            List[Dict[str, Any]]: 新闻数据列表
                每个字典包含: title, content, timestamp, source等
        """
        pass
