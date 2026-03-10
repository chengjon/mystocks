#!/usr/bin/env python3
"""Support tests extracted from `scripts/tests/test_data_source_manager.py`."""

import pandas as pd
import pytest

from src.adapters.data_source_manager import DataSourceManager
from src.interfaces.data_source import IDataSource


class TestDataSourceManagerErrorHandling:
    """测试数据源管理器错误处理"""

    @pytest.fixture
    def manager(self):
        return DataSourceManager()

    def test_data_source_exception_handling(self, manager):
        """测试数据源抛出异常的处理"""

        class ExceptionDataSource(IDataSource):
            def get_real_time_data(self, symbol: str):
                raise Exception("网络连接失败")

            def get_stock_daily(self, symbol: str, start_date: str, end_date: str):
                raise Exception("数据获取失败")

            def get_index_daily(self, symbol: str, start_date: str, end_date: str):
                return pd.DataFrame()

            def get_stock_basic(self, symbol: str):
                return {}

            def get_index_components(self, symbol: str):
                return []

            def get_market_calendar(self, start_date: str, end_date: str):
                return pd.DataFrame()

            def get_financial_data(self, symbol: str, period: str = "annual"):
                return pd.DataFrame()

            def get_news_data(self, symbol: str = None, limit: int = 10):
                return []

        exception_source = ExceptionDataSource()
        manager.register_source("exception", exception_source)

        with pytest.raises(Exception):
            manager.get_real_time_data("600519", source="exception")

        with pytest.raises(Exception):
            manager.get_stock_daily("600519", "2024-01-01", "2024-01-10", source="exception")

    def test_source_returns_invalid_types(self, manager):
        """测试数据源返回无效类型"""

        class InvalidTypeDataSource(IDataSource):
            def get_real_time_data(self, symbol: str):
                return 123

            def get_stock_daily(self, symbol: str, start_date: str, end_date: str):
                return "invalid"

            def get_index_daily(self, symbol: str, start_date: str, end_date: str):
                return pd.DataFrame()

            def get_stock_basic(self, symbol: str):
                return {}

            def get_index_components(self, symbol: str):
                return []

            def get_market_calendar(self, start_date: str, end_date: str):
                return pd.DataFrame()

            def get_financial_data(self, symbol: str, period: str = "annual"):
                return pd.DataFrame()

            def get_news_data(self, symbol: str = None, limit: int = 10):
                return []

        invalid_source = InvalidTypeDataSource()
        manager.register_source("invalid", invalid_source)

        result = manager.get_real_time_data("600519", source="invalid")
        assert result == 123

        df_result = manager.get_stock_daily("600519", "2024-01-01", "2024-01-10", source="invalid")
        assert df_result == "invalid"
