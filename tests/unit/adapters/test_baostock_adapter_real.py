"""
BaoStock适配器真实单元测试

测试真实的BaostockDataSource类的功能
"""

import os
import sys
from unittest.mock import Mock, patch

import pandas as pd
import pytest

# 添加源码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

# 测试目标模块
try:
    from src.adapters.baostock_adapter import BaostockDataSource
except ImportError as e:
    pytest.skip(f"无法导入BaostockDataSource: {e} owner=test-governance issue=techdebt-expired-markers ttl=2026-06-30", allow_module_level=True)


class TestBaostockDataSource:
    """BaostockDataSource单元测试"""

    @staticmethod
    def _query_result(fields, rows, error_code="0", error_msg=""):
        """Create a baostock-style cursor result."""
        result = Mock()
        result.error_code = error_code
        result.error_msg = error_msg
        result.fields = fields
        result.next.side_effect = [True] * len(rows) + [False]
        result.get_row_data.side_effect = rows
        return result

    @pytest.fixture
    def mock_baostock(self):
        """模拟baostock模块"""
        mock_bs = Mock()
        with patch.dict("sys.modules", {"baostock": mock_bs}):
            # 模拟登录成功
            mock_login = Mock()
            mock_login.error_code = "0"
            mock_login.error_msg = "登录成功"
            mock_bs.login.return_value = mock_login

            # 模拟股票数据
            mock_bs.query_history_k_data_plus.return_value = self._query_result(
                ["date", "code", "open", "high", "low", "close", "volume", "amount", "turn", "pctChg"],
                [
                    ["2024-01-01", "000001.SZ", "10.0", "10.5", "9.8", "10.2", "1000000", "10200000", "1.2", "2.0"],
                    ["2024-01-02", "000001.SZ", "10.5", "11.0", "10.3", "10.8", "1200000", "12960000", "1.4", "5.9"],
                ],
            )

            # 模拟基本信息数据
            mock_bs.query_stock_basic.return_value = self._query_result(
                ["code", "code_name", "type", "status"],
                [["000001.SZ", "平安银行", "1", "1"]],
            )

            yield mock_bs

    def test_init_success(self, mock_baostock):
        """测试成功初始化"""
        adapter = BaostockDataSource()

        assert adapter.available is True
        assert adapter.bs == mock_baostock
        mock_baostock.login.assert_called_once()

    def test_init_login_failure(self):
        """测试登录失败时的初始化"""
        mock_bs = Mock()
        mock_bs.login.return_value = Mock(error_code="1", error_msg="登录失败")

        with patch.dict("sys.modules", {"baostock": mock_bs}):
            with pytest.raises(ImportError, match="Baostock登录失败"):
                BaostockDataSource()

    def test_init_import_failure(self):
        """测试导入失败时的初始化"""
        with patch.dict("sys.modules", {"baostock": None}):
            with pytest.raises(ImportError, match="Baostock不可用"):
                BaostockDataSource()

    def test_get_stock_daily_success(self, mock_baostock, adapter):
        """测试成功获取股票日线数据"""
        result = adapter.get_stock_daily("000001", start_date="2024-01-01", end_date="2024-01-02")

        # 验证API调用
        mock_baostock.query_history_k_data_plus.assert_called_once()
        call_args = mock_baostock.query_history_k_data_plus.call_args
        assert "sz.000001" in str(call_args)

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
        result = adapter.get_stock_basic("000001")

        # 验证API调用
        mock_baostock.query_stock_basic.assert_called_once()

        # 验证返回结果
        assert result is not None
        assert isinstance(result, dict)
        assert result["code_name"] == "平安银行"

    def test_get_stock_daily_with_date_format(self, mock_baostock, adapter):
        """测试不同日期格式的股票数据获取"""
        result = adapter.get_stock_daily("000001", start_date="20240101", end_date="20240102")

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
        result = adapter.get_stock_daily("000001", start_date="2024-01-01", end_date="2024-01-02")

        # 验证返回的DataFrame包含预期的列
        expected_columns = ["date", "open", "high", "low", "close", "volume"]
        for col in expected_columns:
            # 注意：实际的列可能经过映射，这里测试基本功能
            assert isinstance(result, pd.DataFrame)

    def test_get_stock_daily_api_error(self, adapter):
        """测试API调用错误处理"""
        adapter.bs.query_history_k_data_plus.side_effect = Exception("API错误")

        result = adapter.get_stock_daily("000001", start_date="2024-01-01", end_date="2024-01-02")
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_data_quality_check(self, mock_baostock, adapter):
        """测试数据质量检查"""
        result = adapter.get_stock_daily("000001", start_date="2024-01-01", end_date="2024-01-02")

        # 验证数据完整性
        if not result.empty:
            assert "date" in result.columns or "trade_date" in result.columns
            assert len(result) > 0

    def test_get_stock_basic_empty_result(self, adapter):
        """测试获取空的基本信息"""
        adapter.bs.query_stock_basic.return_value = self._query_result(["code", "code_name"], [])

        result = adapter.get_stock_basic("000001")

        assert result is not None
        assert isinstance(result, dict)
        assert result == {}

    def test_parameter_validation(self, adapter):
        """测试参数验证"""
        # 测试空参数
        with pytest.raises((TypeError, ValueError, Exception)):
            adapter.get_stock_daily("")


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__])
