"""
Compatibility shim for risk_management.py (was 2,112 lines).

Split into:
  risk/metrics.py   - VaR/CVaR, Beta, Dashboard, calculation
  risk/stop_loss.py - Stop-loss position management
  risk/alerts.py    - Alert CRUD, rules, notifications
  risk/v31.py       - V3.1 stock/portfolio risk, WebSocket

Remove after deprecation period (4-8 weeks).
"""

import warnings

from app.api.risk import router  # noqa: F401

warnings.warn(
    "app.api.risk_management is deprecated. "
    "Use app.api.risk instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["router"]
