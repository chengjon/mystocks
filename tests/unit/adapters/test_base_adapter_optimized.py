"""Contract tests for the current `BaseDataSourceAdapter` helper behavior."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pandas as pd

from src.adapters.base_adapter import BaseDataSourceAdapter


class DummyAdapter(BaseDataSourceAdapter):
    pass


def make_adapter() -> DummyAdapter:
    adapter = DummyAdapter.__new__(DummyAdapter)
    adapter.source_name = "demo"
    adapter.quality_validator = MagicMock()
    adapter.logger = MagicMock()
    return adapter


def make_daily_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": ["2026-04-01", "2026-04-02"],
            "open": [10.0, 10.5],
            "high": [10.5, 10.9],
            "low": [9.8, 10.2],
            "close": [10.2, 10.7],
            "volume": [1000, 1500],
        }
    )


def test_init_creates_validator_and_namespaced_logger() -> None:
    with patch("src.adapters.base_adapter.DataQualityValidator") as validator_cls, patch(
        "src.adapters.base_adapter.logging.getLogger"
    ) as get_logger:
        adapter_logger = MagicMock()
        get_logger.return_value = adapter_logger

        adapter = DummyAdapter("demo")

    validator_cls.assert_called_once_with("demo")
    get_logger.assert_called_once_with("src.adapters.base_adapter.demo")
    assert adapter.source_name == "demo"
    assert adapter.quality_validator is validator_cls.return_value
    assert adapter.logger is adapter_logger
    adapter_logger.info.assert_called_once()


def test_apply_quality_check_returns_original_dataframe_for_empty_input() -> None:
    adapter = make_adapter()
    df = pd.DataFrame()

    result = adapter._apply_quality_check(df, "600519")

    assert result is df
    adapter.quality_validator.validate_stock_data.assert_not_called()
    adapter.logger.warning.assert_called_once()


def test_apply_quality_check_logs_issues_for_low_quality_results() -> None:
    adapter = make_adapter()
    df = make_daily_frame()
    adapter.quality_validator.validate_stock_data.return_value = {
        "quality_score": 65.0,
        "issues": [
            {"severity": "critical", "type": "missing_columns", "message": "critical issue"},
            {"severity": "warning", "type": "duplicate_rows", "message": "warning issue"},
        ],
    }

    result = adapter._apply_quality_check(df, "600519", "daily")

    assert result is df
    adapter.quality_validator.validate_stock_data.assert_called_once_with(df, "600519", "daily")
    adapter.logger.warning.assert_called()
    adapter.logger.error.assert_called_once_with("  - %s: %s", "missing_columns", "critical issue")


def test_apply_quality_check_logs_success_for_high_quality_results() -> None:
    adapter = make_adapter()
    df = make_daily_frame()
    adapter.quality_validator.validate_stock_data.return_value = {"quality_score": 95.0, "issues": []}

    result = adapter._apply_quality_check(df, "600519")

    assert result is df
    adapter.logger.info.assert_called()
    adapter.logger.error.assert_not_called()


def test_apply_quality_check_realtime_adds_timestamp_for_validation_and_returns_original_data() -> None:
    adapter = make_adapter()
    adapter.quality_validator.validate_stock_data.return_value = {"quality_score": 90.0, "issues": []}
    realtime_data = {"code": "600519", "name": "Kweichow Moutai", "price": 1500.0, "volume": 2000}

    result = adapter._apply_quality_check_realtime(realtime_data, "600519")

    assert result is realtime_data
    validate_df = adapter.quality_validator.validate_stock_data.call_args.args[0]
    assert "timestamp" in validate_df.columns
    assert validate_df.loc[0, "code"] == "600519"
    adapter.logger.debug.assert_called_once()


def test_apply_quality_check_realtime_handles_empty_data_and_validation_errors() -> None:
    adapter = make_adapter()

    empty_result = adapter._apply_quality_check_realtime({}, "600519")
    assert empty_result == {}
    adapter.logger.warning.assert_called_once()

    adapter.logger.reset_mock()
    adapter.quality_validator.validate_stock_data.side_effect = RuntimeError("validator boom")
    realtime_data = {"code": "600519", "name": "Kweichow Moutai", "price": 1500.0, "volume": 2000}

    errored_result = adapter._apply_quality_check_realtime(realtime_data, "600519")

    assert errored_result is realtime_data
    adapter.logger.error.assert_called_once()


def test_log_data_fetch_and_handle_empty_data_cover_with_and_without_fallback() -> None:
    adapter = make_adapter()

    adapter._log_data_fetch("600519", "daily", 2, ["date", "close"])
    adapter.logger.info.assert_called_once_with("获取%s数据: %s - 记录数: %s", "daily", "600519", 2)
    adapter.logger.debug.assert_called_once_with("数据列: %s", ["date", "close"])

    fallback = {"source": "fallback"}
    assert adapter._handle_empty_data("600519", "daily", fallback) is fallback
    empty_df = adapter._handle_empty_data("600519", "daily")
    assert isinstance(empty_df, pd.DataFrame)
    assert empty_df.empty
