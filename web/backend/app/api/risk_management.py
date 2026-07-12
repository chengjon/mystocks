"""Compatibility shim for risk_management.py (was 2,112 lines).

Split into:
  risk/metrics.py   - VaR/CVaR, Beta, Dashboard, calculation
  risk/stop_loss.py - Stop-loss position management
  risk/alerts.py    - Alert CRUD, rules, notifications
  risk/v31.py       - V3.1 stock/portfolio risk, WebSocket

Remove after deprecation period (4-8 weeks).
"""

import logging
import warnings

from fastapi import APIRouter


logger = logging.getLogger(__name__)

try:
    from app.api.risk import router as _risk_router
except Exception as exc:  # pylint: disable=broad-exception-caught
    # Keep unrelated API startup paths alive when optional risk/GPU imports fail.
    logger.warning("Risk API unavailable during startup, falling back to empty compatibility router: %s", exc)
    router = APIRouter()
else:
    router = _risk_router

warnings.warn(
    "app.api.risk_management is deprecated. "
    "Use app.api.risk instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["router"]
