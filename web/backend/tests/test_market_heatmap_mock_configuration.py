from __future__ import annotations

from pathlib import Path

import pytest

from app.api.market import _market_heatmap_router as module


def test_market_heatmap_route_source_contains_no_direct_use_mock_env_reads():
    source = Path(module.__file__).read_text(encoding="utf-8")

    assert 'os.getenv("USE_MOCK_DATA"' not in source


@pytest.mark.asyncio
async def test_market_heatmap_uses_mock_only_when_settings_enable_it(monkeypatch):
    monkeypatch.setattr(module.settings, "use_mock_apis", True, raising=False)
    monkeypatch.setattr(
        module,
        "_get_mock_market_heatmap",
        lambda market, limit: {
            "data": [{"symbol": "000001", "name": market, "change_pct": limit}],
            "timestamp": "2026-04-16T10:00:00",
        },
    )

    result = await module.get_market_heatmap(market="cn", limit=50)

    assert result["success"] is True
    assert result["source"] == "mock"
    assert result["data"][0]["symbol"] == "000001"
