from __future__ import annotations

import asyncio
import importlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def _load_module():
    sys.modules.pop("app.api.risk.stop_loss", None)
    return importlib.import_module("app.api.risk.stop_loss")


def test_calculate_stop_loss_v31_rejects_missing_symbol(monkeypatch):
    module = _load_module()

    class FakeEngine:
        async def calculate_volatility_stop_loss(self, **kwargs):
            return {"unexpected": kwargs}

    class FakeCore:
        stop_loss_engine = FakeEngine()

    monkeypatch.setattr(module, "RISK_MANAGEMENT_V31_AVAILABLE", True)
    monkeypatch.setattr(module, "get_risk_management_core", lambda: FakeCore())

    try:
        asyncio.run(module.calculate_stop_loss_v31({"strategy_type": "volatility_adaptive", "entry_price": 1688.0}))
    except module.ValidationException as exc:
        assert exc.status_code == 422
        assert "symbol" in str(exc.detail)
    else:
        raise AssertionError("expected ValidationException when symbol is missing")


def test_calculate_stop_loss_v31_rejects_missing_entry_price(monkeypatch):
    module = _load_module()

    class FakeEngine:
        async def calculate_volatility_stop_loss(self, **kwargs):
            return {"unexpected": kwargs}

    class FakeCore:
        stop_loss_engine = FakeEngine()

    monkeypatch.setattr(module, "RISK_MANAGEMENT_V31_AVAILABLE", True)
    monkeypatch.setattr(module, "get_risk_management_core", lambda: FakeCore())

    try:
        asyncio.run(module.calculate_stop_loss_v31({"strategy_type": "volatility_adaptive", "symbol": "600519.SH"}))
    except module.ValidationException as exc:
        assert exc.status_code == 422
        assert "entry_price" in str(exc.detail)
    else:
        raise AssertionError("expected ValidationException when entry_price is missing")
