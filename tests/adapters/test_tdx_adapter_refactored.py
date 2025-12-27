"""
TDD测试框架 - TDX适配器重构
遵循红-绿-重构循环，确保拆分后的功能完整性
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
import sys
import os

# 添加项目根路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


class TestTdxConnectionManager:
    """TDX连接管理器测试类"""

    def test_init_connection_manager(self):
        """测试：初始化TDX连接管理器"""
        # TODO: 这个测试在重构前应该失败，因为没有拆分的模块
        from src.adapters.tdx_connection_manager import TdxConnectionManager

        manager = TdxConnectionManager()

        assert manager is not None
        assert hasattr(manager, "connection")
        assert hasattr(manager, "market_codes")
        assert hasattr(manager, "retry_config")

    def test_create_tdx_connection(self):
        """测试：创建TDX连接"""
        from src.adapters.tdx_connection_manager import TdxConnectionManager

        manager = TdxConnectionManager()

        # 模拟成功连接
        with patch.object(manager, "_connect_to_tdx_server") as mock_connect:
            mock_connect.return_value = Mock()

            result = manager.create_connection()

            assert result is not None
            mock_connect.assert_called_once()

    def test_get_market_code(self):
        """测试：获取市场代码"""
        from src.adapters.tdx_connection_manager import TdxConnectionManager

        manager = TdxConnectionManager()

        # 测试深交所股票
        sh_code = manager.get_market_code("000001")
        assert sh_code == 1

        # 测试上交所股票
        sz_code = manager.get_market_code("600000")
        assert sz_code == 0

    def test_retry_api_call_success(self):
        """测试：API调用重试成功"""
        from src.adapters.tdx_connection_manager import TdxConnectionManager

        manager = TdxConnectionManager()

        def test_func():
            return {"data": "test"}

        decorated_func = manager._retry_api_call(test_func)
        result = decorated_func()

        assert result == {"data": "test"}

    def test_retry_api_call_failure_then_success(self):
        """测试：API调用重试失败后成功"""
        from src.adapters.tdx_connection_manager import TdxConnectionManager

        manager = TdxConnectionManager()

        def test_func():
            if not hasattr(test_func, "call_count"):
                test_func.call_count = 0
            test_func.call_count += 1
            if test_func.call_count == 1:
                raise ConnectionError("Temporary failure")
            return {"data": "success"}

        decorated_func = manager._retry_api_call(test_func)
        result = decorated_func()

        assert result == {"data": "success"}
        assert test_func.call_count == 2

    def test_connection_health_check(self):
        """测试：连接健康检查"""
        from src.adapters.tdx_connection_manager import TdxConnectionManager

        manager = TdxConnectionManager()

        with patch.object(manager, "_test_connection_health") as mock_health:
            mock_health.return_value = True

            is_healthy = manager.check_connection_health()

            assert is_healthy is True
            mock_health.assert_called_once()


class TestTdxDataParser:
    """TDX数据解析器测试类"""

    def test_validate_kline_data(self):
        """测试：验证K线数据"""
        # TODO: 重构前应该失败
        from src.adapters.tdx_data_parser import TdxDataParser

        parser = TdxDataParser()

        # 测试有效数据
        valid_data = pd.DataFrame(
            {
                "time": [1609459200, 1609459260, 1609459320],
                "open": [10.0, 10.5, 11.0],
                "high": [10.8, 11.2, 11.5],
                "low": [9.8, 10.2, 10.8],
                "close": [10.5, 11.0, 11.2],
                "volume": [1000, 1500, 1200],
            }
        )

        result = parser.validate_kline_data(valid_data)

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert len(result) == 3

    def test_validate_kline_data_invalid(self):
        """测试：验证无效K线数据"""
        from src.adapters.tdx_data_parser import TdxDataParser

        parser = TdxDataParser()

        # 测试无效数据（高价低于开盘价）
        invalid_data = pd.DataFrame(
            {
                "time": [1609459200],
                "open": [10.0],
                "high": [9.5],  # high < open
                "low": [9.8],
                "close": [10.5],
                "volume": [1000],
            }
        )

        result = parser.validate_kline_data(invalid_data)

        # 应该过滤无效数据
        assert result is not None  # 或者返回空DataFrame

    def test_parse_kline_response(self):
        """测试：解析K线响应"""
        from src.adapters.tdx_data_parser import TdxDataParser

        parser = TdxDataParser()

        # 模拟TDX响应数据
        mock_response = {
            "count": 2,
            "data": [
                {
                    "time": 1609459200,
                    "open": 10.0,
                    "high": 10.8,
                    "low": 9.8,
                    "close": 10.5,
                    "volume": 1000,
                },
                {
                    "time": 1609459260,
                    "open": 10.5,
                    "high": 11.2,
                    "low": 10.2,
                    "close": 11.0,
                    "volume": 1500,
                },
            ],
        }

        result = parser.parse_kline_response(mock_response)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "close" in result.columns

    def test_convert_to_dataframe(self):
        """测试：转换为DataFrame"""
        from src.adapters.tdx_data_parser import TdxDataParser

        parser = TdxDataParser()

        # 测试数据转换
        raw_data = [
            {
                "time": 1609459200,
                "open": 10.0,
                "high": 10.8,
                "low": 9.8,
                "close": 10.5,
                "volume": 1000,
            },
            {
                "time": 1609459260,
                "open": 10.5,
                "high": 11.2,
                "low": 10.2,
                "close": 11.0,
                "volume": 1500,
            },
        ]

        result = parser.convert_to_dataframe(raw_data)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert list(result.columns) == [
            "time",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]

    def test_normalize_symbol(self):
        """测试：标准化股票代码"""
        from src.adapters.tdx_data_parser import TdxDataParser

        parser = TdxDataParser()

        # 测试股票代码标准化
        assert parser.normalize_symbol("000001") == "000001"
        assert parser.normalize_symbol("SH000001") == "000001"
        assert parser.normalize_symbol("SZ000001") == "000001"


class TestTdxKlineDataFetcher:
    """TDX K线数据获取器测试类"""

    def test_get_stock_daily(self):
        """测试：获取股票日线数据"""
        # TODO: 重构前应该失败
        from src.adapters.tdx_kline_fetcher import TdxKlineDataFetcher

        fetcher = TdxKlineDataFetcher()
        symbol = "000001"
        start_date = "2024-01-01"
        end_date = "2024-01-05"

        with patch.object(fetcher, "_fetch_kline_data") as mock_fetch:
            mock_data = pd.DataFrame({"time": [1609459200, 1609459260], "close": [10.5, 11.0]})
            mock_fetch.return_value = mock_data

            result = fetcher.get_stock_daily(symbol, start_date, end_date)

            assert isinstance(result, pd.DataFrame)
            assert not result.empty

    def test_get_index_daily(self):
        """测试：获取指数日线数据"""
        from src.adapters.tdx_kline_fetcher import TdxKlineDataFetcher

        fetcher = TdxKlineDataFetcher()
        index_code = "000001"
        start_date = "2024-01-01"
        end_date = "2024-01-05"

        with patch.object(fetcher, "_fetch_kline_data") as mock_fetch:
            mock_data = pd.DataFrame({"time": [1609459200, 1609459260], "close": [3000.0, 3050.0]})
            mock_fetch.return_value = mock_data

            result = fetcher.get_index_daily(index_code, start_date, end_date)

            assert isinstance(result, pd.DataFrame)
            assert not result.empty

    def test_fetch_kline_batch(self):
        """测试：批量获取K线数据"""
        from src.adapters.tdx_kline_fetcher import TdxKlineDataFetcher

        fetcher = TdxKlineDataFetcher()

        with patch.object(fetcher, "_make_batch_request") as mock_batch:
            mock_batch.return_value = [
                {"time": 1609459200, "close": 10.5},
                {"time": 1609459260, "close": 11.0},
                {"time": 1609459320, "close": 11.2},
            ]

            result = fetcher.fetch_kline_batch("000001", 0, 100)

            assert isinstance(result, list)
            assert len(result) == 3

    def test_kline_data_performance(self):
        """测试：K线数据获取性能基准"""
        from src.adapters.tdx_kline_fetcher import TdxKlineDataFetcher
        import time

        fetcher = TdxKlineDataFetcher()

        with patch.object(fetcher, "_fetch_kline_data") as mock_fetch:
            mock_fetch.return_value = pd.DataFrame({"close": [10.0] * 100})

            # 性能测试：50次调用应在2秒内完成
            start_time = time.time()
            for _ in range(50):
                fetcher.get_stock_daily("000001", "2024-01-01", "2024-01-31")
            end_time = time.time()

            total_time = end_time - start_time
            assert total_time < 2.0, f"Kline data performance failed: {total_time:.2f}s > 2.0s"


class TestTdxRealtimeManager:
    """TDX实时数据管理器测试类"""

    def test_get_real_time_data(self):
        """测试：获取实时数据"""
        # TODO: 重构前应该失败
        from src.adapters.tdx_realtime_manager import TdxRealtimeManager

        manager = TdxRealtimeManager()
        symbol = "000001"

        with patch.object(manager, "_fetch_realtime_quote") as mock_quote:
            mock_quote.return_value = {
                "symbol": symbol,
                "price": 10.5,
                "change": 0.1,
                "volume": 10000,
            }

            result = manager.get_real_time_data(symbol)

            assert isinstance(result, dict)
            assert result["symbol"] == symbol
            assert result["price"] == 10.5

    def test_fetch_realtime_batch(self):
        """测试：批量获取实时数据"""
        from src.adapters.tdx_realtime_manager import TdxRealtimeManager

        manager = TdxRealtimeManager()
        symbols = ["000001", "000002", "000003"]

        with patch.object(manager, "_fetch_realtime_batch_internal") as mock_batch:
            mock_batch.return_value = {
                "000001": {"symbol": "000001", "price": 10.5},
                "000002": {"symbol": "000002", "price": 15.2},
                "000003": {"symbol": "000003", "price": 20.8},
            }

            result = manager.fetch_realtime_batch(symbols)

            assert isinstance(result, list)
            assert len(result) == 3

    def test_subscribe_realtime_updates(self):
        """测试：订阅实时更新"""
        from src.adapters.tdx_realtime_manager import TdxRealtimeManager

        manager = TdxRealtimeManager()
        symbol = "000001"
        callback = Mock()

        with patch.object(manager, "_setup_realtime_subscription") as mock_subscribe:
            mock_subscribe.return_value = "subscription_id_123"

            result = manager.subscribe_realtime_updates(symbol, callback)

            assert result == "subscription_id_123"
            mock_subscribe.assert_called_once()

    def test_realtime_data_performance(self):
        """测试：实时数据获取性能基准"""
        from src.adapters.tdx_realtime_manager import TdxRealtimeManager
        import time

        manager = TdxRealtimeManager()

        with patch.object(manager, "_fetch_realtime_quote") as mock_quote:
            mock_quote.return_value = {"symbol": "000001", "price": 10.5}

            # 性能测试：100次调用应在1秒内完成
            start_time = time.time()
            for _ in range(100):
                manager.get_real_time_data("000001")
            end_time = time.time()

            total_time = end_time - start_time
            assert total_time < 1.0, f"Realtime data performance failed: {total_time:.2f}s > 1.0s"


class TestTdxBasicDataManager:
    """TDX基础数据管理器测试类"""

    def test_get_stock_basic(self):
        """测试：获取股票基础信息"""
        # TODO: 重构前应该失败
        from src.adapters.tdx_basic_data_manager import TdxBasicDataManager

        manager = TdxBasicDataManager()
        symbol = "000001"

        with patch.object(manager, "_fetch_stock_basic_info") as mock_basic:
            mock_basic.return_value = {
                "symbol": symbol,
                "name": "平安银行",
                "industry": "银行",
                "market": "深交所",
            }

            result = manager.get_stock_basic(symbol)

            assert isinstance(result, dict)
            assert result["symbol"] == symbol
            assert result["name"] == "平安银行"

    def test_get_index_components(self):
        """测试：获取指数成分股"""
        from src.adapters.tdx_basic_data_manager import TdxBasicDataManager

        manager = TdxBasicDataManager()
        index_code = "000001"

        with patch.object(manager, "_fetch_index_components") as mock_components:
            mock_components.return_value = [
                "000001",
                "000002",
                "000003",
                "600000",
                "600036",
            ]

            result = manager.get_index_components(index_code)

            assert isinstance(result, list)
            assert len(result) == 5
            assert "000001" in result

    def test_get_market_calendar(self):
        """测试：获取交易日历"""
        from src.adapters.tdx_basic_data_manager import TdxBasicDataManager

        manager = TdxBasicDataManager()
        start_date = "2024-01-01"
        end_date = "2024-01-07"

        with patch.object(manager, "_fetch_trading_calendar") as mock_calendar:
            mock_calendar.return_value = [
                {"date": "2024-01-02", "is_trading": True},
                {"date": "2024-01-03", "is_trading": False},
            ]

            result = manager.get_market_calendar(start_date, end_date)

            assert isinstance(result, list)
            assert len(result) == 2


if __name__ == "__main__":
    # 运行测试以验证当前状态（应该全部失败）
    pytest.main([__file__, "-v", "--tb=short"])
