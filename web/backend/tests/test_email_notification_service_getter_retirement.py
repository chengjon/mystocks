from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def load_email_notification_module():
    module_path = Path("web/backend/app/services/email_notification_service.py")
    module_name = "test_email_notification_service_getter_retirement_module"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_legacy_getter_and_module_singleton_are_retired():
    module = load_email_notification_module()

    assert hasattr(module, "EmailNotificationService")
    assert not hasattr(module, "get_email_service")
    assert not hasattr(module, "_email_service")
