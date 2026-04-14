from __future__ import annotations

import importlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def _load_module():
    sys.modules.pop("app.api.technical.routes", None)
    return importlib.import_module("app.api.technical.routes")


async def test_technical_analyze_returns_unified_placeholder_response():
    module = _load_module()

    payload = await module.analyze_data(
        {
            "symbol": "600519",
            "period": "daily",
            "model_type": "comprehensive",
            "indicators": {"ma5": 1850.5, "ma20": 1820.3},
        }
    )

    assert payload.success is False
    assert payload.code == 503
    assert payload.message == "Technical AI analysis is not implemented yet"
    assert payload.data == {
        "status": "placeholder",
        "endpoint": "technical",
        "symbol": "600519",
        "period": "daily",
        "model_type": "comprehensive",
        "summary": None,
        "signals": [],
        "patterns": [],
        "trend": None,
    }
