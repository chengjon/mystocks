#!/usr/bin/env python3
"""Support tests extracted from `scripts/tests/test_price_data_adapter.py`."""

from datetime import datetime, timedelta

import pandas as pd
import pytest

from src.adapters.price_data_adapter import PriceDataAdapter


class TestPerformance:
    """性能测试类"""

    def test_adapter_initialization_performance(self):
        """测试适配器初始化性能"""
        iterations = 100

        import time

        start_time = time.time()
        for _ in range(iterations):
            PriceDataAdapter()
        end_time = time.time()

        avg_time = (end_time - start_time) / iterations * 1000
        assert avg_time < 10, f"适配器初始化平均耗时 {avg_time:.2f} 毫秒，超过预期"

    def test_data_retrieval_performance(self):
        """测试数据检索性能"""
        adapter = PriceDataAdapter()
        adapter.get_stock_daily("000001", "2024-01-01", "2024-01-05")

        iterations = 50

        import time

        start_time = time.time()
        for _ in range(iterations):
            adapter.get_stock_daily("000002", "2024-01-01", "2024-01-05")
        end_time = time.time()

        avg_time = (end_time - start_time) / iterations * 1000
        assert avg_time < 50, f"数据检索平均耗时 {avg_time:.2f} 毫秒，超过预期"

    def test_cache_performance_improvement(self):
        """测试缓存性能提升"""
        adapter = PriceDataAdapter()
        symbol = "000001"
        start_date = "2024-01-01"
        end_date = "2024-01-31"

        import time

        start_time = time.time()
        result1 = adapter.get_stock_daily(symbol, start_date, end_date)
        first_call_time = time.time() - start_time

        start_time = time.time()
        result2 = adapter.get_stock_daily(symbol, start_date, end_date)
        second_call_time = time.time() - start_time

        if first_call_time > 0.001:
            improvement_ratio = first_call_time / second_call_time if second_call_time > 0 else float("inf")
            assert improvement_ratio > 5, f"缓存性能提升不足: {improvement_ratio:.1f}倍"

        assert id(result1) == id(result2)

    def test_large_dataset_performance(self):
        """测试大数据集性能"""
        adapter = PriceDataAdapter()

        import time

        start_time = time.time()
        result = adapter.get_stock_daily("000001", "2024-01-01", "2024-12-31")
        end_time = time.time()

        processing_time = end_time - start_time
        assert processing_time < 1.0, f"大数据集处理耗时 {processing_time:.2f} 秒，超过预期"

        if not result.empty:
            assert len(result) <= 262

    def test_multiple_concurrent_requests(self):
        """测试多个并发请求"""
        adapter = PriceDataAdapter()
        symbols = ["000001", "000002", "000003", "000004", "000005"]

        import time

        start_time = time.time()
        results = [adapter.get_stock_daily(symbol, "2024-01-01", "2024-01-05") for symbol in symbols]
        total_time = time.time() - start_time

        avg_time = total_time / len(symbols) * 1000
        assert avg_time < 20, f"并发请求平均耗时 {avg_time:.2f} 毫秒，超过预期"
        assert len(adapter.cache) == len(symbols)
        assert len(results) == len(symbols)


class TestIntegration:
    """集成测试类"""

    def test_end_to_end_workflow(self):
        """测试端到端工作流程"""
        adapter = PriceDataAdapter()
        symbols = ["000001", "000002"]
        results = {symbol: adapter.get_stock_daily(symbol, "2024-01-01", "2024-01-05") for symbol in symbols}

        for symbol, result in results.items():
            assert isinstance(result, pd.DataFrame)
            assert all(result["symbol"] == symbol)
            assert not result.isnull().any().any()

    def test_integration_with_date_validation(self):
        """测试与日期验证的集成"""
        adapter = PriceDataAdapter()
        valid_date_ranges = [
            ("000001", "2024-01-01", "2024-01-05"),
            ("000002", "2024-03-01", "2024-03-08"),
            ("000003", "2024-12-01", "2024-12-06"),
        ]

        for symbol, start_date, end_date in valid_date_ranges:
            result = adapter.get_stock_daily(symbol, start_date, end_date)
            assert isinstance(result, pd.DataFrame)

    def test_integration_with_symbol_validation(self):
        """测试与股票代码验证的集成"""
        adapter = PriceDataAdapter()
        valid_symbols = ["000001", "123456", "999999"]

        for symbol in valid_symbols:
            result = adapter.get_stock_daily(symbol, "2024-01-01", "2024-01-05")
            assert isinstance(result, pd.DataFrame)
            assert all(result["symbol"] == symbol)

    def test_data_consistency_across_calls(self):
        """测试多次调用的数据一致性"""
        adapter = PriceDataAdapter()
        results = []

        for _ in range(5):
            adapter.cache.clear()
            result = adapter.get_stock_daily("000001", "2024-01-01", "2024-01-05")
            results.append(result)

        for index in range(1, len(results)):
            assert results[index].equals(results[0])
            assert list(results[index].columns) == list(results[0].columns)
            assert results[index].index.equals(results[0].index)

    def test_realistic_trading_scenario(self):
        """测试真实交易场景"""
        adapter = PriceDataAdapter()
        popular_stocks = ["000001", "000002", "600000", "600036"]
        stock_data = {}

        for symbol in popular_stocks:
            try:
                stock_data[symbol] = adapter.get_stock_daily(symbol, "2024-01-01", "2024-01-07")
            except ValueError:
                continue

        assert len(stock_data) > 0, "至少应该有一个股票的数据获取成功"

        for symbol, data in stock_data.items():
            assert not data.empty, f"股票 {symbol} 应该有数据"
            assert all(data["symbol"] == symbol), f"股票 {symbol} 的symbol列应该一致"

    def test_error_handling_integration(self):
        """测试错误处理集成"""
        adapter = PriceDataAdapter()
        error_cases = [
            ("invalid_symbol", "000001", "2024-01-01", "2024-01-05"),
            ("invalid_start", "000001", "invalid-date", "2024-01-05"),
            ("invalid_end", "000001", "2024-01-01", "invalid-date"),
            ("invalid_range", "000001", "2024-01-05", "2024-01-01"),
        ]

        for _, symbol, start_date, end_date in error_cases:
            with pytest.raises(ValueError):
                adapter.get_stock_daily(symbol, start_date, end_date)

    def test_cache_state_isolation(self):
        """测试缓存状态隔离"""
        adapter1 = PriceDataAdapter()
        adapter2 = PriceDataAdapter()

        result1 = adapter1.get_stock_daily("000001", "2024-01-01", "2024-01-05")
        result2 = adapter2.get_stock_daily("000001", "2024-01-01", "2024-01-05")

        assert len(adapter1.cache) == 1
        assert len(adapter2.cache) == 1
        assert id(result1) != id(result2)


class TestDataQuality:
    """数据质量测试类"""

    def test_data_completeness(self):
        """测试数据完整性"""
        adapter = PriceDataAdapter()
        result = adapter.get_stock_daily("000001", "2024-01-01", "2024-01-10")

        if not result.empty:
            assert not result.isnull().any().any()
            required_columns = ["open", "high", "low", "close", "volume", "symbol"]
            assert all(column in result.columns for column in required_columns)

    def test_data_format_standards(self):
        """测试数据格式标准"""
        adapter = PriceDataAdapter()
        result = adapter.get_stock_daily("000001", "2024-01-01", "2024-01-05")

        if not result.empty:
            assert isinstance(result.index, pd.DatetimeIndex)
            for column in ["open", "high", "low", "close"]:
                sample_values = result[column].dropna().head()
                for value in sample_values:
                    if isinstance(value, (int, float)):
                        decimal_part = str(value).split(".")[-1] if "." in str(value) else "0"
                        assert len(decimal_part) <= 2

    def test_business_logic_validation(self):
        """测试业务逻辑验证"""
        adapter = PriceDataAdapter()
        result = adapter.get_stock_daily("000001", "2024-01-01", "2024-01-05")

        if not result.empty:
            for idx in result.index:
                row = result.loc[idx]
                assert row["high"] >= row["low"], f"日期 {idx}: High ({row['high']}) < Low ({row['low']})"
                assert row["high"] >= row["open"], f"日期 {idx}: High ({row['high']}) < Open ({row['open']})"
                assert row["high"] >= row["close"], f"日期 {idx}: High ({row['high']}) < Close ({row['close']})"
                assert row["low"] <= row["open"], f"日期 {idx}: Low ({row['low']}) > Open ({row['open']})"
                assert row["low"] <= row["close"], f"日期 {idx}: Low ({row['low']}) > Close ({row['close']})"

    def test_weekday_data_availability(self):
        """测试工作日数据可用性"""
        adapter = PriceDataAdapter()
        start_date = "2024-01-01"
        end_date = "2024-01-05"
        result = adapter.get_stock_daily("000001", start_date, end_date)

        expected_weekdays = []
        current_date = datetime.strptime(start_date, "%Y-%m-%d")
        while current_date <= datetime.strptime(end_date, "%Y-%m-%d"):
            if current_date.weekday() < 5:
                expected_weekdays.append(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)

        if expected_weekdays:
            actual_dates = set(result.index) if not result.empty else set()
            expected_dates = set(expected_weekdays)
            intersection = actual_dates.intersection(expected_dates)
            coverage_ratio = len(intersection) / len(expected_dates)
            assert coverage_ratio >= 0.8, f"工作日数据覆盖率 {coverage_ratio:.2f} 过低"

    def test_price_volatility_reasonableness(self):
        """测试价格波动合理性"""
        adapter = PriceDataAdapter()
        result = adapter.get_stock_daily("000001", "2024-01-01", "2024-01-31")

        if len(result) > 1:
            daily_returns = result["close"].pct_change().dropna()
            assert daily_returns.min() >= -0.2, f"最小日收益率 {daily_returns.min():.2f} 过低"
            assert daily_returns.max() <= 0.2, f"最大日收益率 {daily_returns.max():.2f} 过高"

            std_return = daily_returns.std()
            assert std_return <= 0.1, f"收益率标准差 {std_return:.2f} 过高，可能存在异常值"

    def test_volume_price_relationship(self):
        """测试成交量价格关系"""
        adapter = PriceDataAdapter()
        result = adapter.get_stock_daily("000001", "2024-01-01", "2024-01-10")

        if not result.empty:
            avg_price = result["close"].mean()
            avg_volume = result["volume"].mean()
            assert 10 <= avg_price <= 100, f"平均价格 {avg_price:.2f} 不在合理范围内"
            assert 1000 <= avg_volume <= 100000, f"平均成交量 {avg_volume:.2f} 不在合理范围内"
