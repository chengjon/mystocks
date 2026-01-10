
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from src.governance.core.fetcher_bridge import GovernanceDataFetcher, RoutePolicy, TimeFrame

class TestGovernanceDataFetcher:
    
    @pytest.fixture
    def mock_manager(self):
        with patch('src.governance.core.fetcher_bridge.DataSourceManagerV2') as MockManager:
            manager_instance = MockManager.return_value
            yield manager_instance

    def test_initialization(self, mock_manager):
        fetcher = GovernanceDataFetcher()
        assert fetcher.manager is not None

    def test_fetch_batch_kline_smart(self, mock_manager):
        # Setup mock return
        mock_df = pd.DataFrame({'close': [10, 11, 12]})
        mock_manager.get_best_endpoint.return_value = {'endpoint_name': 'mock_endpoint', 'source_type': 'mock'}
        mock_manager._call_endpoint.return_value = mock_df
        
        fetcher = GovernanceDataFetcher()
        results = fetcher.fetch_batch_kline(
            symbols=["000001"], 
            start_date="20240101", 
            end_date="20240105",
            policy=RoutePolicy.SMART_ROUTING
        )
        
        assert "000001" in results
        assert not results["000001"].empty
        mock_manager.get_best_endpoint.assert_called_with("DAILY_KLINE")
        mock_manager._call_endpoint.assert_called()

    def test_fetch_batch_kline_specific(self, mock_manager):
        # Setup mock
        mock_df = pd.DataFrame({'close': [10, 11, 12]})
        mock_manager.find_endpoints.return_value = [{'endpoint_name': 'specific_endpoint', 'source_type': 'tushare'}]
        mock_manager._call_endpoint.return_value = mock_df
        
        fetcher = GovernanceDataFetcher()
        results = fetcher.fetch_batch_kline(
            symbols=["000001"], 
            start_date="20240101", 
            end_date="20240105",
            policy=RoutePolicy.SPECIFIC_SOURCE,
            source_id="tushare"
        )
        
        assert "000001" in results
        mock_manager.find_endpoints.assert_called_with(data_category="DAILY_KLINE", source_type="tushare")

    def test_fetch_batch_empty(self, mock_manager):
        # Test case where no endpoint is found
        mock_manager.get_best_endpoint.return_value = None
        
        fetcher = GovernanceDataFetcher()
        results = fetcher.fetch_batch_kline(
            symbols=["000001"], 
            start_date="20240101", 
            end_date="20240105"
        )
        
        assert results == {}
