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


async def test_announcement_analyze_returns_rule_based_response():
    module = _load_module()

    payload = await module.analyze_data(
        {
            "title": "2026年第一季度业绩预增公告",
            "stock_code": "600519",
            "content": "预计2026年第一季度归母净利润同比增长18%-22%。",
            "analysis_mode": "summary",
        }
    )

    assert payload.success is True
    assert payload.code == 200
    assert payload.data == {
        "status": "available",
        "endpoint": "announcement",
        "stock_code": "600519",
        "analysis_mode": "summary",
        "summary": "公告内容偏利多，核心信号集中在业绩增长预期。",
        "signals": ["earnings_growth", "positive_guidance"],
        "sentiment": "positive",
        "importance_level": 4,
    }
