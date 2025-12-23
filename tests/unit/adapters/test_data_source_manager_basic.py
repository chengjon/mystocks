"""
Data Source Manager基础测试
专注于提升Data Source Manager覆盖率（128行代码）
"""

import os
import sys
from unittest.mock import Mock, patch

import pytest

# 添加源码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

# 测试目标模块
try:
    from src.adapters.data_source_manager import DataSourceManager
except ImportError as e:
    pytest.skip(f"无法导入DataSourceManager: {e}", allow_module_level=True)


class TestDataSourceManagerBasic:
    """DataSourceManager基础测试 - 专注覆盖率"""

    def test_initialization(self):
        """测试管理器初始化"""
        manager = DataSourceManager()

        # 验证基本属性
        assert hasattr(manager, "sources")
        assert isinstance(manager.sources, dict)
        assert len(manager.sources) == 0  # 初始状态为空

    def test_register_source_method(self):
        """测试注册数据源方法"""
        manager = DataSourceManager()

        # 创建模拟数据源
        mock_source = Mock()
        mock_source.get_stock_daily.return_value = "test_data"

        # 注册数据源
        manager.register_source("test_source", mock_source)

        # 验证注册成功
        assert "test_source" in manager.sources
        assert manager.sources["test_source"] == mock_source

    def test_get_source_existing(self):
        """测试获取已存在的数据源"""
        manager = DataSourceManager()

        # 创建并注册模拟数据源
        mock_source = Mock()
        manager.register_source("existing_source", mock_source)

        # 获取数据源
        result = manager.get_source("existing_source")
        assert result == mock_source

    def test_get_source_non_existing(self):
        """测试获取不存在的数据源"""
        manager = DataSourceManager()

        # 获取不存在的数据源
        result = manager.get_source("non_existing_source")
        assert result is None

    def test_list_sources_empty(self):
        """测试列出空数据源列表"""
        manager = DataSourceManager()

        # 列出数据源
        result = manager.list_sources()
        assert isinstance(result, list)
        assert len(result) == 0

    def test_list_sources_with_data(self):
        """测试列出有数据源的列表"""
        manager = DataSourceManager()

        # 添加几个数据源
        mock_source1 = Mock()
        mock_source2 = Mock()
        manager.register_source("source1", mock_source1)
        manager.register_source("source2", mock_source2)

        # 列出数据源
        result = manager.list_sources()
        assert isinstance(result, list)
        assert len(result) == 2
        assert "source1" in result
        assert "source2" in result

    @patch("src.adapters.data_source_manager.DataSourceManager.get_source")
    def test_get_real_time_data_method(self, mock_get_source):
        """测试获取实时数据方法"""
        manager = DataSourceManager()
        mock_source = Mock()
        mock_get_source.return_value = mock_source

        # 设置模拟返回值
        mock_source.get_real_time_data.return_value = {"price": 10.0}

        # 调用方法
        result = manager.get_real_time_data("symbol", "source_name")

        # 验证调用
        mock_get_source.assert_called_once_with("source_name")
        mock_source.get_real_time_data.assert_called_once_with("symbol")

    @patch("src.adapters.data_source_manager.DataSourceManager.get_source")
    def test_get_stock_daily_method(self, mock_get_source):
        """测试获取股票日线数据方法"""
        manager = DataSourceManager()
        mock_source = Mock()
        mock_get_source.return_value = mock_source

        # 设置模拟返回值
        mock_source.get_stock_daily.return_value = "test_daily_data"

        # 调用方法
        result = manager.get_stock_daily("symbol", "source_name", "start", "end")

        # 验证调用
        mock_get_source.assert_called_once_with("source_name")
        mock_source.get_stock_daily.assert_called_once()

    @patch("src.adapters.data_source_manager.DataSourceManager.get_source")
    def test_get_index_daily_method(self, mock_get_source):
        """测试获取指数日线数据方法"""
        manager = DataSourceManager()
        mock_source = Mock()
        mock_get_source.return_value = mock_source

        # 设置模拟返回值
        mock_source.get_index_daily.return_value = "test_index_data"

        # 调用方法
        result = manager.get_index_daily("symbol", "source_name", "start", "end")

        # 验证调用
        mock_get_source.assert_called_once_with("source_name")
        mock_source.get_index_daily.assert_called_once()

    @patch("src.adapters.data_source_manager.DataSourceManager.get_source")
    def test_get_stock_basic_method(self, mock_get_source):
        """测试获取股票基本信息方法"""
        manager = DataSourceManager()
        mock_source = Mock()
        mock_get_source.return_value = mock_source

        # 设置模拟返回值
        mock_source.get_stock_basic.return_value = {"symbol": "TEST"}

        # 调用方法
        result = manager.get_stock_basic("symbol", "source_name")

        # 验证调用
        mock_get_source.assert_called_once_with("source_name")
        mock_source.get_stock_basic.assert_called_once_with("symbol")

    def test_register_source_with_duplicate_name(self):
        """测试重复注册同名数据源"""
        manager = DataSourceManager()

        # 创建两个模拟数据源
        mock_source1 = Mock()
        mock_source2 = Mock()

        # 注册同名数据源（应该覆盖）
        manager.register_source("duplicate_source", mock_source1)
        manager.register_source("duplicate_source", mock_source2)

        # 验证最后一次注册生效
        assert manager.sources["duplicate_source"] == mock_source2
        assert len(manager.sources) == 1

    def test_factory_pattern_implementation(self):
        """测试工厂模式实现"""
        manager = DataSourceManager()

        # 验证工厂方法存在
        factory_methods = ["register_source", "get_source", "list_sources"]

        for method in factory_methods:
            assert hasattr(manager, method), f"缺少工厂方法: {method}"
            assert callable(getattr(manager, method)), f"方法不可调用: {method}"

    def test_data_source_storage(self):
        """测试数据源存储机制"""
        manager = DataSourceManager()

        # 添加多个数据源
        sources = {"akshare": Mock(), "baostock": Mock(), "tushare": Mock()}

        for name, source in sources.items():
            manager.register_source(name, source)

        # 验证存储完整性
        assert len(manager.sources) == 3
        for name in sources.keys():
            assert name in manager.sources
            assert manager.sources[name] == sources[name]

    def test_method_error_handling(self):
        """测试方法错误处理"""
        manager = DataSourceManager()

        # 测试获取不存在的数据源不会崩溃
        result = manager.get_source("non_existent")
        assert result is None

        # 测试空列表
        result = manager.list_sources()
        assert isinstance(result, list)

    def test_manager_class_structure(self):
        """测试管理器类结构"""
        manager = DataSourceManager()

        # 验证核心属性
        expected_attrs = ["sources"]

        for attr in expected_attrs:
            assert hasattr(manager, attr), f"缺少属性: {attr}"

        # 验证核心方法
        expected_methods = ["register_source", "get_source", "list_sources"]

        for method in expected_methods:
            assert hasattr(manager, method), f"缺少方法: {method}"
            assert callable(getattr(manager, method)), f"方法不可调用: {method}"

    def test_import_compatibility(self):
        """测试导入兼容性"""
        try:
            from src.adapters.data_source_manager import DataSourceManager

            manager = DataSourceManager()
            assert manager is not None
            assert isinstance(manager, DataSourceManager)
        except ImportError:
            pytest.skip("DataSourceManager不可用")

    def test_flexibility_with_different_sources(self):
        """测试对不同数据源的灵活性"""
        manager = DataSourceManager()

        # 测试不同类型的模拟数据源
        source_types = [
            ("api_source", Mock()),
            ("file_source", Mock()),
            ("cache_source", Mock()),
        ]

        for source_name, source_obj in source_types:
            manager.register_source(source_name, source_obj)
            assert source_name in manager.sources
            assert manager.sources[source_name] == source_obj

    def test_empty_manager_operations(self):
        """测试空管理器操作"""
        manager = DataSourceManager()

        # 测试空列表
        sources = manager.list_sources()
        assert isinstance(sources, list)
        assert len(sources) == 0

        # 测试获取不存在的源
        source = manager.get_source("non_existent")
        assert source is None


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__])
