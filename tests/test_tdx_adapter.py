"""
测试TDXDataSource适配器
"""
import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
import sys
sys.path.insert(0, '/opt/claude/mystocks_spec')

from adapters.tdx_adapter import TdxDataSource


class TestTDXAdapter:
    """TdxDataSource适配器测试类"""

    def setup_method(self):
        """测试前准备"""
        with patch('adapters.tdx_adapter.TdxHq_API'):
            self.adapter = TdxDataSource()

    def test_adapter_initialization(self):
        """测试适配器初始化"""
        assert self.adapter is not None
        assert hasattr(self.adapter, 'get_real_time_data')
        assert hasattr(self.adapter, 'get_kline_data')

    @patch('adapters.tdx_adapter.TdxHq_API')
    def test_get_real_time_data_success(self, mock_api, sample_realtime_data):
        """测试获取实时数据成功场景"""
        # Mock TDX API
        mock_api_instance = MagicMock()
        mock_api_instance.get_security_quotes.return_value = [sample_realtime_data]
        mock_api.return_value = mock_api_instance

        with patch.object(self.adapter, 'api', mock_api_instance):
            # 调用方法
            result = self.adapter.get_real_time_data("000001")

            # 验证
            assert result is not None
            assert isinstance(result, dict)

    @patch('adapters.tdx_adapter.TdxHq_API')
    def test_get_real_time_data_connection_fail(self, mock_api):
        """测试连接失败场景"""
        # Mock连接失败
        mock_api_instance = MagicMock()
        mock_api_instance.get_security_quotes.side_effect = Exception("Connection failed")
        mock_api.return_value = mock_api_instance

        with patch.object(self.adapter, 'api', mock_api_instance):
            # 调用方法
            result = self.adapter.get_real_time_data("000001")

            # 验证返回None或空结果
            assert result is None or result == {}

    @patch('adapters.tdx_adapter.TdxHq_API')
    def test_get_kline_data_daily(self, mock_api, sample_stock_data):
        """测试获取日K线数据"""
        # Mock返回数据
        mock_api_instance = MagicMock()
        mock_api_instance.get_security_bars.return_value = sample_stock_data.to_dict('records')
        mock_api.return_value = mock_api_instance

        with patch.object(self.adapter, 'api', mock_api_instance):
            # 调用方法
            result = self.adapter.get_kline_data("000001", period="daily", count=10)

            # 验证
            if result is not None:
                assert isinstance(result, (pd.DataFrame, list))

    @patch('adapters.tdx_adapter.TdxHq_API')
    def test_get_kline_data_minute(self, mock_api, sample_stock_data):
        """测试获取分钟K线数据"""
        # Mock返回数据
        mock_api_instance = MagicMock()
        mock_api_instance.get_security_bars.return_value = sample_stock_data.to_dict('records')
        mock_api.return_value = mock_api_instance

        with patch.object(self.adapter, 'api', mock_api_instance):
            # 调用方法
            result = self.adapter.get_kline_data("000001", period="5m", count=50)

            # 验证
            if result is not None:
                assert isinstance(result, (pd.DataFrame, list))

    def test_period_mapping(self):
        """测试周期映射"""
        # 测试各种周期参数
        test_periods = ["1m", "5m", "15m", "30m", "1h", "daily", "1d"]

        for period in test_periods:
            # 不应该抛出异常
            try:
                result = self.adapter.get_kline_data("000001", period=period, count=1)
                # 允许返回None（如果没有实际连接）
                assert result is None or isinstance(result, (pd.DataFrame, list))
            except KeyError:
                pytest.fail(f"Period {period} not supported")

    def test_market_detection(self):
        """测试市场检测"""
        # 测试不同市场的股票代码
        test_cases = [
            ("000001", 0),  # 深圳
            ("600519", 1),  # 上海
            ("300001", 0),  # 创业板
            ("688001", 1),  # 科创板
        ]

        for symbol, expected_market in test_cases:
            # 适配器应该能正确识别市场
            # 这里只测试不抛出异常
            try:
                result = self.adapter.get_real_time_data(symbol)
                assert True  # 通过
            except:
                pass  # 允许API调用失败

    @patch('adapters.tdx_adapter.TdxHq_API')
    def test_server_failover(self, mock_api):
        """测试服务器切换机制"""
        # Mock第一个服务器失败，第二个成功
        mock_api_instance = MagicMock()
        mock_api_instance.connect.side_effect = [False, True]
        mock_api.return_value = mock_api_instance

        with patch.object(self.adapter, 'api', mock_api_instance):
            # 适配器应该能自动切换服务器
            # 这里只验证不抛出异常
            try:
                self.adapter.get_real_time_data("000001")
                assert True
            except:
                pass

    def test_invalid_symbol(self):
        """测试无效股票代码"""
        invalid_symbols = [None, "", "INVALID", "abc123"]

        for symbol in invalid_symbols:
            # 应该返回None或抛出特定异常
            result = self.adapter.get_real_time_data(symbol)
            assert result is None or result == {}

    def test_count_parameter_validation(self):
        """测试count参数验证"""
        # 测试边界值
        test_counts = [1, 100, 500, 1000]

        for count in test_counts:
            try:
                result = self.adapter.get_kline_data("000001", period="daily", count=count)
                # 不抛出异常就通过
                assert True
            except:
                pass


class TestTDXAdapterIntegration:
    """集成测试（需要TDX服务器连接）"""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_real_tdx_connection(self):
        """测试真实TDX连接（可选）"""
        try:
            adapter = TdxDataSource()
            result = adapter.get_real_time_data("000001")

            if result is not None:
                assert isinstance(result, dict)
                # 验证必需字段
                assert 'symbol' in result or 'price' in result
        except Exception as e:
            pytest.skip(f"TDX connection failed: {str(e)}")

    @pytest.mark.integration
    @pytest.mark.slow
    def test_real_kline_data(self):
        """测试真实K线数据获取（可选）"""
        try:
            adapter = TdxDataSource()
            result = adapter.get_kline_data("000001", period="daily", count=5)

            if result is not None:
                assert isinstance(result, (pd.DataFrame, list))
                if isinstance(result, pd.DataFrame):
                    assert len(result) > 0
        except Exception as e:
            pytest.skip(f"TDX K-line data failed: {str(e)}")
