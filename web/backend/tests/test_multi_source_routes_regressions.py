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


async def test_multi_source_analyze_returns_weighted_summary_response():
    module = _load_module()

    payload = await module.analyze_data(
        {
            "symbol": "600519",
            "data_sources": ["technical", "fundamental", "sentiment"],
            "analysis_depth": "advanced",
            "weights": {
                "technical": 0.3,
                "fundamental": 0.5,
                "sentiment": 0.2,
            },
        }
    )

    assert payload.success is True
    assert payload.code == 200
    assert payload.data == {
        "status": "available",
        "endpoint": "multi_source",
        "symbol": "600519",
        "analysis_depth": "advanced",
        "data_sources": ["technical", "fundamental", "sentiment"],
        "summary": "fundamental 面权重占优，综合结论偏多。",
        "insights": [
            "fundamental 权重最高，作为主判断来源。",
            "technical 与 fundamental 共同提供交叉确认。",
            "fundamental 子评分达到 84.0，对综合结果形成强化。",
        ],
        "scores": {
            "technical": 78.0,
            "fundamental": 84.0,
            "sentiment": 72.0,
        },
        "weights": {
            "technical": 0.3,
            "fundamental": 0.5,
            "sentiment": 0.2,
        },
        "comprehensive_score": 79.8,
        "recommendation": "buy",
        "confidence": 0.85,
    }
