from __future__ import annotations

from pathlib import Path

import pytest


SOURCE_FILES = [
    "web/backend/app/core/password_policy.py",
    "web/backend/app/core/data_formats.py",
    "web/backend/app/core/adapter_factory.py",
    "web/backend/app/services/data_service_enhanced.py",
    "web/backend/app/services/redis/redis_pubsub.py",
    "web/backend/app/api/realtime_mtm_init.py",
]


@pytest.mark.parametrize("module_path", SOURCE_FILES)
def test_demo_and_example_modules_source_contains_no_print_statements(module_path: str):
    source = Path(module_path).read_text(encoding="utf-8")

    assert "print(" not in source
