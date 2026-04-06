"""Contract tests for deterministic TDX `.day` file parsing."""

import struct
from pathlib import Path

import pandas as pd
import pytest

from src.adapters.tdx.tdx_adapter import TdxDataSource


DAY_COLUMNS = [
    "code",
    "tradeDate",
    "open",
    "high",
    "low",
    "close",
    "amount",
    "vol",
]


def write_day_file(file_path: Path, rows: list[tuple[int, int, int, int, int, float, int]]) -> Path:
    payload = b"".join(
        struct.pack("IIIIIfII", trade_date, open_, high, low, close, amount, volume, 0)
        for trade_date, open_, high, low, close, amount, volume in rows
    )
    file_path.write_bytes(payload)
    return file_path


class TestTdxBinaryRead:
    @pytest.fixture
    def tdx_adapter(self):
        return TdxDataSource()

    @pytest.fixture
    def sample_day_file(self, tmp_path: Path):
        return write_day_file(
            tmp_path / "sh000001.day",
            [
                (20260102, 1012, 1050, 1001, 1045, 1234567.5, 100000),
                (20260103, 1045, 1060, 1038, 1058, 2345678.0, 120000),
            ],
        )

    def test_read_day_file_returns_dataframe_with_expected_columns(self, tdx_adapter, sample_day_file):
        df = tdx_adapter.read_day_file(str(sample_day_file))

        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == DAY_COLUMNS
        assert len(df) == 2
        assert not df.empty

    def test_read_day_file_parses_code_dates_and_price_scaling(self, tdx_adapter, sample_day_file):
        df = tdx_adapter.read_day_file(str(sample_day_file))

        assert df["code"].tolist() == ["sh000001", "sh000001"]
        assert df["tradeDate"].tolist() == ["20260102", "20260103"]
        assert df["open"].tolist() == [10.12, 10.45]
        assert df["high"].tolist() == [10.50, 10.60]
        assert df["low"].tolist() == [10.01, 10.38]
        assert df["close"].tolist() == [10.45, 10.58]

    def test_read_day_file_preserves_numeric_types_and_valid_ohlc_relationships(self, tdx_adapter, sample_day_file):
        df = tdx_adapter.read_day_file(str(sample_day_file))

        assert df["code"].dtype == object
        assert df["tradeDate"].dtype == object
        for column in ["open", "high", "low", "close", "amount", "vol"]:
            assert pd.api.types.is_numeric_dtype(df[column])

        assert (df[["open", "high", "low", "close"]] > 0).all().all()
        assert (df["high"] >= df["low"]).all()
        assert (df["high"] >= df["close"]).all()
        assert (df["low"] <= df["close"]).all()
        pd.to_datetime(df["tradeDate"], format="%Y%m%d")

    def test_read_day_file_reads_amount_and_volume_values(self, tdx_adapter, sample_day_file):
        df = tdx_adapter.read_day_file(str(sample_day_file))

        assert df["amount"].tolist() == pytest.approx([1234567.5, 2345678.0])
        assert df["vol"].tolist() == [100000, 120000]

    def test_read_day_file_returns_empty_dataframe_for_empty_file(self, tdx_adapter, tmp_path: Path):
        empty_file = tmp_path / "sz000001.day"
        empty_file.write_bytes(b"")

        df = tdx_adapter.read_day_file(str(empty_file))

        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == DAY_COLUMNS
        assert df.empty

    def test_read_day_file_rejects_invalid_file_size(self, tdx_adapter, tmp_path: Path):
        broken_file = tmp_path / "broken.day"
        broken_file.write_bytes(b"broken-payload")

        with pytest.raises(ValueError, match="不是32的倍数"):
            tdx_adapter.read_day_file(str(broken_file))

    def test_read_day_file_not_found(self, tdx_adapter):
        with pytest.raises(FileNotFoundError):
            tdx_adapter.read_day_file("/nonexistent/path/file.day")
