import ast
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.api import tradingview as tradingview_routes
from app.services import tradingview_widget_service
from app.services.tradingview_widget_service import (
    TRADINGVIEW_SERVICE_STATE_KEY,
    close_tradingview_service,
    get_tradingview_service_dependency,
    install_tradingview_service,
)


class DummyTradingViewService:
    def __init__(self, marker: str):
        self.marker = marker

    @staticmethod
    def convert_symbol_to_tradingview_format(symbol: str, market: str) -> str:
        return f"stub:{market}:{symbol}"


def _build_probe_app():
    app = FastAPI()

    @app.get("/probe")
    def probe(service=Depends(get_tradingview_service_dependency)):
        return {"marker": service.marker}

    return app


def test_tradingview_dependency_uses_app_state_instance():
    app = _build_probe_app()
    install_tradingview_service(app, DummyTradingViewService("state"))

    response = TestClient(app).get("/probe")

    assert response.status_code == 200
    assert response.json() == {"marker": "state"}


def test_tradingview_dependency_can_be_overridden():
    app = _build_probe_app()
    app.dependency_overrides[get_tradingview_service_dependency] = lambda: DummyTradingViewService("override")

    response = TestClient(app).get("/probe")

    assert response.status_code == 200
    assert response.json() == {"marker": "override"}


def test_tradingview_dependency_falls_back_to_default_service_factory(monkeypatch):
    app = _build_probe_app()
    fallback = DummyTradingViewService("fallback")
    calls = 0

    def build_default_service():
        nonlocal calls
        calls += 1
        return fallback

    monkeypatch.setattr(tradingview_widget_service, "TradingViewWidgetService", build_default_service)

    client = TestClient(app)
    first_response = client.get("/probe")
    second_response = client.get("/probe")

    assert first_response.status_code == 200
    assert first_response.json() == {"marker": "fallback"}
    assert second_response.status_code == 200
    assert second_response.json() == {"marker": "fallback"}
    assert calls == 1
    assert getattr(app.state, TRADINGVIEW_SERVICE_STATE_KEY) is fallback


def test_public_tradingview_service_getter_is_retired():
    content = Path(tradingview_widget_service.__file__).read_text(encoding="utf-8")

    assert not hasattr(tradingview_widget_service, "get_tradingview_service")
    assert "_tradingview_service =" not in content
    assert "global _tradingview_service" not in content
    assert "get_tradingview_service()" not in content


def test_close_installed_tradingview_service_calls_optional_close():
    app = FastAPI()
    closed = False

    class Service(DummyTradingViewService):
        def close(self):
            nonlocal closed
            closed = True

    install_tradingview_service(app, Service("teardown"))

    close_tradingview_service(app)

    assert closed is True
    assert not hasattr(app.state, TRADINGVIEW_SERVICE_STATE_KEY)


@pytest.mark.asyncio
async def test_convert_symbol_uses_injected_tradingview_service_when_mock_disabled(monkeypatch):
    monkeypatch.setattr(tradingview_routes.settings, "use_mock_apis", False, raising=False)

    result = await tradingview_routes.convert_symbol(
        symbol="0700",
        market="HKEX",
        current_user=SimpleNamespace(id=1, username="tester"),
        service=DummyTradingViewService("route"),
    )

    payload = result.model_dump()
    assert payload["success"] is True
    assert payload["data"]["tradingview_symbol"] == "stub:HKEX:0700"


def test_tradingview_routes_do_not_call_compatibility_getter_directly():
    content = Path(tradingview_routes.__file__).read_text(encoding="utf-8")

    assert "get_tradingview_service()" not in content


def test_app_factory_lifespan_calls_service_lifecycle_outside_exception_handlers():
    app_factory_path = Path(tradingview_routes.__file__).parents[1] / "app_factory.py"
    tree = ast.parse(app_factory_path.read_text(encoding="utf-8"))
    lifespan = next(node for node in tree.body if isinstance(node, ast.AsyncFunctionDef) and node.name == "lifespan")
    required_calls = {
        "install_akshare_extension",
        "install_tradingview_service",
        "close_akshare_extension",
        "close_tradingview_service",
    }

    call_names = {
        call.func.id for call in ast.walk(lifespan) if isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
    }
    assert required_calls <= call_names

    for handler in (node for node in ast.walk(lifespan) if isinstance(node, ast.ExceptHandler)):
        handler_call_names = {
            call.func.id for call in ast.walk(handler) if isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
        }
        assert required_calls.isdisjoint(handler_call_names)
