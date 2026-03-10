from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

from pydantic import BaseModel
from fastapi import APIRouter

LINE_LIMIT = 850


def _line_count(path: str) -> int:
    with open(path, "r", encoding="utf-8") as file:
        return sum(1 for _ in file)


def _load_algorithms_module():
    module_path = Path("web/backend/app/api/algorithms/get_algorithms_module.py")
    module_name = "test_algorithms_module_split_regressions_module"

    fake_app = ModuleType("app")
    fake_app_api = ModuleType("app.api")
    fake_app_api_algorithms = ModuleType("app.api.algorithms")
    fake_app_core = ModuleType("app.core")
    fake_responses = ModuleType("app.core.responses")
    fake_security = ModuleType("app.core.security")
    fake_schemas = ModuleType("app.schemas.algorithm_schemas")
    fake_services = ModuleType("app.services.algorithm_service")
    fake_metadata = ModuleType("app.api.algorithms.algorithm_metadata")
    fake_naive_bayes_router = ModuleType("app.api.algorithms._naive_bayes_router")

    class FakeUser:
        id = 1
        username = "tester"
        role = "admin"

    class FakeRequest(BaseModel):
        model_id: str | None = None
        training_data: list = []
        config: dict | None = None
        algorithm_type: str | None = None
        algorithm_name: str | None = None

    fake_responses.UnifiedResponse = dict
    fake_responses.bad_request = lambda *args, **kwargs: {"ok": False}
    fake_responses.not_found = lambda *args, **kwargs: {"ok": False}
    fake_responses.ok = lambda *args, **kwargs: {"ok": True}
    fake_responses.server_error = lambda *args, **kwargs: {"ok": False}
    fake_security.User = FakeUser
    fake_security.get_current_user = lambda: FakeUser()
    fake_schemas.AlgorithmPredictRequest = FakeRequest
    fake_schemas.AlgorithmTrainRequest = FakeRequest
    fake_schemas.DecisionTreeTrainRequest = FakeRequest
    fake_services.algorithm_service = ModuleType("algorithm_service")
    fake_metadata.get_algorithm_description = lambda algorithm: "desc"
    fake_metadata.get_algorithm_parameters = lambda algorithm: {}
    fake_metadata.get_algorithm_performance = lambda algorithm: {}
    fake_metadata.get_algorithm_use_cases = lambda algorithm: []
    fake_naive_bayes_router.router = APIRouter()

    previous = {
        "app": sys.modules.get("app"),
        "app.api": sys.modules.get("app.api"),
        "app.api.algorithms": sys.modules.get("app.api.algorithms"),
        "app.api.algorithms._naive_bayes_router": sys.modules.get("app.api.algorithms._naive_bayes_router"),
        "app.api.algorithms.algorithm_metadata": sys.modules.get("app.api.algorithms.algorithm_metadata"),
        "app.core": sys.modules.get("app.core"),
        "app.core.responses": sys.modules.get("app.core.responses"),
        "app.core.security": sys.modules.get("app.core.security"),
        "app.schemas.algorithm_schemas": sys.modules.get("app.schemas.algorithm_schemas"),
        "app.services.algorithm_service": sys.modules.get("app.services.algorithm_service"),
        module_name: sys.modules.get(module_name),
    }

    sys.modules["app"] = fake_app
    sys.modules["app.api"] = fake_app_api
    sys.modules["app.api.algorithms"] = fake_app_api_algorithms
    sys.modules["app.api.algorithms._naive_bayes_router"] = fake_naive_bayes_router
    sys.modules["app.api.algorithms.algorithm_metadata"] = fake_metadata
    sys.modules["app.core"] = fake_app_core
    sys.modules["app.core.responses"] = fake_responses
    sys.modules["app.core.security"] = fake_security
    sys.modules["app.schemas.algorithm_schemas"] = fake_schemas
    sys.modules["app.services.algorithm_service"] = fake_services

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    for name, previous_module in previous.items():
        if previous_module is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = previous_module

    return module


def test_algorithms_module_stays_below_850_lines():
    assert _line_count("web/backend/app/api/algorithms/get_algorithms_module.py") < LINE_LIMIT


def test_algorithms_module_remains_importable():
    module = _load_algorithms_module()

    assert module.router is not None
