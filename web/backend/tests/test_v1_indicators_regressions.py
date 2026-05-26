from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pandas as pd
import pytest

from app.core.exceptions import BusinessException


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


class _FakeDataService:
    def get_daily_ohlcv(self, symbol: str, start_date, end_date):
        dates = pd.date_range("2026-01-01", periods=80, freq="D")
        frame = pd.DataFrame(
            {
                "trade_date": dates,
                "open": [100 + i * 0.4 for i in range(80)],
                "high": [101 + i * 0.4 for i in range(80)],
                "low": [99 + i * 0.4 for i in range(80)],
                "close": [100 + i * 0.5 for i in range(80)],
                "volume": [1000 + i * 10 for i in range(80)],
            }
        )
        return frame, {}


def _load_module():
    sys.modules.pop("app.api.v1.strategy.indicators", None)
    return importlib.import_module("app.api.v1.strategy.indicators")


async def test_v1_indicators_returns_runtime_indicator_values():
    module = _load_module()
    module.get_data_service = lambda: _FakeDataService()

    payload = await module.get_technical_indicators("IF9999.CCFX", ["rsi", "macd", "sma", "ema"], 14)

    assert payload.success is True
    assert payload.code == 200
    assert payload.data["symbol"] == "IF9999.CCFX"
    assert payload.data["data_points"] == 80
    assert set(payload.data["indicators"].keys()) == {"rsi", "macd", "sma", "ema"}
    assert payload.data["indicators"]["rsi"]["value"] is not None
    assert payload.data["indicators"]["macd"]["macd"] is not None
    assert payload.data["indicators"]["sma"]["signal"] == "bullish"
    assert payload.data["indicators"]["ema"]["signal"] == "bullish"


async def test_v1_indicators_rejects_unsupported_indicator():
    module = _load_module()
    module.get_data_service = lambda: _FakeDataService()

    with pytest.raises(BusinessException) as exc_info:
        await module.get_technical_indicators("IF9999.CCFX", ["bollinger"], 14)

    assert exc_info.value.status_code == 400
    assert "Unsupported indicators" in exc_info.value.detail
