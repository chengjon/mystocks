"""Regression tests for the data source registry manager provider seam."""

import ast
import inspect

from fastapi.params import Depends as DependsParam

from app.api import data_source_registry


HANDLER_NAMES = (
    "search_data_sources",
    "get_category_stats",
    "get_data_source",
    "update_data_source",
    "test_data_source",
    "health_check_data_source",
    "health_check_all_data_sources",
)


def test_data_source_registry_manager_provider_delegates_to_existing_get_manager(monkeypatch):
    sentinel = object()

    monkeypatch.setattr(data_source_registry, "get_manager", lambda: sentinel)

    assert data_source_registry.get_data_source_registry_manager() is sentinel


def test_data_source_registry_handlers_receive_manager_from_fastapi_dependency():
    for handler_name in HANDLER_NAMES:
        handler = getattr(data_source_registry, handler_name)
        manager_parameter = inspect.signature(handler).parameters.get("manager")

        assert manager_parameter is not None, f"{handler_name} must declare manager dependency"
        assert isinstance(manager_parameter.default, DependsParam)
        assert manager_parameter.default.dependency is data_source_registry.get_data_source_registry_manager


def test_data_source_registry_handlers_do_not_call_get_manager_inside_route_body():
    for handler_name in HANDLER_NAMES:
        source = inspect.getsource(getattr(data_source_registry, handler_name))
        tree = ast.parse(source)
        direct_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "get_manager"
        ]

        assert direct_calls == [], f"{handler_name} still calls get_manager() in the route body"
