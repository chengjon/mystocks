"""Regression tests for data-quality route provider injection."""

from __future__ import annotations

import ast
from pathlib import Path


ROUTE_FILE = Path("web/backend/app/api/data_quality.py")

ROUTES_REQUIRING_MONITOR_PROVIDER = {
    "get_data_quality_metrics",
    "get_active_alerts",
    "acknowledge_alert",
    "resolve_alert",
    "get_system_status_overview",
    "test_data_quality",
    "get_quality_trends",
}


def _module_tree() -> ast.Module:
    return ast.parse(ROUTE_FILE.read_text(encoding="utf-8"))


def _function(tree: ast.Module, name: str) -> ast.AsyncFunctionDef:
    for node in tree.body:
        if isinstance(node, ast.AsyncFunctionDef) and node.name == name:
            return node
    raise AssertionError(f"{name} not found")


def _depends_provider_name(default: ast.expr) -> str | None:
    if not isinstance(default, ast.Call):
        return None
    if not isinstance(default.func, ast.Name) or default.func.id != "Depends":
        return None
    if not default.args or not isinstance(default.args[0], ast.Name):
        return None
    return default.args[0].id


def test_data_quality_route_handlers_use_monitor_provider_dependency():
    tree = _module_tree()

    provider_defs = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}
    assert "get_data_quality_monitor_provider" in provider_defs
    assert "_resolve_direct_call_dependency" in provider_defs

    for route_name in ROUTES_REQUIRING_MONITOR_PROVIDER:
        route = _function(tree, route_name)
        args = route.args.args
        defaults = route.args.defaults
        defaults_by_name = {
            arg.arg: default for arg, default in zip(args[-len(defaults) :], defaults) if defaults
        }

        assert "monitor" in defaults_by_name, f"{route_name} must accept monitor provider param"
        assert _depends_provider_name(defaults_by_name["monitor"]) == "get_data_quality_monitor_provider"


def test_data_quality_route_bodies_do_not_call_monitor_singletons_directly():
    tree = _module_tree()

    for route_name in ROUTES_REQUIRING_MONITOR_PROVIDER:
        route = _function(tree, route_name)
        direct_calls = [
            node.func.id
            for node in ast.walk(route)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in {"get_data_quality_monitor", "monitor_data_quality"}
        ]
        assert direct_calls == [], f"{route_name} still calls singleton helpers: {direct_calls}"
