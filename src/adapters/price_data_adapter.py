"""
价格数据适配器 - 从 financial_adapter.py 拆分
职责：股票和指数价格数据获取、处理、验证
遵循 TDD 原则：仅实现满足测试的最小功能
"""

import os
import re
import sys
from datetime import datetime, timedelta

import pandas as pd

# 添加项目根路径以导入验证模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class PriceDataAdapter:
    """价格数据适配器 - 专注于价格数据获取和处理"""

    def __init__(self):
        """初始化价格数据适配器"""
        self.cache = {}  # 简单缓存实现
        # 导入数据验证器
        try:
            from .data_validator import DataValidator

            self.validator = DataValidator()
        except ImportError:
            # 如果验证器还不存在，创建一个简单的验证器
            self.validator = self._create_simple_validator()

    def _create_simple_validator(self):
        """创建简单验证器（临时实现）"""

        class SimpleValidator:
            def validate_stock_symbol(self, symbol: str) -> bool:
                if not symbol or not isinstance(symbol, str):
                    return False
                # 简单的股票代码格式验证
                return bool(re.match(r"^[0-9]{6}$", symbol))

            def validate_date_format(self, date_str: str) -> bool:
                try:
                    datetime.strptime(date_str, "%Y-%m-%d")
                    return True
                except ValueError:
                    return False

        return SimpleValidator()

    def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取股票日线数据

        Args:
            symbol: 股票代码 (如: "000001")
            start_date: 开始日期 (格式: "2024-01-01")
            end_date: 结束日期 (格式: "2024-01-31")

        Returns:
            pd.DataFrame: 包含OHLCV数据的DataFrame

        Raises:
            ValueError: 参数验证失败时抛出
        """
        # 参数验证
        if not self.validator.validate_stock_symbol(symbol):
            raise ValueError("Invalid symbol format")

        if not self.validator.validate_date_format(start_date):
            raise ValueError("Invalid start_date format")

        if not self.validator.validate_date_format(end_date):
            raise ValueError("Invalid end_date format")

        # 检查日期范围
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        if end_dt <= start_dt:
            raise ValueError("End date must be after start date")

        # 缓存键
        cache_key = f"{symbol}_{start_date}_{end_date}"

        # 尝试从缓存获取
        if cache_key in self.cache:
            return self.cache[cache_key]

        # 模拟数据获取（最小实现）
        # 在实际实现中，这里会调用真实的数据源
        data = self._generate_mock_data(symbol, start_date, end_date)

        # 缓存结果
        self.cache[cache_key] = data

        return data

    def _generate_mock_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """生成模拟价格数据（仅用于测试）"""
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        # 生成日期范围
        dates = []
        current_dt = start_dt
        while current_dt <= end_dt:
            # 只生成工作日数据（简单实现）
            if current_dt.weekday() < 5:  # 0-4 是周一到周五
                dates.append(current_dt)
            current_dt += timedelta(days=1)

        # 生成模拟价格数据
        import random

        base_price = 10.0 + random.random() * 90  # 基础价格 10-100

        data = []
        for i, date in enumerate(dates):
            price_change = random.uniform(-0.05, 0.05)  # ±5% 价格波动
            current_price = base_price * (1 + price_change)

            # 生成OHLC数据（确保High >= Low, Close在High和Low之间）
            open_price = current_price
            high_price = open_price * (1 + random.uniform(0, 0.03))
            low_price = open_price * (1 - random.uniform(0, 0.03))
            close_price = random.uniform(low_price, high_price)
            volume = random.randint(1000, 100000)

            data.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "open": round(open_price, 2),
                    "high": round(high_price, 2),
                    "low": round(low_price, 2),
                    "close": round(close_price, 2),
                    "volume": volume,
                    "symbol": symbol,
                }
            )

        df = pd.DataFrame(data)
        df.set_index("date", inplace=True)

        return df
