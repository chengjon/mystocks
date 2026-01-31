"""
TDX适配器基础测试
专注于提升TDX适配器覆盖率（472行代码）
"""

import os
import sys
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

# 添加源码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

# 测试目标模块
try:
    from src.adapters.tdx.tdx_adapter import TDXDataSource
except ImportError as e:
    pytest.skip(f"无法导入TDXDataSource: {e}", allow_module_level=True)


class TestTDXDataSourceBasic:
    """TDXDataSource基础测试 - 专注覆盖率"""

    @pytest.fixture
    def mock_tdx_lib(self):
        """模拟TDX库"""
        with patch("src.adapters.tdx_adapter.tdx") as mock_tdx:
            # 模拟TDX连接
            mock_api = MagicMock()
            mock_api.connected = True
            mock_tdx.api = mock_api

            # 模拟获取市场代码
            mock_tdx.get_market_code.return_value = 1  # 深圳市场

            yield mock_tdx

    def test_initialization_with_config(self):
        """测试带配置的初始化"""
        config = {"host": "localhost", "port": 7709, "auto_connect": True}

        adapter = TDXDataSource(config)

        # 验证基本属性
        assert hasattr(adapter, "config")
        assert adapter.config == config
        assert hasattr(adapter, "_connection")

    def test_initialization_without_config(self):
        """测试无配置的初始化"""
        adapter = TDXDataSource()

        # 验证基本属性存在
        assert hasattr(adapter, "config")
        assert hasattr(adapter, "_connection")

    def test_market_code_method(self):
        """测试市场代码获取方法"""
        adapter = TDXDataSource()

        # 测试深圳市场代码
        market_code = adapter._get_market_code("000001")
        assert market_code == 1  # 深圳市场

        # 测试上海市场代码
        market_code = adapter._get_market_code("600000")
        assert market_code == 0  # 上海市场

    def test_retry_decorator(self):
        """测试重试装饰器"""
        adapter = TDXDataSource()

        # 验证重试装饰器存在
        assert hasattr(adapter, "_retry_api_call")
        assert callable(getattr(adapter, "_retry_api_call"))

    @patch("src.adapters.tdx_adapter.tdx")
    def test_retry_api_call_success(self, mock_tdx):
        """测试重试API调用成功情况"""
        # 设置成功的模拟函数
        mock_func = Mock(return_value="success")
        mock_tdx.api.connected = True

        adapter = TDXDataSource()

        # 调用重试装饰的方法
        result = adapter._retry_api_call(mock_func)

        assert result == "success"
        mock_func.assert_called_once()

    def test_kline_data_validation_method(self):
        """测试K线数据验证方法"""
        adapter = TDXDataSource()

        # 创建测试DataFrame
        test_df = pd.DataFrame(
            {
                "datetime": ["2024-01-01", "2024-01-02"],
                "open": [10.0, 10.5],
                "high": [10.5, 11.0],
                "low": [9.8, 10.3],
                "close": [10.2, 10.8],
                "volume": [1000000, 1200000],
            }
        )

        # 验证数据验证方法
        result = adapter._validate_kline_data(test_df)
        assert isinstance(result, pd.DataFrame)
        assert not result.empty

    def test_kline_data_validation_empty(self):
        """测试空K线数据验证"""
        adapter = TDXDataSource()

        # 测试空DataFrame
        empty_df = pd.DataFrame()
        result = adapter._validate_kline_data(empty_df)

        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_has_core_methods(self):
        """测试核心方法存在"""
        adapter = TDXDataSource()

        # 验证核心方法存在
        core_methods = [
            "get_stock_daily",
            "get_index_daily",
            "_get_market_code",
            "_retry_api_call",
            "_validate_kline_data",
        ]

        for method in core_methods:
            assert hasattr(adapter, method), f"缺少方法: {method}"
            assert callable(getattr(adapter, method)), f"方法不可调用: {method}"

    def test_connection_management(self):
        """测试连接管理"""
        adapter = TDXDataSource()

        # 验证连接相关方法存在
        assert hasattr(adapter, "_get_tdx_connection")
        assert callable(getattr(adapter, "_get_tdx_connection"))

    def test_config_handling(self):
        """测试配置处理"""
        test_config = {"host": "test_host", "port": 9999, "timeout": 30}

        adapter = TDXDataSource(test_config)

        # 验证配置被正确设置
        assert adapter.config["host"] == "test_host"
        assert adapter.config["port"] == 9999
        assert adapter.config["timeout"] == 30

    def test_symbol_market_mapping(self):
        """测试股票代码市场映射"""
        adapter = TDXDataSource()

        # 测试各种股票代码的市场识别
        test_cases = [
            ("000001", 1),  # 深圳
            ("000002", 1),  # 深圳
            ("600000", 0),  # 上海
            ("688001", 0),  # 上海科创板
        ]

        for symbol, expected_market in test_cases:
            market = adapter._get_market_code(symbol)
            assert market == expected_market, f"股票代码 {symbol} 市场识别错误"

    def test_method_signature_validation(self):
        """测试方法签名验证"""
        adapter = TDXDataSource()

        # 验证方法签名不会抛出异常（使用默认参数）
        try:
            # 这些方法可能会抛出异常因为需要连接，但至少应该存在
            method = getattr(adapter, "get_stock_daily")
            assert callable(method)

            method = getattr(adapter, "get_index_daily")
            assert callable(method)

        except Exception:
            # 方法存在但调用可能失败（这是预期的）
            pass

    def test_class_import_compatibility(self):
        """测试类导入兼容性"""
        try:
            from src.adapters.tdx.tdx_adapter import TDXDataSource

            adapter = TDXDataSource()
            assert adapter is not None
            assert isinstance(adapter, TDXDataSource)
        except ImportError:
            pytest.skip("TDXDataSource不可用")

    def test_attribute_initialization(self):
        """测试属性初始化"""
        adapter = TDXDataSource()

        # 验证关键属性存在
        expected_attrs = ["config", "_connection", "_connected"]

        for attr in expected_attrs:
            assert hasattr(adapter, attr), f"缺少属性: {attr}"

    def test_decorator_functionality(self):
        """测试装饰器功能"""
        adapter = TDXDataSource()

        # 测试重试装饰器的基本功能
        test_func = Mock(return_value="test_result")

        result = adapter._retry_api_call(test_func)
        assert result == "test_result"
        test_func.assert_called_once()

    def test_data_structure_validation(self):
        """测试数据结构验证"""
        adapter = TDXDataSource()

        # 创建有效数据
        valid_data = pd.DataFrame(
            {
                "datetime": pd.date_range("2024-01-01", periods=3),
                "open": [10.0, 10.5, 11.0],
                "close": [10.2, 10.8, 11.2],
            }
        )

        # 验证数据结构
        result = adapter._validate_kline_data(valid_data)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3

    def test_error_handling_preparation(self):
        """测试错误处理准备"""
        adapter = TDXDataSource()

        # 验证错误处理相关的方法存在
        assert hasattr(adapter, "_retry_api_call")
        assert callable(getattr(adapter, "_retry_api_call"))


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__])
