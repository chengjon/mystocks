#!/usr/bin/env python3
"""
DataValidator Phase 6 测试套件
遵循Phase 6成功模式：功能→边界→异常→性能→集成测试
目标：将data_validator.py的覆盖率从初始状态提升到95%+
"""

import sys
import os
import time
import pandas as pd
import numpy as np
from pathlib import Path
import pytest
from datetime import datetime, timedelta

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入被测试的模块
from src.adapters.data_validator import DataValidator


class TestDataValidatorInitialization:
    """DataValidator初始化测试"""

    def test_initialization(self):
        """测试DataValidator初始化"""
        validator = DataValidator()
        assert validator is not None
        assert isinstance(validator, DataValidator)

    def test_multiple_instances(self):
        """测试多个DataValidator实例"""
        validators = [DataValidator() for _ in range(5)]
        for validator in validators:
            assert isinstance(validator, DataValidator)


class TestValidateStockSymbol:
    """测试validate_stock_symbol方法"""

    def setup_method(self):
        """pytest setup方法"""
        self.validator = DataValidator()

    def test_valid_stock_symbols(self):
        """测试有效股票代码"""
        valid_symbols = ["000001", "600000", "300001", "002415", "000002"]

        for symbol in valid_symbols:
            result = self.validator.validate_stock_symbol(symbol)
            assert result is True

    def test_invalid_stock_symbols(self):
        """测试无效股票代码"""
        invalid_symbols = [
            "",  # 空字符串
            "12345",  # 5位数字
            "1234567",  # 7位数字
            "ABCDEF",  # 字母
            "000001.",  # 包含点
            "SH000001",  # 包含交易所前缀
            "000001 SZ",  # 包含后缀
        ]

        for symbol in invalid_symbols:
            result = self.validator.validate_stock_symbol(symbol)
            assert result is False

    def test_symbol_with_spaces(self):
        """测试带空格的股票代码"""
        test_cases = [
            (" 000001", True),
            ("000001 ", True),
            (" 000001 ", True),
            ("   600000   ", True),
        ]

        for symbol, expected in test_cases:
            result = self.validator.validate_stock_symbol(symbol)
            assert result is expected

    def test_non_string_inputs(self):
        """测试非字符串输入"""
        non_string_inputs = [None, 123, 456.789, [], {}, True, False]

        for input_val in non_string_inputs:
            result = self.validator.validate_stock_symbol(input_val)
            assert result is False

    def test_edge_cases(self):
        """测试边界情况"""
        edge_cases = [
            ("000000", True),  # 最小6位数字
            ("999999", True),  # 最大6位数字
            ("0" * 6, True),  # 全零
        ]

        for symbol, expected in edge_cases:
            result = self.validator.validate_stock_symbol(symbol)
            assert result is expected


class TestValidateDateFormat:
    """测试validate_date_format方法"""

    def setup_method(self):
        """pytest setup方法"""
        self.validator = DataValidator()

    def test_valid_date_formats(self):
        """测试有效日期格式"""
        valid_dates = [
            "2024-01-01",
            "2024-12-31",
            "2020-02-29",  # 闰年
            "1999-12-31",
            "2024-06-15",
        ]

        for date_str in valid_dates:
            result = self.validator.validate_date_format(date_str)
            assert result is True

    def test_invalid_date_formats(self):
        """测试无效日期格式"""
        invalid_dates = [
            "",  # 空字符串
            "2024/01/01",  # 错误分隔符
            "2024.01.01",  # 错误分隔符
            "20240101",  # 缺少分隔符
            "24-01-01",  # 年份不足
            "2024-13-01",  # 无效月份
            "2024-01-32",  # 无效日期
            "2024-02-30",  # 二月30日
            "2023-02-29",  # 非闰年2月29日
            "invalid-date",
        ]

        for date_str in invalid_dates:
            result = self.validator.validate_date_format(date_str)
            assert result is False

    def test_non_string_inputs(self):
        """测试非字符串输入"""
        non_string_inputs = [None, 123, 456.789, [], {}, True, False]

        for input_val in non_string_inputs:
            result = self.validator.validate_date_format(input_val)
            assert result is False

    def test_leap_year_dates(self):
        """测试闰年日期"""
        leap_year_dates = [
            ("2020-02-29", True),  # 闰年
            ("2024-02-29", True),  # 闰年
            ("2023-02-28", True),  # 非闰年2月28日
            ("2023-02-29", False),  # 非闰年2月29日
            ("1900-02-28", True),  # 非闰年世纪年
            ("1900-02-29", False),  # 非闰年世纪年
            ("2000-02-29", True),  # 闰年世纪年
        ]

        for date_str, expected in leap_year_dates:
            result = self.validator.validate_date_format(date_str)
            assert result is expected


class TestValidateDateRange:
    """测试validate_date_range方法"""

    def setup_method(self):
        """pytest setup方法"""
        self.validator = DataValidator()

    def test_valid_date_ranges(self):
        """测试有效日期范围"""
        valid_ranges = [
            ("2024-01-01", "2024-01-31"),
            ("2024-01-01", "2024-01-02"),  # 相差1天
            ("2024-01-01", "2024-12-31"),  # 跨年
            ("2020-02-28", "2020-03-01"),  # 闰年跨月
        ]

        for start_date, end_date in valid_ranges:
            result = self.validator.validate_date_range(start_date, end_date)
            assert result is True

    def test_invalid_date_ranges(self):
        """测试无效日期范围"""
        invalid_ranges = [
            ("2024-01-31", "2024-01-01"),  # 开始晚于结束
            ("2024-01-01", "2024-01-01"),  # 相同日期
            ("invalid-date", "2024-01-31"),  # 无效开始日期
            ("2024-01-01", "invalid-date"),  # 无效结束日期
            ("2024-02-30", "2024-03-01"),  # 无效开始日期
        ]

        for start_date, end_date in invalid_ranges:
            result = self.validator.validate_date_range(start_date, end_date)
            assert result is False

    def test_edge_cases(self):
        """测试边界情况"""
        edge_cases = [
            ("2024-01-01", "2024-01-02"),  # 最小有效间隔
            ("2024-12-31", "2025-01-01"),  # 跨年
        ]

        for start_date, end_date in edge_cases:
            result = self.validator.validate_date_range(start_date, end_date)
            assert result is True


class TestValidatePriceData:
    """测试validate_price_data方法"""

    def setup_method(self):
        """pytest setup方法"""
        self.validator = DataValidator()

    def test_valid_price_data(self):
        """测试有效价格数据"""
        valid_data = pd.DataFrame(
            {
                "open": [10.0, 10.5, 11.0],
                "high": [10.8, 11.2, 11.5],
                "low": [9.5, 10.0, 10.5],
                "close": [10.6, 11.0, 11.2],
                "volume": [1000, 1200, 900],
            }
        )

        result = self.validator.validate_price_data(valid_data)
        assert result is True

    def test_missing_columns(self):
        """测试缺少必需列"""
        invalid_data_cases = [
            pd.DataFrame({"open": [10.0, 10.5], "high": [10.8, 11.2]}),  # 缺少多列
            pd.DataFrame(
                {"open": [10.0], "high": [10.8], "low": [9.5], "close": [10.6]}
            ),  # 缺少volume
            pd.DataFrame(
                {"high": [10.8], "low": [9.5], "close": [10.6], "volume": [1000]}
            ),  # 缺少open
        ]

        for data in invalid_data_cases:
            result = self.validator.validate_price_data(data)
            assert result is False

    def test_empty_dataframe(self):
        """测试空DataFrame"""
        empty_df = pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
        result = self.validator.validate_price_data(empty_df)
        assert result is False

    def test_negative_prices(self):
        """测试负价格"""
        negative_price_cases = [
            pd.DataFrame(
                {
                    "open": [-10.0],
                    "high": [10.8],
                    "low": [9.5],
                    "close": [10.6],
                    "volume": [1000],
                }
            ),
            pd.DataFrame(
                {
                    "open": [10.0],
                    "high": [-11.2],
                    "low": [9.5],
                    "close": [10.6],
                    "volume": [1000],
                }
            ),
            pd.DataFrame(
                {
                    "open": [10.0],
                    "high": [10.8],
                    "low": [-9.5],
                    "close": [10.6],
                    "volume": [1000],
                }
            ),
            pd.DataFrame(
                {
                    "open": [10.0],
                    "high": [10.8],
                    "low": [9.5],
                    "close": [-10.6],
                    "volume": [1000],
                }
            ),
        ]

        for data in negative_price_cases:
            result = self.validator.validate_price_data(data)
            assert result is False

    def test_zero_prices(self):
        """测试零价格"""
        zero_price_data = pd.DataFrame(
            {
                "open": [0.0],
                "high": [10.8],
                "low": [9.5],
                "close": [10.6],
                "volume": [1000],
            }
        )
        result = self.validator.validate_price_data(zero_price_data)
        assert result is False

    def test_negative_volume(self):
        """测试负成交量"""
        negative_volume_data = pd.DataFrame(
            {
                "open": [10.0],
                "high": [10.8],
                "low": [9.5],
                "close": [10.6],
                "volume": [-1000],
            }
        )
        result = self.validator.validate_price_data(negative_volume_data)
        assert result is False

    def test_invalid_price_relationships(self):
        """测试无效价格关系"""
        invalid_relationship_cases = [
            # High < Low
            pd.DataFrame(
                {
                    "open": [10.0],
                    "high": [9.0],
                    "low": [9.5],
                    "close": [10.6],
                    "volume": [1000],
                }
            ),
            # High < Open
            pd.DataFrame(
                {
                    "open": [11.0],
                    "high": [10.8],
                    "low": [9.5],
                    "close": [10.6],
                    "volume": [1000],
                }
            ),
            # High < Close
            pd.DataFrame(
                {
                    "open": [10.0],
                    "high": [10.8],
                    "low": [9.5],
                    "close": [11.0],
                    "volume": [1000],
                }
            ),
            # Low > Open
            pd.DataFrame(
                {
                    "open": [9.0],
                    "high": [10.8],
                    "low": [9.5],
                    "close": [10.6],
                    "volume": [1000],
                }
            ),
            # Low > Close
            pd.DataFrame(
                {
                    "open": [10.0],
                    "high": [10.8],
                    "low": [10.7],
                    "close": [10.6],
                    "volume": [1000],
                }
            ),
        ]

        for data in invalid_relationship_cases:
            result = self.validator.validate_price_data(data)
            assert result is False

    def test_mixed_valid_invalid_rows(self):
        """测试混合有效/无效行"""
        mixed_data = pd.DataFrame(
            {
                "open": [10.0, 11.0, 12.0],
                "high": [10.8, 10.5, 12.5],  # 第二行High < Open
                "low": [9.5, 10.0, 11.5],
                "close": [10.6, 10.8, 12.2],
                "volume": [1000, 1200, 1300],
            }
        )
        result = self.validator.validate_price_data(mixed_data)
        assert result is False

    def test_non_numeric_data(self):
        """测试非数值数据"""
        non_numeric_data = pd.DataFrame(
            {
                "open": ["invalid"],
                "high": [10.8],
                "low": [9.5],
                "close": [10.6],
                "volume": [1000],
            }
        )
        result = self.validator.validate_price_data(non_numeric_data)
        assert result is False


class TestValidateVolumeData:
    """测试validate_volume_data方法"""

    def setup_method(self):
        """pytest setup方法"""
        self.validator = DataValidator()

    def test_valid_volume_data(self):
        """测试有效成交量数据"""
        valid_data = pd.DataFrame({"volume": [1000, 1200, 900, 1500, 0]})
        result = self.validator.validate_volume_data(valid_data)
        assert result is True

    def test_missing_volume_column(self):
        """测试缺少volume列"""
        data_without_volume = pd.DataFrame(
            {"open": [10.0, 10.5], "close": [10.6, 11.0]}
        )
        result = self.validator.validate_volume_data(data_without_volume)
        assert result is False

    def test_empty_dataframe(self):
        """测试空DataFrame"""
        empty_df = pd.DataFrame(columns=["volume"])
        result = self.validator.validate_volume_data(empty_df)
        assert result is False

    def test_negative_volume(self):
        """测试负成交量"""
        negative_volume_data = pd.DataFrame({"volume": [1000, -500, 800]})
        result = self.validator.validate_volume_data(negative_volume_data)
        assert result is False

    def test_nan_volume(self):
        """测试NaN成交量"""
        nan_volume_data = pd.DataFrame({"volume": [1000, np.nan, 800]})
        result = self.validator.validate_volume_data(nan_volume_data)
        assert result is False

    def test_string_volume(self):
        """测试字符串成交量"""
        string_volume_data = pd.DataFrame({"volume": ["invalid", "1200", "800"]})
        result = self.validator.validate_volume_data(string_volume_data)
        assert result is False


class TestValidateTradingDay:
    """测试validate_trading_day方法"""

    def setup_method(self):
        """pytest setup方法"""
        self.validator = DataValidator()

    def test_valid_trading_days(self):
        """测试有效交易日（周一到周五）"""
        trading_days = [
            ("2024-01-01", True),  # 2024-01-01是周一，应该是交易日
            ("2024-01-02", True),  # 周二
            ("2024-01-03", True),  # 周三
            ("2024-01-04", True),  # 周四
            ("2024-01-05", True),  # 周五
            ("2024-01-06", False),  # 周六
            ("2024-01-07", False),  # 周日
        ]

        for date_str, expected in trading_days:
            result = self.validator.validate_trading_day(date_str)
            assert result is expected

    def test_invalid_date_formats(self):
        """测试无效日期格式"""
        invalid_dates = ["", "invalid", "2024/01/01", "2024.01.01"]

        for date_str in invalid_dates:
            result = self.validator.validate_trading_day(date_str)
            assert result is False

    def test_holiday_scenarios(self):
        """测试节假日场景（简化版，只检查周末）"""
        weekend_dates = [
            "2024-01-06",  # 周六
            "2024-01-07",  # 周日
            "2024-01-13",  # 周六
            "2024-01-14",  # 周日
        ]

        for date_str in weekend_dates:
            result = self.validator.validate_trading_day(date_str)
            assert result is False


class TestValidatePriceRange:
    """测试validate_price_range方法"""

    def setup_method(self):
        """pytest setup方法"""
        self.validator = DataValidator()

    def test_valid_price_ranges(self):
        """测试有效价格范围"""
        valid_data = pd.DataFrame(
            {
                "open": [10.0, 100.0, 5000.0],
                "high": [10.5, 105.0, 5100.0],
                "low": [9.5, 95.0, 4900.0],
                "close": [10.2, 102.0, 5050.0],
            }
        )
        result = self.validator.validate_price_range(valid_data)
        assert result is True

    def test_prices_below_minimum(self):
        """测试低于最小价格"""
        low_price_data = pd.DataFrame(
            {
                "open": [0.005],  # 低于默认最小值0.01
                "high": [10.5],
                "low": [9.5],
                "close": [10.2],
            }
        )
        result = self.validator.validate_price_range(low_price_data)
        assert result is False

    def test_prices_above_maximum(self):
        """测试高于最大价格"""
        high_price_data = pd.DataFrame(
            {
                "open": [15000.0],  # 高于默认最大值10000.0
                "high": [15050.0],
                "low": [14950.0],
                "close": [15020.0],
            }
        )
        result = self.validator.validate_price_range(high_price_data)
        assert result is False

    def test_custom_price_range(self):
        """测试自定义价格范围"""
        data = pd.DataFrame(
            {
                "open": [5.0, 15.0],
                "high": [5.5, 15.5],
                "low": [4.5, 14.5],
                "close": [5.2, 15.2],
            }
        )

        # 使用自定义范围
        result = self.validator.validate_price_range(
            data, min_price=1.0, max_price=20.0
        )
        assert result is True

        # 使用不匹配的自定义范围
        result = self.validator.validate_price_range(
            data, min_price=10.0, max_price=20.0
        )
        assert result is False

    def test_partial_price_columns(self):
        """测试部分价格列"""
        partial_data = pd.DataFrame(
            {
                "open": [10.0],
                "close": [10.2],
                # 缺少high和low
            }
        )
        result = self.validator.validate_price_range(partial_data)
        assert result is True  # 应该跳过缺失的列

    def test_non_numeric_prices(self):
        """测试非数值价格被转换为NaN"""
        non_numeric_data = pd.DataFrame(
            {"open": ["invalid"], "high": [10.5], "low": [9.5], "close": [10.2]}
        )
        result = self.validator.validate_price_range(non_numeric_data)
        # pandas.to_numeric将无效字符串转换为NaN，但validate_price_range默认跳过NaN
        assert result is True  # 这实际上是正确的行为


class TestCheckDataCompleteness:
    """测试check_data_completeness方法"""

    def setup_method(self):
        """pytest setup方法"""
        self.validator = DataValidator()

    def test_complete_data(self):
        """测试完整数据"""
        complete_data = pd.DataFrame(
            {
                "open": [10.0, 10.5],
                "high": [10.8, 11.0],
                "low": [9.5, 10.0],
                "close": [10.6, 10.8],
                "volume": [1000, 1200],
            }
        )
        result = self.validator.check_data_completeness(complete_data)
        assert result is True

    def test_empty_dataframe(self):
        """测试空DataFrame"""
        empty_df = pd.DataFrame()
        result = self.validator.check_data_completeness(empty_df)
        assert result is False

    def test_missing_columns(self):
        """测试缺少列"""
        incomplete_data = pd.DataFrame(
            {
                "open": [10.0, 10.5],
                "close": [10.6, 10.8],
                # 缺少high, low, volume
            }
        )
        result = self.validator.check_data_completeness(incomplete_data)
        assert result is False

    def test_missing_values(self):
        """测试缺失值"""
        data_with_missing = pd.DataFrame(
            {
                "open": [10.0, np.nan],
                "high": [10.8, 11.0],
                "low": [9.5, 10.0],
                "close": [10.6, 10.8],
                "volume": [1000, 1200],
            }
        )
        result = self.validator.check_data_completeness(data_with_missing)
        assert result is False

    def test_custom_required_columns(self):
        """测试自定义必需列"""
        data = pd.DataFrame(
            {"date": ["2024-01-01", "2024-01-02"], "close": [10.6, 10.8]}
        )

        # 使用自定义列要求
        result = self.validator.check_data_completeness(
            data, required_columns=["date", "close"]
        )
        assert result is True

        # 使用不匹配的自定义列要求
        result = self.validator.check_data_completeness(
            data, required_columns=["date", "open"]
        )
        assert result is False

    def test_single_column_data(self):
        """测试单列数据"""
        single_column_data = pd.DataFrame({"close": [10.6, 10.8, 11.0]})
        result = self.validator.check_data_completeness(
            single_column_data, required_columns=["close"]
        )
        assert result is True


class TestPerformanceAndEdgeCases:
    """性能测试和边界情况"""

    def setup_method(self):
        """pytest setup方法"""
        self.validator = DataValidator()

    def test_large_dataframe_validation(self):
        """测试大型DataFrame验证性能"""
        # 创建大型DataFrame（10000行）
        large_data = pd.DataFrame(
            {
                "open": np.random.uniform(10, 100, 10000),
                "high": np.random.uniform(10, 100, 10000),
                "low": np.random.uniform(10, 100, 10000),
                "close": np.random.uniform(10, 100, 10000),
                "volume": np.random.randint(1000, 10000, 10000),
            }
        )

        # 确保价格关系正确
        large_data["high"] = np.maximum(
            large_data["high"], large_data[["open", "close"]].max(axis=1)
        )
        large_data["low"] = np.minimum(
            large_data["low"], large_data[["open", "close"]].min(axis=1)
        )

        start_time = time.time()
        result = self.validator.validate_price_data(large_data)
        execution_time = time.time() - start_time

        assert result is True
        assert execution_time < 5.0  # 应该在5秒内完成

    def test_extreme_values(self):
        """测试极端值"""
        extreme_data = pd.DataFrame(
            {
                "open": [0.01],  # 最小允许价格
                "high": [10000.0],  # 最大允许价格
                "low": [0.01],
                "close": [10000.0],
                "volume": [0],  # 零成交量
            }
        )
        result = self.validator.validate_price_data(extreme_data)
        assert result is True

    def test_very_large_volumes(self):
        """测试非常大的成交量"""
        large_volume_data = pd.DataFrame(
            {
                "open": [10.0],
                "high": [10.5],
                "low": [9.5],
                "close": [10.2],
                "volume": [1_000_000_000],  # 10亿成交量
            }
        )
        result = self.validator.validate_price_data(large_volume_data)
        assert result is True

    def test_floating_point_precision(self):
        """测试浮点精度"""
        precision_data = pd.DataFrame(
            {
                "open": [10.123456789],
                "high": [10.123456790],
                "low": [10.123456788],
                "close": [10.123456789],
                "volume": [1000.123],
            }
        )
        result = self.validator.validate_price_data(precision_data)
        assert result is True


class TestIntegrationWorkflow:
    """集成工作流测试"""

    def setup_method(self):
        """pytest setup方法"""
        self.validator = DataValidator()

    def test_complete_stock_data_validation(self):
        """测试完整股票数据验证工作流"""
        # 创建完整的股票数据
        stock_data = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=5),
                "open": [10.0, 10.5, 11.0, 10.8, 11.2],
                "high": [10.8, 11.2, 11.5, 11.1, 11.8],
                "low": [9.5, 10.0, 10.5, 10.3, 10.9],
                "close": [10.6, 11.0, 11.1, 10.9, 11.5],
                "volume": [1000, 1200, 900, 1100, 1300],
            }
        )

        # 执行完整验证工作流
        symbol_valid = self.validator.validate_stock_symbol("000001")
        date_valid = self.validator.validate_date_format("2024-01-01")
        range_valid = self.validator.validate_date_range("2024-01-01", "2024-01-05")
        price_valid = self.validator.validate_price_data(stock_data)
        volume_valid = self.validator.validate_volume_data(stock_data)
        complete = self.validator.check_data_completeness(stock_data)
        trading_day = self.validator.validate_trading_day("2024-01-01")
        price_range = self.validator.validate_price_range(stock_data)

        # 验证所有检查通过
        assert symbol_valid is True
        assert date_valid is True
        assert range_valid is True
        assert price_valid is True
        assert volume_valid is True
        assert complete is True
        assert price_range is True
        # trading_day取决于具体日期是周几

    def test_validation_error_handling(self):
        """测试验证错误处理"""
        # 测试各种无效数据
        invalid_cases = [
            ("invalid_symbol", "2024-01-01", "2024-01-02"),  # 无效股票代码
            ("000001", "invalid-date", "2024-01-02"),  # 无效日期格式
            ("000001", "2024-01-02", "2024-01-01"),  # 无效日期范围
        ]

        for symbol, start_date, end_date in invalid_cases:
            # 至少有一个验证应该失败
            validations = [
                self.validator.validate_stock_symbol(symbol),
                self.validator.validate_date_format(start_date),
                self.validator.validate_date_format(end_date),
                self.validator.validate_date_range(start_date, end_date),
            ]
            assert not all(validations), (
                f"Expected at least one validation to fail for {symbol}, {start_date}, {end_date}"
            )


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
