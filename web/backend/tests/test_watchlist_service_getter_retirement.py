from __future__ import annotations

import inspect
from types import SimpleNamespace

from app.services import watchlist_service
from app.services.adapters.watchlist_adapter import (
    WatchlistDataSourceAdapter as LegacyWatchlistDataSourceAdapter,
)
from app.services.data_adapters.watchlist import (
    WatchlistDataSourceAdapter as DataWatchlistDataSourceAdapter,
)


def test_watchlist_service_module_getter_and_singleton_are_retired():
    assert not hasattr(watchlist_service, "get_watchlist_service")
    assert not hasattr(watchlist_service, "_watchlist_service")
    assert hasattr(watchlist_service, "WatchlistService")
    assert hasattr(watchlist_service, "install_watchlist_service")
    assert hasattr(watchlist_service, "get_watchlist_service_dependency")


def test_watchlist_service_dependency_installs_constructed_service(monkeypatch):
    fake_service = object()
    fake_app = SimpleNamespace(state=SimpleNamespace())
    request = SimpleNamespace(app=fake_app)

    monkeypatch.setattr(watchlist_service, "WatchlistService", lambda: fake_service)

    assert watchlist_service.get_watchlist_service_dependency(request) is fake_service
    assert getattr(fake_app.state, watchlist_service.WATCHLIST_SERVICE_STATE_KEY) is fake_service


def test_watchlist_adapters_do_not_import_retired_getter():
    for adapter_cls in [DataWatchlistDataSourceAdapter, LegacyWatchlistDataSourceAdapter]:
        source = inspect.getsource(adapter_cls._get_watchlist_service)
        assert "import get_watchlist_service" not in source
        assert "get_watchlist_service()" not in source
