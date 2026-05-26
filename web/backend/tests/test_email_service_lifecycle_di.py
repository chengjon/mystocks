from __future__ import annotations

import importlib.util
import inspect
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest


def load_email_service_module():
    module_name = "email_service_lifecycle_under_test"
    module_path = Path("web/backend/app/services/email_service.py").resolve()
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(module_name, None)
    return module


def load_notification_module():
    api_root = Path("web/backend/app/api").resolve()
    app_root = Path("web/backend/app").resolve()
    services_root = Path("web/backend/app/services").resolve()
    module_name = "app.api.notification"
    module_paths = {
        "app.api.notification_models": api_root / "notification_models.py",
        "app.api.notification_support": api_root / "notification_support.py",
    }

    fake_app = ModuleType("app")
    fake_api = ModuleType("app.api")
    fake_services = ModuleType("app.services")
    fake_auth = ModuleType("app.api.auth")
    fake_email_service = ModuleType("app.services.email_service")

    fake_app.__path__ = [str(app_root)]
    fake_api.__path__ = [str(api_root)]
    fake_services.__path__ = [str(services_root)]
    fake_app.api = fake_api
    fake_app.services = fake_services
    fake_api.auth = fake_auth
    fake_services.email_service = fake_email_service

    class FakeEmailService:
        def is_configured(self):
            return True

        def send_email(self, **_kwargs):
            return {"success": True, "message": "ok"}

    fake_auth.User = SimpleNamespace
    fake_auth.get_current_user = lambda: None
    fake_auth.get_current_active_user = lambda: None
    fake_email_service.EmailService = FakeEmailService
    fake_email_service.get_email_service_dependency = lambda: FakeEmailService()

    previous = {
        "app": sys.modules.get("app"),
        "app.api": sys.modules.get("app.api"),
        "app.services": sys.modules.get("app.services"),
        "app.api.auth": sys.modules.get("app.api.auth"),
        "app.services.email_service": sys.modules.get("app.services.email_service"),
        module_name: sys.modules.get(module_name),
    }
    for dotted_name in module_paths:
        previous[dotted_name] = sys.modules.get(dotted_name)

    sys.modules["app"] = fake_app
    sys.modules["app.api"] = fake_api
    sys.modules["app.services"] = fake_services
    sys.modules["app.api.auth"] = fake_auth
    sys.modules["app.services.email_service"] = fake_email_service

    try:
        for dotted_name, module_path in module_paths.items():
            spec = importlib.util.spec_from_file_location(dotted_name, module_path)
            module = importlib.util.module_from_spec(spec)
            assert spec is not None
            assert spec.loader is not None
            sys.modules[dotted_name] = module
            spec.loader.exec_module(module)

        spec = importlib.util.spec_from_file_location(module_name, api_root / "notification.py")
        module = importlib.util.module_from_spec(spec)
        assert spec is not None
        assert spec.loader is not None
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    finally:
        for name, previous_module in previous.items():
            if previous_module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = previous_module

    return module


def test_email_service_dependency_installs_app_state_when_missing(monkeypatch):
    module = load_email_service_module()
    fake_service = object()
    fake_app = SimpleNamespace(state=SimpleNamespace())
    request = SimpleNamespace(app=fake_app)

    monkeypatch.setattr(module, "EmailService", lambda: fake_service)

    assert module.get_email_service_dependency(request) is fake_service
    assert getattr(fake_app.state, module.EMAIL_SERVICE_STATE_KEY) is fake_service


def test_notification_email_routes_accept_injected_email_service():
    module = load_notification_module()

    for function_name in [
        "get_email_service_status",
        "send_email",
        "send_welcome_email",
        "send_daily_newsletter",
        "send_price_alert",
        "send_test_email",
    ]:
        signature = inspect.signature(getattr(module, function_name))
        assert "email_service" in signature.parameters


@pytest.mark.asyncio
async def test_send_test_email_uses_injected_email_service():
    module = load_notification_module()

    class FakeEmailService:
        def __init__(self):
            self.sent_to = None

        def is_configured(self):
            return True

        def send_email(self, *, to_addresses, **_kwargs):
            self.sent_to = to_addresses
            return {"success": True, "message": "ok"}

    fake_service = FakeEmailService()
    current_user = SimpleNamespace(id=1, username="tester", email="tester@example.com")

    response = await module.send_test_email(current_user=current_user, email_service=fake_service)

    assert response["success"] is True
    assert fake_service.sent_to == ["tester@example.com"]
