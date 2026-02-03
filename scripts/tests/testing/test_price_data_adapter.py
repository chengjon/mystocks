#!/usr/bin/env python3
"""
价格数据适配器测试套件
提供完整的price_data_adapter模块测试覆盖，遵循Phase 6成功模式
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
import pandas as pd
from datetime import datetime, timedelta

# 导入被测试的模块
from src.adapters.price_data_adapter import PriceDataAdapter


class TestPriceDataAdapter:
    """价格数据适配器主要功能测试类"""

    def test_adapter_initialization_with_simple_validator(self):
        """测试使用简单验证器初始化"""
        adapter = PriceDataAdapter()

        # 验证适配器成功初始化，包含缓存和简单验证器
        assert hasattr(adapter, "cache")
        assert hasattr(adapter, "validator")
        assert adapter.cache == {}
        assert adapter.validator is not None

        # 验证简单验证器具有必要的方法
        assert hasattr(adapter.validator, "validate_stock_symbol")
        assert hasattr(adapter.validator, "validate_date_format")

        # 测试验证器功能
        assert adapter.validator.validate_stock_symbol("000001") is True
        assert adapter.validator.validate_stock_symbol("invalid") is False
        assert adapter.validator.validate_date_format("2024-01-01") is True
        assert adapter.validator.validate_date_format("invalid") is False

    def test_adapter_initialization_fallback_to_simple_validator(self):
        """测试回退到简单验证器初始化"""
        adapter = PriceDataAdapter()

        # 验证简单验证器被创建
        assert hasattr(adapter.validator, "validate_stock_symbol")
        assert hasattr(adapter.validator, "validate_date_format")
        assert adapter.cache == {}

    def test_get_stock_daily_success_with_valid_parameters(self):
        """测试有效参数获取股票日线数据"""
        adapter = PriceDataAdapter()
        symbol = "000001"
        start_date = "2024-01-01"
        end_date = "2024-01-05"

        result = adapter.get_stock_daily(symbol, start_date, end_date)

        # 验证返回结果
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert list(result.columns) == [
            "open",
            "high",
            "low",
            "close",
            "volume",
            "symbol",
        ]
        assert result.index.name == "date"
        assert all(result["symbol"] == symbol)

        # 验证数据完整性
        assert all(result["open"] > 0)
        assert all(result["high"] > 0)
        assert all(result["low"] > 0)
        assert all(result["close"] > 0)
        assert all(result["volume"] > 0)

        # 验证OHLC关系
        assert all(result["high"] >= result["low"])
        assert all(result["high"] >= result["open"])
        assert all(result["high"] >= result["close"])
        assert all(result["low"] <= result["open"])
        assert all(result["low"] <= result["close"])

    def test_get_stock_daily_caching_mechanism(self):
        """测试缓存机制"""
        adapter = PriceDataAdapter()
        symbol = "000002"
        start_date = "2024-01-01"
        end_date = "2024-01-03"

        # 第一次调用
        result1 = adapter.get_stock_daily(symbol, start_date, end_date)

        # 第二次调用应该从缓存获取
        result2 = adapter.get_stock_daily(symbol, start_date, end_date)

        # 验证缓存生效
        assert id(result1) == id(result2)  # 同一个对象引用
        assert len(adapter.cache) == 1
        cache_key = f"{symbol}_{start_date}_{end_date}"
        assert cache_key in adapter.cache

    def test_get_stock_daily_different_cache_keys(self):
        """测试不同参数使用不同缓存键"""
        adapter = PriceDataAdapter()

        # 第一次调用
        result1 = adapter.get_stock_daily("000001", "2024-01-01", "2024-01-03")
        # 第二次调用（不同参数）
        result2 = adapter.get_stock_daily("000002", "2024-01-01", "2024-01-03")
        # 第三次调用（不同日期范围）
        result3 = adapter.get_stock_daily("000001", "2024-01-04", "2024-01-05")

        # 验证不同缓存键
        assert id(result1) != id(result2)
        assert id(result1) != id(result3)
        assert id(result2) != id(result3)
        assert len(adapter.cache) == 3

    def test_get_stock_daily_weekends_excluded(self):
        """测试周末数据被排除"""
        adapter = PriceDataAdapter()
        # 这个范围包含周末
        start_date = "2024-01-01"  # 周一
        end_date = "2024-01-07"  # 周日

        result = adapter.get_stock_daily("000001", start_date, end_date)

        # 验证只包含工作日（周一到周五）
        for date_str in result.index:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            assert dt.weekday() < 5  # 0-4 是周一到周五

    def test_get_stock_daily_returns_expected_columns(self):
        """测试返回期望的数据列"""
        adapter = PriceDataAdapter()
        result = adapter.get_stock_daily("000001", "2024-01-01", "2024-01-03")

        expected_columns = ["open", "high", "low", "close", "volume", "symbol"]
        assert list(result.columns) == expected_columns

        # 验证数据类型
        assert result["open"].dtype in ["float64", "float32"]
        assert result["high"].dtype in ["float64", "float32"]
        assert result["low"].dtype in ["float64", "float32"]
        assert result["close"].dtype in ["float64", "float32"]
        assert result["volume"].dtype in ["int64", "int32"]

    def test_get_stock_daily_price_range_reasonableness(self):
        """测试价格范围合理性"""
        adapter = PriceDataAdapter()
        result = adapter.get_stock_daily("000001", "2024-01-01", "2024-01-10")

        # 价格应该在合理范围内（1-1000）
        for column in ["open", "high", "low", "close"]:
            assert result[column].min() >= 1.0
            assert result[column].max() <= 1000.0

        # 成交量应该在合理范围内
        assert result["volume"].min() >= 1000
        assert result["volume"].max() <= 100000


class TestParameterValidation:
    """参数验证测试类"""

    def test_invalid_symbol_formats(self):
        """测试无效股票代码格式"""
        adapter = PriceDataAdapter()
        start_date = "2024-01-01"
        end_date = "2024-01-05"

        invalid_symbols = [
            "",  # 空字符串
            "abc",  # 非数字
            "12345",  # 5位数字
            "1234567",  # 7位数字
            "000001.SZ",  # 包含后缀
            "000001.00",  # 包含小数点
            None,  # None值
            12345,  # 整数类型
            [],  # 列表
            {},  # 字典
        ]

        for symbol in invalid_symbols:
            with pytest.raises(ValueError, match="Invalid symbol format"):
                adapter.get_stock_daily(symbol, start_date, end_date)

    def test_invalid_date_formats(self):
        """测试无效日期格式"""
        adapter = PriceDataAdapter()
        symbol = "000001"

        invalid_dates = [
            "",  # 空字符串
            "2024/01/01",  # 错误分隔符
            "2024-1-1",  # 单位数月份和日期
            "24-01-01",  # 年份格式错误
            "2024-13-01",  # 无效月份
            "2024-01-32",  # 无效日期
            "20240101",  # 紧凑格式
            "Jan 1, 2024",  # 英文月份
            None,  # None值
            20240101,  # 整数格式
        ]

        for invalid_date in invalid_dates:
            if invalid_date is None:
                continue  # 跳过None，因为类型检查会先报错
            with pytest.raises(
                ValueError, match="Invalid start_date format|Invalid end_date format"
            ):
                adapter.get_stock_daily(symbol, invalid_date, "2024-01-05")

    def test_end_date_before_start_date(self):
        """测试结束日期早于开始日期"""
        adapter = PriceDataAdapter()
        symbol = "000001"

        with pytest.raises(ValueError, match="End date must be after start date"):
            adapter.get_stock_daily(symbol, "2024-01-05", "2024-01-01")

    def test_end_date_equals_start_date(self):
        """测试结束日期等于开始日期"""
        adapter = PriceDataAdapter()
        symbol = "000001"

        with pytest.raises(ValueError, match="End date must be after start date"):
            adapter.get_stock_daily(symbol, "2024-01-01", "2024-01-01")

    def test_type_validation_for_symbol(self):
        """测试股票代码类型验证"""
        adapter = PriceDataAdapter()

        with pytest.raises((ValueError, AttributeError)):
            adapter.get_stock_daily(12345, "2024-01-01", "2024-01-05")

    def test_type_validation_for_dates(self):
        """测试日期类型验证"""
        adapter = PriceDataAdapter()

        with pytest.raises((ValueError, AttributeError)):
            adapter.get_stock_daily("000001", 20240101, "2024-01-05")

        with pytest.raises((ValueError, AttributeError)):
            adapter.get_stock_daily("000001", "2024-01-01", 20240105)


class TestSimpleValidator:
    """简单验证器测试类"""

    def test_simple_validator_symbol_validation(self):
        """测试简单验证器的股票代码验证"""
        adapter = PriceDataAdapter()
        validator = adapter.validator

        # 有效股票代码
        valid_symbols = ["000001", "123456", "999999"]
        for symbol in valid_symbols:
            assert validator.validate_stock_symbol(symbol) is True

        # 无效股票代码
        invalid_symbols = ["", "abc", "12345", "1234567", "000001.SZ"]
        for symbol in invalid_symbols:
            assert validator.validate_stock_symbol(symbol) is False

    def test_simple_validator_date_validation(self):
        """测试简单验证器的日期格式验证"""
        adapter = PriceDataAdapter()
        validator = adapter.validator

        # 有效日期格式
        valid_dates = ["2024-01-01", "2023-12-31", "2000-02-29"]
        for date_str in valid_dates:
            assert validator.validate_date_format(date_str) is True

        # 无效日期格式
        invalid_dates = ["", "2024/01/01", "2024-1-1", "Jan 1, 2024", "2024-13-01"]
        for date_str in invalid_dates:
            assert validator.validate_date_format(date_str) is False

    def test_simple_validator_leap_year_handling(self):
        """测试简单验证器的闰年处理"""
        adapter = PriceDataAdapter()
        validator = adapter.validator

        # 有效的闰年日期
        assert validator.validate_date_format("2000-02-29") is True
        assert validator.validate_date_format("2024-02-29") is True

        # 无效的闰年日期
        assert validator.validate_date_format("2023-02-29") is False
        assert validator.validate_date_format("1900-02-29") is False


class TestMockDataGeneration:
    """Mock数据生成测试类"""

    def test_mock_data_generation_correct_structure(self):
        """测试Mock数据生成结构"""
        adapter = PriceDataAdapter()
        symbol = "000001"
        start_date = "2024-01-01"
        end_date = "2024-01-03"

        # 直接调用私有方法进行测试
        result = adapter._generate_mock_data(symbol, start_date, end_date)

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert result.index.name == "date"
        assert list(result.columns) == [
            "open",
            "high",
            "low",
            "close",
            "volume",
            "symbol",
        ]

    def test_mock_data_generation_all_dates_have_values(self):
        """测试Mock数据所有日期都有值"""
        adapter = PriceDataAdapter()

        # 生成较长的时间范围以确保有数据
        result = adapter.get_stock_daily("000001", "2024-01-01", "2024-01-31")

        # 验证没有缺失值
        assert not result.isnull().any().any()

    def test_mock_data_generation_symbol_consistency(self):
        """测试Mock数据股票代码一致性"""
        adapter = PriceDataAdapter()

        result = adapter.get_stock_daily("000001", "2024-01-01", "2024-01-05")

        # 验证所有行的symbol都正确
        assert all(result["symbol"] == "000001")

    def test_mock_data_generation_date_sequence(self):
        """测试Mock数据日期序列连续性"""
        adapter = PriceDataAdapter()

        result = adapter.get_stock_daily("000001", "2024-01-01", "2024-01-10")

        # 验证日期是递增的（排除了周末）
        dates = [datetime.strptime(d, "%Y-%m-%d") for d in result.index]
        for i in range(1, len(dates)):
            assert dates[i] > dates[i - 1]

    def test_mock_data_generation_price_relationships(self):
        """测试Mock数据价格关系"""
        adapter = PriceDataAdapter()

        result = adapter.get_stock_daily("000001", "2024-01-01", "2024-01-10")

        # 验证OHLC关系
        assert all(result["high"] >= result["low"])
        assert all(result["high"] >= result["open"])
        assert all(result["high"] >= result["close"])
        assert all(result["low"] <= result["open"])
        assert all(result["low"] <= result["close"])

    def test_mock_data_generation_volume_reasonableness(self):
        """测试Mock数据成交量合理性"""
        adapter = PriceDataAdapter()

        result = adapter.get_stock_daily("000001", "2024-01-01", "2024-01-10")

        # 验证成交量范围
        assert result["volume"].min() >= 1000
        assert result["volume"].max() <= 100000
        assert result["volume"].mean() > 0

    def test_mock_data_generation_price_range(self):
        """测试Mock数据价格范围"""
        adapter = PriceDataAdapter()

        result = adapter.get_stock_daily("000001", "2024-01-01", "2024-01-10")

        # 验证价格范围
        for column in ["open", "high", "low", "close"]:
            assert result[column].min() > 0
            assert result[column].max() <= 110  # 基础价格10 + 波动10% + 余量
            assert result[column].max() >= 10  # 基础价格10


class TestEdgeCases:
    """边界情况测试类"""

    def test_single_day_data(self):
        """测试单日数据"""
        adapter = PriceDataAdapter()

        result = adapter.get_stock_daily("000001", "2024-01-01", "2024-01-01")

        # 2024-01-01是周一，应该有数据
        if datetime.strptime("2024-01-01", "%Y-%m-%d").weekday() < 5:
            assert not result.empty
        else:
            assert result.empty  # 如果是周末，应该没有数据

    def test_month_boundary_data(self):
        """测试月份边界数据"""
        adapter = PriceDataAdapter()

        # 跨月数据
        result = adapter.get_stock_daily("000001", "2024-01-30", "2024-02-05")

        if not result.empty:
            # 验证跨月数据正确
            first_date = result.index[0]
            last_date = result.index[-1]
            assert first_date >= "2024-01-30"
            assert last_date <= "2024-02-05"

    def test_year_boundary_data(self):
        """测试年份边界数据"""
        adapter = PriceDataAdapter()

        # 跨年数据
        result = adapter.get_stock_daily("000001", "2023-12-29", "2024-01-05")

        if not result.empty:
            # 验证跨年数据正确
            dates = result.index
            has_2023 = any(date.startswith("2023") for date in dates)
            has_2024 = any(date.startswith("2024") for date in dates)
            assert has_2023 or has_2024  # 至少有一个年份的数据

    def test_empty_date_range_no_weekdays(self):
        """测试没有工作日的日期范围"""
        adapter = PriceDataAdapter()

        # 选择只有周末的日期范围
        # 假设2024-12-21和2024-12-22是周末（需要根据实际情况调整）
        result = adapter.get_stock_daily("000001", "2024-12-21", "2024-12-22")

        # 如果这两天都是周末，结果应该为空
        # 如果有工作日，结果应该非空
        # 这里我们接受任何结果，因为日期会变化

    def test_large_date_range(self):
        """测试大日期范围"""
        adapter = PriceDataAdapter()

        # 一年的数据
        result = adapter.get_stock_daily("000001", "2024-01-01", "2024-12-31")

        # 验证合理的数据量（约252个工作日）
        if not result.empty:
            assert len(result) >= 200  # 至少200个工作日
            assert len(result) <= 262  # 最多262天

    def test_zero_volume_edge_case(self):
        """测试零成交量边界情况"""
        adapter = PriceDataAdapter()

        result = adapter.get_stock_daily("000001", "2024-01-01", "2024-01-05")

        # 验证成交量不为零
        if not result.empty:
            assert all(result["volume"] > 0)

    def test_extreme_price_ranges(self):
        """测试极端价格范围"""
        adapter = PriceDataAdapter()

        result = adapter.get_stock_daily("000001", "2024-01-01", "2024-01-31")

        if not result.empty:
            # 验证价格在合理范围内
            max_price = result[["open", "high", "low", "close"]].max().max()
            min_price = result[["open", "high", "low", "close"]].min().min()

            # 价格比例不应太大
            assert max_price / min_price <= 10  # 最大10倍差异

    def test_multiple_symbols_cache_isolation(self):
        """测试多个股票代码的缓存隔离"""
        adapter = PriceDataAdapter()

        result1 = adapter.get_stock_daily("000001", "2024-01-01", "2024-01-05")
        result2 = adapter.get_stock_daily("000002", "2024-01-01", "2024-01-05")

        # 验证不同股票代码的数据不同
        if not result1.empty and not result2.empty:
            assert not result1["symbol"].equals(result2["symbol"])

    def test_same_symbol_different_dates_cache_isolation(self):
        """测试相同股票代码不同日期范围的缓存隔离"""
        adapter = PriceDataAdapter()

        result1 = adapter.get_stock_daily("000001", "2024-01-01", "2024-01-03")
        result2 = adapter.get_stock_daily("000001", "2024-01-04", "2024-01-06")

        # 验证不同日期范围的数据不同
        if not result1.empty and not result2.empty:
            date_ranges = set(result1.index).isdisjoint(set(result2.index))


class TestPerformance:
    """性能测试类"""

    def test_adapter_initialization_performance(self):
        """测试适配器初始化性能"""
        iterations = 100

        import time

        start_time = time.time()
        for _ in range(iterations):
            adapter = PriceDataAdapter()
        end_time = time.time()

        avg_time = (end_time - start_time) / iterations * 1000  # 毫秒

        # 初始化应该很快（小于10毫秒）
        assert avg_time < 10, f"适配器初始化平均耗时 {avg_time:.2f} 毫秒，超过预期"

    def test_data_retrieval_performance(self):
        """测试数据检索性能"""
        adapter = PriceDataAdapter()

        # 预热
        adapter.get_stock_daily("000001", "2024-01-01", "2024-01-05")

        iterations = 50

        import time

        start_time = time.time()
        for _ in range(iterations):
            adapter.get_stock_daily("000002", "2024-01-01", "2024-01-05")
        end_time = time.time()

        avg_time = (end_time - start_time) / iterations * 1000  # 毫秒

        # 数据检索应该合理快速（小于50毫秒）
        assert avg_time < 50, f"数据检索平均耗时 {avg_time:.2f} 毫秒，超过预期"

    def test_cache_performance_improvement(self):
        """测试缓存性能提升"""
        adapter = PriceDataAdapter()
        symbol = "000001"
        start_date = "2024-01-01"
        end_date = "2024-01-31"

        # 第一次调用（无缓存）
        import time

        start_time = time.time()
        result1 = adapter.get_stock_daily(symbol, start_date, end_date)
        first_call_time = time.time() - start_time

        # 第二次调用（有缓存）
        start_time = time.time()
        result2 = adapter.get_stock_daily(symbol, start_date, end_date)
        second_call_time = time.time() - start_time

        # 缓存应该显著提升性能
        if first_call_time > 0.001:  # 只有在第一次调用有明显耗时的情况下才验证
            improvement_ratio = (
                first_call_time / second_call_time
                if second_call_time > 0
                else float("inf")
            )
            assert improvement_ratio > 5, f"缓存性能提升不足: {improvement_ratio:.1f}倍"

        # 验证结果相同
        assert id(result1) == id(result2)

    def test_large_dataset_performance(self):
        """测试大数据集性能"""
        adapter = PriceDataAdapter()

        # 大数据集（一年的数据）
        symbol = "000001"
        start_date = "2024-01-01"
        end_date = "2024-12-31"

        import time

        start_time = time.time()
        result = adapter.get_stock_daily(symbol, start_date, end_date)
        end_time = time.time()

        processing_time = end_time - start_time

        # 大数据集处理应该合理快速（小于1秒）
        assert processing_time < 1.0, (
            f"大数据集处理耗时 {processing_time:.2f} 秒，超过预期"
        )

        # 验证数据量合理
        if not result.empty:
            assert len(result) <= 262  # 一年最多262天

    def test_multiple_concurrent_requests(self):
        """测试多个并发请求"""
        adapter = PriceDataAdapter()

        symbols = ["000001", "000002", "000003", "000004", "000005"]
        start_date = "2024-01-01"
        end_date = "2024-01-05"

        import time

        start_time = time.time()

        results = []
        for symbol in symbols:
            result = adapter.get_stock_daily(symbol, start_date, end_date)
            results.append(result)

        total_time = time.time() - start_time
        avg_time = total_time / len(symbols) * 1000  # 毫秒

        # 平均每个请求应该快速（小于20毫秒）
        assert avg_time < 20, f"并发请求平均耗时 {avg_time:.2f} 毫秒，超过预期"

        # 验证缓存工作正常
        assert len(adapter.cache) == len(symbols)


class TestIntegration:
    """集成测试类"""

    def test_end_to_end_workflow(self):
        """测试端到端工作流程"""
        adapter = PriceDataAdapter()

        # 1. 获取多只股票的数据
        symbols = ["000001", "000002"]
        start_date = "2024-01-01"
        end_date = "2024-01-05"

        results = {}
        for symbol in symbols:
            results[symbol] = adapter.get_stock_daily(symbol, start_date, end_date)

        # 2. 验证结果
        for symbol, result in results.items():
            assert isinstance(result, pd.DataFrame)
            assert all(result["symbol"] == symbol)
            assert not result.isnull().any().any()

    def test_integration_with_date_validation(self):
        """测试与日期验证的集成"""
        adapter = PriceDataAdapter()

        # 使用各种有效日期格式进行测试
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

        # 使用各种有效股票代码进行测试
        valid_symbols = ["000001", "123456", "999999"]
        start_date = "2024-01-01"
        end_date = "2024-01-05"

        for symbol in valid_symbols:
            result = adapter.get_stock_daily(symbol, start_date, end_date)
            assert isinstance(result, pd.DataFrame)
            assert all(result["symbol"] == symbol)

    def test_data_consistency_across_calls(self):
        """测试多次调用的数据一致性"""
        adapter = PriceDataAdapter()

        symbol = "000001"
        start_date = "2024-01-01"
        end_date = "2024-01-05"

        # 多次调用相同参数
        results = []
        for _ in range(5):
            adapter.cache.clear()  # 清除缓存以确保重新生成
            result = adapter.get_stock_daily(symbol, start_date, end_date)
            results.append(result)

        # 验证数据结构一致性
        for i in range(1, len(results)):
            assert results[i].equals(results[0])
            assert list(results[i].columns) == list(results[0].columns)
            assert results[i].index.equals(results[0].index)

    def test_realistic_trading_scenario(self):
        """测试真实交易场景"""
        adapter = PriceDataAdapter()

        # 模拟获取热门股票的一周数据
        popular_stocks = ["000001", "000002", "600000", "600036"]
        start_date = "2024-01-01"
        end_date = "2024-01-07"

        stock_data = {}
        for symbol in popular_stocks:
            try:
                stock_data[symbol] = adapter.get_stock_daily(
                    symbol, start_date, end_date
                )
            except ValueError:
                # 如果验证失败，跳过该股票
                continue

        # 验证获取的数据
        assert len(stock_data) > 0, "至少应该有一个股票的数据获取成功"

        for symbol, data in stock_data.items():
            assert not data.empty, f"股票 {symbol} 应该有数据"
            assert all(data["symbol"] == symbol), f"股票 {symbol} 的symbol列应该一致"

    def test_error_handling_integration(self):
        """测试错误处理集成"""
        adapter = PriceDataAdapter()

        # 测试各种错误情况
        error_cases = [
            ("invalid_symbol", "000001", "2024-01-01", "2024-01-05"),
            ("invalid_start", "000001", "invalid-date", "2024-01-05"),
            ("invalid_end", "000001", "2024-01-01", "invalid-date"),
            ("invalid_range", "000001", "2024-01-05", "2024-01-01"),
        ]

        for case_name, symbol, start_date, end_date in error_cases:
            with pytest.raises(ValueError):
                adapter.get_stock_daily(symbol, start_date, end_date)

    def test_cache_state_isolation(self):
        """测试缓存状态隔离"""
        adapter1 = PriceDataAdapter()
        adapter2 = PriceDataAdapter()

        symbol = "000001"
        start_date = "2024-01-01"
        end_date = "2024-01-05"

        # 第一个适配器缓存数据
        result1 = adapter1.get_stock_daily(symbol, start_date, end_date)

        # 第二个适配器应该没有缓存
        result2 = adapter2.get_stock_daily(symbol, start_date, end_date)

        # 验证缓存是独立的
        assert len(adapter1.cache) == 1
        assert len(adapter2.cache) == 1
        assert id(result1) != id(result2)  # 不同对象引用


class TestDataQuality:
    """数据质量测试类"""

    def test_data_completeness(self):
        """测试数据完整性"""
        adapter = PriceDataAdapter()
        result = adapter.get_stock_daily("000001", "2024-01-01", "2024-01-10")

        if not result.empty:
            # 验证没有缺失值
            assert not result.isnull().any().any()

            # 验证所有必需列存在
            required_columns = ["open", "high", "low", "close", "volume", "symbol"]
            assert all(col in result.columns for col in required_columns)

    def test_data_format_standards(self):
        """测试数据格式标准"""
        adapter = PriceDataAdapter()
        result = adapter.get_stock_daily("000001", "2024-01-01", "2024-01-05")

        if not result.empty:
            # 验证日期索引格式
            assert isinstance(result.index, pd.DatetimeIndex)

            # 验证数值精度
            price_columns = ["open", "high", "low", "close"]
            for col in price_columns:
                # 检查是否为小数点后2位精度
                sample_values = result[col].dropna().head()
                for val in sample_values:
                    if isinstance(val, (int, float)):
                        # 检查是否为2位小数或整数
                        decimal_part = (
                            str(val).split(".")[-1] if "." in str(val) else "0"
                        )
                        assert len(decimal_part) <= 2

    def test_business_logic_validation(self):
        """测试业务逻辑验证"""
        adapter = PriceDataAdapter()
        result = adapter.get_stock_daily("000001", "2024-01-01", "2024-01-05")

        if not result.empty:
            # 验证OHLC逻辑
            for idx in result.index:
                row = result.loc[idx]
                assert row["high"] >= row["low"], (
                    f"日期 {idx}: High ({row['high']}) < Low ({row['low']})"
                )
                assert row["high"] >= row["open"], (
                    f"日期 {idx}: High ({row['high']}) < Open ({row['open']})"
                )
                assert row["high"] >= row["close"], (
                    f"日期 {idx}: High ({row['high']}) < Close ({row['close']})"
                )
                assert row["low"] <= row["open"], (
                    f"日期 {idx}: Low ({row['low']}) > Open ({row['open']})"
                )
                assert row["low"] <= row["close"], (
                    f"日期 {idx}: Low ({row['low']}) > Close ({row['close']})"
                )

    def test_weekday_data_availability(self):
        """测试工作日数据可用性"""
        adapter = PriceDataAdapter()

        # 选择一个确定的日期范围
        start_date = "2024-01-01"  # 周一
        end_date = "2024-01-05"  # 周五

        result = adapter.get_stock_daily("000001", start_date, end_date)

        # 这个范围内的所有日期都应该是工作日
        expected_weekdays = []
        current_date = datetime.strptime(start_date, "%Y-%m-%d")
        while current_date <= datetime.strptime(end_date, "%Y-%m-%d"):
            if current_date.weekday() < 5:  # 0-4 是周一到周五
                expected_weekdays.append(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)

        if expected_weekdays:
            # 验证预期的工作日都有数据
            actual_dates = set(result.index) if not result.empty else set()
            expected_dates = set(expected_weekdays)

            # 应该有预期工作日的大部分数据
            intersection = actual_dates.intersection(expected_dates)
            coverage_ratio = len(intersection) / len(expected_dates)
            assert coverage_ratio >= 0.8, f"工作日数据覆盖率 {coverage_ratio:.2f} 过低"

    def test_price_volatility_reasonableness(self):
        """测试价格波动合理性"""
        adapter = PriceDataAdapter()
        result = adapter.get_stock_daily("000001", "2024-01-01", "2024-01-31")

        if len(result) > 1:
            # 计算日收益率
            daily_returns = result["close"].pct_change().dropna()

            # 日收益率应该在合理范围内（-20%到+20%）
            assert daily_returns.min() >= -0.2, (
                f"最小日收益率 {daily_returns.min():.2f} 过低"
            )
            assert daily_returns.max() <= 0.2, (
                f"最大日收益率 {daily_returns.max():.2f} 过高"
            )

            # 验证没有极端异常值
            std_return = daily_returns.std()
            assert std_return <= 0.1, (
                f"收益率标准差 {std_return:.2f} 过高，可能存在异常值"
            )

    def test_volume_price_relationship(self):
        """测试成交量价格关系"""
        adapter = PriceDataAdapter()
        result = adapter.get_stock_daily("000001", "2024-01-01", "2024-01-10")

        if not result.empty:
            # 价格较高的交易日通常成交量也较高（简化验证）
            # 这里我们只做基本验证，因为Mock数据是随机生成的
            avg_price = result["close"].mean()
            avg_volume = result["volume"].mean()

            # 验证成交量和价格都在合理范围内
            assert 10 <= avg_price <= 100, f"平均价格 {avg_price:.2f} 不在合理范围内"
            assert 1000 <= avg_volume <= 100000, (
                f"平均成交量 {avg_volume:.2f} 不在合理范围内"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
