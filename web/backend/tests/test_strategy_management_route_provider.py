from __future__ import annotations

import inspect

import pytest
from fastapi.params import Depends

from app.api.strategy_management import _strategy_execution_router as module


class FakeStrategyService:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    def query_strategy_results(self, **kwargs):
        self.calls.append(("query_strategy_results", kwargs))
        return [{"symbol": "600519.SH", "match_result": True}]

    def get_matched_stocks(self, **kwargs):
        self.calls.append(("get_matched_stocks", kwargs))
        return ["600519.SH"]

    def get_strategy_definitions(self):
        self.calls.append(("get_strategy_definitions", {}))
        return [
            {
                "strategy_code": "double_ma",
                "strategy_name_cn": "双均线",
                "strategy_name_en": "Double MA",
            }
        ]


def test_strategy_execution_router_exposes_route_local_provider(monkeypatch):
    fake_service = FakeStrategyService()
    monkeypatch.setattr(module, "get_strategy_service", lambda: fake_service)

    assert module.get_strategy_service_dependency() is fake_service


def test_strategy_execution_handlers_depend_on_route_local_provider():
    for handler in [
        module.query_strategy_results,
        module.get_matched_stocks,
        module.get_strategy_summary,
    ]:
        parameter = inspect.signature(handler).parameters["strategy_service"]
        default = parameter.default
        assert isinstance(default, Depends)
        assert default.dependency is module.get_strategy_service_dependency


@pytest.mark.asyncio
async def test_query_strategy_results_uses_injected_strategy_service(monkeypatch):
    monkeypatch.setattr(
        module,
        "get_strategy_service",
        lambda: (_ for _ in ()).throw(AssertionError("public getter should not be called")),
    )
    fake_service = FakeStrategyService()

    response = await module.query_strategy_results(
        strategy_code=None,
        symbol=None,
        check_date=None,
        match_result=None,
        limit=100,
        offset=0,
        strategy_service=fake_service,
    )

    assert fake_service.calls[0][0] == "query_strategy_results"
    assert response.data["total"] == 1


@pytest.mark.asyncio
async def test_get_matched_stocks_uses_injected_strategy_service(monkeypatch):
    monkeypatch.setattr(
        module,
        "get_strategy_service",
        lambda: (_ for _ in ()).throw(AssertionError("public getter should not be called")),
    )
    fake_service = FakeStrategyService()

    response = await module.get_matched_stocks(
        strategy_code="double_ma",
        check_date=None,
        limit=100,
        strategy_service=fake_service,
    )

    assert fake_service.calls[0][0] == "get_matched_stocks"
    assert response.data["matched_stocks"] == ["600519.SH"]


@pytest.mark.asyncio
async def test_get_strategy_summary_uses_injected_strategy_service(monkeypatch):
    monkeypatch.setattr(
        module,
        "get_strategy_service",
        lambda: (_ for _ in ()).throw(AssertionError("public getter should not be called")),
    )
    fake_service = FakeStrategyService()

    response = await module.get_strategy_summary(check_date=None, strategy_service=fake_service)

    assert [name for name, _ in fake_service.calls] == [
        "get_strategy_definitions",
        "get_matched_stocks",
    ]
    assert response.data["strategy_summary"][0]["matched_count"] == 1
