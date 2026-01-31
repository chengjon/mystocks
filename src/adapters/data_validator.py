"""
数据校验器 - 从 financial_adapter.py 拆分
职责：数据格式验证、完整性检查、业务规则验证
遵循 TDD 原则：仅实现满足测试的最小功能
"""

import re
from datetime import datetime
from typing import List

import pandas as pd


class DataValidator:
    """数据校验器 - 专注于数据质量验证"""

    def __init__(self):
        """初始化数据校验器"""

    def validate_stock_symbol(self, symbol: str) -> bool:
        """
        验证股票代码格式

        Args:
            symbol: 股票代码

        Returns:
            bool: 验证结果
        """
        if not symbol or not isinstance(symbol, str):
            return False

        # 移除空格
        symbol = symbol.strip()

        # A股代码格式：6位数字
        if re.match(r"^[0-9]{6}$", symbol):
            return True

        return False

    def validate_date_format(self, date_str: str) -> bool:
        """
        验证日期格式

        Args:
            date_str: 日期字符串

        Returns:
            bool: 验证结果
        """
        if not date_str or not isinstance(date_str, str):
            return False

        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def validate_date_range(self, start_date: str, end_date: str) -> bool:
        """
        验证日期范围

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            bool: 验证结果
        """
        if not self.validate_date_format(start_date) or not self.validate_date_format(end_date):
            return False

        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            return end_dt > start_dt
        except ValueError:
            return False

    def validate_price_data(self, data: pd.DataFrame) -> bool:
        """
        验证价格数据

        Args:
            data: 包含价格数据的DataFrame

        Returns:
            bool: 验证结果
        """
        required_columns = ["open", "high", "low", "close", "volume"]

        # 检查必需列是否存在
        if not all(col in data.columns for col in required_columns):
            return False

        # 检查数据是否为空
        if data.empty:
            return False

        try:
            # 验证价格数据的逻辑关系
            for _, row in data.iterrows():
                open_price = float(row["open"])
                high_price = float(row["high"])
                low_price = float(row["low"])
                close_price = float(row["close"])
                volume = float(row["volume"])

                # 价格必须为正数
                if any(price <= 0 for price in [open_price, high_price, low_price, close_price]):
                    return False

                # 成交量必须为非负数
                if volume < 0:
                    return False

                # High >= Low
                if high_price < low_price:
                    return False

                # High >= Open, Close
                if high_price < max(open_price, close_price):
                    return False

                # Low <= Open, Close
                if low_price > min(open_price, close_price):
                    return False

            return True

        except (ValueError, TypeError):
            return False

    def validate_volume_data(self, data: pd.DataFrame) -> bool:
        """
        验证成交量数据

        Args:
            data: 包含成交量数据的DataFrame

        Returns:
            bool: 验证结果
        """
        if "volume" not in data.columns:
            return False

        if data.empty:
            return False

        try:
            volume = pd.to_numeric(data["volume"], errors="coerce")

            # 检查是否有NaN值
            if volume.isna().any():
                return False

            # 成交量必须为非负数
            if (volume < 0).any():
                return False

            return True

        except (ValueError, TypeError):
            return False

    def validate_trading_day(self, date_str: str) -> bool:
        """
        验证是否为交易日

        Args:
            date_str: 日期字符串

        Returns:
            bool: 验证结果
        """
        if not self.validate_date_format(date_str):
            return False

        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            # 简单实现：周一到周五为交易日
            return dt.weekday() < 5  # 0-4 是周一到周五
        except ValueError:
            return False

    def validate_price_range(self, data: pd.DataFrame, min_price: float = 0.01, max_price: float = 10000.0) -> bool:
        """
        验证价格范围

        Args:
            data: 包含价格数据的DataFrame
            min_price: 最小价格
            max_price: 最大价格

        Returns:
            bool: 验证结果
        """
        price_columns = ["open", "high", "low", "close"]

        for col in price_columns:
            if col not in data.columns:
                continue

            try:
                prices = pd.to_numeric(data[col], errors="coerce")

                # 检查价格范围
                if (prices < min_price).any() or (prices > max_price).any():
                    return False

            except (ValueError, TypeError):
                return False

        return True

    def check_data_completeness(self, data: pd.DataFrame, required_columns: List[str] = None) -> bool:
        """
        检查数据完整性

        Args:
            data: 要检查的DataFrame
            required_columns: 必需的列名列表

        Returns:
            bool: 检查结果
        """
        if data.empty:
            return False

        if required_columns is None:
            required_columns = ["open", "high", "low", "close", "volume"]

        # 检查必需列是否存在
        if not all(col in data.columns for col in required_columns):
            return False

        # 检查是否有缺失值
        for col in required_columns:
            if data[col].isna().any():
                return False

        return True
