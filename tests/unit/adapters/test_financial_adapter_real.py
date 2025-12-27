"""
Financial适配器真实测试
基于实际API结构测试FinancialDataSource类
"""

import pytest
import pandas as pd
from unittest.mock import patch
import sys
import os

# 添加源码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

# 测试目标模块
try:
    from src.adapters.financial_adapter import FinancialDataSource
except ImportError as e:
    pytest.skip(f"无法导入FinancialDataSource: {e}", allow_module_level=True)


class TestFinancialDataSourceReal:
    """FinancialDataSource真实测试 - 基于实际API"""

    def test_initialization(self):
        """测试适配器初始化"""
        adapter = FinancialDataSource()

        # 验证基本属性
        assert hasattr(adapter, "efinance_available")
        assert hasattr(adapter, "easyquotation_available")
        assert hasattr(adapter, "data_cache")
        assert isinstance(adapter.data_cache, dict)

    def test_has_core_methods(self):
        """测试拥有核心方法"""
        adapter = FinancialDataSource()

        # 验证方法存在
        core_methods = [
            "get_stock_daily",
            "get_index_daily",
            "get_stock_basic",
            "get_index_components",
        ]

        for method in core_methods:
            assert hasattr(adapter, method), f"缺少方法: {method}"
            assert callable(getattr(adapter, method)), f"方法不可调用: {method}"

    def test_get_cache_key_method(self):
        """测试缓存键生成方法"""
        adapter = FinancialDataSource()

        # 测试缓存键生成
        cache_key = adapter._get_cache_key("000001", "daily", start_date="20240101")
        assert isinstance(cache_key, str)
        assert "000001" in cache_key
        assert "daily" in cache_key

    def test_cache_methods(self):
        """测试缓存相关方法"""
        adapter = FinancialDataSource()

        # 测试缓存键生成
        cache_key = adapter._get_cache_key("TEST", "data")

        # 测试保存到缓存
        test_data = {"test": "data"}
        adapter._save_to_cache(cache_key, test_data)

        # 测试从缓存获取
        cached_data = adapter._get_from_cache(cache_key)
        assert cached_data == test_data

    @patch("src.adapters.financial_adapter.efinance")
    def test_get_stock_daily_method(self, mock_efinance):
        """测试获取股票日线数据方法"""
        # 设置模拟数据
        mock_df = pd.DataFrame(
            {
                "日期": ["2024-01-01", "2024-01-02"],
                "开盘": [10.0, 10.5],
                "收盘": [10.2, 10.8],
                "最高": [10.5, 11.0],
                "最低": [9.8, 10.3],
                "成交量": [1000000, 1200000],
            }
        )
        mock_efinance.stock.get_quote_history.return_value = mock_df

        adapter = FinancialDataSource()

        # 调用方法
        result = adapter.get_stock_daily("000001", start_date="20240101", end_date="20240102")

        # 验证结果
        assert isinstance(result, pd.DataFrame)

    @patch("src.adapters.financial_adapter.efinance")
    def test_get_index_daily_method(self, mock_efinance):
        """测试获取指数日线数据方法"""
        # 设置模拟数据
        mock_df = pd.DataFrame({"日期": ["2024-01-01", "2024-01-02"], "收盘": [3000.0, 3020.0]})
        mock_efinance.stock.get_quote_history.return_value = mock_df

        adapter = FinancialDataSource()

        # 调用方法
        result = adapter.get_index_daily("000001", start_date="20240101", end_date="20240102")

        # 验证结果
        assert isinstance(result, pd.DataFrame)

    @patch("src.adapters.financial_adapter.efinance")
    def test_get_stock_basic_method(self, mock_efinance):
        """测试获取股票基本信息方法"""
        # 设置模拟数据
        mock_df = pd.DataFrame({"股票代码": ["000001"], "股票名称": ["平安银行"]})
        mock_efinance.stock.get_base_info.return_value = mock_df

        adapter = FinancialDataSource()

        # 调用方法
        result = adapter.get_stock_basic("000001")

        # 验证结果
        assert isinstance(result, dict)

    def test_method_availability_flags(self):
        """测试数据源可用性标志"""
        adapter = FinancialDataSource()

        # 验证所有可用性标志存在
        flags = [
            "efinance_available",
            "easyquotation_available",
            "akshare_available",
            "tushare_available",
            "byapi_available",
            "sina_crawler_available",
        ]

        for flag in flags:
            assert hasattr(adapter, flag)
            assert isinstance(getattr(adapter, flag), bool)

    def test_data_cache_structure(self):
        """测试数据缓存结构"""
        adapter = FinancialDataSource()

        # 验证缓存是字典
        assert isinstance(adapter.data_cache, dict)

        # 测试缓存操作
        cache_key = adapter._get_cache_key("TEST", "test_type")

        # 保存测试数据
        test_data = {"key": "value"}
        adapter._save_to_cache(cache_key, test_data)

        # 验证数据已保存
        assert cache_key in adapter.data_cache
        assert adapter.data_cache[cache_key] == test_data

    def test_import_compatibility(self):
        """测试导入兼容性"""
        # 验证可以正常导入
        try:
            from src.adapters.financial_adapter import FinancialDataSource

            adapter = FinancialDataSource()
            assert adapter is not None
        except ImportError:
            pytest.skip("FinancialDataSource不可用")

    def test_class_docstring(self):
        """测试类文档"""
        adapter = FinancialDataSource()
        assert adapter.__class__.__doc__ is not None
        assert len(adapter.__class__.__doc__) > 0

    def test_init_data_sources_method_exists(self):
        """测试初始化数据源方法存在"""
        adapter = FinancialDataSource()
        assert hasattr(adapter, "_init_data_sources")
        assert callable(getattr(adapter, "_init_data_sources"))


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__])
