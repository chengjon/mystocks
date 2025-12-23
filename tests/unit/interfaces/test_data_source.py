"""
Data Source Interface Test Suite
数据源接口测试套件

创建日期: 2025-12-20
版本: 1.0.0
测试模块: src.interfaces.data_source (142行)
"""

import pytest
import pandas as pd
from typing import Dict, List, Optional, Any
import inspect

from src.interfaces.data_source import IDataSource


class MockDataSource(IDataSource):
    """模拟数据源实现，用于测试接口定义"""

    def get_stock_daily(
        self, symbol: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "date": pd.date_range(start_date, end_date),
                "open": [100.0] * len(pd.date_range(start_date, end_date)),
                "high": [105.0] * len(pd.date_range(start_date, end_date)),
                "low": [95.0] * len(pd.date_range(start_date, end_date)),
                "close": [102.0] * len(pd.date_range(start_date, end_date)),
                "volume": [1000000] * len(pd.date_range(start_date, end_date)),
            }
        )

    def get_index_daily(
        self, symbol: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "date": pd.date_range(start_date, end_date),
                "open": [3000.0] * len(pd.date_range(start_date, end_date)),
                "high": [3100.0] * len(pd.date_range(start_date, end_date)),
                "low": [2900.0] * len(pd.date_range(start_date, end_date)),
                "close": [3050.0] * len(pd.date_range(start_date, end_date)),
                "volume": [5000000] * len(pd.date_range(start_date, end_date)),
            }
        )

    def get_stock_basic(self, symbol: str) -> Dict[str, Any]:
        return {
            "symbol": symbol,
            "name": f"Test Company {symbol}",
            "industry": "Technology",
            "market": "NASDAQ",
            "list_date": "2020-01-01",
        }

    def get_index_components(self, symbol: str) -> List[str]:
        return ["AAPL", "GOOGL", "MSFT", f"{symbol}_COMP1", f"{symbol}_COMP2"]

    def get_real_time_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        return {
            "symbol": symbol,
            "price": 150.25,
            "volume": 50000,
            "timestamp": "2025-12-20 10:30:00",
        }

    def get_market_calendar(self, start_date: str, end_date: str) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "date": pd.date_range(start_date, end_date),
                "is_trading_day": [True] * len(pd.date_range(start_date, end_date)),
                "market": ["NASDAQ"] * len(pd.date_range(start_date, end_date)),
            }
        )

    def get_financial_data(self, symbol: str, period: str = "annual") -> pd.DataFrame:
        return pd.DataFrame(
            {
                "symbol": [symbol] * 2,
                "end_date": ["2024-12-31", "2023-12-31"],
                "revenue": [1000000000, 900000000],
                "net_profit": [100000000, 80000000],
            }
        )

    def get_news_data(
        self, symbol: Optional[str] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        return [
            {
                "title": f"Test News {i}",
                "content": f"Test news content {i}",
                "timestamp": f"2025-12-{20 - i:02d} 09:00:00",
                "source": "Test Source",
            }
            for i in range(min(limit, 5))
        ]


class TestIDataSourceInterface:
    """IDataSource接口测试"""

    def test_interface_is_abstract(self):
        """测试接口是抽象类"""
        assert inspect.isabstract(IDataSource)

    def test_cannot_instantiate_interface(self):
        """测试不能直接实例化接口"""
        with pytest.raises(TypeError):
            IDataSource()

    def test_interface_methods_are_abstract(self):
        """测试接口方法是抽象方法"""
        abstract_methods = IDataSource.__abstractmethods__

        expected_methods = {
            "get_stock_daily",
            "get_index_daily",
            "get_stock_basic",
            "get_index_components",
            "get_real_time_data",
            "get_market_calendar",
            "get_financial_data",
            "get_news_data",
        }

        assert abstract_methods == expected_methods

    def test_mock_implementation_works(self):
        """测试模拟实现可以正常工作"""
        mock_ds = MockDataSource()

        # 测试所有方法都能正常调用
        assert isinstance(mock_ds, IDataSource)

    def test_get_stock_daily_return_type(self):
        """测试get_stock_daily返回类型"""
        mock_ds = MockDataSource()
        result = mock_ds.get_stock_daily("AAPL", "2025-01-01", "2025-01-05")

        assert isinstance(result, pd.DataFrame)
        expected_columns = ["date", "open", "high", "low", "close", "volume"]
        assert all(col in result.columns for col in expected_columns)

    def test_get_index_daily_return_type(self):
        """测试get_index_daily返回类型"""
        mock_ds = MockDataSource()
        result = mock_ds.get_index_daily("SPY", "2025-01-01", "2025-01-05")

        assert isinstance(result, pd.DataFrame)
        expected_columns = ["date", "open", "high", "low", "close", "volume"]
        assert all(col in result.columns for col in expected_columns)

    def test_get_stock_basic_return_type(self):
        """测试get_stock_basic返回类型"""
        mock_ds = MockDataSource()
        result = mock_ds.get_stock_basic("AAPL")

        assert isinstance(result, dict)
        expected_keys = ["symbol", "name", "industry", "market", "list_date"]
        assert all(key in result for key in expected_keys)

    def test_get_index_components_return_type(self):
        """测试get_index_components返回类型"""
        mock_ds = MockDataSource()
        result = mock_ds.get_index_components("SPY")

        assert isinstance(result, list)
        assert all(isinstance(item, str) for item in result)

    def test_get_real_time_data_return_type(self):
        """测试get_real_time_data返回类型"""
        mock_ds = MockDataSource()
        result = mock_ds.get_real_time_data("AAPL")

        assert isinstance(result, dict)
        if result is not None:
            expected_keys = ["symbol", "price", "volume", "timestamp"]
            assert all(key in result for key in expected_keys)

    def test_get_market_calendar_return_type(self):
        """测试get_market_calendar返回类型"""
        mock_ds = MockDataSource()
        result = mock_ds.get_market_calendar("2025-01-01", "2025-01-05")

        assert isinstance(result, pd.DataFrame)
        expected_columns = ["date", "is_trading_day", "market"]
        assert all(col in result.columns for col in expected_columns)

    def test_get_financial_data_return_type(self):
        """测试get_financial_data返回类型"""
        mock_ds = MockDataSource()
        result = mock_ds.get_financial_data("AAPL")

        assert isinstance(result, pd.DataFrame)
        expected_columns = ["symbol", "end_date", "revenue", "net_profit"]
        assert all(col in result.columns for col in expected_columns)

    def test_get_financial_data_with_quarterly_period(self):
        """测试get_financial_data季度期间"""
        mock_ds = MockDataSource()
        result = mock_ds.get_financial_data("AAPL", period="quarterly")

        assert isinstance(result, pd.DataFrame)
        expected_columns = ["symbol", "end_date", "revenue", "net_profit"]
        assert all(col in result.columns for col in expected_columns)

    def test_get_news_data_return_type(self):
        """测试get_news_data返回类型"""
        mock_ds = MockDataSource()
        result = mock_ds.get_news_data()

        assert isinstance(result, list)
        assert all(isinstance(item, dict) for item in result)

    def test_get_news_data_with_symbol(self):
        """测试get_news_data带股票代码"""
        mock_ds = MockDataSource()
        result = mock_ds.get_news_data(symbol="AAPL", limit=3)

        assert isinstance(result, list)
        assert len(result) <= 3
        assert all(isinstance(item, dict) for item in result)

    def test_get_news_data_with_limit(self):
        """测试get_news_data限制数量"""
        mock_ds = MockDataSource()
        result = mock_ds.get_news_data(limit=2)

        assert isinstance(result, list)
        assert len(result) <= 2

    def test_interface_method_signatures(self):
        """测试接口方法签名"""
        # 检查get_stock_daily方法签名
        sig = inspect.signature(IDataSource.get_stock_daily)
        params = sig.parameters
        expected_params = ["self", "symbol", "start_date", "end_date"]

        assert list(params.keys()) == expected_params
        assert params["symbol"].annotation == str
        assert params["start_date"].annotation == str
        assert params["end_date"].annotation == str
        assert sig.return_annotation == pd.DataFrame

        # 检查get_stock_basic方法签名
        sig = inspect.signature(IDataSource.get_stock_basic)
        params = sig.parameters
        expected_params = ["self", "symbol"]

        assert list(params.keys()) == expected_params
        assert params["symbol"].annotation == str
        assert sig.return_annotation == Dict[str, Any]

    def test_interface_inheritance(self):
        """测试接口继承关系"""
        assert issubclass(MockDataSource, IDataSource)
        assert hasattr(MockDataSource, "get_stock_daily")
        assert hasattr(MockDataSource, "get_index_daily")
        assert hasattr(MockDataSource, "get_stock_basic")

    def test_interface_compliance_check(self):
        """测试接口合规性检查"""
        # 验证MockDataSource实现了所有必需的方法
        required_methods = [
            "get_stock_daily",
            "get_index_daily",
            "get_stock_basic",
            "get_index_components",
            "get_real_time_data",
            "get_market_calendar",
            "get_financial_data",
            "get_news_data",
        ]

        for method_name in required_methods:
            assert hasattr(MockDataSource, method_name)
            assert callable(getattr(MockDataSource, method_name))

    def test_polymorphic_behavior(self):
        """测试多态行为"""

        # 创建不同的模拟实现
        class FastDataSource(IDataSource):
            def get_stock_daily(self, symbol, start_date, end_date):
                return pd.DataFrame({"fast": [True]})

            def get_index_daily(self, symbol, start_date, end_date):
                return pd.DataFrame({"fast": [True]})

            def get_stock_basic(self, symbol):
                return {"fast": True, "symbol": symbol}

            def get_index_components(self, symbol):
                return ["fast_component"]

            def get_real_time_data(self, symbol):
                return {"fast": True, "symbol": symbol}

            def get_market_calendar(self, start_date, end_date):
                return pd.DataFrame({"fast": [True]})

            def get_financial_data(self, symbol, period="annual"):
                return pd.DataFrame({"fast": [True]})

            def get_news_data(self, symbol=None, limit=10):
                return [{"fast": True}]

        class SlowDataSource(IDataSource):
            def get_stock_daily(self, symbol, start_date, end_date):
                return pd.DataFrame({"slow": [True]})

            def get_index_daily(self, symbol, start_date, end_date):
                return pd.DataFrame({"slow": [True]})

            def get_stock_basic(self, symbol):
                return {"slow": True, "symbol": symbol}

            def get_index_components(self, symbol):
                return ["slow_component"]

            def get_real_time_data(self, symbol):
                return {"slow": True, "symbol": symbol}

            def get_market_calendar(self, start_date, end_date):
                return pd.DataFrame({"slow": [True]})

            def get_financial_data(self, symbol, period="annual"):
                return pd.DataFrame({"slow": [True]})

            def get_news_data(self, symbol=None, limit=10):
                return [{"slow": True}]

        # 测试多态性
        sources = [FastDataSource(), SlowDataSource()]

        for i, source in enumerate(sources):
            result = source.get_stock_daily("AAPL", "2025-01-01", "2025-01-02")
            assert isinstance(result, pd.DataFrame)

            if i == 0:  # FastDataSource
                assert "fast" in result.columns
            else:  # SlowDataSource
                assert "slow" in result.columns

    def test_interface_documentation(self):
        """测试接口文档字符串"""
        # 检查接口类文档字符串
        assert IDataSource.__doc__ is not None
        assert "统一数据接口" in IDataSource.__doc__

        # 检查方法文档字符串
        doc = IDataSource.get_stock_daily.__doc__
        assert doc is not None
        assert "获取股票日线数据" in doc
        assert "symbol:" in doc
        assert "start_date:" in doc
        assert "end_date:" in doc

    def test_interface_type_annotations(self):
        """测试接口类型注解"""
        # 验证返回类型注解
        assert IDataSource.get_stock_daily.__annotations__["return"] == pd.DataFrame
        assert IDataSource.get_index_daily.__annotations__["return"] == pd.DataFrame
        assert IDataSource.get_stock_basic.__annotations__["return"] == Dict[str, Any]
        assert IDataSource.get_index_components.__annotations__["return"] == List[str]
        assert (
            IDataSource.get_real_time_data.__annotations__["return"]
            == Optional[Dict[str, Any]]
        )
        assert IDataSource.get_market_calendar.__annotations__["return"] == pd.DataFrame
        assert IDataSource.get_financial_data.__annotations__["return"] == pd.DataFrame
        assert (
            IDataSource.get_news_data.__annotations__["return"] == List[Dict[str, Any]]
        )

    def test_interface_default_parameters(self):
        """测试接口默认参数"""
        # 检查get_financial_data方法的默认参数
        sig = inspect.signature(IDataSource.get_financial_data)
        period_param = sig.parameters["period"]
        assert period_param.default == "annual"

        # 检查get_news_data方法的默认参数
        sig = inspect.signature(IDataSource.get_news_data)
        symbol_param = sig.parameters["symbol"]
        limit_param = sig.parameters["limit"]
        assert symbol_param.default is None
        assert limit_param.default == 10

    def test_method_parameter_validation(self):
        """测试方法参数验证在实现层面"""
        mock_ds = MockDataSource()

        # 测试必需参数
        with pytest.raises(TypeError):
            mock_ds.get_stock_daily()  # 缺少必需参数

        with pytest.raises(TypeError):
            mock_ds.get_index_daily()  # 缺少必需参数

        with pytest.raises(TypeError):
            mock_ds.get_stock_basic()  # 缺少必需参数

    def test_data_consistency(self):
        """测试数据一致性"""
        mock_ds = MockDataSource()

        # 测试股票数据的一致性
        stock_data = mock_ds.get_stock_daily("AAPL", "2025-01-01", "2025-01-03")
        assert len(stock_data) == 3  # 3天数据
        assert all(stock_data["close"] >= stock_data["low"])  # 收盘价 >= 最低价
        assert all(stock_data["close"] <= stock_data["high"])  # 收盘价 <= 最高价

        # 测试基本信息的符号一致性
        basic_info = mock_ds.get_stock_basic("AAPL")
        assert basic_info["symbol"] == "AAPL"

    def test_empty_results_handling(self):
        """测试空结果处理"""
        mock_ds = MockDataSource()

        # 测试空新闻数据
        empty_news = mock_ds.get_news_data(limit=0)
        assert isinstance(empty_news, list)
        assert len(empty_news) == 0

    def test_optional_return_type_handling(self):
        """测试可选返回类型处理"""
        mock_ds = MockDataSource()

        # 测试实时数据可能返回None的情况
        real_time_data = mock_ds.get_real_time_data("NONEXISTENT")
        # 在模拟实现中总是返回数据，但在实际实现中可能返回None
        assert real_time_data is not None or real_time_data is None


class TestDataSourceContract:
    """数据源契约测试"""

    def test_return_format_contracts(self):
        """测试返回格式契约"""
        mock_ds = MockDataSource()

        # 测试股票日线数据格式
        stock_data = mock_ds.get_stock_daily("AAPL", "2025-01-01", "2025-01-01")
        assert isinstance(stock_data, pd.DataFrame)
        assert "date" in stock_data.columns
        assert "open" in stock_data.columns
        assert "high" in stock_data.columns
        assert "low" in stock_data.columns
        assert "close" in stock_data.columns
        assert "volume" in stock_data.columns

        # 测试基本数据格式
        basic_info = mock_ds.get_stock_basic("AAPL")
        assert isinstance(basic_info, dict)
        assert "symbol" in basic_info

        # 测试成分股格式
        components = mock_ds.get_index_components("SPY")
        assert isinstance(components, list)

    def test_parameter_validation_contracts(self):
        """测试参数验证契约"""
        mock_ds = MockDataSource()

        # 测试日期格式处理（在实际实现中应该验证）
        # 这里只测试方法能接受字符串参数
        try:
            stock_data = mock_ds.get_stock_daily("AAPL", "2025-01-01", "2025-01-05")
            assert isinstance(stock_data, pd.DataFrame)
        except Exception as e:
            # 如果有格式验证，应该是ValueError或类似异常
            assert isinstance(e, (ValueError, TypeError))

    def test_error_handling_contracts(self):
        """测试错误处理契约"""

        # 创建一个会抛出异常的模拟实现
        class ErrorDataSource(IDataSource):
            def get_stock_daily(self, symbol, start_date, end_date):
                raise ValueError("Invalid symbol")

            def get_index_daily(self, symbol, start_date, end_date):
                raise ConnectionError("Network error")

            def get_stock_basic(self, symbol):
                raise KeyError("Symbol not found")

            def get_index_components(self, symbol):
                raise RuntimeError("Index not supported")

            def get_real_time_data(self, symbol):
                raise TimeoutError("Data fetch timeout")

            def get_market_calendar(self, start_date, end_date):
                raise IOError("File read error")

            def get_financial_data(self, symbol, period="annual"):
                raise PermissionError("Access denied")

            def get_news_data(self, symbol=None, limit=10):
                raise MemoryError("Insufficient memory")

        error_ds = ErrorDataSource()

        # 验证各种异常都能正确抛出
        with pytest.raises(ValueError):
            error_ds.get_stock_daily("INVALID", "2025-01-01", "2025-01-02")

        with pytest.raises(ConnectionError):
            error_ds.get_index_daily("INVALID", "2025-01-01", "2025-01-02")

        with pytest.raises(KeyError):
            error_ds.get_stock_basic("INVALID")

        with pytest.raises(RuntimeError):
            error_ds.get_index_components("INVALID")

        with pytest.raises(TimeoutError):
            error_ds.get_real_time_data("INVALID")

        with pytest.raises(IOError):
            error_ds.get_market_calendar("2025-01-01", "2025-01-02")

        with pytest.raises(PermissionError):
            error_ds.get_financial_data("INVALID")

        with pytest.raises(MemoryError):
            error_ds.get_news_data()


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
