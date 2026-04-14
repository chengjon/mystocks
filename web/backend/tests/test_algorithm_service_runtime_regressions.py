from __future__ import annotations

import asyncio
import importlib
import sys
from pathlib import Path


def _import_algorithm_service_module():
    backend_root = Path("web/backend").resolve()
    backend_root_str = str(backend_root)
    if backend_root_str not in sys.path:
        sys.path.insert(0, backend_root_str)

    sys.modules.pop("app.services.algorithm_service", None)
    return importlib.import_module("app.services.algorithm_service")


def test_algorithm_factory_fails_honestly_when_framework_unavailable(monkeypatch):
    module = _import_algorithm_service_module()
    factory = module.AlgorithmFactory()

    monkeypatch.setattr(module, "ALGORITHMS_AVAILABLE", False)

    try:
        asyncio.run(factory.create_algorithm(module.AlgorithmType.SVM, module.AlgorithmConfig(enable_gpu=False)))
    except RuntimeError as exc:
        assert str(exc) == (
            f"Algorithm creation failed: {module.ALGORITHM_FRAMEWORK_UNAVAILABLE_MESSAGE}"
        )
    else:
        raise AssertionError("expected RuntimeError when algorithm framework is unavailable")


def test_algorithm_service_info_fails_with_runtime_availability_message(monkeypatch):
    module = _import_algorithm_service_module()
    service = module.AlgorithmService()

    monkeypatch.setattr(module, "ALGORITHMS_AVAILABLE", False)

    try:
        asyncio.run(service.get_algorithm_info(module.AlgorithmInfoRequest(algorithm_type=module.AlgorithmType.SVM)))
    except module.HTTPException as exc:
        assert exc.status_code == 500
        assert module.ALGORITHM_FRAMEWORK_UNAVAILABLE_MESSAGE in str(exc.detail)
    else:
        raise AssertionError("expected HTTPException when algorithm framework is unavailable")
