from __future__ import annotations

from threading import RLock
from typing import Any, Callable, Generic, TypeVar

SyncManagerT = TypeVar("SyncManagerT")
AsyncManagerT = TypeVar("AsyncManagerT")


class CacheLifecycleProvider(Generic[SyncManagerT, AsyncManagerT]):
    """Owns cache manager lifecycle while legacy getters remain compatibility wrappers."""

    def __init__(
        self,
        sync_manager_factory: Callable[..., SyncManagerT],
        async_manager_factory: Callable[..., AsyncManagerT],
    ) -> None:
        self._sync_manager_factory = sync_manager_factory
        self._async_manager_factory = async_manager_factory
        self._sync_manager: SyncManagerT | None = None
        self._async_manager: AsyncManagerT | None = None
        self._lock = RLock()

    def get_sync(self, tdengine_manager: Any | None = None) -> SyncManagerT:
        with self._lock:
            if self._sync_manager is None:
                self._sync_manager = self._sync_manager_factory(tdengine_manager=tdengine_manager)
            return self._sync_manager

    async def get_async(
        self,
        tdengine_manager: Any | None = None,
        redis_cache: Any | None = None,
    ) -> AsyncManagerT:
        with self._lock:
            sync_manager = self.get_sync(tdengine_manager=tdengine_manager)
            if self._async_manager is None:
                self._async_manager = self._async_manager_factory(sync_manager, redis_cache=redis_cache)
            return self._async_manager

    def reset(self) -> None:
        with self._lock:
            async_manager = self._async_manager
            sync_manager = self._sync_manager
            if async_manager is not None:
                close_async = getattr(async_manager, "close", None)
                if callable(close_async):
                    close_async()
            elif sync_manager is not None:
                close_sync = getattr(sync_manager, "close", None)
                if callable(close_sync):
                    close_sync()
            self._async_manager = None
            self._sync_manager = None
