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
    metrics = RiskCalculator.calculate_var_cvar(returns, 0.95)
    assert "var_95_hist" in metrics
    assert "cvar_95" in metrics

def test_risk_calculator_beta():
    asset = pd.Series([0.01, 0.02, -0.01])
    market = pd.Series([0.01, 0.01, -0.01])
    beta = RiskCalculator.calculate_beta(asset, market)
    assert isinstance(beta, float)

@pytest.mark.asyncio
async def test_risk_service_calculate_var_success():
    mock_manager = MagicMock()
    mock_manager.save_data_by_classification.return_value = True

    mock_db = MagicMock()

    service = RiskService(mock_manager, mock_db)

    result = await service.calculate_var_cvar_logic({
        "entity_type": "portfolio",
        "entity_id": 101,
        "confidence_level": 0.95,
    })

    assert result is not None
    assert "var_95_hist" in result or "entity_id" in result

@pytest.mark.asyncio
async def test_risk_service_calculate_beta_success():
    """Test beta calculation via RiskCalculator static method"""
    asset_returns = pd.Series([0.01, 0.02, -0.01, 0.03, -0.02])
    market_returns = pd.Series([0.01, 0.01, -0.01, 0.02, -0.01])

    beta = RiskCalculator.calculate_beta(asset_returns, market_returns)

    assert beta is not None
    assert isinstance(beta, float)
    assert beta > 0  # positive correlation expected
