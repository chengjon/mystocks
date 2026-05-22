from __future__ import annotations

import pytest

from app.services import watchlist_service
from app.services.adapters.watchlist_adapter import (
    WatchlistDataSourceAdapter as LegacyWatchlistDataSourceAdapter,
)
from app.services.data_adapters.watchlist import (
    WatchlistDataSourceAdapter as DataWatchlistDataSourceAdapter,
)


@pytest.mark.parametrize(
    "adapter_cls",
    [
        DataWatchlistDataSourceAdapter,
        LegacyWatchlistDataSourceAdapter,
    ],
)
def test_watchlist_adapters_use_injected_provider_in_live_mode(monkeypatch, adapter_cls):
    fake_service = object()
    provider_calls = 0

    def fail_global_getter():
        raise AssertionError("global watchlist getter should not be called")

    def provider():
        nonlocal provider_calls
        provider_calls += 1
        return fake_service

    monkeypatch.setattr(watchlist_service, "get_watchlist_service", fail_global_getter)

    adapter = adapter_cls(
        {
            "mode": "live",
            "watchlist_service_provider": provider,
        }
    )

    assert adapter._get_watchlist_service() is fake_service
    assert adapter._get_watchlist_service() is fake_service
    assert provider_calls == 1


@pytest.mark.parametrize(
    "adapter_cls",
    [
        DataWatchlistDataSourceAdapter,
        LegacyWatchlistDataSourceAdapter,
    ],
)
def test_watchlist_adapters_allow_explicit_provider_in_mock_mode(adapter_cls):
    fake_service = object()

    adapter = adapter_cls(
        {
            "mode": "mock",
            "watchlist_service_provider": lambda: fake_service,
        }
    )

    assert adapter._get_watchlist_service() is fake_service


@pytest.mark.parametrize(
    "adapter_cls",
    [
        DataWatchlistDataSourceAdapter,
        LegacyWatchlistDataSourceAdapter,
    ],
)
def test_watchlist_adapters_preserve_mock_mode_without_provider(adapter_cls):
    adapter = adapter_cls({"mode": "mock"})

    assert adapter._get_watchlist_service() is None
