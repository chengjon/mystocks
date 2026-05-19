from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.adapters import cninfo_adapter
from app.adapters.cninfo_adapter import (
    CNINFO_ADAPTER_STATE_KEY,
    CninfoAdapter,
    close_cninfo_adapter,
    get_cninfo_adapter_dependency,
    install_cninfo_adapter,
)


class DummyAdapter:
    def __init__(self, marker: str):
        self.marker = marker


def _build_probe_app():
    app = FastAPI()

    @app.get("/probe")
    def probe(adapter=Depends(get_cninfo_adapter_dependency)):
        return {"marker": adapter.marker}

    return app


def test_cninfo_dependency_uses_app_state_instance():
    app = _build_probe_app()
    install_cninfo_adapter(app, DummyAdapter("state"))

    response = TestClient(app).get("/probe")

    assert response.status_code == 200
    assert response.json() == {"marker": "state"}


def test_cninfo_dependency_can_be_overridden():
    app = _build_probe_app()
    app.dependency_overrides[get_cninfo_adapter_dependency] = lambda: DummyAdapter("override")

    response = TestClient(app).get("/probe")

    assert response.status_code == 200
    assert response.json() == {"marker": "override"}


def test_cninfo_dependency_falls_back_to_compatibility_getter(monkeypatch):
    app = _build_probe_app()
    fallback = DummyAdapter("fallback")
    calls = 0

    def get_fallback():
        nonlocal calls
        calls += 1
        return fallback

    monkeypatch.setattr(cninfo_adapter, "get_cninfo_adapter", get_fallback)

    client = TestClient(app)
    first_response = client.get("/probe")
    second_response = client.get("/probe")

    assert first_response.status_code == 200
    assert first_response.json() == {"marker": "fallback"}
    assert second_response.status_code == 200
    assert second_response.json() == {"marker": "fallback"}
    assert calls == 1
    assert getattr(app.state, CNINFO_ADAPTER_STATE_KEY) is fallback


def test_cninfo_adapter_close_closes_session():
    adapter = CninfoAdapter.__new__(CninfoAdapter)
    closed = False

    class Session:
        def close(self):
            nonlocal closed
            closed = True

    adapter.session = Session()

    adapter.close()

    assert closed is True


def test_close_installed_cninfo_adapter_closes_and_removes_app_state():
    app = FastAPI()
    closed = False

    class Adapter(DummyAdapter):
        def close(self):
            nonlocal closed
            closed = True

    install_cninfo_adapter(app, Adapter("teardown"))

    close_cninfo_adapter(app)

    assert closed is True
    assert not hasattr(app.state, CNINFO_ADAPTER_STATE_KEY)
