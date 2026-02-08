import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, AsyncMock
import pandas as pd
import numpy as np
from datetime import datetime, date
import sys
import os

# Add web/backend to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../web/backend")))

# Import the router
try:
    from app.api.risk_management import router
    from fastapi import FastAPI
except ImportError as e:
    print(f"Import Error: {e}")
    raise

app = FastAPI()
app.include_router(router)

client = TestClient(app)

@pytest.fixture
def mock_unified_manager():
    with patch("app.api.risk_management.MyStocksUnifiedManager") as mock:
        manager_instance = MagicMock()
        mock.return_value = manager_instance
        yield manager_instance

@pytest.fixture
def mock_monitoring_db():
    with patch("app.utils.risk_utils.MonitoringDatabase") as mock:
        db_instance = MagicMock()
        mock.return_value = db_instance
        yield db_instance

@pytest.fixture
def mock_timeseries_source_factory():
    with patch("src.data_sources.factory.get_timeseries_source") as mock: 
        source_instance = MagicMock()
        mock.return_value = source_instance
        yield mock

# --- Tests for /var-cvar ---

def test_calculate_var_cvar_success(mock_unified_manager, mock_timeseries_source_factory):
    """Test successful calculation of VaR/CVaR."""
    mock_unified_manager.save_data_by_classification.return_value = True
    
    mock_source = MagicMock()
    mock_timeseries_source_factory.return_value = mock_source
    
    dates = pd.date_range(start="2025-01-01", periods=100)
    df = pd.DataFrame({"close": np.random.uniform(10, 20, 100)}, index=dates)
    mock_source.get_kline_data.return_value = df

    payload = {"entity_type": "portfolio", "entity_id": 101, "confidence_level": 0.95}
    response = client.post("/api/v1/risk/var-cvar", json=payload)
    
    assert response.status_code == 200
    assert response.json()["entity_id"] == 101

def test_calculate_var_cvar_failure(mock_unified_manager, mock_timeseries_source_factory):
    """Test failure when calculation or save fails."""
    mock_unified_manager.save_data_by_classification.return_value = False
    
    mock_source = MagicMock()
    mock_timeseries_source_factory.return_value = mock_source
    mock_source.get_kline_data.return_value = pd.DataFrame({"close": [1, 2]})

    payload = {"entity_type": "portfolio", "entity_id": 101, "confidence_level": 0.95}
    response = client.post("/api/v1/risk/var-cvar", json=payload)
    assert response.status_code == 500

# --- Tests for /beta ---

def test_calculate_beta_success(mock_unified_manager, mock_timeseries_source_factory):
    """Test successful calculation of Beta."""
    mock_unified_manager.save_data_by_classification.return_value = True
    
    mock_source = MagicMock()
    mock_timeseries_source_factory.return_value = mock_source
    mock_source.get_kline_data.return_value = pd.DataFrame({"close": np.random.uniform(10, 20, 100)})

    payload = {"entity_type": "portfolio", "entity_id": 101, "market_index": "000001"}
    response = client.post("/api/v1/risk/beta", json=payload)
    
    assert response.status_code == 200
    assert "beta" in response.json()

# --- Tests for /dashboard ---

def test_get_dashboard(mock_unified_manager):
    """Test dashboard data retrieval."""
    metrics_data = [{"metric_date": pd.Timestamp.now().normalize(), "var_95_hist": 0.05, "cvar_95": 0.07, "beta": 1.2}]
    mock_metrics = pd.DataFrame(metrics_data)
    
    mock_alerts = pd.DataFrame([{"id": 1, "name": "Test Alert", "metric_type": "price", "threshold_value": 100, "is_active": True}])
    
    mock_unified_manager.load_data_by_classification.side_effect = [mock_metrics, mock_alerts, mock_metrics]
    
    response = client.get("/api/v1/risk/dashboard")
    assert response.status_code == 200

# --- V3.1 Tests ---

def test_v31_stop_loss_calculate():
    """Test V3.1 stop loss calculation."""
    with patch("app.api.risk_v31.stop_loss.get_risk_management_core") as mock_get_core:
        core = MagicMock()
        mock_get_core.return_value = core
        
        mock_engine = MagicMock()
        core.stop_loss_engine = mock_engine
        mock_engine.calculate_volatility_stop_loss = AsyncMock(return_value={"stop_price": 95.0, "type": "volatility"})
        
        payload = {"strategy_type": "volatility_adaptive", "symbol": "sh600000", "entry_price": 100.0, "k_factor": 2.0}
        
        with patch("app.api.risk_v31.stop_loss.RISK_MANAGEMENT_V31_AVAILABLE", True):
            response = client.post("/api/v1/risk/v31/stop-loss/calculate", json=payload)
            
            assert response.status_code == 200
            assert response.json()["data"]["stop_price"] == 95.0