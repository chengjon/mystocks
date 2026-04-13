from __future__ import annotations

import importlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def _load_module():
    sys.modules.pop("app.api.multi_source.routes", None)
    return importlib.import_module("app.api.multi_source.routes")


async def test_multi_source_analyze_returns_unified_placeholder_response():
    module = _load_module()

    payload = await module.analyze_data(
        {
            "symbol": "600519",
            "data_sources": ["technical", "fundamental", "sentiment"],
            "analysis_depth": "advanced",
        }
    )

    assert payload.success is False
    assert payload.code == 503
    assert payload.data == {
        "status": "placeholder",
        "endpoint": "multi_source",
        "symbol": "600519",
        "analysis_depth": "advanced",
        "data_sources": ["technical", "fundamental", "sentiment"],
        "summary": None,
        "insights": [],
    }
