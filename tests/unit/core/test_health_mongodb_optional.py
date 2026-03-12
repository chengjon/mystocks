from __future__ import annotations

import asyncio
import importlib.util
import sys
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import AsyncMock, patch


HEALTH_MODULE_PATH = Path("/opt/claude/mystocks_spec/web/backend/app/api/health.py")


def _load_health_module(module_name: str = "test_web_backend_health_module"):
    sys.modules.pop(module_name, None)

    fake_exceptions = SimpleNamespace(BusinessException=Exception, NotFoundException=Exception)
    fake_responses = SimpleNamespace(
        ErrorCodes=SimpleNamespace(INTERNAL_SERVER_ERROR='500'),
        create_error_response=lambda **kwargs: kwargs,
        create_health_response=lambda **kwargs: kwargs,
    )

    def _fake_get_current_user():
        return None

    fake_security = SimpleNamespace(User=object, get_current_user=_fake_get_current_user)
    fake_readiness = SimpleNamespace(check_mongodb_readiness=lambda: {'status': 'optional_unconfigured', 'detail': 'stub', 'required': False, 'latency_ms': 0.0})

    spec = importlib.util.spec_from_file_location(module_name, HEALTH_MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None

    with patch.dict(
        sys.modules,
        {
            "app": type("FakeApp", (), {})(),
            "app.core": type("FakeCore", (), {})(),
            "app.core.exceptions": fake_exceptions,
            "app.core.responses": fake_responses,
            "app.core.security": fake_security,
            "app.core.readiness": fake_readiness,
        },
    ):
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    return module


def test_check_system_health_includes_optional_mongodb_without_degrading() -> None:
    module = _load_health_module("test_web_backend_health_optional")
    request = type("Req", (), {"state": type("State", (), {"request_id": "req-1"})()})()

    with patch.object(module, "check_postgresql_service", AsyncMock(return_value=module.HealthStatus(service="postgresql", status="normal"))), patch.object(
        module, "check_tdengine_service", AsyncMock(return_value=module.HealthStatus(service="tdengine", status="normal"))
    ), patch.object(module, "check_disk_space", AsyncMock(return_value=module.HealthStatus(service="disk", status="normal"))), patch.object(
        module, "check_system_resources", AsyncMock(return_value=module.HealthStatus(service="system", status="normal"))
    ), patch.object(
        module,
        "check_mongodb_service",
        AsyncMock(return_value=module.HealthStatus(service="mongodb", status="normal", details="MongoDB optional and not configured")),
    ):
        response = asyncio.run(module.check_system_health(request))

    assert response["status"] == "healthy"
    assert response["details"]["services"]["mongodb"].status == "normal"


def test_check_system_health_degrades_when_optional_mongodb_unavailable() -> None:
    module = _load_health_module("test_web_backend_health_warning")
    request = type("Req", (), {"state": type("State", (), {"request_id": "req-2"})()})()

    with patch.object(module, "check_postgresql_service", AsyncMock(return_value=module.HealthStatus(service="postgresql", status="normal"))), patch.object(
        module, "check_tdengine_service", AsyncMock(return_value=module.HealthStatus(service="tdengine", status="normal"))
    ), patch.object(module, "check_disk_space", AsyncMock(return_value=module.HealthStatus(service="disk", status="normal"))), patch.object(
        module, "check_system_resources", AsyncMock(return_value=module.HealthStatus(service="system", status="normal"))
    ), patch.object(
        module,
        "check_mongodb_service",
        AsyncMock(return_value=module.HealthStatus(service="mongodb", status="warning", details="MongoDB optional but unavailable")),
    ):
        response = asyncio.run(module.check_system_health(request))

    assert response["status"] == "degraded"
    assert response["details"]["services"]["mongodb"].status == "warning"
