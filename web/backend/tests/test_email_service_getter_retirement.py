from __future__ import annotations

from app.services import email_service


def test_legacy_getter_and_module_singleton_are_retired():
    assert hasattr(email_service, "EmailService")
    assert hasattr(email_service, "install_email_service")
    assert hasattr(email_service, "get_email_service_dependency")
    assert not hasattr(email_service, "get_email_service")
    assert not hasattr(email_service, "_email_service")
