import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import pandas as pd
import numpy as np
import sys
import os

# Add web/backend to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../web/backend")))

from app.api.risk_management_core import RiskCalculator, RiskService
from app.core.exceptions import BusinessException

def test_risk_calculator_var():
    returns = pd.Series([-0.01, -0.02, 0.01, 0.02, -0.05])
    metrics = RiskCalculator.calculate_all(returns, 0.95)
    assert "var_95_hist" in metrics
    assert "cvar_95" in metrics

def test_risk_calculator_beta():
    asset = pd.Series([0.01, 0.02, -0.01])
    market = pd.Series([0.01, 0.01, -0.01])
    beta = RiskCalculator.beta(asset, market)
    assert isinstance(beta, float)

@pytest.mark.asyncio
async def test_risk_service_calculate_var_success():
    mock_manager = MagicMock()
    mock_manager.save_data_by_classification.return_value = True
    
    mock_db = MagicMock()
    
    mock_factory = MagicMock()
    mock_source = MagicMock()
    mock_source.get_kline_data.return_value = pd.DataFrame({"close": [1, 2, 3]})
    mock_factory.return_value = mock_source
    
    result = await RiskService.calculate_var_cvar_logic(
        "portfolio", 101, 0.95, mock_manager, mock_db, mock_factory
    )
    
    assert result.entity_id == 101
    assert result.cvar_95 is not None
    mock_manager.save_data_by_classification.assert_called_once()

@pytest.mark.asyncio
async def test_risk_service_calculate_beta_success():
    mock_manager = MagicMock()
    mock_manager.save_data_by_classification.return_value = True
    
    mock_db = MagicMock()
    
    mock_factory = MagicMock()
    mock_source = MagicMock()
    # Need >1 data points
    mock_source.get_kline_data.return_value = pd.DataFrame({"close": [1, 2, 3]})
    mock_factory.return_value = mock_source
    
    result = await RiskService.calculate_beta_logic(
        "portfolio", 101, "000001", mock_manager, mock_db, mock_factory
    )
    
    assert result.beta is not None
    mock_manager.save_data_by_classification.assert_called_once()
