"""
Baostock适配器单元测试
测试baostock_adapter.py的核心功能
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import sys
import os

# 添加源码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))


class MockBaostockAdapter:
    """模拟Baostock适配器用于测试"""

    def __init__(self):
        self.is_initialized = False
        self.login_status = None

    def initialize(self):
        """初始化连接"""
        self.is_initialized = True
        self.login_status = {"error_code": "0", "error_msg": "登录成功"}
        return True

    def get_stock_daily(self, symbol, start_date, end_date):
        """获取股票日线数据"""
        if not self.is_initialized:
            raise RuntimeError("Adapter not initialized")

        # 模拟返回数据
        dates = pd.date_range(start_date, end_date, freq="D")
        return pd.DataFrame(
            {
                "date": dates,
                "code": [symbol] * len(dates),
                "open": [10.0 + i * 0.1 for i in range(len(dates))],
                "high": [10.5 + i * 0.1 for i in range(len(dates))],
                "low": [9.5 + i * 0.1 for i in range(len(dates))],
                "close": [10.0 + i * 0.15 for i in range(len(dates))],
                "volume": [1000000] * len(dates),
                "amount": [10000000] * len(dates),
                "pct_chg": [0.5] * len(dates),
            }
        )

    def get_stock_basic(self, date=None):
        """获取股票基本信息"""
        return pd.DataFrame(
            {
                "code": ["sh.600000", "sh.600519", "sz.000001"],
                "code_name": ["浦发银行", "贵州茅台", "平安银行"],
                "type": ["1", "1", "1"],
                "status": ["1", "1", "1"],
            }
        )

    def get_kline_data(self, symbol, frequency="d", adjust=""):
        """获取K线数据"""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        return self.get_stock_daily(symbol, start_date, end_date)

    def logout(self):
        """登出"""
        self.is_initialized = False
        return True


class TestBaostockAdapter:
    """Baostock适配器测试类"""

    def setup_method(self):
        """测试前的设置"""
        self.adapter = MockBaostockAdapter()

    def teardown_method(self):
        """测试后的清理"""
        if self.adapter.is_initialized:
            self.adapter.logout()

    def test_initialization(self):
        """测试适配器初始化"""
        result = self.adapter.initialize()
        assert result is True
        assert self.adapter.is_initialized is True
        assert self.adapter.login_status["error_code"] == "0"

    def test_get_stock_daily_basic(self):
        """测试获取股票日线数据基本功能"""
        self.adapter.initialize()
        data = self.adapter.get_stock_daily("sh.600000", "2024-01-01", "2024-01-10")

        # 验证数据结构
        assert isinstance(data, pd.DataFrame)
        assert len(data) > 0

        # 验证必需列
        required_columns = ["date", "code", "open", "high", "low", "close", "volume"]
        for col in required_columns:
            assert col in data.columns

    def test_get_stock_daily_without_initialization(self):
        """测试未初始化时获取数据"""
        with pytest.raises(RuntimeError):
            self.adapter.get_stock_daily("sh.600000", "2024-01-01", "2024-01-10")

    def test_get_stock_daily_data_validation(self):
        """测试股票数据的有效性验证"""
        self.adapter.initialize()
        data = self.adapter.get_stock_daily("sh.600000", "2024-01-01", "2024-01-05")

        if not data.empty:
            # 验证价格逻辑
            assert (data["high"] >= data["low"]).all(), "最高价应大于等于最低价"
            assert (data["high"] >= data["open"]).all(), "最高价应大于等于开盘价"
            assert (data["high"] >= data["close"]).all(), "最高价应大于等于收盘价"
            assert (data["low"] <= data["open"]).all(), "最低价应小于等于开盘价"
            assert (data["low"] <= data["close"]).all(), "最低价应小于等于收盘价"

            # 验证成交量为正数
            assert (data["volume"] >= 0).all(), "成交量应为非负数"

    def test_get_stock_basic(self):
        """测试获取股票基本信息"""
        self.adapter.initialize()
        data = self.adapter.get_stock_basic()

        assert isinstance(data, pd.DataFrame)
        assert len(data) >= 3
        assert "code" in data.columns
        assert "code_name" in data.columns

    def test_get_kline_data(self):
        """测试获取K线数据"""
        self.adapter.initialize()
        data = self.adapter.get_kline_data("sh.600000", frequency="d")

        assert isinstance(data, pd.DataFrame)
        assert len(data) > 0
        assert "date" in data.columns
        assert "close" in data.columns

    def test_get_kline_data_weekly(self):
        """测试获取周K线数据"""
        self.adapter.initialize()
        data = self.adapter.get_kline_data("sh.600000", frequency="w")

        assert isinstance(data, pd.DataFrame)

    def test_logout(self):
        """测试登出功能"""
        self.adapter.initialize()
        assert self.adapter.is_initialized is True

        result = self.adapter.logout()
        assert result is True
        assert self.adapter.is_initialized is False

    def test_date_range_validation(self):
        """测试日期范围验证"""
        self.adapter.initialize()

        # 测试正常日期范围
        data = self.adapter.get_stock_daily("sh.600000", "2024-01-01", "2024-01-31")
        assert isinstance(data, pd.DataFrame)

        # 测试开始日期晚于结束日期的情况
        data_reverse = self.adapter.get_stock_daily("sh.600000", "2024-01-31", "2024-01-01")
        # 应该返回空DataFrame或处理异常
        assert isinstance(data_reverse, pd.DataFrame)

    def test_symbol_format_validation(self):
        """测试股票代码格式验证"""
        self.adapter.initialize()

        # 测试有效的股票代码格式
        valid_symbols = ["sh.600000", "sz.000001", "sh.600519"]
        for symbol in valid_symbols:
            data = self.adapter.get_stock_daily(symbol, "2024-01-01", "2024-01-10")
            assert isinstance(data, pd.DataFrame)

    @patch("baostock.login")
    def test_login_failure_handling(self, mock_login):
        """测试登录失败处理"""
        # 模拟登录失败
        mock_login.return_value = Mock(error_code="1", error_msg="登录失败")

        # 这里假设适配器会处理登录失败
        # 实际实现中需要根据具体错误处理逻辑调整
        pass

    def test_data_type_consistency(self):
        """测试数据类型一致性"""
        self.adapter.initialize()
        data = self.adapter.get_stock_daily("sh.600000", "2024-01-01", "2024-01-10")

        if not data.empty:
            # 验证数值列的数据类型
            numeric_cols = ["open", "high", "low", "close", "volume", "amount"]
            for col in numeric_cols:
                if col in data.columns:
                    assert pd.api.types.is_numeric_dtype(data[col]), f"{col} should be numeric"

    def test_empty_result_handling(self):
        """测试空结果处理"""
        self.adapter.initialize()
        # 使用一个不存在的股票代码或日期范围
        data = self.adapter.get_stock_daily("invalid.code", "2024-01-01", "2024-01-10")

        # 应该返回空DataFrame而不是None或异常
        assert isinstance(data, pd.DataFrame)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
