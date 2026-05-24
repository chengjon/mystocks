from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.services.data_source_factory import data_source_factory as data_source_factory_module


@pytest.mark.asyncio
async def test_install_data_source_factory_accepts_explicit_factory():
    fake_factory = object()
    fake_app = SimpleNamespace(state=SimpleNamespace())

    result = await data_source_factory_module.install_data_source_factory(fake_app, fake_factory)

    assert result is fake_factory
    assert getattr(fake_app.state, data_source_factory_module.DATA_SOURCE_FACTORY_STATE_KEY) is fake_factory


@pytest.mark.asyncio
async def test_data_source_factory_dependency_returns_installed_factory(monkeypatch):
    fake_factory = object()
    fake_app = SimpleNamespace(state=SimpleNamespace())
    setattr(fake_app.state, data_source_factory_module.DATA_SOURCE_FACTORY_STATE_KEY, fake_factory)
    request = SimpleNamespace(app=fake_app)

    async def unexpected_fallback():
        raise AssertionError("fallback getter should not run when app-state factory is installed")

    monkeypatch.setattr(data_source_factory_module, "get_data_source_factory", unexpected_fallback)

    result = await data_source_factory_module.get_data_source_factory_dependency(request)

    assert result is fake_factory


@pytest.mark.asyncio
async def test_data_source_factory_dependency_installs_fallback_factory(monkeypatch):
    fake_factory = object()
    fake_app = SimpleNamespace(state=SimpleNamespace())
    request = SimpleNamespace(app=fake_app)
    calls = []

    async def fake_get_data_source_factory():
        calls.append("fallback")
        return fake_factory

    monkeypatch.setattr(data_source_factory_module, "get_data_source_factory", fake_get_data_source_factory)

    result = await data_source_factory_module.get_data_source_factory_dependency(request)

    assert result is fake_factory
    assert getattr(fake_app.state, data_source_factory_module.DATA_SOURCE_FACTORY_STATE_KEY) is fake_factory
    assert calls == ["fallback"]


@pytest.mark.asyncio
async def test_get_data_source_factory_compatibility_getter_still_initializes(monkeypatch):
    class FakeDataSourceFactory:
        def __init__(self):
            self.initialized = False

        async def initialize(self):
            self.initialized = True

    monkeypatch.setattr(data_source_factory_module, "DataSourceFactory", FakeDataSourceFactory)
    monkeypatch.setattr(data_source_factory_module, "_global_factory", None)

    result = await data_source_factory_module.get_data_source_factory()

    assert isinstance(result, FakeDataSourceFactory)
    assert result.initialized is True
    assert data_source_factory_module._global_factory is result
