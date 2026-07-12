from __future__ import annotations

import importlib.util
import logging
import sys
from pathlib import Path


class StubSMTP:
    def __init__(self, *_args, **_kwargs):
        self.started_tls = False
        self.logged_in = False
        self.sent = False
        self.quit_called = False

    def starttls(self):
        self.started_tls = True

    def login(self, *_args, **_kwargs):
        self.logged_in = True

    def send_message(self, _msg):
        self.sent = True

    def quit(self):
        self.quit_called = True


def load_email_notification_module():
    module_path = Path("web/backend/app/services/email_notification_service.py")
    module_name = "test_email_notification_service_logging_module"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_email_notification_service_source_contains_no_print_statements():
    source = Path("web/backend/app/services/email_notification_service.py").read_text(encoding="utf-8")

    assert "print(" not in source


def test_init_logs_warning_when_smtp_config_incomplete(caplog):
    module = load_email_notification_module()

    with caplog.at_level(logging.WARNING, logger=module.__name__):
        service = module.EmailNotificationService(
            config={
                "smtp_host": "smtp.example.com",
                "smtp_port": 587,
                "username": "",
                "password": "",
            },
        )

    assert service.username == ""
    assert any("SMTP 配置未完整" in record.getMessage() for record in caplog.records)


def test_send_email_logs_success(monkeypatch, caplog):
    module = load_email_notification_module()
    monkeypatch.setattr(module.smtplib, "SMTP", StubSMTP)
    service = module.EmailNotificationService(
        config={
            "smtp_host": "smtp.example.com",
            "smtp_port": 587,
            "username": "bot@example.com",
            "password": "secret",
            "use_tls": True,
            "from_name": "MyStocks Bot",
        },
    )

    with caplog.at_level(logging.INFO, logger=module.__name__):
        result = service.send_email(["alice@example.com"], "hello", "<p>world</p>")

    assert result is True
    assert any("邮件已成功发送到" in record.getMessage() for record in caplog.records)


def test_send_email_logs_smtp_errors(monkeypatch, caplog):
    module = load_email_notification_module()

    class FailingSMTP:
        def __init__(self, *_args, **_kwargs):
            pass

        def starttls(self):
            return None

        def login(self, *_args, **_kwargs):
            raise module.smtplib.SMTPException("auth failed")

    monkeypatch.setattr(module.smtplib, "SMTP", FailingSMTP)
    service = module.EmailNotificationService(
        config={
            "smtp_host": "smtp.example.com",
            "smtp_port": 587,
            "username": "bot@example.com",
            "password": "secret",
            "use_tls": True,
        },
    )

    with caplog.at_level(logging.ERROR, logger=module.__name__):
        result = service.send_email(["alice@example.com"], "hello", "<p>world</p>")

    assert result is False
    assert any("发送邮件时发生 SMTP 错误" in record.getMessage() for record in caplog.records)
    assert any(record.exc_info is not None for record in caplog.records)
