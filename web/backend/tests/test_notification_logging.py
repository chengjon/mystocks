from __future__ import annotations

import importlib.util
import logging
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest
from fastapi import BackgroundTasks


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

    fake_auth.User = SimpleNamespace
    fake_auth.get_current_user = lambda: None
    fake_auth.get_current_active_user = lambda: None
    fake_email_service.get_email_service = lambda: SimpleNamespace(is_configured=lambda: False)

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

    for dotted_name, module_path in module_paths.items():
        spec = importlib.util.spec_from_file_location(dotted_name, module_path)
        module = importlib.util.module_from_spec(spec)
        assert spec is not None and spec.loader is not None
        sys.modules[dotted_name] = module
        spec.loader.exec_module(module)

    spec = importlib.util.spec_from_file_location(module_name, api_root / "notification.py")
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


def test_notification_source_contains_no_print_statements():
    source = Path("web/backend/app/api/notification.py").read_text(encoding="utf-8")

    assert "print(" not in source


@pytest.mark.asyncio
async def test_send_daily_newsletter_background_task_logs_success(monkeypatch, caplog):
    module = load_notification_module()
    monkeypatch.setattr(module, "logger", logging.getLogger("test.notification.success"))

    class FakeEmailService:
        @staticmethod
        def is_configured():
            return True

        @staticmethod
        def send_daily_newsletter(**_kwargs):
            return {"success": True, "message": "ok"}

    monkeypatch.setattr(module, "get_email_service", lambda: FakeEmailService())
    background_tasks = BackgroundTasks()
    request = module.SendNewsletterRequest(
        user_email="user@example.com",
        user_name="Tester",
        watchlist_symbols=["600519"],
        news_data=[{"headline": "demo"}],
    )

    response = await module.send_daily_newsletter(request=request, background_tasks=background_tasks, current_user=None)
    assert response["success"] is True
    assert len(background_tasks.tasks) == 1

    task = background_tasks.tasks[0]
    with caplog.at_level(logging.INFO, logger="test.notification.success"):
        task.func(*task.args, **task.kwargs)

    assert any("新闻简报已发送至" in record.getMessage() for record in caplog.records)


@pytest.mark.asyncio
async def test_send_price_alert_background_task_logs_failure(monkeypatch, caplog):
    module = load_notification_module()
    monkeypatch.setattr(module, "logger", logging.getLogger("test.notification.failure"))

    class FakeEmailService:
        @staticmethod
        def is_configured():
            return True

        @staticmethod
        def send_price_alert(**_kwargs):
            return {"success": False, "message": "smtp down"}

    monkeypatch.setattr(module, "get_email_service", lambda: FakeEmailService())
    background_tasks = BackgroundTasks()
    request = module.SendPriceAlertRequest(
        user_email="user@example.com",
        user_name="Tester",
        symbol="600519.SH",
        stock_name="贵州茅台",
        current_price=1500.0,
        alert_condition="高于",
        alert_price=1550.0,
    )

    response = await module.send_price_alert(request=request, background_tasks=background_tasks, current_user=None)
    assert response["success"] is True
    assert len(background_tasks.tasks) == 1

    task = background_tasks.tasks[0]
    with caplog.at_level(logging.ERROR, logger="test.notification.failure"):
        task.func(*task.args, **task.kwargs)

    assert any("价格提醒发送失败" in record.getMessage() for record in caplog.records)
