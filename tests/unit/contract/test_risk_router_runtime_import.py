from __future__ import annotations

import importlib
import logging
import sys
import warnings
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = PROJECT_ROOT / "web/backend"

# Keep the repository root ahead of web/backend so `src` resolves to the
# primary source tree instead of the legacy duplicate under `web/backend/src`.
sys.path = [entry for entry in sys.path if entry not in {str(PROJECT_ROOT), str(BACKEND_ROOT)}]
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(1, str(BACKEND_ROOT))


def test_risk_management_compat_router_uses_runtime_risk_routes(caplog) -> None:
    for module_name in [
        "app",
        "app.api",
        "app.api.risk_management",
        "app.api.risk",
        "app.api.risk.metrics",
        "app.api.risk.stop_loss",
        "app.api.risk.alerts",
        "app.api.risk.v31",
        "app.api.risk._shared",
    ]:
        sys.modules.pop(module_name, None)

    with caplog.at_level(logging.WARNING, logger="app.api.risk_management"):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            risk_management = importlib.import_module("app.api.risk_management")

    assert risk_management.router.routes
    assert not any(
        "falling back to empty compatibility router" in record.message
        for record in caplog.records
    )


def test_app_main_registers_canonical_risk_router_without_loading_compat_shim() -> None:
    for module_name in [
        "app",
        "app.api",
        "app.main",
        "app.router_registry",
        "app.api.risk_management",
        "app.api.risk",
        "app.api.risk.metrics",
        "app.api.risk.stop_loss",
        "app.api.risk.alerts",
        "app.api.risk.v31",
        "app.api.risk._shared",
    ]:
        sys.modules.pop(module_name, None)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        importlib.import_module("app.main")

    assert "app.api.risk" in sys.modules
    assert "app.api.risk_management" not in sys.modules
