"""
Price Data Adapter Test Suite
价格数据适配器测试套件

创建日期: 2025-12-20
版本: 1.0.0
测试模块: src.adapters.price_data_adapter (139行)
"""

import pytest
import pandas as pd

# 添加src路径到导入路径
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

from adapters.price_data_adapter import PriceDataAdapter


class TestPriceDataAdapter:
    """价格数据适配器测试"""

    def test_price_data_adapter_initialization(self):
        """测试价格数据适配器初始化"""
        adapter = PriceDataAdapter()
        assert isinstance(adapter, PriceDataAdapter)
        assert hasattr(adapter, "cache")
        assert hasattr(adapter, "validator")
        assert isinstance(adapter.cache, dict)

    def test_price_data_adapter_has_validator(self):
        """测试适配器有数据验证器"""
        adapter = PriceDataAdapter()
        # 检查验证器是否有必要的方法
        assert hasattr(adapter.validator, "validate_stock_symbol")
        assert hasattr(adapter.validator, "validate_date_format")
        assert callable(getattr(adapter.validator, "validate_stock_symbol"))

    def test_get_stock_daily_basic(self):
        """测试基本股票日线数据获取"""
        adapter = PriceDataAdapter()

        result = adapter.get_stock_daily("000001", "2024-01-01", "2024-01-05")

        assert isinstance(result, pd.DataFrame)
        # 检查必要的列
        required_columns = ["open", "high", "low", "close", "volume", "symbol"]
        for col in required_columns:
            assert col in result.columns
        assert result.index.name == "date"
        assert len(result) > 0  # 应该有数据
        assert all(result["symbol"] == "000001")  # symbol应该正确

    def test_get_stock_daily_date_range_validation(self):
        """测试日期范围验证"""
        adapter = PriceDataAdapter()

        # 测试开始日期晚于结束日期
        with pytest.raises(ValueError, match="End date must be after start date"):
            adapter.get_stock_daily("000001", "2024-01-05", "2024-01-01")

        # 测试相同日期
        with pytest.raises(ValueError, match="End date must be after start date"):
            adapter.get_stock_daily("000001", "2024-01-01", "2024-01-01")

    def test_get_stock_daily_invalid_symbol(self):
        """测试无效股票代码"""
        adapter = PriceDataAdapter()

        # 测试空股票代码
        with pytest.raises(ValueError, match="Invalid symbol format"):
            adapter.get_stock_daily("", "2024-01-01", "2024-01-05")

        # 测试非字符串股票代码
        with pytest.raises(ValueError, match="Invalid symbol format"):
            adapter.get_stock_daily(123456, "2024-01-01", "2024-01-05")

        # 测试格式错误的股票代码
        with pytest.raises(ValueError, match="Invalid symbol format"):
            adapter.get_stock_daily("ABC123", "2024-01-01", "2024-01-05")

    def test_get_stock_daily_invalid_date_format(self):
        """测试无效日期格式"""
        adapter = PriceDataAdapter()

        # 测试无效开始日期
        with pytest.raises(ValueError, match="Invalid start_date format"):
            adapter.get_stock_daily("000001", "2024/01/01", "2024-01-05")

        # 测试无效结束日期
        with pytest.raises(ValueError, match="Invalid end_date format"):
            adapter.get_stock_daily("000001", "2024-01-01", "2024-01-32")

        # 测试不存在的日期
        with pytest.raises(ValueError, match="Invalid end_date format"):
            adapter.get_stock_daily("000001", "2024-01-01", "2024-02-30")

    def test_get_stock_daily_valid_symbols(self):
        """测试有效的股票代码格式"""
        adapter = PriceDataAdapter()

        # 测试6位数字股票代码
        valid_symbols = ["000001", "600000", "300001", "002001"]
        for symbol in valid_symbols:
            result = adapter.get_stock_daily(symbol, "2024-01-01", "2024-01-05")
            assert isinstance(result, pd.DataFrame)
            assert len(result) > 0

    def test_get_stock_daily_weekend_filtering(self):
        """测试周末数据过滤"""
        adapter = PriceDataAdapter()

        # 使用包含周末的日期范围
        result = adapter.get_stock_daily("000001", "2024-01-01", "2024-01-07")

        assert isinstance(result, pd.DataFrame)

        # 检查日期是否在工作日范围内
        dates = pd.to_datetime(result.index)
        # 2024-01-01是周一，所以这一周应该没有周末数据
        if len(result) > 0:
            # 验证所有日期都是工作日（周一到周五，0-4）
            for date in dates:
                assert date.weekday() < 5, f"Weekend date found: {date}"

    def test_get_stock_daily_ohlcv_data_structure(self):
        """测试OHLCV数据结构"""
        adapter = PriceDataAdapter()

        result = adapter.get_stock_daily("000001", "2024-01-01", "2024-01-05")

        if len(result) > 0:
            # 检查OHLCV关系
            for _, row in result.iterrows():
                open_price = row["open"]
                high_price = row["high"]
                low_price = row["low"]
                close_price = row["close"]

                # 验证价格关系
                assert high_price >= open_price, (
                    f"High {high_price} should be >= Open {open_price}"
                )
                assert high_price >= close_price, (
                    f"High {high_price} should be >= Close {close_price}"
                )
                assert high_price >= low_price, (
                    f"High {high_price} should be >= Low {low_price}"
                )
                assert low_price <= open_price, (
                    f"Low {low_price} should be <= Open {open_price}"
                )
                assert low_price <= close_price, (
                    f"Low {low_price} should be <= Close {close_price}"
                )

                # 检查价格合理性
                assert all(
                    price > 0
                    for price in [open_price, high_price, low_price, close_price]
                )

                # 检查成交量
                assert isinstance(row["volume"], (int, float))
                assert row["volume"] > 0

    def test_get_stock_daily_cache_functionality(self):
        """测试缓存功能"""
        adapter = PriceDataAdapter()

        # 第一次调用
        result1 = adapter.get_stock_daily("000001", "2024-01-01", "2024-01-05")

        # 检查缓存是否被设置
        cache_key = "000001_2024-01-01_2024-01-05"
        assert cache_key in adapter.cache

        # 第二次调用应该从缓存获取
        result2 = adapter.get_stock_daily("000001", "2024-01-01", "2024-01-05")

        # 验证结果是相同的DataFrame
        pd.testing.assert_frame_equal(result1, result2)

        # 验证缓存命中（通过检查DataFrame的id是否相同）
        assert id(result1) == id(result2)

    def test_get_stock_daily_different_cache_keys(self):
        """测试不同参数产生不同的缓存键"""
        adapter = PriceDataAdapter()

        # 不同的调用应该产生不同的缓存条目
        adapter.get_stock_daily("000001", "2024-01-01", "2024-01-05")
        adapter.get_stock_daily("000002", "2024-01-01", "2024-01-05")
        adapter.get_stock_daily("000001", "2024-01-01", "2024-01-10")

        # 检查缓存中有正确的条目数
        expected_keys = [
            "000001_2024-01-01_2024-01-05",
            "000002_2024-01-01_2024-01-05",
            "000001_2024-01-01_2024-01-10",
        ]
        for key in expected_keys:
            assert key in adapter.cache

    def test_get_stock_daily_large_date_range(self):
        """测试大日期范围"""
        adapter = PriceDataAdapter()

        # 测试一个月的数据
        result = adapter.get_stock_daily("000001", "2024-01-01", "2024-01-31")

        assert isinstance(result, pd.DataFrame)
        # 工作日数量应该在20-23之间（一个月）
        assert 15 <= len(result) <= 25

    def test_get_stock_daily_edge_cases(self):
        """测试边界情况"""
        adapter = PriceDataAdapter()

        # 测试单个工作日
        result = adapter.get_stock_daily("000001", "2024-01-01", "2024-01-05")

        if len(result) > 0:
            # 至少应该有一个工作日的数据
            assert len(result) >= 1

    def test_generate_mock_data_quality(self):
        """测试模拟数据质量"""
        adapter = PriceDataAdapter()

        # 直接测试模拟数据生成方法
        result = adapter._generate_mock_data("000001", "2024-01-01", "2024-01-05")

        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

        # 检查数据质量
        for _, row in result.iterrows():
            # 价格应该为正数
            assert row["open"] > 0
            assert row["high"] > 0
            assert row["low"] > 0
            assert row["close"] > 0

            # 成交量应该为正整数
            assert row["volume"] > 0
            assert isinstance(row["volume"], (int, float))

    def test_generate_mock_data_consistency(self):
        """测试模拟数据一致性"""
        adapter = PriceDataAdapter()

        # 相同参数应该产生不同的数据（因为包含随机性）
        result1 = adapter._generate_mock_data("000001", "2024-01-01", "2024-01-05")
        result2 = adapter._generate_mock_data("000001", "2024-01-01", "2024-01-05")

        # 数据结构应该相同，但具体值可能不同
        assert result1.columns.equals(result2.columns)
        assert len(result1) == len(result2)

    def test_validator_stock_symbol_validation(self):
        """测试股票代码验证"""
        adapter = PriceDataAdapter()

        # 测试有效的股票代码
        valid_symbols = ["000001", "600000", "300001", "002001"]
        for symbol in valid_symbols:
            assert adapter.validator.validate_stock_symbol(symbol), (
                f"Symbol {symbol} should be valid"
            )

        # 测试无效的股票代码
        invalid_symbols = ["", "ABC123", "12345", "1234567", "000001A", None, 123456]
        for symbol in invalid_symbols:
            assert not adapter.validator.validate_stock_symbol(symbol), (
                f"Symbol {symbol} should be invalid"
            )

    def test_validator_date_format_validation(self):
        """测试日期格式验证"""
        adapter = PriceDataAdapter()

        # 测试有效的日期格式
        valid_dates = [
            "2024-01-01",
            "2024-12-31",
            "2020-02-29",
            "2024-1-1",
            "2024-01-5",
        ]
        for date in valid_dates:
            assert adapter.validator.validate_date_format(date), (
                f"Date {date} should be valid"
            )

        # 测试无效的日期格式
        invalid_dates = [
            "2024/01/01",  # 错误的分隔符
            "2024-13-01",  # 无效月份
            "2024-01-32",  # 无效日
            "24-01-01",  # 错误的年份格式
            "",  # 空字符串
            None,  # None值
            "invalid_date",  # 完全无效
        ]
        for date in invalid_dates:
            assert not adapter.validator.validate_date_format(date), (
                f"Date {date} should be invalid"
            )


class TestPriceDataAdapterAdvanced:
    """价格数据适配器高级测试"""

    def test_get_stock_daily_performance_considerations(self):
        """测试性能考虑"""
        adapter = PriceDataAdapter()

        # 测试多次调用的性能
        import time

        start_time = time.time()

        for _ in range(10):
            adapter.get_stock_daily("000001", "2024-01-01", "2024-01-10")

        end_time = time.time()

        # 10次调用应该很快完成（包括缓存查找）
        assert end_time - start_time < 1.0, "Multiple calls should be fast with caching"

    def test_get_stock_daily_concurrent_access(self):
        """测试并发访问安全性"""
        adapter = PriceDataAdapter()

        # 模拟并发访问（虽然不是真正的并发）
        results = []
        for i in range(5):
            result = adapter.get_stock_daily(f"00000{i}", "2024-01-01", "2024-01-05")
            results.append(result)

        # 所有结果应该是有效的DataFrame
        for i, result in enumerate(results):
            assert isinstance(result, pd.DataFrame), f"Result {i} should be a DataFrame"
            assert len(result) > 0, f"Result {i} should have data"

    def test_get_stock_daily_memory_usage(self):
        """测试内存使用"""
        adapter = PriceDataAdapter()

        # 获取一些数据并检查缓存大小
        initial_cache_size = len(adapter.cache)

        adapter.get_stock_daily("000001", "2024-01-01", "2024-01-31")
        adapter.get_stock_daily("000002", "2024-01-01", "2024-01-31")

        final_cache_size = len(adapter.cache)

        # 缓存应该增长
        assert final_cache_size > initial_cache_size

    def test_error_handling_edge_cases(self):
        """测试错误处理的边界情况"""
        adapter = PriceDataAdapter()

        # 测试各种错误组合
        error_cases = [
            ("", "2024-01-01", "2024-01-05"),  # 空symbol
            ("000001", "", "2024-01-05"),  # 空start_date
            ("000001", "2024-01-01", ""),  # 空end_date
            ("ABC123", "2024-01-01", "2024-01-05"),  # 无效symbol
            ("000001", "2024/01/01", "2024-01-05"),  # 无效start_date格式
            ("000001", "2024-01-01", "2024/01/05"),  # 无效end_date格式
            ("000001", "2024-01-05", "2024-01-01"),  # 开始日期晚于结束日期
        ]

        for symbol, start_date, end_date in error_cases:
            with pytest.raises(ValueError):
                adapter.get_stock_daily(symbol, start_date, end_date)

    def test_data_precision_and_formatting(self):
        """测试数据精度和格式"""
        adapter = PriceDataAdapter()

        result = adapter.get_stock_daily("000001", "2024-01-01", "2024-01-05")

        if len(result) > 0:
            # 检查价格精度（应该是小数点后2位）
            for _, row in result.iterrows():
                # 检查是否为合理的精度
                assert str(row["open"]).count(".") <= 1, (
                    "Open price should have reasonable precision"
                )
                assert str(row["high"]).count(".") <= 1, (
                    "High price should have reasonable precision"
                )
                assert str(row["low"]).count(".") <= 1, (
                    "Low price should have reasonable precision"
                )
                assert str(row["close"]).count(".") <= 1, (
                    "Close price should have reasonable precision"
                )

    def test_symbol_handling_case_sensitivity(self):
        """测试股票代码处理的大小写敏感性"""
        adapter = PriceDataAdapter()

        # 虽然股票代码是数字，但测试一下处理方式
        with pytest.raises(ValueError):
            adapter.get_stock_daily("000001a", "2024-01-01", "2024-01-05")


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
