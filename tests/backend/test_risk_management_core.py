import sys
import os

# Add web/backend to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../web/backend")))

from app.services.risk_management.risk_base import RiskBase
from app.services.risk_management_new import RiskManagementService

def test_risk_calculator_var():
    returns = [-0.01, -0.02, 0.01, 0.02, -0.05]
    risk_base = RiskBase()
    metrics = {
        "var": risk_base.calculate_var(returns),
        "cvar": risk_base.calculate_cvar(returns, 0.95),
    }
    assert isinstance(metrics["var"], float)
    assert isinstance(metrics["cvar"], float)
    assert metrics["var"] >= 0
    assert metrics["cvar"] >= 0

def test_risk_calculator_adjusted_var():
    returns = [0.01, 0.02, -0.01]
    adjusted_var = RiskBase().calculate_var_with_return(returns, risk_free_rate=0.01)
    assert isinstance(adjusted_var, float)
    assert adjusted_var >= 0

def test_risk_service_calculate_var_success():
    service = RiskManagementService()
    result = service.calculate_var([0.01, -0.02, 0.03, -0.01])
    assert isinstance(result, float)
    assert result >= 0

def test_risk_service_calculate_adjusted_var_success():
    service = RiskManagementService()
    adjusted_var = service.calculate_var_with_return([0.01, 0.02, -0.01, 0.03, -0.02], risk_free_rate=0.01)
    assert isinstance(adjusted_var, float)
    assert adjusted_var >= 0
