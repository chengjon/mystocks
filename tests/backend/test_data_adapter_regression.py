import pytest
from unittest.mock import MagicMock, patch

import sys
import os

# Add web/backend to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../web/backend")))

from app.services.data_adapter import (
    DataDataSourceAdapter,
    DashboardDataSourceAdapter,
    TechnicalAnalysisDataSourceAdapter,
    StrategyDataSourceAdapter,
    WatchlistDataSourceAdapter
)

@pytest.fixture
def mock_db_service():
    with patch("app.services.adapters.data_adapter.db_service") as mock:
        yield mock

@pytest.fixture
def mock_akshare():
    with patch("utils.data_format_converter.get_akshare_adapter") as mock:
        yield mock

# --- DataDataSourceAdapter Tests ---

@pytest.mark.asyncio
async def test_data_adapter_stocks_basic(mock_db_service):
    adapter = DataDataSourceAdapter({"name": "test"})

    # Mock db response
    import pandas as pd
    mock_df = pd.DataFrame([{"symbol": "000001", "name": "PingAn", "price": 10.0}])
    mock_db_service.query_stocks_basic.return_value = mock_df

    result = await adapter.get_data("stocks/basic", {"limit": 10})

    assert result["status"] == "success"
    assert len(result["data"]) == 1
    assert result["data"][0]["symbol"] == "000001"

@pytest.mark.asyncio
async def test_data_adapter_stocks_daily(mock_db_service):
    adapter = DataDataSourceAdapter({"name": "test"})

    import pandas as pd
    mock_df = pd.DataFrame([{"date": "2023-01-01", "open": 10, "close": 11}])
    mock_db_service.query_daily_kline.return_value = mock_df

    result = await adapter.get_data("stocks/daily", {"symbol": "000001"})

    assert result["status"] == "success"
    assert len(result["data"]) == 1

# --- DashboardDataSourceAdapter Tests ---

@pytest.mark.asyncio
async def test_dashboard_adapter_summary():
    adapter = DashboardDataSourceAdapter({"name": "test"})

    result = await adapter.get_data("summary", {"user_id": 1})

    assert result["status"] == "success"
    assert "summary" in result["data"]
    assert "market_overview" in result["data"]

# --- TechnicalAnalysisDataSourceAdapter Tests ---

@pytest.mark.asyncio
async def test_technical_adapter_indicators():
    adapter = TechnicalAnalysisDataSourceAdapter({"name": "test"})

    # Mock internal service
    with patch.object(adapter, "_get_technical_service") as mock_service_getter:
        mock_service = MagicMock()
        mock_service_getter.return_value = mock_service

        # Mock calculate_all_indicators
        mock_service.calculate_all_indicators.return_value = {"rsi": 50, "macd": 0.1}

        result = await adapter.get_data("indicators", {"symbol": "000001"})

        assert result["success"] is True
        assert result["data"]["rsi"] == 50


@pytest.mark.asyncio
async def test_technical_adapter_indicators_falls_back_to_mock_when_real_returns_error():
    adapter = TechnicalAnalysisDataSourceAdapter({"name": "test", "fallback_enabled": True})

    with (
        patch.object(adapter, "_get_technical_service") as mock_service_getter,
        patch.object(adapter, "_get_mock_manager") as mock_mock_manager_getter,
    ):
        mock_service = MagicMock()
        mock_service_getter.return_value = mock_service
        mock_service.calculate_all_indicators.return_value = {"error": "No data available"}

        mock_manager = MagicMock()
        mock_manager.get_data.return_value = {
            "indicators": {
                "trend": {"ma5": 10.5},
                "momentum": {"rsi6": 65.5},
                "volatility": {"bb_upper": 12.5},
                "volume": {"obv": 1250000},
            },
            "signals": {"overall_signal": "hold"},
        }
        mock_mock_manager_getter.return_value = mock_manager

        result = await adapter.get_data("indicators", {"symbol": "000001"})

        assert result["success"] is True
        assert result["data"]["trend"]["ma5"] == 10.5
        mock_manager.get_data.assert_called_once_with("technical", symbol="000001")


@pytest.mark.asyncio
async def test_technical_adapter_signals_falls_back_to_mock_when_real_returns_error():
    adapter = TechnicalAnalysisDataSourceAdapter({"name": "test", "fallback_enabled": True})

    with (
        patch.object(adapter, "_get_trading_signals", return_value={"error": "Insufficient data"}),
        patch.object(adapter, "_get_mock_manager") as mock_mock_manager_getter,
    ):
        mock_manager = MagicMock()
        mock_manager.get_data.return_value = {
            "indicators": {},
            "signals": {"overall_signal": "hold", "signal_strength": 0.5, "signals": []},
        }
        mock_mock_manager_getter.return_value = mock_manager

        result = await adapter.get_data("signals", {"symbol": "000001"})

        assert result["success"] is True
        assert result["data"]["overall_signal"] == "hold"
        mock_manager.get_data.assert_called_once_with("technical", symbol="000001")


@pytest.mark.asyncio
async def test_technical_adapter_falls_back_to_mock_when_service_init_fails():
    adapter = TechnicalAnalysisDataSourceAdapter({"name": "test", "fallback_enabled": True})

    with (
        patch.object(
            adapter,
            "_get_technical_service",
            side_effect=RuntimeError("technical service boot failed"),
        ),
        patch.object(adapter, "_get_mock_manager") as mock_mock_manager_getter,
    ):
        mock_manager = MagicMock()
        mock_manager.get_data.return_value = {
            "indicators": {
                "trend": {"ma5": 10.5},
                "momentum": {"rsi6": 65.5},
                "volatility": {"bb_upper": 12.5},
                "volume": {"obv": 1250000},
            },
            "signals": {"overall_signal": "hold", "signal_strength": 0.5, "signals": []},
        }
        mock_mock_manager_getter.return_value = mock_manager

        result = await adapter.get_data("signals", {"symbol": "000001"})

        assert result["success"] is True
        assert result["data"]["overall_signal"] == "hold"
        mock_manager.get_data.assert_called_once_with("technical", symbol="000001")

# --- StrategyDataSourceAdapter Tests ---

@pytest.mark.asyncio
async def test_strategy_adapter_definitions():
    adapter = StrategyDataSourceAdapter({"name": "test"})

    # Mock internal service
    with patch.object(adapter, "_get_strategy_service") as mock_service_getter:
        mock_service = MagicMock()
        mock_service_getter.return_value = mock_service

        mock_service.get_strategy_definitions.return_value = [{"code": "s1", "name": "Strategy 1"}]

        result = await adapter.get_data("definitions")

        assert result["success"] is True
        assert len(result["data"]) == 1
        assert result["data"][0]["code"] == "s1"

# --- WatchlistDataSourceAdapter Tests ---

@pytest.mark.asyncio
async def test_watchlist_adapter_list():
    adapter = WatchlistDataSourceAdapter({"name": "test", "mode": "real"}) # Force real mode to test service mocking

    with patch.object(adapter, "_get_watchlist_service") as mock_service_getter:
        mock_service = MagicMock()
        mock_service_getter.return_value = mock_service

        mock_service.get_user_watchlist.return_value = [{"symbol": "000001"}]

        result = await adapter.get_data("list", {"user_id": 1})

        assert result["success"] is True
        assert len(result["data"]) == 1
        assert result["data"][0]["symbol"] == "000001"
