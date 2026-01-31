"""
Phase 6: Market Data Context 验证测试
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.domain.market_data.value_objects import Bar, Quote
from src.infrastructure.market_data.adapter import DataSourceV2Adapter


class TestDataSourceV2Adapter:

    @pytest.fixture
    def mock_manager(self):
        with patch("src.infrastructure.market_data.adapter.DataSourceManagerV2") as MockManager:
            manager_instance = MockManager.return_value
            yield manager_instance

    def test_get_history_kline(self, mock_manager):
        # Setup mock DataFrame
        mock_df = pd.DataFrame(
            {
                "trade_date": ["2024-01-01", "2024-01-02"],
                "open": [10.0, 11.0],
                "high": [12.0, 13.0],
                "low": [9.0, 10.0],
                "close": [11.0, 12.0],
                "volume": [1000, 2000],
                "amount": [10000, 24000],
            }
        )
        mock_manager.get_stock_daily.return_value = mock_df

        adapter = DataSourceV2Adapter()
        bars = adapter.get_history_kline("000001", "20240101", "20240102")

        assert len(bars) == 2
        assert isinstance(bars[0], Bar)
        assert bars[0].symbol == "000001"
        assert bars[0].close == 11.0
        assert bars[1].volume == 2000

        mock_manager.get_stock_daily.assert_called_with("000001", "20240101", "20240102")

    def test_get_realtime_quote(self, mock_manager):
        # Setup mock DataFrame
        mock_df = pd.DataFrame(
            {
                "symbol": ["000001"],
                "price": [10.5],
                "open": [10.0],
                "high": [11.0],
                "low": [9.9],
                "pre_close": [10.0],
                "volume": [5000],
                "amount": [52500],
                "bid1_price": [10.49],
                "bid1_volume": [100],
                "ask1_price": [10.51],
                "ask1_volume": [200],
            }
        )
        mock_manager.get_stock_realtime.return_value = mock_df

        adapter = DataSourceV2Adapter()
        quotes = adapter.get_realtime_quote(["000001"])

        assert len(quotes) == 1
        assert isinstance(quotes[0], Quote)
        assert quotes[0].last_price == 10.5
        assert quotes[0].bid_price1 == 10.49

        mock_manager.get_stock_realtime.assert_called_with(["000001"])

    def test_get_latest_price(self, mock_manager):
        # Setup mock
        mock_df = pd.DataFrame({"symbol": ["000001"], "price": [15.8]})
        mock_manager.get_stock_realtime.return_value = mock_df

        adapter = DataSourceV2Adapter()
        price = adapter.get_latest_price("000001")

        assert price == 15.8


if __name__ == "__main__":
    # 简单的手动运行入口
    pytest.main([__file__])
