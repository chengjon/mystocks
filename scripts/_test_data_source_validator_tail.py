#!/usr/bin/env python3
"""Support tests extracted from `scripts/tests/test_data_source_validator.py`."""

import sys
import time
from unittest.mock import Mock, patch

import pandas as pd

sys.modules["src.storage.database.connection_manager"] = Mock()
sys.modules["src.data_access"] = Mock()
sys.modules["src.database.database_service"] = Mock()
sys.modules["src.factories.data_source_factory"] = Mock()

from src.utils.data_source_validator import compare_data_structure, validate_data_source_compatibility


class TestPerformanceAndScalability:
    """性能和可扩展性测试类"""

    def test_large_data_structure_comparison(self):
        """测试大型数据结构比较性能"""
        large_dict1 = {}
        large_dict2 = {}

        for i in range(1000):
            large_dict1[f"item_{i}"] = {
                "data": list(range(100)),
                "metadata": {
                    "id": i,
                    "name": f"item_{i}",
                    "tags": [f"tag_{j}" for j in range(10)],
                },
            }
            large_dict2[f"item_{i}"] = {
                "data": list(range(100)),
                "metadata": {
                    "id": i,
                    "name": f"item_{i}",
                    "tags": [f"tag_{j}" for j in range(10)],
                },
            }

        start_time = time.time()
        errors = compare_data_structure(large_dict1, large_dict2)
        elapsed = time.time() - start_time

        assert errors == []
        assert elapsed < 2.0

    def test_large_dataframe_comparison(self):
        """测试大型DataFrame比较性能"""
        large_df1 = pd.DataFrame(
            {
                "col1": range(10000),
                "col2": [f"value_{i}" for i in range(10000)],
                "col3": [i % 100 for i in range(10000)],
            }
        )
        large_df2 = pd.DataFrame(
            {
                "col1": range(10000),
                "col2": [f"value_{i}" for i in range(10000)],
                "col3": [i % 100 for i in range(10000)],
            }
        )

        start_time = time.time()
        errors = compare_data_structure(large_df1, large_df2)
        elapsed = time.time() - start_time

        assert errors == []
        assert elapsed < 1.0

    def test_deep_nested_structure_performance(self):
        """测试深层嵌套结构性能"""

        def create_nested_structure(depth, value):
            if depth == 0:
                return {"final": value}
            return {"level": create_nested_structure(depth - 1, value)}

        nested1 = create_nested_structure(10, "test1")
        nested2 = create_nested_structure(10, "test2")

        start_time = time.time()
        errors = compare_data_structure(nested1, nested2)
        elapsed = time.time() - start_time

        assert errors == []
        assert elapsed < 0.1

    def test_concurrent_compatibility_validation(self):
        """测试并发兼容性验证 - 专注于性能测试"""
        import concurrent.futures

        def create_simple_mock_source():
            mock_source = Mock()
            simple_return = "test_data"
            all_methods = [
                "get_stock_detail",
                "get_real_time_quote",
                "get_all_indicators",
                "get_trend_indicators",
                "get_momentum_indicators",
                "get_volatility_indicators",
                "get_trading_signals",
                "get_kline_data",
                "get_pattern_recognition",
                "get_monitoring_summary",
                "get_monitoring_status",
                "get_stock_list",
                "get_realtime_alerts",
            ]
            for method_name in all_methods:
                getattr(mock_source, method_name).return_value = simple_return
            return mock_source

        source_pairs = [(create_simple_mock_source(), create_simple_mock_source()) for _ in range(3)]

        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(validate_data_source_compatibility, mock_source, real_source)
                for mock_source, real_source in source_pairs
            ]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]

        elapsed = time.time() - start_time

        assert len(results) == 3
        assert elapsed < 5.0

        for result in results:
            assert "overall_status" in result
            assert "details" in result
            assert "errors" in result
            assert isinstance(result["details"], dict)
            assert isinstance(result["errors"], list)


class TestIntegrationScenarios:
    """集成场景测试类"""

    @patch("src.utils.data_source_validator.MockDataSource")
    @patch("src.utils.data_source_validator.RealDataSource")
    def test_real_world_compatibility_check(self, mock_real_class, mock_mock_class):
        """测试真实世界兼容性检查场景"""
        mock_source = Mock()
        real_source = Mock()

        stock_detail = {
            "symbol": "600519",
            "name": "贵州茅台",
            "price": 1689.50,
            "change": 15.30,
            "change_pct": 0.91,
            "volume": 1200000,
            "market_cap": "2.1万亿",
        }
        real_time_quote = {
            "symbol": "600519",
            "current_price": 1689.50,
            "open_price": 1674.20,
            "high_price": 1692.00,
            "low_price": 1668.00,
            "volume": 1200000,
            "timestamp": "2025-01-22 10:30:00",
        }
        indicators = {
            "ma5": 1685.20,
            "ma10": 1678.90,
            "ma20": 1665.40,
            "rsi": 65.2,
            "macd": {"dif": 12.3, "dea": 8.7, "histogram": 3.6},
        }

        mock_source.get_stock_detail.return_value = stock_detail
        real_source.get_stock_detail.return_value = stock_detail
        mock_source.get_real_time_quote.return_value = real_time_quote
        real_source.get_real_time_quote.return_value = real_time_quote
        mock_source.get_all_indicators.return_value = indicators
        real_source.get_all_indicators.return_value = indicators

        simple_return = {"status": "ok", "data": []}
        method_names = [
            "get_trend_indicators",
            "get_momentum_indicators",
            "get_volatility_indicators",
            "get_volume_indicators",
            "get_trading_signals",
            "get_kline_data",
            "get_pattern_recognition",
            "get_monitoring_summary",
            "get_monitoring_status",
        ]
        for method_name in method_names:
            getattr(mock_source, method_name).return_value = simple_return
            getattr(real_source, method_name).return_value = simple_return

        stock_list = {
            "stocks": [
                {"symbol": "600519", "name": "贵州茅台"},
                {"symbol": "000001", "name": "平安银行"},
            ],
            "total": 2,
        }
        mock_source.get_stock_list.return_value = stock_list
        real_source.get_stock_list.return_value = stock_list

        alerts = {"alerts": [], "count": 0}
        mock_source.get_realtime_alerts.return_value = alerts
        real_source.get_realtime_alerts.return_value = alerts

        result = validate_data_source_compatibility(mock_source, real_source, "600519")

        assert result["overall_status"] == "success"
        assert len(result["errors"]) == 0
        assert len(result["details"]) == 13
        for detail in result["details"].values():
            assert detail["status"] == "success"

    def test_mixed_data_types_validation(self):
        """测试混合数据类型验证"""
        mock_source = Mock()
        real_source = Mock()

        mixed_returns = [
            (pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]}), "DataFrame测试"),
            ({"key1": "value1", "key2": [1, 2, 3]}, "字典测试"),
            ([{"item": 1}, {"item": 2}], "列表测试"),
            ("simple_string", "字符串测试"),
            (12345, "数字测试"),
        ]
        method_names = [
            "get_stock_detail",
            "get_real_time_quote",
            "get_all_indicators",
            "get_trend_indicators",
            "get_momentum_indicators",
            "get_volatility_indicators",
        ]

        for index, (return_value, _description) in enumerate(mixed_returns):
            method_name = method_names[index]
            getattr(mock_source, method_name).return_value = return_value
            getattr(real_source, method_name).return_value = return_value

        getattr(mock_source, "get_stock_list").return_value = {"result": "ok"}
        getattr(real_source, "get_stock_list").return_value = {"result": "ok"}
        getattr(mock_source, "get_realtime_alerts").return_value = {"result": "ok"}
        getattr(real_source, "get_realtime_alerts").return_value = {"result": "ok"}

        remaining_methods = [
            "get_trading_signals",
            "get_kline_data",
            "get_pattern_recognition",
            "get_monitoring_summary",
            "get_monitoring_status",
        ]
        for method_name in remaining_methods:
            getattr(mock_source, method_name).return_value = {"status": "ok"}
            getattr(real_source, method_name).return_value = {"status": "ok"}

        result = validate_data_source_compatibility(mock_source, real_source)

        assert len(result["errors"]) <= 2
        if result["errors"]:
            for error in result["errors"]:
                assert any(keyword in error for keyword in ["类型不一致", "缺少字段", "Mock"])
