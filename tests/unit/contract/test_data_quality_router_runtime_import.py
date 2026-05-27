"""Contract smoke for data-quality route provider injection."""

from __future__ import annotations


def test_app_openapi_keeps_data_quality_provider_dependency_hidden(monkeypatch):
    monkeypatch.setenv("POSTGRESQL_HOST", "localhost")
    monkeypatch.setenv("POSTGRESQL_USER", "postgres")
    monkeypatch.setenv("POSTGRESQL_PASSWORD", "postgres")
    monkeypatch.setenv("JWT_SECRET_KEY", "0123456789abcdef0123456789abcdef")
    monkeypatch.setenv("BACKEND_PORT", "8020")
    monkeypatch.setenv("BACKEND_BACKUP_PORT", "8021")

    from app.main import app

    schema = app.openapi()
    data_quality_paths = {
        path: methods
        for path, methods in schema.get("paths", {}).items()
        if "/data-quality" in path
    }
    leaked_params = [
        {
            "path": path,
            "method": method,
            "name": param.get("name", ""),
        }
        for path, methods in data_quality_paths.items()
        for method, operation in methods.items()
        for param in operation.get("parameters", []) or []
        if "monitor" in param.get("name", "") or "quality_monitor" in param.get("name", "")
    ]

    assert len(data_quality_paths) == 9
    assert leaked_params == []
