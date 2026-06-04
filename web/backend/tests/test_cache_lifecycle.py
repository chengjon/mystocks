from __future__ import annotations

import asyncio
import importlib
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class DummySyncManager:
    def __init__(self, tdengine_manager: Any | None = None) -> None:
        self.tdengine_manager = tdengine_manager
        self.closed = 0

    def close(self) -> None:
        self.closed += 1


class DummyAsyncManager:
    def __init__(self, sync_manager: DummySyncManager, redis_cache: Any | None = None) -> None:
        self.sync_manager = sync_manager
        self.redis_cache = redis_cache
        self.closed = 0

    def close(self) -> None:
        self.closed += 1
        self.sync_manager.close()


def test_provider_reuses_sync_manager_until_reset() -> None:
    from app.core.cache_lifecycle import CacheLifecycleProvider

    created: list[DummySyncManager] = []

    def create_sync(tdengine_manager: Any | None = None) -> DummySyncManager:
        manager = DummySyncManager(tdengine_manager)
        created.append(manager)
        return manager

    provider = CacheLifecycleProvider(sync_manager_factory=create_sync, async_manager_factory=DummyAsyncManager)

    first = provider.get_sync(tdengine_manager="tdengine-a")
    second = provider.get_sync(tdengine_manager="tdengine-b")

    assert first is second
    assert first.tdengine_manager == "tdengine-a"
    assert created == [first]


def test_provider_async_manager_shares_sync_backing_manager() -> None:
    from app.core.cache_lifecycle import CacheLifecycleProvider

    provider = CacheLifecycleProvider(
        sync_manager_factory=DummySyncManager,
        async_manager_factory=DummyAsyncManager,
    )

    async_manager = asyncio.run(provider.get_async(tdengine_manager="tdengine-a", redis_cache="redis-a"))
    second_async_manager = asyncio.run(provider.get_async(tdengine_manager="tdengine-b", redis_cache="redis-b"))
    sync_manager = provider.get_sync()

    assert async_manager is second_async_manager
    assert async_manager.sync_manager is sync_manager
    assert async_manager.redis_cache == "redis-a"
    assert sync_manager.tdengine_manager == "tdengine-a"


def test_provider_reset_closes_async_wrapper_and_recreates_state() -> None:
    from app.core.cache_lifecycle import CacheLifecycleProvider

    provider = CacheLifecycleProvider(
        sync_manager_factory=DummySyncManager,
        async_manager_factory=DummyAsyncManager,
    )
    async_manager = asyncio.run(provider.get_async())
    sync_manager = async_manager.sync_manager

    provider.reset()
    recreated_sync_manager = provider.get_sync()

    assert async_manager.closed == 1
    assert sync_manager.closed == 1
    assert recreated_sync_manager is not sync_manager


def test_provider_reset_closes_sync_manager_when_async_wrapper_was_never_created() -> None:
    from app.core.cache_lifecycle import CacheLifecycleProvider

    provider = CacheLifecycleProvider(
        sync_manager_factory=DummySyncManager,
        async_manager_factory=DummyAsyncManager,
    )
    sync_manager = provider.get_sync()

    provider.reset()

    assert sync_manager.closed == 1
    assert provider.get_sync() is not sync_manager


def test_cache_manager_public_getters_delegate_to_lifecycle_provider(monkeypatch) -> None:
    from app.core import cache_manager

    class ProviderStub:
        def __init__(self) -> None:
            self.sync = DummySyncManager()
            self.async_manager = DummyAsyncManager(self.sync)
            self.reset_called = False

        def get_sync(self) -> DummySyncManager:
            return self.sync

        async def get_async(
            self,
            tdengine_manager: Any | None = None,
            redis_cache: Any | None = None,
        ) -> DummyAsyncManager:
            self.async_manager.sync_manager.tdengine_manager = tdengine_manager
            self.async_manager.redis_cache = redis_cache
            return self.async_manager

        def reset(self) -> None:
            self.reset_called = True

    provider = ProviderStub()
    monkeypatch.setattr(cache_manager, "_cache_lifecycle_provider", provider, raising=False)

    assert cache_manager.get_cache_manager() is provider.sync
    assert asyncio.run(cache_manager.get_cache_manager_async(tdengine_manager="tdengine", redis_cache="redis")) is (
        provider.async_manager
    )

    cache_manager.reset_cache_manager()

    assert provider.reset_called is True


def test_stats_health_async_getter_delegates_to_canonical_cache_manager(monkeypatch) -> None:
    stats_health = importlib.import_module("app.core.cache.stats_health")
    from app.core import cache_manager

    sentinel = object()
    calls: list[tuple[object | None, object | None]] = []

    async def get_cache_manager_async(
        tdengine_manager: object | None = None,
        redis_cache: object | None = None,
    ) -> object:
        calls.append((tdengine_manager, redis_cache))
        return sentinel

    monkeypatch.setattr(cache_manager, "get_cache_manager_async", get_cache_manager_async)

    assert asyncio.run(stats_health.get_cache_manager_async(tdengine_manager="tdengine", redis_cache="redis")) is sentinel
    assert calls == [("tdengine", "redis")]


def test_package_cache_manager_still_includes_stats_health_mixin() -> None:
    cache_package = importlib.import_module("app.core.cache")
    stats_health = importlib.import_module("app.core.cache.stats_health")

    assert issubclass(cache_package.CacheManager, stats_health.CacheStatsHealthMixin)


def test_cache_factory_imports_as_compatibility_wrapper() -> None:
    factory = importlib.import_module("app.core.cache.factory")

    assert factory.__name__ == "app.core.cache.factory"


def test_cache_factory_getter_delegates_to_canonical_cache_manager(monkeypatch) -> None:
    factory = importlib.import_module("app.core.cache.factory")
    sentinel = object()
    calls: list[object | None] = []

    class ProviderStub:
        def get_sync(self, tdengine_manager: object | None = None) -> object:
            calls.append(tdengine_manager)
            return sentinel

    monkeypatch.setattr(factory.canonical_cache_manager, "_get_cache_lifecycle_provider", lambda: ProviderStub())

    assert factory.get_cache_manager(tdengine_manager="tdengine") is sentinel
    assert calls == ["tdengine"]


def test_cache_factory_reset_delegates_to_canonical_cache_manager(monkeypatch) -> None:
    factory = importlib.import_module("app.core.cache.factory")
    calls: list[str] = []

    def reset() -> None:
        calls.append("reset")

    monkeypatch.setattr(factory.canonical_cache_manager, "reset_cache_manager", reset)

    factory.reset_cache_manager()

    assert calls == ["reset"]
