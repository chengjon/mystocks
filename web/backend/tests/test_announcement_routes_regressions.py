from __future__ import annotations

import importlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def _load_module():
    sys.modules.pop("app.api.announcement.routes", None)
    return importlib.import_module("app.api.announcement.routes")


async def test_announcement_analyze_returns_unified_placeholder_response():
    module = _load_module()

    payload = await module.analyze_data(
        {
            "title": "2026年第一季度业绩预增公告",
            "stock_code": "600519",
            "analysis_mode": "summary",
        }
    )

    assert payload.success is False
    assert payload.code == 503
    assert payload.data == {
        "status": "placeholder",
        "endpoint": "announcement",
        "stock_code": "600519",
        "analysis_mode": "summary",
        "summary": None,
        "signals": [],
    }
