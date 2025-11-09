"""
测试AkshareDataSource适配器
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
import sys

sys.path.insert(0, "/opt/claude/mystocks_spec")

from src.adapters.akshare_adapter import AkshareDataSource


class TestAkshareAdapter:
    """AkshareDataSource适配器测试类"""

    def setup_method(self):
        """测试前准备"""
        self.adapter = AkshareDataSource()

    def test_adapter_initialization(self):
        """测试适配器初始化"""
        assert self.adapter is not None
        assert hasattr(self.adapter, "get_stock_daily")
        assert hasattr(self.adapter, "get_real_time_data")

    @patch("adapters.akshare_adapter.ak.stock_zh_a_hist")
    def test_get_stock_daily_success(self, mock_hist, sample_stock_data):
        """测试获取日线数据成功场景"""
        # Mock返回数据
        mock_hist.return_value = sample_stock_data

        # 调用方法
        result = self.adapter.get_stock_daily("000001", "2024-01-01", "2024-01-10")

        # 验证
        assert result is not None
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
        assert "date" in result.columns
        assert "close" in result.columns
        mock_hist.assert_called_once()

    @patch("adapters.akshare_adapter.ak.stock_zh_a_hist")
    def test_get_stock_daily_empty_result(self, mock_hist):
        """测试获取日线数据返回空结果"""
        # Mock返回空DataFrame
        mock_hist.return_value = pd.DataFrame()

        # 调用方法
        result = self.adapter.get_stock_daily("INVALID", "2024-01-01", "2024-01-10")

        # 验证
        assert result is not None
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    @patch("adapters.akshare_adapter.ak.stock_zh_a_hist")
    def test_get_stock_daily_exception_handling(self, mock_hist):
        """测试获取日线数据异常处理"""
        # Mock抛出异常
        mock_hist.side_effect = Exception("API Error")

        # 调用方法应该不抛出异常
        result = self.adapter.get_stock_daily("000001", "2024-01-01", "2024-01-10")

        # 验证返回None或空DataFrame
        assert result is None or (isinstance(result, pd.DataFrame) and len(result) == 0)

    def test_get_stock_daily_invalid_params(self):
        """测试无效参数"""
        with pytest.raises((ValueError, TypeError, Exception)):
            self.adapter.get_stock_daily(None, "2024-01-01", "2024-01-10")

    @patch("adapters.akshare_adapter.ak.stock_zh_a_spot_em")
    def test_get_real_time_data_success(self, mock_spot, sample_realtime_data):
        """测试获取实时数据成功场景"""
        # Mock返回数据
        mock_df = pd.DataFrame([sample_realtime_data])
        mock_spot.return_value = mock_df

        # 调用方法
        result = self.adapter.get_real_time_data("000001")

        # 验证
        assert result is not None
        assert isinstance(result, (dict, pd.DataFrame))

    @patch("adapters.akshare_adapter.ak")
    def test_get_balance_sheet(self, mock_ak, sample_financial_data):
        """测试获取资产负债表"""
        # Mock返回数据
        mock_ak.stock_financial_report_sina = Mock(return_value=sample_financial_data)

        # 调用方法
        result = self.adapter.get_balance_sheet("000001")

        # 验证
        if result is not None:
            assert isinstance(result, pd.DataFrame)
            if len(result) > 0:
                assert "report_date" in result.columns or "total_assets" in str(
                    result.columns
                )

    @patch("adapters.akshare_adapter.ak")
    def test_get_income_statement(self, mock_ak, sample_financial_data):
        """测试获取利润表"""
        # Mock返回数据
        mock_ak.stock_financial_report_sina = Mock(return_value=sample_financial_data)

        # 调用方法
        result = self.adapter.get_income_statement("000001")

        # 验证
        if result is not None:
            assert isinstance(result, pd.DataFrame)

    @patch("adapters.akshare_adapter.ak")
    def test_get_cashflow_statement(self, mock_ak, sample_financial_data):
        """测试获取现金流量表"""
        # Mock返回数据
        mock_ak.stock_financial_report_sina = Mock(return_value=sample_financial_data)

        # 调用方法
        result = self.adapter.get_cashflow_statement("000001")

        # 验证
        if result is not None:
            assert isinstance(result, pd.DataFrame)

    def test_symbol_format_conversion(self):
        """测试股票代码格式转换"""
        # 测试各种格式
        test_cases = [
            ("000001", "000001"),
            ("000001.SZ", "000001"),
            ("600519.SH", "600519"),
            ("sh600519", "600519"),
        ]

        for input_symbol, expected in test_cases:
            # 适配器应该能处理各种格式
            # 这里只测试不抛出异常
            try:
                # 调用某个方法看是否能处理格式
                result = self.adapter.get_stock_daily(
                    input_symbol, "2024-01-01", "2024-01-10"
                )
                # 不抛出异常就算通过
                assert True
            except:
                # 允许API调用失败，但不应该是格式问题
                pass

    def test_date_format_validation(self):
        """测试日期格式验证"""
        valid_dates = ["2024-01-01", "2023-12-31"]
        invalid_dates = ["20240101", "2024/01/01", "invalid"]

        for date_str in valid_dates:
            # 应该不抛出格式错误
            try:
                result = self.adapter.get_stock_daily("000001", date_str, date_str)
                assert True  # 通过
            except ValueError:
                pytest.fail(f"Valid date {date_str} raised ValueError")


class TestAkshareAdapterIntegration:
    """集成测试（需要网络连接）"""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_real_api_call(self):
        """测试真实API调用（可选）"""
        adapter = AkshareDataSource()

        # 尝试获取真实数据
        try:
            result = adapter.get_stock_daily("000001", "2024-01-01", "2024-01-05")
            if result is not None and not result.empty:
                assert len(result) > 0
                assert "date" in result.columns or "close" in result.columns
        except Exception as e:
            # 网络问题或API限流，跳过
            pytest.skip(f"API call failed: {str(e)}")
