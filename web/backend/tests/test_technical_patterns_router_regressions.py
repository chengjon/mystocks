from __future__ import annotations

import asyncio
import importlib
import sys
from pathlib import Path


def _import_patterns_router_module():
    backend_root = Path("web/backend").resolve()
    backend_root_str = str(backend_root)
    if backend_root_str not in sys.path:
        sys.path.insert(0, backend_root_str)

    sys.modules.pop("app.api._technical_patterns_router", None)
    return importlib.import_module("app.api._technical_patterns_router")


def test_detect_patterns_returns_rule_based_pattern_response():
    module = _import_patterns_router_module()

    response = asyncio.run(module.detect_patterns(symbol="600519.SH", period="weekly"))

    assert response.success is True
    assert response.code == 200
    assert response.message
    assert response.data == {
        "status": "available",
        "symbol": "600519.SH",
        "period": "weekly",
        "patterns": ["primary_trend_channel", "breakout_setup", "volatility_expansion_watch"],
    }
