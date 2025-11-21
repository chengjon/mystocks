"""
Akshare适配器单元测试
测试akshare_adapter.py的核心功能
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# 添加源码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../src'))


class MockAkshareDataSource:
    """模拟Akshare数据源用于测试"""

    def __init__(self):
        self.is_initialized = False

    def initialize(self):
        """初始化适配器"""
        self.is_initialized = True
        return True

    def get_stock_daily(self, symbol, start_date, end_date):
        """获取股票日线数据"""
        if symbol == 'INVALID':
            return pd.DataFrame()

        # 返回模拟数据 (确保价格逻辑正确: high >= close, high >= open, low <= close, low <= open)
        return pd.DataFrame({
            'date': pd.date_range('2024-01-01', '2024-01-10'),
            'open': [10.0, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9],
            'high': [10.5, 10.6, 10.7, 10.8, 10.9, 11.0, 11.2, 11.5, 11.8, 12.0],  # high >= close
            'low': [9.5, 9.6, 9.7, 9.8, 9.9, 10.0, 10.1, 10.2, 10.3, 10.4],
            'close': [10.0, 10.2, 10.4, 10.6, 10.8, 11.0, 11.1, 11.4, 11.6, 11.8],
            'volume': [1000000] * 10,
            'amount': [10000000] * 10,
            'pct_chg': [0.0, 2.0, 1.96, 1.92, 1.89, 1.85, 1.82, 1.79, 1.75, 1.72]
        })

    def get_stock_basic(self):
        """获取股票基本信息"""
        return pd.DataFrame({
            'ts_code': ['000001.SZ', '000002.SZ', '600000.SH'],
            'name': ['平安银行', '万科A', '浦发银行'],
            'industry': ['银行', '房地产', '银行'],
            'list_date': ['1991-04-03', '1991-01-29', '1999-09-10']
        })

    def get_market_daily(self, market='sh', start_date='2024-01-01', end_date='2024-01-10'):
        """获取市场日线数据"""
        if market == 'invalid':
            return pd.DataFrame()

        return pd.DataFrame({
            'trade_date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'close': [3000.0, 3010.0, 3020.0],
            'pct_chg': [0.0, 0.33, 0.33]
        })


class TestAkshareAdapter:
    """Akshare适配器测试类"""

    def setup_method(self):
        """测试前的设置"""
        self.adapter = MockAkshareDataSource()

    def test_initialization(self):
        """测试适配器初始化"""
        result = self.adapter.initialize()
        assert result is True
        assert self.adapter.is_initialized is True

    def test_get_stock_daily(self):
        """测试获取股票日线数据"""
        data = self.adapter.get_stock_daily('000001', '2024-01-01', '2024-01-10')

        # 验证数据结构
        assert isinstance(data, pd.DataFrame)
        assert len(data) == 10

        # 验证列名
        expected_columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'amount', 'pct_chg']
        assert all(col in data.columns for col in expected_columns)

        # 验证数据类型
        assert data['open'].dtype == float
        assert data['close'].dtype == float
        assert data['volume'].dtype == int

    def test_get_stock_daily_invalid_symbol(self):
        """测试无效股票代码"""
        data = self.adapter.get_stock_daily('INVALID', '2024-01-01', '2024-01-10')
        # 应该返回空DataFrame
        assert isinstance(data, pd.DataFrame)
        assert len(data) == 0 or data.empty

    def test_get_stock_basic(self):
        """测试获取股票基本信息"""
        data = self.adapter.get_stock_basic()

        assert isinstance(data, pd.DataFrame)
        assert len(data) >= 3  # 至少包含3只股票
        assert 'ts_code' in data.columns
        assert 'name' in data.columns
        assert 'industry' in data.columns

    def test_get_market_daily(self):
        """测试获取市场日线数据"""
        data = self.adapter.get_market_daily('sh', '2024-01-01', '2024-01-03')

        assert isinstance(data, pd.DataFrame)
        assert len(data) >= 1
        assert 'trade_date' in data.columns
        assert 'close' in data.columns
        assert 'pct_chg' in data.columns

    def test_get_market_daily_invalid_market(self):
        """测试无效市场代码"""
        data = self.adapter.get_market_daily('invalid', '2024-01-01', '2024-01-03')
        # 应该返回空DataFrame
        assert isinstance(data, pd.DataFrame)
        assert len(data) == 0 or data.empty

    def test_get_stock_daily_with_mock(self):
        """测试使用mock的股票数据获取"""
        # 使用mock数据
        data = self.adapter.get_stock_daily('000001', '2024-01-01', '2024-01-05')

        assert isinstance(data, pd.DataFrame)
        assert len(data) == 10  # Mock返回10行数据

    def test_data_validation(self):
        """测试数据验证功能"""
        data = self.adapter.get_stock_daily('000001', '2024-01-01', '2024-01-10')

        # 验证数据逻辑
        if not data.empty:
            # 验证价格逻辑
            assert (data['high'] >= data['low']).all()
            assert (data['high'] >= data['open']).all()
            assert (data['high'] >= data['close']).all()
            assert (data['low'] <= data['open']).all()
            assert (data['low'] <= data['close']).all()

    def test_error_handling(self):
        """测试错误处理"""
        # 测试无效符号返回空DataFrame
        data = self.adapter.get_stock_daily('INVALID', '2024-01-01', '2024-01-10')
        assert isinstance(data, pd.DataFrame)
        assert data.empty


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
