from unittest.mock import patch

import pandas as pd
import pytest

from src.governance.core.fetcher_bridge import GovernanceDataFetcher, RoutePolicy


class TestGovernanceDataFetcher:

    @pytest.fixture
    def mock_manager(self):
        with patch("src.governance.core.fetcher_bridge.DataSourceManagerV2") as MockManager:
            manager_instance = MockManager.return_value
            yield manager_instance

    def test_initialization(self, mock_manager):
        fetcher = GovernanceDataFetcher()
        assert fetcher.manager is not None

    def test_fetch_batch_kline_smart(self, mock_manager):
        # Setup mock return
        mock_df = pd.DataFrame({"close": [10, 11, 12]})
        mock_manager.get_best_endpoint.return_value = {"endpoint_name": "mock_endpoint", "source_type": "mock"}
        mock_manager._call_endpoint.return_value = mock_df

        fetcher = GovernanceDataFetcher()
        results = fetcher.fetch_batch_kline(
            symbols=["000001"], start_date="20240101", end_date="20240105", policy=RoutePolicy.SMART_ROUTING
        )

        assert "000001" in results
        assert not results["000001"].empty
        mock_manager.get_best_endpoint.assert_called_with("DAILY_KLINE")
        mock_manager._call_endpoint.assert_called()

    def test_fetch_batch_kline_specific(self, mock_manager):
        # Setup mock
        mock_df = pd.DataFrame({"close": [10, 11, 12]})
        mock_manager.find_endpoints.return_value = [{"endpoint_name": "specific_endpoint", "source_type": "tushare"}]
        mock_manager._call_endpoint.return_value = mock_df

        fetcher = GovernanceDataFetcher()
        results = fetcher.fetch_batch_kline(
            symbols=["000001"],
            start_date="20240101",
            end_date="20240105",
            policy=RoutePolicy.SPECIFIC_SOURCE,
            source_id="tushare",
        )

        assert "000001" in results
        mock_manager.find_endpoints.assert_called_with(data_category="DAILY_KLINE", source_type="tushare")

    def test_fetch_batch_empty(self, mock_manager):
        # Test case where no endpoint is found
        mock_manager.get_best_endpoint.return_value = None

        fetcher = GovernanceDataFetcher()
        results = fetcher.fetch_batch_kline(symbols=["000001"], start_date="20240101", end_date="20240105")

        assert results == {}

    def test_fetch_batch_kline_uses_batch_processor_and_preserves_public_shape(self, mock_manager):
        mock_df = pd.DataFrame({"close": [10, 11, 12]})

        fetcher = GovernanceDataFetcher()

        with patch.object(
            fetcher.batch_processor,
            "fetch_batch_kline",
            return_value={
                "success": False,
                "data": {"000001": mock_df},
                "errors": {"000002": "boom"},
                "stats": {"failed": 1},
            },
        ) as mock_batch:
            results = fetcher.fetch_batch_kline(
                symbols=["000001", "000002"],
                start_date="20240101",
                end_date="20240105",
                policy=RoutePolicy.SMART_ROUTING,
            )

        assert results == {"000001": mock_df}
        mock_batch.assert_called_once()

    def test_shutdown_delegates_to_batch_processor(self, mock_manager):
        fetcher = GovernanceDataFetcher()

        with patch.object(fetcher.batch_processor, "shutdown") as mock_shutdown:
            fetcher.shutdown()

        mock_shutdown.assert_called_once_with(wait=True)

    def test_batch_path_reuses_manager_instance_without_cross_wiring(self, mock_manager):
        mock_manager.get_best_endpoint.return_value = {"endpoint_name": "mock_endpoint", "source_type": "mock"}

        def _build_dataframe(endpoint, symbol, start_date, end_date, adjust):
            return pd.DataFrame({"symbol": [symbol], "close": [10.0]})

        mock_manager._call_endpoint.side_effect = _build_dataframe

        fetcher = GovernanceDataFetcher()
        results = fetcher.fetch_batch_kline(
            symbols=["000001", "000002", "000003"],
            start_date="20240101",
            end_date="20240105",
            policy=RoutePolicy.SMART_ROUTING,
        )

        assert fetcher.manager is mock_manager
        assert set(results) == {"000001", "000002", "000003"}
        assert {frame.iloc[0]["symbol"] for frame in results.values()} == {"000001", "000002", "000003"}
        assert mock_manager.get_best_endpoint.call_count == 3
        assert {call.kwargs["symbol"] for call in mock_manager._call_endpoint.call_args_list} == {
            "000001",
            "000002",
            "000003",
        }
