from __future__ import annotations

import ast
import importlib
import inspect
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture
def data_source_config_module(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("POSTGRESQL_HOST", "localhost")
    monkeypatch.setenv("POSTGRESQL_USER", "postgres")
    monkeypatch.setenv("POSTGRESQL_PASSWORD", "password")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("BACKEND_PORT", "8020")
    monkeypatch.setenv("BACKEND_BACKUP_PORT", "8021")
    return importlib.import_module("app.api.data_source_config")


ROUTE_HANDLER_NAMES = {
    "create_data_source",
    "update_data_source",
    "delete_data_source",
    "get_data_source",
    "list_data_sources",
    "batch_operations",
    "get_version_history",
    "rollback_to_version",
    "reload_config",
}


def test_data_source_config_routes_expose_config_manager_dependency(data_source_config_module):
    dependency = getattr(data_source_config_module, "get_config_manager_dependency", None)

    assert dependency is not None

    for route in data_source_config_module.router.routes:
        if route.name not in ROUTE_HANDLER_NAMES:
            continue

        signature = inspect.signature(route.endpoint)
        manager_parameter = signature.parameters.get("manager")

        assert manager_parameter is not None, route.name
        assert getattr(manager_parameter.default, "dependency", None) is dependency


def test_data_source_config_route_bodies_do_not_call_config_manager_getter(data_source_config_module):
    source = inspect.getsource(data_source_config_module)
    tree = ast.parse(source)
    direct_calls: list[tuple[str, int]] = []

    for node in tree.body:
        if not isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
            continue
        if node.name not in ROUTE_HANDLER_NAMES:
            continue

        for child in ast.walk(node):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name) and child.func.id == "get_config_manager":
                direct_calls.append((node.name, child.lineno))

    assert direct_calls == []
