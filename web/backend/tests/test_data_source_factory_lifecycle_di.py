from __future__ import annotations

from types import SimpleNamespace

import pytest

import app.services.data_source_factory as data_source_factory_package
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

    monkeypatch.setattr(data_source_factory_module, "_get_or_create_data_source_factory", unexpected_fallback)

    result = await data_source_factory_module.get_data_source_factory_dependency(request)

    assert result is fake_factory


@pytest.mark.asyncio
async def test_data_source_factory_dependency_installs_fallback_factory(monkeypatch):
    fake_factory = object()
    fake_app = SimpleNamespace(state=SimpleNamespace())
    request = SimpleNamespace(app=fake_app)
    calls = []

    async def fake_get_or_create_data_source_factory():
        calls.append("fallback")
        return fake_factory

    monkeypatch.setattr(
        data_source_factory_module, "_get_or_create_data_source_factory", fake_get_or_create_data_source_factory
    )

    result = await data_source_factory_module.get_data_source_factory_dependency(request)

    assert result is fake_factory
    assert getattr(fake_app.state, data_source_factory_module.DATA_SOURCE_FACTORY_STATE_KEY) is fake_factory
    assert calls == ["fallback"]


@pytest.mark.asyncio
def test_package_no_longer_exports_public_compatibility_getter():
    assert not hasattr(data_source_factory_module, "get_data_source_factory")
    assert not hasattr(data_source_factory_package, "get_data_source_factory")
    assert "get_data_source_factory" not in data_source_factory_package.__all__


@pytest.mark.asyncio
async def test_convenience_helpers_use_internal_factory_initializer(monkeypatch):
    class FakeFactory:
        async def get_data_source(self, source_name):
            return {"source": source_name}

        async def get_data(self, domain, endpoint, params=None):
            return {"domain": domain, "endpoint": endpoint, "params": params}

    fake_factory = FakeFactory()
    calls = []

    async def fake_get_or_create_data_source_factory():
        calls.append("internal")
        return fake_factory

    monkeypatch.setattr(
        data_source_factory_module, "_get_or_create_data_source_factory", fake_get_or_create_data_source_factory
    )

    assert await data_source_factory_module.get_data_source("akshare") == {"source": "akshare"}
    assert await data_source_factory_module.get_market_data("quotes", {"symbol": "000001"}) == {
        "domain": "market",
        "endpoint": "quotes",
        "params": {"symbol": "000001"},
    }
    assert await data_source_factory_module.get_dashboard_data("summary") == {
        "domain": "dashboard",
        "endpoint": "summary",
        "params": None,
    }
    assert await data_source_factory_module.get_technical_analysis_data("signals", {"limit": 3}) == {
        "domain": "technical_analysis",
        "endpoint": "signals",
        "params": {"limit": 3},
    }
    assert calls == ["internal", "internal", "internal", "internal"]
