import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime
from typing import cast  # Added this line

from src.adapters.customer_adapter import CustomerDataSource


class TestCustomerDataSource(unittest.TestCase):

    def setUp(self):
        # Patch COLUMN_MAPPER_AVAILABLE to True for the duration of setUp
        # This is for internal check within CustomerDataSource.__init__
        with patch("src.adapters.customer_adapter.COLUMN_MAPPER_AVAILABLE", True):
            self.datasource = CustomerDataSource(use_column_mapping=True)

        # Explicitly set self.datasource.ef and self.datasource.eq to MagicMocks
        self.mock_efinance = MagicMock()
        self.mock_efinance.stock = MagicMock()
        self.mock_efinance.index = MagicMock()
        self.datasource.ef = self.mock_efinance
        self.datasource.efinance_available = True

        self.mock_easyquotation = MagicMock()
        self.mock_easyquotation.use.return_value = MagicMock()
        self.datasource.eq = self.mock_easyquotation
        self.datasource.easyquotation_available = True

        # Patch _standardize_dataframe directly on the instance using patch.object
        self.mock_standardize_dataframe = patch.object(self.datasource, "_standardize_dataframe", autospec=True).start()
        self.addCleanup(patch.stopall)  # Ensures all patches are stopped after the test

    def tearDown(self):
        # Reset COLUMN_MAPPER_AVAILABLE to its original state or None if not important
        # This is important if other tests might rely on its actual value
        pass

    def test_initialization_with_column_mapping(self):
        # We assume COLUMN_MAPPER_AVAILABLE is True for this test due to patch
        assert self.datasource.efinance_available
        assert self.datasource.easyquotation_available
        assert self.datasource.use_column_mapping

    @patch("src.adapters.customer_adapter.datetime")
    def test_get_real_time_data_efinance_market_wide_success(self, mock_datetime):
        # Mock datetime.now() for consistent timestamps
        mock_now = datetime(2025, 1, 1, 10, 0, 0)
        mock_datetime.now.return_value = mock_now

        # Mock efinance to return market-wide data
        mock_efinance_df = pd.DataFrame(
            {
                "股票代码": ["000001", "000002"],
                "股票名称": ["平安银行", "万科A"],
                "最新价": [10.0, 20.0],
                "涨跌幅": [0.05, -0.02],
                "成交量": [1000, 2000],
                "成交额": [10000, 40000],
                "总市值": [100000, 200000],
                "流通市值": [80000, 150000],
                "最高": [10.5, 20.5],
                "最低": [9.5, 19.5],
                "开盘": [9.8, 20.2],
                "涨跌额": [0.5, -0.4],
                "换手率": [0.01, 0.02],
            }
        )
        self.datasource.ef.stock.get_realtime_quotes.return_value = mock_efinance_df

        # Configure mock_standardize_dataframe return value
        mock_standardized_df_return = pd.DataFrame(
            {
                "symbol": ["000001", "000002"],
                "name": ["平安银行", "万科A"],
                "close": [10.0, 20.0],
                "pct_chg": [0.05, -0.02],
                "volume": [1000, 2000],
                "amount": [10000, 40000],
                "total_mv": [100000, 200000],
                "circ_mv": [80000, 150000],
                "high": [10.5, 20.5],
                "low": [9.5, 19.5],
                "open": [9.8, 20.2],
                "change": [0.5, -0.4],
                "turnover_rate": [0.01, 0.02],
                "fetch_timestamp": [mock_now, mock_now],
                "data_source": ["efinance", "efinance"],
                "data_type": ["realtime_quotes", "realtime_quotes"],
                "market": ["SH", "SH"],
            }
        )
        self.mock_standardize_dataframe.return_value = mock_standardized_df_return

        # Test for market-wide data (e.g., "sh")
        result = self.datasource.get_real_time_data("sh")

        assert isinstance(result, pd.DataFrame)
        result = cast(pd.DataFrame, result)  # Explicitly cast for MyPy
        assert not result.empty
        assert len(result) == 2
        self.mock_efinance.stock.get_realtime_quotes.assert_called_once()
        self.mock_standardize_dataframe.assert_called_once()
        pd.testing.assert_frame_equal(
            result,
            mock_standardized_df_return[
                [
                    "symbol",
                    "name",
                    "pct_chg",
                    "close",
                    "high",
                    "low",
                    "open",
                    "change",
                    "turnover_rate",
                    "volume",
                    "amount",
                    "total_mv",
                    "circ_mv",
                    "fetch_timestamp",
                    "data_source",
                    "data_type",
                    "market",
                ]
            ],
        )
        assert result["market"].iloc[0] == "SH"
        assert result["data_source"].iloc[0] == "efinance"

    @patch("src.adapters.customer_adapter.datetime")
    def test_get_real_time_data_efinance_market_wide_failure_fallback_easyquotation(self, mock_datetime):
        # Mock datetime.now()
        mock_now = datetime(2025, 1, 1, 10, 0, 0)
        mock_datetime.now.return_value = mock_now

        # Mock efinance to raise an exception, forcing fallback
        self.datasource.ef.stock.get_realtime_quotes.side_effect = Exception("Efinance error")

        # Mock easyquotation
        mock_easyquotation_market_data = {
            "sh": {
                "name": "上证指数",
                "open": "3000",
                "close": "3010",
                "high": "3020",
                "low": "2990",
                "volume": "10000000",
                "amount": "200000000",
                "turnover_rate": "0.01",
                "pct_chg": "0.003",
            }
        }
        mock_quotation = MagicMock()
        mock_quotation.market_snapshot.return_value = mock_easyquotation_market_data
        self.mock_easyquotation.use.return_value = mock_quotation

        mock_standardized_df_return = pd.DataFrame(
            {
                "name": ["上证指数"],
                "open": [3000.0],
                "close": [3010.0],
                "high": [3020.0],
                "low": [2990.0],
                "volume": [10000000.0],
                "amount": [200000000.0],
                "turnover_rate": [0.01],
                "pct_chg": [0.003],
                "fetch_timestamp": [mock_now],
                "data_source": ["easyquotation"],
                # No market column from easyquotation market_snapshot in this mock example
            }
        )
        self.mock_standardize_dataframe.return_value = mock_standardized_df_return

        result = self.datasource.get_real_time_data("sh")

        assert isinstance(result, pd.DataFrame)
        result = cast(pd.DataFrame, result)  # Explicitly cast for MyPy
        assert not result.empty
        assert len(result) == 1
        self.datasource.ef.stock.get_realtime_quotes.assert_called_once()  # Should be called and fail
        self.datasource.eq.use.assert_called_once_with("sina")
        self.datasource.eq.use.return_value.market_snapshot.assert_called_once()
        self.mock_standardize_dataframe.assert_called_once()

        # Check if the dataframe contains expected columns and values
        assert "fetch_timestamp" in result.columns
        assert "data_source" in result.columns
        assert result["data_source"].iloc[0] == "easyquotation"
