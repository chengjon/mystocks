"""Optimized contract tests for the current `DataValidator` implementation."""

import pandas as pd
import pytest

from src.adapters.data_validator import DataValidator


@pytest.fixture
def validator():
    return DataValidator()


def make_valid_ohlcv_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "open": [10.0, 10.5, 11.0],
            "high": [10.8, 11.1, 11.4],
            "low": [9.8, 10.2, 10.7],
            "close": [10.6, 10.9, 11.2],
            "volume": [1000, 1200, 1500],
        }
    )


class TestDataValidatorOptimized:
    def test_validate_price_data_accepts_valid_ohlcv_dataframe(self, validator):
        assert validator.validate_price_data(make_valid_ohlcv_frame()) is True

    @pytest.mark.parametrize(
        "mutator",
        [
            lambda df: df.assign(high=[9.0, 11.1, 11.4]),
            lambda df: df.assign(low=[10.7, 10.2, 10.7]),
            lambda df: df.assign(open=[-1.0, 10.5, 11.0]),
            lambda df: df.assign(volume=[1000, -10, 1500]),
        ],
    )
    def test_validate_price_data_rejects_invalid_ohlcv_relationships(self, validator, mutator):
        invalid_df = mutator(make_valid_ohlcv_frame())

        assert validator.validate_price_data(invalid_df) is False

    def test_validate_volume_data_rejects_missing_negative_and_nan_values(self, validator):
        assert validator.validate_volume_data(pd.DataFrame({"volume": [100, 200, 0]})) is True
        assert validator.validate_volume_data(pd.DataFrame({"price": [1, 2, 3]})) is False
        assert validator.validate_volume_data(pd.DataFrame({"volume": [100, -1, 5]})) is False
        assert validator.validate_volume_data(pd.DataFrame({"volume": [100, None, 5]})) is False

    def test_check_data_completeness_rejects_missing_values_and_missing_columns(self, validator):
        complete_df = make_valid_ohlcv_frame()
        missing_value_df = complete_df.copy()
        missing_value_df.loc[1, "close"] = None
        missing_column_df = complete_df.drop(columns=["volume"])

        assert validator.check_data_completeness(complete_df) is True
        assert validator.check_data_completeness(missing_value_df) is False
        assert validator.check_data_completeness(missing_column_df) is False
        assert validator.check_data_completeness(
            pd.DataFrame({"symbol": ["000001"], "price": [10.2]}),
            required_columns=["symbol", "price"],
        ) is True

    def test_validate_price_range_enforces_custom_and_default_bounds(self, validator):
        assert validator.validate_price_range(make_valid_ohlcv_frame(), min_price=1.0, max_price=100.0) is True

        out_of_range_df = make_valid_ohlcv_frame().assign(high=[10.8, 11.1, 10050.0])
        assert validator.validate_price_range(out_of_range_df) is False

        narrow_range_df = make_valid_ohlcv_frame().assign(low=[9.8, 0.5, 10.7])
        assert validator.validate_price_range(narrow_range_df, min_price=1.0, max_price=100.0) is False

    def test_validate_stock_symbol_and_date_helpers_cover_success_and_failure_paths(self, validator):
        assert validator.validate_stock_symbol("000001") is True
        assert validator.validate_stock_symbol(" 600000 ") is True
        assert validator.validate_stock_symbol("ABC123") is False
        assert validator.validate_stock_symbol(None) is False

        assert validator.validate_date_format("2026-04-02") is True
        assert validator.validate_date_format("2026/04/02") is False
        assert validator.validate_date_range("2026-04-01", "2026-04-02") is True
        assert validator.validate_date_range("2026-04-02", "2026-04-02") is False

    def test_validate_trading_day_distinguishes_weekday_from_weekend_and_invalid_dates(self, validator):
        assert validator.validate_trading_day("2026-04-02") is True
        assert validator.validate_trading_day("2026-04-04") is False
        assert validator.validate_trading_day("invalid-date") is False
