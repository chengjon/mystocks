from __future__ import annotations

import importlib.util
import logging
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest


SOURCE_FILES = [
    "web/backend/app/db/user_repository.py",
    "web/backend/app/services/email_service.py",
    "web/backend/app/api/health.py",
    "web/backend/app/api/system/system_health.py",
    "web/backend/app/core/user_experience_monitor.py",
    "web/backend/app/api/data_source_registry.py",
]


def _load_module(module_path: str, module_name: str, fake_modules: dict[str, ModuleType] | None = None):
    previous_fake_modules = {}
    fake_modules = fake_modules or {}

    if not fake_modules and module_name in sys.modules:
        return sys.modules[module_name]

    for name, module in fake_modules.items():
        previous_fake_modules[name] = sys.modules.get(name)
        sys.modules[name] = module

    spec = importlib.util.spec_from_file_location(module_name, Path(module_path))
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    for name, previous_module in previous_fake_modules.items():
        if previous_module is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = previous_module

    return module


@pytest.mark.parametrize("module_path", SOURCE_FILES)
def test_runtime_modules_source_contains_no_print_statements(module_path: str):
    source = Path(module_path).read_text(encoding="utf-8")

    assert "print(" not in source


def test_email_service_logs_missing_smtp_config(caplog):
    module = _load_module(
        "web/backend/app/services/email_service.py",
        "test_email_service_logging_wave2_module",
    )

    with caplog.at_level(logging.WARNING, logger=module.__name__):
        module.EmailService(username="", password="")

    assert any("邮件服务未配置" in record.getMessage() for record in caplog.records)


def test_email_service_logs_send_failures(caplog, monkeypatch):
    module = _load_module(
        "web/backend/app/services/email_service.py",
        "test_email_service_logging_wave2_send_module",
    )

    class FailingSMTP:
        def __init__(self, *_args, **_kwargs):
            raise RuntimeError("smtp down")

    monkeypatch.setattr(module.smtplib, "SMTP", FailingSMTP)
    service = module.EmailService(username="bot@example.com", password="secret")

    with caplog.at_level(logging.ERROR, logger=module.__name__):
        result = service.send_email(["user@example.com"], "Subject", "Body")

    assert result["success"] is False
    assert any("发送邮件失败" in record.getMessage() for record in caplog.records)


def test_user_repository_logs_audit_failures(caplog):
    fake_app = ModuleType("app")
    fake_app_core = ModuleType("app.core")
    fake_security = ModuleType("app.core.security")
    fake_src = ModuleType("src")
    fake_src_core = ModuleType("src.core")
    fake_exceptions = ModuleType("src.core.exceptions")

    class FakeUserInDB:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    class FakeDatabaseOperationError(Exception):
        pass

    class FakeDataValidationError(Exception):
        pass

    fake_security.UserInDB = FakeUserInDB
    fake_exceptions.DatabaseOperationError = FakeDatabaseOperationError
    fake_exceptions.DataValidationError = FakeDataValidationError

    module = _load_module(
        "web/backend/app/db/user_repository.py",
        "test_user_repository_logging_wave2_module",
        fake_modules={
            "app": fake_app,
            "app.core": fake_app_core,
            "app.core.security": fake_security,
            "src": fake_src,
            "src.core": fake_src_core,
            "src.core.exceptions": fake_exceptions,
        },
    )

    class FailingSession:
        def __init__(self):
            self.rolled_back = False

        def execute(self, *_args, **_kwargs):
            raise RuntimeError("db down")

        def rollback(self):
            self.rolled_back = True

    session = FailingSession()
    repository = module.UserRepository(session)

    with caplog.at_level(logging.WARNING, logger=module.__name__):
        result = repository.log_user_action(user_id=1, action="login")

    assert result is False
    assert session.rolled_back is True
    assert any("Failed to log user action" in record.getMessage() for record in caplog.records)


def test_user_experience_monitor_logs_metric_update_failures(caplog, monkeypatch):
    module = _load_module(
        "web/backend/app/core/user_experience_monitor.py",
        "test_user_experience_monitor_logging_wave2_module",
    )
    monitor = module.UserExperienceMonitor()

    monkeypatch.setattr(module.time, "time", lambda: 1000)

    def raise_cpu_percent(*_args, **_kwargs):
        raise RuntimeError("psutil down")

    monkeypatch.setattr(module.psutil, "cpu_percent", raise_cpu_percent)

    with caplog.at_level(logging.ERROR, logger=module.__name__):
        monitor.update_system_metrics()

    assert any("Failed to update system metrics" in record.getMessage() for record in caplog.records)


def test_user_experience_monitor_logs_health_score_failures(caplog, monkeypatch):
    module = _load_module(
        "web/backend/app/core/user_experience_monitor.py",
        "test_user_experience_monitor_logging_wave2_module",
    )
    monitor = module.UserExperienceMonitor()

    monkeypatch.setattr(module, "SYSTEM_CPU_USAGE", SimpleNamespace(_value="oops"))
    monkeypatch.setattr(module, "SYSTEM_MEMORY_USAGE", SimpleNamespace(_value=0))
    monkeypatch.setattr(
        module,
        "USER_EXPERIENCE_HEALTH",
        SimpleNamespace(labels=lambda **_kwargs: SimpleNamespace(set=lambda *_args, **_kwargs: None)),
    )

    with caplog.at_level(logging.ERROR, logger=module.__name__):
        monitor.update_health_score()

    assert any("Failed to calculate health score" in record.getMessage() for record in caplog.records)


def _load_data_source_registry_module():
    fake_app = ModuleType("app")
    fake_app_core = ModuleType("app.core")
    fake_config = ModuleType("app.core.config")
    fake_responses = ModuleType("app.core.responses")
    fake_security = ModuleType("app.core.security")

    fake_config.settings = SimpleNamespace(testing=True)
    fake_responses.ErrorCodes = SimpleNamespace(UNAUTHORIZED="UNAUTHORIZED")
    fake_responses.create_error_response = lambda code, message: SimpleNamespace(dict=lambda: {"code": code, "message": message})
    fake_security.verify_token = lambda token: {"sub": "tester"} if token else None

    return _load_module(
        "web/backend/app/api/data_source_registry.py",
        "test_data_source_registry_logging_wave2_module",
        fake_modules={
            "app": fake_app,
            "app.core": fake_app_core,
            "app.core.config": fake_config,
            "app.core.responses": fake_responses,
            "app.core.security": fake_security,
        },
    )


async def test_data_source_registry_logs_startup_event(caplog):
    module = _load_data_source_registry_module()

    with caplog.at_level(logging.INFO, logger=module.__name__):
        await module.startup_event()

    assert any("数据源管理API已启动" in record.getMessage() for record in caplog.records)


async def test_data_source_registry_logs_shutdown_event(caplog):
    module = _load_data_source_registry_module()

    with caplog.at_level(logging.INFO, logger=module.__name__):
        await module.shutdown_event()

    assert any("数据源管理API已关闭" in record.getMessage() for record in caplog.records)
