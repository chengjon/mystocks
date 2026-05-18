from types import SimpleNamespace

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.adapters import eastmoney_enhanced
from app.adapters.eastmoney_enhanced import (
    EASTMONEY_ENHANCED_ADAPTER_STATE_KEY,
    EastMoneyEnhancedAdapter,
    close_eastmoney_enhanced_adapter,
    get_eastmoney_enhanced_adapter_dependency,
    install_eastmoney_enhanced_adapter,
)


class DummyAdapter:
    def __init__(self, marker: str):
        self.marker = marker


def _build_probe_app():
    app = FastAPI()

    @app.get("/probe")
    def probe(adapter=Depends(get_eastmoney_enhanced_adapter_dependency)):
        return {"marker": adapter.marker}

    return app


def test_eastmoney_enhanced_dependency_uses_app_state_instance():
    app = _build_probe_app()
    install_eastmoney_enhanced_adapter(app, DummyAdapter("state"))

    response = TestClient(app).get("/probe")

    assert response.status_code == 200
    assert response.json() == {"marker": "state"}


def test_eastmoney_enhanced_dependency_can_be_overridden():
    app = _build_probe_app()
    app.dependency_overrides[get_eastmoney_enhanced_adapter_dependency] = lambda: DummyAdapter("override")

    response = TestClient(app).get("/probe")

    assert response.status_code == 200
    assert response.json() == {"marker": "override"}


def test_eastmoney_enhanced_dependency_falls_back_to_compatibility_getter(monkeypatch):
    app = _build_probe_app()
    fallback = DummyAdapter("fallback")
    calls = 0

    def get_fallback():
        nonlocal calls
        calls += 1
        return fallback

    monkeypatch.setattr(eastmoney_enhanced, "get_eastmoney_enhanced_adapter", get_fallback)

    client = TestClient(app)
    first_response = client.get("/probe")
    second_response = client.get("/probe")

    assert first_response.status_code == 200
    assert first_response.json() == {"marker": "fallback"}
    assert second_response.status_code == 200
    assert second_response.json() == {"marker": "fallback"}
    assert calls == 1
    assert getattr(app.state, EASTMONEY_ENHANCED_ADAPTER_STATE_KEY) is fallback


def test_eastmoney_enhanced_adapter_close_closes_underlying_session():
    adapter = EastMoneyEnhancedAdapter.__new__(EastMoneyEnhancedAdapter)
    closed = False

    class Session:
        def close(self):
            nonlocal closed
            closed = True

    adapter._adapter = SimpleNamespace(session=Session())

    adapter.close()

    assert closed is True


def test_close_installed_eastmoney_enhanced_adapter_closes_and_removes_app_state():
    app = FastAPI()
    closed = False

    class Adapter(DummyAdapter):
        def close(self):
            nonlocal closed
            closed = True

    install_eastmoney_enhanced_adapter(app, Adapter("teardown"))

    close_eastmoney_enhanced_adapter(app)

    assert closed is True
    assert not hasattr(app.state, EASTMONEY_ENHANCED_ADAPTER_STATE_KEY)
