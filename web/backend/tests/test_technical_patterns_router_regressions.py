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


def test_detect_patterns_returns_unified_placeholder_response():
    module = _import_patterns_router_module()

    response = asyncio.run(module.detect_patterns(symbol="600519.SH", period="weekly"))

    assert response.success is False
    assert response.code == 503
    assert response.message
    assert response.data == {
        "status": "placeholder",
        "symbol": "600519.SH",
        "period": "weekly",
        "patterns": [],
    }
