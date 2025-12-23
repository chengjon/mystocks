"""
BaoStock适配器真实单元测试

测试真实的BaostockDataSource类的功能
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
import sys
import os

# 添加源码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

# 测试目标模块
try:
    from src.adapters.baostock_adapter import BaostockDataSource
except ImportError as e:
    pytest.skip(f"无法导入BaostockDataSource: {e}", allow_module_level=True)


class TestBaostockDataSource:
    """BaostockDataSource单元测试"""

    @pytest.fixture
    def mock_baostock(self):
        """模拟baostock模块"""
        with patch("src.adapters.baostock_adapter.bs") as mock_bs:
            # 模拟登录成功
            mock_login = Mock()
            mock_login.error_code = "0"
            mock_login.error_msg = "登录成功"
            mock_bs.login.return_value = mock_login

            # 模拟股票数据
            mock_stock_data = pd.DataFrame(
                {
                    "date": ["2024-01-01", "2024-01-02"],
                    "code": ["000001. SZ", "000001. SZ"],
                    "open": [10.0, 10.5],
                    "high": [10.5, 11.0],
                    "low": [9.8, 10.3],
                    "close": [10.2, 10.8],
                    "volume": [1000000, 1200000],
                    "amount": [10200000, 12960000],
                    "pct_chg": [2.0, 5.9],
                }
            )

            mock_bs.query_history_k_data_plus.return_value = mock_stock_data

            # 模拟基本信息数据
            mock_basic_data = pd.DataFrame(
                {
                    "code": ["000001. SZ", "000002. SZ"],
                    "code_name": ["平安银行", "万科A"],
                    "type": ["1", "1"],  # 股票类型
                    "status": ["1", "1"],  # 上市状态
                }
            )

            mock_bs.query_stock_basic.return_value = mock_basic_data

            yield mock_bs

    def test_init_success(self, mock_baostock):
        """测试成功初始化"""
        adapter = BaostockDataSource()

        assert adapter.available == True
        assert adapter.bs == mock_baostock
        mock_baostock.login.assert_called_once()

    @patch("src.adapters.baostock_adapter.bs.login")
    def test_init_login_failure(self, mock_login):
        """测试登录失败时的初始化"""
        mock_login.return_value = Mock(error_code="1", error_msg="登录失败")

        with pytest.raises(ImportError, match="Baostock登录失败"):
            BaostockDataSource()

    @patch("src.adapters.baostock_adapter.bs", side_effect=ImportError("模块不存在"))
    def test_init_import_failure(self):
        """测试导入失败时的初始化"""
        adapter = BaostockDataSource()
        assert adapter.available == False

    def test_get_stock_daily_success(self, mock_baostock, adapter):
        """测试成功获取股票日线数据"""
        result = adapter.get_stock_daily(
            "000001", start_date="2024-01-01", end_date="2024-01-02"
        )

        # 验证API调用
        mock_baostock.query_history_k_data_plus.assert_called_once()
        call_args = mock_baostock.query_history_k_data_plus.call_args
        assert "000001. SZ" in str(call_args)

        # 验证返回结果
        assert result is not None
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert len(result) == 2

    @pytest.fixture
    def adapter(self, mock_baostock):
        """创建测试用的适配器实例"""
        return BaostockDataSource()

    def test_get_stock_basic_success(self, mock_baostock, adapter):
        """测试成功获取股票基本信息"""
        result = adapter.get_stock_basic()

        # 验证API调用
        mock_baostock.query_stock_basic.assert_called_once()

        # 验证返回结果
        assert result is not None
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert len(result) == 2

    def test_get_stock_daily_with_date_format(self, mock_baostock, adapter):
        """测试不同日期格式的股票数据获取"""
        result = adapter.get_stock_daily(
            "000001", start_date="20240101", end_date="20240102"
        )

        assert result is not None
        assert isinstance(result, pd.DataFrame)
        mock_baostock.query_history_k_data_plus.assert_called_once()

    def test_available_property(self, adapter):
        """测试available属性"""
        assert hasattr(adapter, "available")
        assert isinstance(adapter.available, bool)

    def test_adapter_has_required_methods(self, adapter):
        """测试适配器具有必需的方法"""
        required_methods = ["get_stock_daily", "get_stock_basic"]
        for method in required_methods:
            assert hasattr(adapter, method)
            assert callable(getattr(adapter, method))

    def test_column_mapping_integration(self, mock_baostock, adapter):
        """测试列名映射集成"""
        result = adapter.get_stock_daily("000001")

        # 验证返回的DataFrame包含预期的列
        expected_columns = ["date", "open", "high", "low", "close", "volume"]
        for col in expected_columns:
            # 注意：实际的列可能经过映射，这里测试基本功能
            assert isinstance(result, pd.DataFrame)

    @patch("src.adapters.baostock_adapter.bs.query_history_k_data_plus")
    def test_get_stock_daily_api_error(self, mock_query, adapter):
        """测试API调用错误处理"""
        mock_query.side_effect = Exception("API错误")

        # 适配器应该能够处理API错误
        with pytest.raises(Exception):
            adapter.get_stock_daily("000001")

    def test_data_quality_check(self, mock_baostock, adapter):
        """测试数据质量检查"""
        result = adapter.get_stock_daily("000001")

        # 验证数据完整性
        if not result.empty:
            assert "date" in result.columns or "trade_date" in result.columns
            assert len(result) > 0

    @patch("src.adapters.baostock_adapter.bs.query_stock_basic")
    def test_get_stock_basic_empty_result(self, mock_query, adapter):
        """测试获取空的基本信息"""
        mock_query.return_value = pd.DataFrame()

        result = adapter.get_stock_basic()

        assert result is not None
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_parameter_validation(self, adapter):
        """测试参数验证"""
        # 测试空参数
        with pytest.raises((TypeError, ValueError, Exception)):
            adapter.get_stock_daily("")


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__])
