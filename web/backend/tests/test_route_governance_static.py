from __future__ import annotations

import ast
import os
import sys
import types
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from fastapi import FastAPI


os.environ.setdefault("POSTGRESQL_HOST", "localhost")
os.environ.setdefault("POSTGRESQL_USER", "tester")
os.environ.setdefault("POSTGRESQL_PASSWORD", "tester")
os.environ.setdefault("POSTGRESQL_DATABASE", "tester")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_APP_ROOT = PROJECT_ROOT / "web/backend/app"


def _load_module(module_name: str, relative_path: str):
    module_path = PROJECT_ROOT / relative_path
    spec = spec_from_file_location(module_name, module_path)
    module = module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _read_router_prefix(relative_path: str) -> str:
    module_path = PROJECT_ROOT / relative_path
    tree = ast.parse(module_path.read_text(encoding="utf-8"))

    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "router" for target in node.targets):
            continue
        if not isinstance(node.value, ast.Call):
            continue
        if not isinstance(node.value.func, ast.Name) or node.value.func.id != "APIRouter":
            continue
        for keyword in node.value.keywords:
            if keyword.arg == "prefix":
                return ast.literal_eval(keyword.value)
        return ""

    raise AssertionError(f"router APIRouter() assignment not found in {relative_path}")


def test_governed_route_prefixes_are_defined_in_version_mapping():
    version_mapping_module = _load_module(
        "route_governance_version_mapping",
        "web/backend/app/api/VERSION_MAPPING.py",
    )

    assert version_mapping_module.VERSION_MAPPING["market_v2"]["prefix"] == "/api/v2/market"
    assert version_mapping_module.VERSION_MAPPING["monitoring_analysis"]["prefix"] == "/api/v1/monitoring/analysis"
    assert version_mapping_module.VERSION_MAPPING["monitoring_watchlists"]["prefix"] == "/api/v1/monitoring/watchlists"
    assert version_mapping_module.VERSION_MAPPING["multi_source"]["prefix"] == "/api/multi-source"


def test_scoped_router_modules_do_not_bake_in_runtime_prefixes():
    assert _read_router_prefix("web/backend/app/api/technical/routes.py") == ""
    assert _read_router_prefix("web/backend/app/api/monitoring_analysis.py") == ""
    assert _read_router_prefix("web/backend/app/api/monitoring_watchlists.py") == ""
    assert _read_router_prefix("web/backend/app/api/multi_source/routes.py") == ""
    assert _read_router_prefix("web/backend/app/api/market_v2.py") == ""


def test_register_all_routers_delegates_to_central_registry(monkeypatch):
    fake_router_registry = types.ModuleType("app.router_registry")
    fake_router_registry.register_api_routes = lambda *args, **kwargs: None
    monkeypatch.setitem(sys.modules, "app.router_registry", fake_router_registry)

    fake_core_package = types.ModuleType("app.core")
    fake_core_package.__path__ = [str(BACKEND_APP_ROOT / "core")]
    monkeypatch.setitem(sys.modules, "app.core", fake_core_package)

    fake_core_config = types.ModuleType("app.core.config")
    fake_core_config.settings = types.SimpleNamespace(use_mock_apis=False)
    monkeypatch.setitem(sys.modules, "app.core.config", fake_core_config)

    fake_api_package = types.ModuleType("app.api")
    fake_api_package.__path__ = [str(BACKEND_APP_ROOT / "api")]
    monkeypatch.setitem(sys.modules, "app.api", fake_api_package)

    register_routers = _load_module(
        "app.api.register_routers",
        "web/backend/app/api/register_routers.py",
    )
    calls: list[dict[str, object]] = []

    def _fake_register_api_routes(app: FastAPI, *, use_mock_apis: bool, logger) -> None:
        calls.append(
            {
                "app": app,
                "use_mock_apis": use_mock_apis,
                "logger": logger,
            },
        )

    monkeypatch.setattr(register_routers, "register_api_routes", _fake_register_api_routes)

    app = FastAPI()
    register_routers.register_all_routers(app)

    assert len(calls) == 1
    assert calls[0]["app"] is app
    assert calls[0]["use_mock_apis"] == register_routers.settings.use_mock_apis
    assert calls[0]["logger"] is register_routers.logger
