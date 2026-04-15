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


async def test_technical_analyze_returns_rule_based_analysis_response():
    module = _load_module()

    payload = await module.analyze_data(
        {
            "symbol": "600519",
            "period": "daily",
            "model_type": "comprehensive",
            "indicators": {"ma5": 1850.5, "ma20": 1820.3, "macd": 12.3, "rsi": 65.5},
        }
    )

    assert payload.success is True
    assert payload.code == 200
    assert payload.message == "Technical analysis completed from provided indicators"
    assert payload.data == {
        "status": "available",
        "endpoint": "technical",
        "symbol": "600519",
        "period": "daily",
        "model_type": "comprehensive",
        "summary": "短期趋势强于中期趋势，指标组合偏多头。",
        "signals": ["ma_bullish_cross", "macd_positive", "rsi_neutral"],
        "patterns": ["trend_following_setup"],
        "trend": "bullish",
        "confidence": 0.8,
    }
