from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from app.api import tradingview as module


def test_tradingview_route_source_contains_no_direct_use_mock_env_reads():
    source = Path(module.__file__).read_text(encoding="utf-8")

    assert 'os.getenv("USE_MOCK_DATA"' not in source


@pytest.mark.asyncio
async def test_convert_symbol_uses_mock_only_when_config_enabled(monkeypatch):
    monkeypatch.setattr(module.settings, "use_mock_apis", True, raising=False)
    monkeypatch.setattr(module, "_get_mock_tradingview_symbol", lambda symbol, market: f"{market}:{symbol}")

    result = await module.convert_symbol(
        symbol="600519",
        market="SSE",
        current_user=SimpleNamespace(id=1, username="tester"),
    )

    assert result["success"] is True
    assert result["tradingview_symbol"] == "SSE:600519"


@pytest.mark.asyncio
async def test_convert_symbol_uses_real_service_when_mock_disabled(monkeypatch):
    monkeypatch.setattr(module.settings, "use_mock_apis", False, raising=False)

    class _ServiceStub:
        @staticmethod
        def convert_symbol_to_tradingview_format(symbol: str, market: str) -> str:
            return f"{market}:{symbol}"

    monkeypatch.setattr(module, "get_tradingview_service", lambda: _ServiceStub())

    result = await module.convert_symbol(
        symbol="0700",
        market="HKEX",
        current_user=SimpleNamespace(id=1, username="tester"),
    )

    assert result["success"] is True
    assert result["tradingview_symbol"] == "HKEX:0700"
