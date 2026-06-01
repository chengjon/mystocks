from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from app.api.market import market_data_request as module


def test_market_stock_list_source_contains_no_direct_use_mock_env_reads():
    source = Path(module.__file__).read_text(encoding="utf-8")

    assert 'os.getenv("USE_MOCK_DATA"' not in source


@pytest.mark.asyncio
async def test_market_stock_list_uses_mock_only_when_settings_enable_it(monkeypatch):
    monkeypatch.setattr(module.settings, "use_mock_apis", True, raising=False)
    monkeypatch.setattr(
        module,
        "_get_mock_stock_list",
        lambda **kwargs: {
            "data": [{"symbol": "000001", "name": "平安银行", "kwargs": kwargs}],
        },
    )

    result = await module.get_stock_list(limit=5, search="平安", exchange="SZSE", security_type="stock")

    assert result.success is True
    assert result.data["source"] == "mock"
    assert result.data["stocks"][0]["symbol"] == "000001"


def test_market_stock_list_exposes_route_local_session_factory_dependency():
    signature = inspect.signature(module.get_stock_list)

    session_factory = signature.parameters["session_factory"]

    assert session_factory.default.dependency is module.get_market_stock_list_postgresql_session_factory


@pytest.mark.asyncio
async def test_market_stock_list_real_branch_uses_injected_session_factory_and_closes(monkeypatch):
    class FakeRow:
        _mapping = {
            "symbol": "000001",
            "name": "平安银行",
            "exchange": "SZSE",
            "security_type": "stock",
            "list_date": None,
            "status": "listed",
            "listing_board": "main",
            "market_cap": 100,
            "circulating_market_cap": 80,
        }

    class FakeSession:
        def __init__(self):
            self.closed = False
            self.params = None

        def execute(self, sql, params):
            self.params = params
            return [FakeRow()]

        def close(self):
            self.closed = True

    session = FakeSession()
    calls = []

    def session_factory():
        calls.append("called")
        return session

    monkeypatch.setattr(module.settings, "use_mock_apis", False, raising=False)

    result = await module.get_stock_list(
        limit=5,
        search="平安",
        exchange="SZSE",
        security_type="stock",
        session_factory=session_factory,
    )

    assert calls == ["called"]
    assert session.closed is True
    assert session.params == {
        "search": "%平安%",
        "exchange": "SZSE",
        "security_type": "stock",
        "limit": 5,
    }
    assert result.success is True
    assert result.data["source"] == "real"
    assert result.data["stocks"][0]["symbol"] == "000001"


@pytest.mark.asyncio
async def test_market_stock_list_mock_branch_does_not_open_session_factory(monkeypatch):
    def fail_session_factory():
        raise AssertionError("mock branch must not open PostgreSQL session")

    monkeypatch.setattr(module.settings, "use_mock_apis", True, raising=False)
    monkeypatch.setattr(
        module,
        "_get_mock_stock_list",
        lambda **kwargs: {
            "data": [{"symbol": "000001", "name": "平安银行", "kwargs": kwargs}],
        },
    )

    result = await module.get_stock_list(
        limit=5,
        search="平安",
        exchange="SZSE",
        security_type="stock",
        session_factory=fail_session_factory,
    )

    assert result.success is True
    assert result.data["source"] == "mock"
