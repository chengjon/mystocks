from __future__ import annotations

import asyncio

import pytest

from src.monitoring.infrastructure import postgresql_async_v3 as postgres_module
from src.monitoring.infrastructure.postgresql_async_v3 import (
    close_postgres_async,
    get_postgres_async,
    initialize_postgres_async,
    reset_postgres_async_provider,
    set_postgres_async_provider,
)


class FakePostgresAsync:
    def __init__(self) -> None:
        self.initialized = False
        self.closed = False

    async def initialize(self) -> None:
        self.initialized = True

    async def close(self) -> None:
        self.closed = True


@pytest.fixture(autouse=True)
def reset_provider_state():
    reset_postgres_async_provider()
    yield
    reset_postgres_async_provider()


def test_get_postgres_async_uses_explicit_provider():
    fake = FakePostgresAsync()
    calls = 0

    def provider() -> FakePostgresAsync:
        nonlocal calls
        calls += 1
        return fake

    set_postgres_async_provider(provider)

    assert get_postgres_async() is fake
    assert get_postgres_async() is fake
    assert calls == 2


def test_reset_postgres_async_provider_restores_lazy_singleton(monkeypatch):
    set_postgres_async_provider(FakePostgresAsync)
    assert isinstance(get_postgres_async(), FakePostgresAsync)

    created: list[FakePostgresAsync] = []

    class ReplacementPostgresAsync(FakePostgresAsync):
        def __init__(self) -> None:
            super().__init__()
            created.append(self)

    monkeypatch.setattr(postgres_module, "MonitoringPostgreSQLAccess", ReplacementPostgresAsync)

    reset_postgres_async_provider()

    first = get_postgres_async()
    second = get_postgres_async()

    assert isinstance(first, ReplacementPostgresAsync)
    assert first is second
    assert created == [first]


def test_lifecycle_helpers_use_explicit_provider():
    fake = FakePostgresAsync()
    set_postgres_async_provider(lambda: fake)

    assert asyncio.run(initialize_postgres_async()) is True
    asyncio.run(close_postgres_async())

    assert fake.initialized is True
    assert fake.closed is True
