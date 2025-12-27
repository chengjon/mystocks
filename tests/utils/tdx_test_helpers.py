import pytest
import os
import pandas as pd
import sys

# Add project root to path for src imports
# Assuming tests/utils is two levels down from project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, project_root)

from src.adapters.tdx_adapter import TdxDataSource


# Common TDX file path (e.g., for day files)
# This path might need to be configured via a test config or environment variable
# For now, keeping it relative to project root as in original test
TDX_TEST_DATA_DIR = os.path.join(project_root, "temp", "pyprof", "data")


@pytest.fixture(scope="module")
def tdx_adapter():
    """Provides a TdxDataSource instance for tests."""
    return TdxDataSource()


@pytest.fixture(scope="module")
def tdx_day_file_path():
    """Provides a path to a sample TDX .day file."""
    # Ensure this file exists for the tests to run
    # For CI/CD, this file should be part of test data or generated.
    file_path = os.path.join(TDX_TEST_DATA_DIR, "sh000001.day")
    if not os.path.exists(file_path):
        pytest.skip(f"TDX test day file not found: {file_path}")
    return file_path


@pytest.fixture(scope="module")
def tdx_minute_file_path():
    """Provides a path to a sample TDX .lc5 file (for minute data)."""
    file_path = os.path.join(TDX_TEST_DATA_DIR, "sh600000.lc5")  # Example minute file
    if not os.path.exists(file_path):
        pytest.skip(f"TDX test minute file not found: {file_path}")
    return file_path


# Common expected columns for day files
TDX_DAY_FILE_EXPECTED_COLUMNS = [
    "code",
    "tradeDate",
    "open",
    "high",
    "low",
    "close",
    "amount",
    "vol",
]


# Helper function for common DataFrame assertions
def assert_tdx_dataframe_basic_structure(df: pd.DataFrame, expected_columns: List[str]):
    """
    断言 TDX DataFrame 的基本结构和内容。
    Args:
        df: 要测试的 Pandas DataFrame。
        expected_columns: 期望的列名列表。
    """
    assert isinstance(df, pd.DataFrame), "返回值应为 DataFrame"
    assert not df.empty, "返回的 DataFrame 不应为空"
    assert list(df.columns) == expected_columns, f"列名不匹配,期望{expected_columns}, 实际{list(df.columns)}"


def assert_tdx_dataframe_data_types(df: pd.DataFrame):
    """
    断言 TDX DataFrame 中数据类型的正确性。
    Args:
        df: 要测试的 Pandas DataFrame。
    """
    assert df["code"].dtype == object, "code 应为字符串类型"
    for col in ["open", "high", "low", "close", "amount", "vol"]:
        assert pd.api.types.is_numeric_dtype(df[col]), f"{col} 应为数值类型"


def assert_tdx_dataframe_data_validity(df: pd.DataFrame):
    """
    断言 TDX DataFrame 中数据的有效性。
    Args:
        df: 要测试的 Pandas DataFrame。
    """
    for col in ["open", "high", "low", "close"]:
        assert (df[col] > 0).all(), f"{col} 应全部为正数"
    assert (df["high"] >= df["low"]).all(), "最高价应 >= 最低价"
    assert (df["high"] >= df["close"]).all(), "最高价应 >= 收盘价"
    assert (df["low"] <= df["close"]).all(), "最低价应 <= 收盘价"


def assert_tdx_dataframe_date_format(df: pd.DataFrame):
    """
    断言 TDX DataFrame 中日期格式的正确性。
    Args:
        df: 要测试的 Pandas DataFrame。
    """
    assert df["tradeDate"].dtype == object, "tradeDate 应为字符串类型"
    assert df["tradeDate"].str.len().iloc[0] == 8, "日期应为8位字符串"
    pd.to_datetime(df["tradeDate"], format="%Y%m%d")  # Test if conversion works
