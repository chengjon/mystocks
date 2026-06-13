from __future__ import annotations

import ast
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
STRATEGY_PATH = PROJECT_ROOT / "web/backend/app/api/strategy.py"
PROVIDER_NAME = "get_strategy_data_source"
ADAPTER_PARAM_NAME = "strategy_adapter"
ROUTE_FUNCTIONS = {
    "get_strategy_definitions",
    "run_strategy_single",
    "run_strategy_batch",
}


def _parse_module() -> ast.Module:
    return ast.parse(STRATEGY_PATH.read_text(encoding="utf-8"))


def _call_name(call: ast.Call) -> str:
    func = call.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return ""


def _decorator_name(decorator: ast.expr) -> str:
    if isinstance(decorator, ast.Call):
        decorator = decorator.func
    if isinstance(decorator, ast.Attribute):
        return decorator.attr
    if isinstance(decorator, ast.Name):
        return decorator.id
    return ""


def _route_functions(tree: ast.Module) -> dict[str, ast.AsyncFunctionDef]:
    route_names = {"get", "post", "put", "delete", "patch", "options", "head", "websocket", "api_route"}
    routes: dict[str, ast.AsyncFunctionDef] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.AsyncFunctionDef):
            continue
        if any(_decorator_name(decorator) in route_names for decorator in node.decorator_list):
            routes[node.name] = node
    return routes


def _body_call_count(node: ast.AsyncFunctionDef, call_name: str) -> int:
    count = 0
    for statement in node.body:
        for child in ast.walk(statement):
            if isinstance(child, ast.Call) and _call_name(child) == call_name:
                count += 1
    return count


def _depends_on_provider(arg: ast.arg, default: ast.expr | None) -> bool:
    if arg.arg != ADAPTER_PARAM_NAME:
        return False
    if not isinstance(default, ast.Call) or _call_name(default) != "Depends" or not default.args:
        return False
    provider = default.args[0]
    return isinstance(provider, ast.Name) and provider.id == PROVIDER_NAME


def _kwonly_default_by_arg(node: ast.AsyncFunctionDef) -> dict[str, ast.expr | None]:
    return dict(zip((arg.arg for arg in node.args.kwonlyargs), node.args.kw_defaults))


def test_strategy_routes_inject_adapter_provider() -> None:
    tree = _parse_module()
    routes = _route_functions(tree)

    missing = sorted(ROUTE_FUNCTIONS - set(routes))
    assert not missing, f"missing expected strategy routes: {missing}"

    inline_factory_routes = []
    inline_getter_routes = []
    missing_provider_routes = []
    for route_name in sorted(ROUTE_FUNCTIONS):
        route = routes[route_name]
        if _body_call_count(route, "DataSourceFactory"):
            inline_factory_routes.append(route_name)
        if _body_call_count(route, "get_data_source"):
            inline_getter_routes.append(route_name)

        defaults = _kwonly_default_by_arg(route)
        provider_arg = next((arg for arg in route.args.kwonlyargs if arg.arg == ADAPTER_PARAM_NAME), None)
        if provider_arg is None or not _depends_on_provider(provider_arg, defaults.get(ADAPTER_PARAM_NAME)):
            missing_provider_routes.append(route_name)

    assert inline_factory_routes == []
    assert inline_getter_routes == []
    assert missing_provider_routes == []


def test_strategy_provider_is_single_factory_boundary() -> None:
    tree = _parse_module()
    provider = next(
        (node for node in ast.walk(tree) if isinstance(node, ast.AsyncFunctionDef) and node.name == PROVIDER_NAME),
        None,
    )

    assert provider is not None
    assert _body_call_count(provider, "DataSourceFactory") == 1
    assert _body_call_count(provider, "get_data_source") == 1

    data_source_names = [
        call.args[0].value
        for call in ast.walk(provider)
        if isinstance(call, ast.Call)
        and _call_name(call) == "get_data_source"
        and call.args
        and isinstance(call.args[0], ast.Constant)
    ]
    assert data_source_names == ["strategy"]
