from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.adapters import akshare_extension
from app.adapters.akshare_extension import (
    AKSHARE_EXTENSION_STATE_KEY,
    AkshareExtension,
    close_akshare_extension,
    get_akshare_extension_dependency,
    install_akshare_extension,
)


class DummyExtension:
    def __init__(self, marker: str):
        self.marker = marker


def _build_probe_app():
    app = FastAPI()

    @app.get("/probe")
    def probe(extension=Depends(get_akshare_extension_dependency)):
        return {"marker": extension.marker}

    return app


def test_akshare_extension_dependency_uses_app_state_instance():
    app = _build_probe_app()
    install_akshare_extension(app, DummyExtension("state"))

    response = TestClient(app).get("/probe")

    assert response.status_code == 200
    assert response.json() == {"marker": "state"}


def test_akshare_extension_dependency_can_be_overridden():
    app = _build_probe_app()
    app.dependency_overrides[get_akshare_extension_dependency] = lambda: DummyExtension("override")

    response = TestClient(app).get("/probe")

    assert response.status_code == 200
    assert response.json() == {"marker": "override"}


def test_akshare_extension_dependency_falls_back_to_compatibility_getter(monkeypatch):
    app = _build_probe_app()
    fallback = DummyExtension("fallback")
    calls = 0

    def get_fallback():
        nonlocal calls
        calls += 1
        return fallback

    monkeypatch.setattr(akshare_extension, "get_akshare_extension", get_fallback)

    client = TestClient(app)
    first_response = client.get("/probe")
    second_response = client.get("/probe")

    assert first_response.status_code == 200
    assert first_response.json() == {"marker": "fallback"}
    assert second_response.status_code == 200
    assert second_response.json() == {"marker": "fallback"}
    assert calls == 1
    assert getattr(app.state, AKSHARE_EXTENSION_STATE_KEY) is fallback


def test_close_installed_akshare_extension_removes_app_state():
    app = FastAPI()
    install_akshare_extension(app, AkshareExtension())

    close_akshare_extension(app)

    assert not hasattr(app.state, AKSHARE_EXTENSION_STATE_KEY)


def test_close_installed_akshare_extension_calls_optional_close():
    app = FastAPI()
    closed = False

    class Extension(DummyExtension):
        def close(self):
            nonlocal closed
            closed = True

    install_akshare_extension(app, Extension("teardown"))

    close_akshare_extension(app)

    assert closed is True
    assert not hasattr(app.state, AKSHARE_EXTENSION_STATE_KEY)
