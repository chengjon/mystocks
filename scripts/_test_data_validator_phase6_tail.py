#!/usr/bin/env python3
"""Support tests extracted from `scripts/tests/test_data_validator_phase6.py`."""

import time

import numpy as np
import pandas as pd

from src.adapters.data_validator import DataValidator


class TestPerformanceAndEdgeCases:
    """性能测试和边界情况"""

    def setup_method(self):
        """pytest setup方法"""
        self.validator = DataValidator()

    def test_large_dataframe_validation(self):
        """测试大型DataFrame验证性能"""
        large_data = pd.DataFrame(
            {
                "open": np.random.uniform(10, 100, 10000),
                "high": np.random.uniform(10, 100, 10000),
                "low": np.random.uniform(10, 100, 10000),
                "close": np.random.uniform(10, 100, 10000),
                "volume": np.random.randint(1000, 10000, 10000),
            }
        )

        large_data["high"] = np.maximum(large_data["high"], large_data[["open", "close"]].max(axis=1))
        large_data["low"] = np.minimum(large_data["low"], large_data[["open", "close"]].min(axis=1))

        start_time = time.time()
        result = self.validator.validate_price_data(large_data)
        execution_time = time.time() - start_time

        assert result is True
        assert execution_time < 5.0

    def test_extreme_values(self):
        """测试极端值"""
        extreme_data = pd.DataFrame(
            {
                "open": [0.01],
                "high": [10000.0],
                "low": [0.01],
                "close": [10000.0],
                "volume": [0],
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
                "volume": [1_000_000_000],
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

        symbol_valid = self.validator.validate_stock_symbol("000001")
        date_valid = self.validator.validate_date_format("2024-01-01")
        range_valid = self.validator.validate_date_range("2024-01-01", "2024-01-05")
        price_valid = self.validator.validate_price_data(stock_data)
        volume_valid = self.validator.validate_volume_data(stock_data)
        complete = self.validator.check_data_completeness(stock_data)
        trading_day = self.validator.validate_trading_day("2024-01-01")
        price_range = self.validator.validate_price_range(stock_data)

        assert symbol_valid is True
        assert date_valid is True
        assert range_valid is True
        assert price_valid is True
        assert volume_valid is True
        assert complete is True
        assert price_range is True
        assert isinstance(trading_day, bool)

    def test_validation_error_handling(self):
        """测试验证错误处理"""
        invalid_cases = [
            ("invalid_symbol", "2024-01-01", "2024-01-02"),
            ("000001", "invalid-date", "2024-01-02"),
            ("000001", "2024-01-02", "2024-01-01"),
        ]

        for symbol, start_date, end_date in invalid_cases:
            validations = [
                self.validator.validate_stock_symbol(symbol),
                self.validator.validate_date_format(start_date),
                self.validator.validate_date_format(end_date),
                self.validator.validate_date_range(start_date, end_date),
            ]
            assert not all(validations), (
                f"Expected at least one validation to fail for {symbol}, {start_date}, {end_date}"
            )
