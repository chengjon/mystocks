from __future__ import annotations

from pathlib import Path

import pytest

from app.services.data_adapters.strategy import StrategyDataSourceAdapter as StrategyAdapter
from app.services.data_adapters.watchlist import WatchlistDataSourceAdapter as WatchlistAdapter


@pytest.mark.asyncio
async def test_strategy_adapter_does_not_silently_fallback_when_disabled(monkeypatch):
    adapter = StrategyAdapter({"mode": "real", "fallback_enabled": False})

    monkeypatch.setattr(adapter, "_get_strategy_service", lambda: (_ for _ in ()).throw(RuntimeError("service down")))
    monkeypatch.setattr(adapter, "_get_mock_manager", lambda: object())
    monkeypatch.setattr(adapter, "_get_mock_strategy_data", lambda endpoint, params: {"success": True, "mock": True})

    with pytest.raises(RuntimeError, match="service down"):
        await adapter._fetch_strategy_data("definitions", {})


@pytest.mark.asyncio
async def test_strategy_adapter_allows_mock_fallback_when_enabled(monkeypatch):
    adapter = StrategyAdapter({"mode": "hybrid", "fallback_enabled": True})

    monkeypatch.setattr(adapter, "_get_strategy_service", lambda: (_ for _ in ()).throw(RuntimeError("service down")))
    monkeypatch.setattr(adapter, "_get_mock_manager", lambda: object())
    monkeypatch.setattr(adapter, "_get_mock_strategy_data", lambda endpoint, params: {"success": True, "mock": True})

    result = await adapter._fetch_strategy_data("definitions", {})

    assert result["mock"] is True


@pytest.mark.asyncio
async def test_watchlist_adapter_does_not_silently_fallback_when_disabled(monkeypatch):
    adapter = WatchlistAdapter({"mode": "real", "fallback_enabled": False})

    monkeypatch.setattr(adapter, "_get_watchlist_service", lambda: object())

    def _raise(*_args, **_kwargs):
        raise RuntimeError("watchlist failed")

    monkeypatch.setattr(adapter, "_get_mock_manager", lambda: object())
    monkeypatch.setattr(adapter, "_get_mock_watchlist_data", lambda endpoint, params: {"success": True, "mock": True})
    monkeypatch.setattr(adapter, "_get_watchlist_service", lambda: type("Svc", (), {"get_user_watchlist": _raise})())

    with pytest.raises(RuntimeError, match="watchlist failed"):
        await adapter._fetch_watchlist_data("list", {"user_id": 1})


@pytest.mark.asyncio
async def test_watchlist_adapter_allows_mock_fallback_when_enabled(monkeypatch):
    adapter = WatchlistAdapter({"mode": "hybrid", "fallback_enabled": True})

    def _raise(*_args, **_kwargs):
        raise RuntimeError("watchlist failed")

    monkeypatch.setattr(adapter, "_get_mock_manager", lambda: object())
    monkeypatch.setattr(adapter, "_get_mock_watchlist_data", lambda endpoint, params: {"success": True, "mock": True})
    monkeypatch.setattr(adapter, "_get_watchlist_service", lambda: type("Svc", (), {"get_user_watchlist": _raise})())

    result = await adapter._fetch_watchlist_data("list", {"user_id": 1})

    assert result["mock"] is True


@pytest.mark.parametrize(
    "path",
    [
        "web/backend/app/services/adapters/strategy_adapter.py",
        "web/backend/app/services/adapters/watchlist_adapter.py",
    ],
)
def test_legacy_adapter_sources_gate_mock_fallback_with_explicit_helper(path: str):
    source = Path(path).read_text(encoding="utf-8")

    assert "def _should_use_mock_fallback" in source
    assert "self._should_use_mock_fallback() and self._get_mock_manager()" in source
