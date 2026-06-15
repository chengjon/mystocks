"""
Data Source Manager基础测试
专注于提升Data Source Manager覆盖率（128行代码）
"""

import os
import sys

import pandas as pd
import pytest

# 添加源码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

# 测试目标模块
try:
    from src.adapters.data_source_manager import DataSourceManager
    from src.interfaces.data_source import IDataSource
except ImportError as e:
    pytest.skip(f"无法导入DataSourceManager: {e} owner=test-governance issue=techdebt-expired-markers ttl=2026-06-30", allow_module_level=True)


class BasicMockDataSource(IDataSource):
    """Minimal IDataSource implementation for DataSourceManager contract tests."""

    def __init__(self, name: str = "source"):
        self.name = name
        self.calls: list[tuple] = []

    def get_stock_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        self.calls.append(("get_stock_daily", symbol, start_date, end_date))
        return pd.DataFrame({"symbol": [symbol], "start_date": [start_date], "end_date": [end_date]})

    def get_index_daily(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        self.calls.append(("get_index_daily", symbol, start_date, end_date))
        return pd.DataFrame({"symbol": [symbol], "start_date": [start_date], "end_date": [end_date]})

    def get_stock_basic(self, symbol: str) -> dict:
        self.calls.append(("get_stock_basic", symbol))
        return {"symbol": symbol, "source": self.name}

    def get_index_components(self, symbol: str) -> list[str]:
        self.calls.append(("get_index_components", symbol))
        return [symbol]

    def get_real_time_data(self, symbol: str) -> dict:
        self.calls.append(("get_real_time_data", symbol))
        return {"symbol": symbol, "price": 10.0, "source": self.name}

    def get_market_calendar(self, start_date: str, end_date: str) -> pd.DataFrame:
        self.calls.append(("get_market_calendar", start_date, end_date))
        return pd.DataFrame({"date": [start_date, end_date]})

    def get_financial_data(self, symbol: str, period: str = "annual") -> pd.DataFrame:
        self.calls.append(("get_financial_data", symbol, period))
        return pd.DataFrame({"symbol": [symbol], "period": [period]})

    def get_news_data(self, symbol: str | None = None, limit: int = 10) -> list[dict]:
        self.calls.append(("get_news_data", symbol, limit))
        return [{"symbol": symbol, "limit": limit}]


class TestDataSourceManagerBasic:
    """DataSourceManager基础测试 - 专注覆盖率"""

    def test_initialization(self):
        """测试管理器初始化"""
        manager = DataSourceManager(use_v2=False)

        # 验证基本属性
        assert hasattr(manager, "_sources")
        assert isinstance(manager._sources, dict)
        assert len(manager._sources) == 0  # 初始状态为空

    def test_register_source_method(self):
        """测试注册数据源方法"""
        manager = DataSourceManager(use_v2=False)

        # 创建模拟数据源
        mock_source = BasicMockDataSource()

        # 注册数据源
        manager.register_source("test_source", mock_source)

        # 验证注册成功
        assert "test_source" in manager._sources
        assert manager._sources["test_source"] == mock_source

    def test_get_source_existing(self):
        """测试获取已存在的数据源"""
        manager = DataSourceManager(use_v2=False)

        # 创建并注册模拟数据源
        mock_source = BasicMockDataSource()
        manager.register_source("existing_source", mock_source)

        # 获取数据源
        result = manager.get_source("existing_source")
        assert result == mock_source

    def test_get_source_non_existing(self):
        """测试获取不存在的数据源"""
        manager = DataSourceManager(use_v2=False)

        # 获取不存在的数据源
        result = manager.get_source("non_existing_source")
        assert result is None

    def test_list_sources_empty(self):
        """测试列出空数据源列表"""
        manager = DataSourceManager(use_v2=False)

        # 列出数据源
        result = manager.list_sources()
        assert isinstance(result, list)
        assert len(result) == 0

    def test_list_sources_with_data(self):
        """测试列出有数据源的列表"""
        manager = DataSourceManager(use_v2=False)

        # 添加几个数据源
        mock_source1 = BasicMockDataSource("source1")
        mock_source2 = BasicMockDataSource("source2")
        manager.register_source("source1", mock_source1)
        manager.register_source("source2", mock_source2)

        # 列出数据源
        result = manager.list_sources()
        assert isinstance(result, list)
        assert len(result) == 2
        assert "source1" in result
        assert "source2" in result

    def test_get_real_time_data_method(self):
        """测试获取实时数据方法"""
        manager = DataSourceManager(use_v2=False)
        mock_source = BasicMockDataSource("source_name")
        manager.register_source("source_name", mock_source)

        # 调用方法
        result = manager.get_real_time_data("symbol", "source_name")

        # 验证调用
        assert result == {"symbol": "symbol", "price": 10.0, "source": "source_name"}
        assert mock_source.calls == [("get_real_time_data", "symbol")]

    def test_get_stock_daily_method(self):
        """测试获取股票日线数据方法"""
        manager = DataSourceManager(use_v2=False)
        mock_source = BasicMockDataSource("source_name")
        manager.register_source("source_name", mock_source)

        # 调用方法
        result = manager.get_stock_daily("symbol", "start", "end", source="source_name")

        # 验证调用
        assert result["symbol"].iloc[0] == "symbol"
        assert mock_source.calls == [("get_stock_daily", "symbol", "start", "end")]

    def test_get_index_daily_method(self):
        """测试获取指数日线数据方法"""
        manager = DataSourceManager(use_v2=False)
        mock_source = BasicMockDataSource("source_name")
        manager.register_source("source_name", mock_source)

        # 调用方法
        result = manager.get_index_daily("symbol", "start", "end", source="source_name")

        # 验证调用
        assert result["symbol"].iloc[0] == "symbol"
        assert mock_source.calls == [("get_index_daily", "symbol", "start", "end")]

    def test_get_stock_basic_method(self):
        """测试获取股票基本信息方法"""
        manager = DataSourceManager(use_v2=False)
        mock_source = BasicMockDataSource("source_name")
        manager.register_source("source_name", mock_source)

        # 调用方法
        result = manager.get_stock_basic("symbol", "source_name")

        # 验证调用
        assert result == {"symbol": "symbol", "source": "source_name"}
        assert mock_source.calls == [("get_stock_basic", "symbol")]

    def test_register_source_with_duplicate_name(self):
        """测试重复注册同名数据源"""
        manager = DataSourceManager(use_v2=False)

        # 创建两个模拟数据源
        mock_source1 = BasicMockDataSource("source1")
        mock_source2 = BasicMockDataSource("source2")

        # 注册同名数据源（应该覆盖）
        manager.register_source("duplicate_source", mock_source1)
        manager.register_source("duplicate_source", mock_source2)

        # 验证最后一次注册生效
        assert manager._sources["duplicate_source"] == mock_source2
        assert len(manager._sources) == 1

    def test_factory_pattern_implementation(self):
        """测试工厂模式实现"""
        manager = DataSourceManager(use_v2=False)

        # 验证工厂方法存在
        factory_methods = ["register_source", "get_source", "list_sources"]

        for method in factory_methods:
            assert hasattr(manager, method), f"缺少工厂方法: {method}"
            assert callable(getattr(manager, method)), f"方法不可调用: {method}"

    def test_data_source_storage(self):
        """测试数据源存储机制"""
        manager = DataSourceManager(use_v2=False)

        # 添加多个数据源
        sources = {
            "akshare": BasicMockDataSource("akshare"),
            "baostock": BasicMockDataSource("baostock"),
            "tushare": BasicMockDataSource("tushare"),
        }

        for name, source in sources.items():
            manager.register_source(name, source)

        # 验证存储完整性
        assert len(manager._sources) == 3
        for name in sources.keys():
            assert name in manager._sources
            assert manager._sources[name] == sources[name]

    def test_method_error_handling(self):
        """测试方法错误处理"""
        manager = DataSourceManager(use_v2=False)

        # 测试获取不存在的数据源不会崩溃
        result = manager.get_source("non_existent")
        assert result is None

        # 测试空列表
        result = manager.list_sources()
        assert isinstance(result, list)

    def test_manager_class_structure(self):
        """测试管理器类结构"""
        manager = DataSourceManager(use_v2=False)

        # 验证核心属性
        expected_attrs = ["_sources", "_priority_config"]

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

            manager = DataSourceManager(use_v2=False)
            assert manager is not None
            assert isinstance(manager, DataSourceManager)
        except ImportError:
            pytest.skip("DataSourceManager不可用 owner=data-adapters issue=techdebt-expired-markers ttl=2026-06-30")

    def test_flexibility_with_different_sources(self):
        """测试对不同数据源的灵活性"""
        manager = DataSourceManager(use_v2=False)

        # 测试不同类型的模拟数据源
        source_types = [
            ("api_source", BasicMockDataSource("api_source")),
            ("file_source", BasicMockDataSource("file_source")),
            ("cache_source", BasicMockDataSource("cache_source")),
        ]

        for source_name, source_obj in source_types:
            manager.register_source(source_name, source_obj)
            assert source_name in manager._sources
            assert manager._sources[source_name] == source_obj

    def test_empty_manager_operations(self):
        """测试空管理器操作"""
        manager = DataSourceManager(use_v2=False)

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
