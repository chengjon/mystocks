"""
统一数据管理器
作为系统的门户，提供简洁的API

作用：
- 统一数据管理器，系统的核心组件
- 作为系统的门户，提供简洁的API
- 协调不同数据源的使用
- 管理数据源实例的生命周期

功能：
- 提供数据源切换和比较功能
- 处理日期和股票代码的标准化
- 简化数据获取的过程
- 提供额外的功能，如数据源比较、代码和日期格式化等
"""

import pandas as pd
from typing import Dict, List, Optional, Union
import sys
import os
import datetime

# 将当前目录的父目录的父目录添加到模块搜索路径中
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from mystocks.interfaces.data_source import IDataSource
from mystocks.factory.data_source_factory import DataSourceFactory
from mystocks.utils.date_utils import normalize_date, get_date_range
from mystocks.utils.symbol_utils import normalize_stock_code, normalize_index_code


class UnifiedDataManager:
    """统一数据管理器：协调数据获取，提供高级功能"""

    def __init__(self):
        """初始化统一数据管理器"""
        self.sources = {}  # 缓存已创建的数据源实例
        self.default_source = "akshare"  # 默认数据源改为Akshare（更稳定）

    def set_default_source(self, source_type: str) -> None:
        """
        设置默认数据源

        Args:
            source_type: 数据源类型名称
        """
        self.default_source = source_type
        print(f"默认数据源已设置为: {source_type}")

    def get_source(self, source_type: Optional[str] = None) -> IDataSource:
        """
        获取数据源实例

        Args:
            source_type: 数据源类型，如果为None则使用默认数据源

        Returns:
            IDataSource: 数据源实例
        """
        if source_type is None:
            source_type = self.default_source

        # 如果数据源实例不存在，则创建
        if source_type not in self.sources:
            self.sources[source_type] = DataSourceFactory.create_source(source_type)

        return self.sources[source_type]

    def get_stock_daily(
        self,
        symbol: str,
        start_date: Union[str, datetime.date],
        end_date: Union[str, datetime.date, None] = None,
        days: Optional[int] = None,
        source_type: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        获取股票日线数据（统一接口）

        Args:
            symbol: 股票代码 (支持多种格式)
            start_date: 开始日期 (支持多种格式)
            end_date: 结束日期 (支持多种格式)，如果为None且提供了days，则自动计算
            days: 从开始日期算起的天数 (可选)
            source_type: 数据源类型，如果为None则使用默认数据源

        Returns:
            DataFrame: 包含股票日线数据的DataFrame
        """
        # 标准化股票代码
        std_symbol = normalize_stock_code(symbol)

        # 标准化日期范围
        start, end = get_date_range(start_date, end_date, days)

        # 获取数据
        source = self.get_source(source_type)
        return source.get_stock_daily(std_symbol, start, end)

    def get_index_daily(
        self,
        symbol: str,
        start_date: Union[str, datetime.date],
        end_date: Union[str, datetime.date, None] = None,
        days: Optional[int] = None,
        source_type: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        获取指数日线数据（统一接口）

        Args:
            symbol: 指数代码 (支持多种格式)
            start_date: 开始日期 (支持多种格式)
            end_date: 结束日期 (支持多种格式)，如果为None且提供了days，则自动计算
            days: 从开始日期算起的天数 (可选)
            source_type: 数据源类型，如果为None则使用默认数据源

        Returns:
            DataFrame: 包含指数日线数据的DataFrame
        """
        # 标准化指数代码
        std_symbol = normalize_index_code(symbol)

        # 标准化日期范围
        start, end = get_date_range(start_date, end_date, days)

        # 获取数据
        source = self.get_source(source_type)
        return source.get_index_daily(std_symbol, start, end)

    def get_stock_basic(self, symbol: str, source_type: Optional[str] = None) -> Dict:
        """
        获取股票基本信息（统一接口）

        Args:
            symbol: 股票代码 (支持多种格式)
            source_type: 数据源类型，如果为None则使用默认数据源

        Returns:
            Dict: 包含股票基本信息的字典
        """
        # 标准化股票代码
        std_symbol = normalize_stock_code(symbol)

        # 获取数据
        source = self.get_source(source_type)
        return source.get_stock_basic(std_symbol)

    def get_index_components(
        self, symbol: str, source_type: Optional[str] = None
    ) -> List[str]:
        """
        获取指数成分股（统一接口）

        Args:
            symbol: 指数代码 (支持多种格式)
            source_type: 数据源类型，如果为None则使用默认数据源

        Returns:
            List[str]: 包含指数成分股代码的列表
        """
        # 标准化指数代码
        std_symbol = normalize_index_code(symbol)

        # 获取数据
        source = self.get_source(source_type)
        return source.get_index_components(std_symbol)

    def compare_data_sources(self, symbol: str, start_date: str, end_date: str):
        """
        比较两个数据源的数据

        Args:
            symbol: 股票代码 (支持多种格式)
            start_date: 开始日期 (支持多种格式)
            end_date: 结束日期 (支持多种格式)
        """
        # 标准化股票代码和日期
        std_symbol = normalize_stock_code(symbol)
        start = normalize_date(start_date)
        end = normalize_date(end_date)

        print(f"\n===== 数据源比较: {std_symbol} =====")

        # 从Akshare获取数据
        ak_data = self.get_stock_daily(std_symbol, start, end, source_type="akshare")
        print(f"Akshare 数据行数: {len(ak_data)}")

        # 从Baostock获取数据
        bs_data = self.get_stock_daily(std_symbol, start, end, source_type="baostock")
        print(f"Baostock 数据行数: {len(bs_data)}")

        # 显示前几行数据
        if not ak_data.empty:
            print("\nAkshare 数据前5行:")
            print(ak_data.head())

        if not bs_data.empty:
            print("\nBaostock 数据前5行:")
            print(bs_data.head())

    def get_financial_data(
        self, symbol: str, period: str = "annual", source_type: Optional[str] = None
    ) -> pd.DataFrame:
        """
        获取股票财务数据（统一接口）

        Args:
            symbol: 股票代码 (支持多种格式)
            period: 报告期类型 ("annual" 或 "quarterly")
            source_type: 数据源类型，如果为None则使用默认数据源

        Returns:
            DataFrame: 包含股票财务数据的DataFrame
        """
        # 标准化股票代码
        std_symbol = normalize_stock_code(symbol)

        # 获取数据
        source = self.get_source(source_type)
        # 检查数据源是否支持财务数据获取
        if hasattr(source, "get_financial_data"):
            return source.get_financial_data(std_symbol, period)
        else:
            print(
                f"[警告] 数据源 {source_type if source_type else self.default_source} 不支持财务数据获取"
            )
            return pd.DataFrame()
