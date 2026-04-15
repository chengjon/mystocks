from __future__ import annotations

import importlib


def _load_module():
    return importlib.import_module("app.api.system.system_health")


async def test_get_system_logs_does_not_fallback_to_mock_logs_when_db_is_empty():
    module = _load_module()

    def fake_get_system_logs_from_db(**kwargs):
        return [], 0

    def fail_if_mock_called(*args, **kwargs):
        raise AssertionError("mock log fallback should not be used")

    original_get_logs = module.get_system_logs_from_db
    original_get_mock_logs = module.get_mock_system_logs
    module.get_system_logs_from_db = fake_get_system_logs_from_db
    module.get_mock_system_logs = fail_if_mock_called

    try:
        response = await module.get_system_logs(filter_errors=False, limit=100, offset=0, level=None, category=None)
    finally:
        module.get_system_logs_from_db = original_get_logs
        module.get_mock_system_logs = original_get_mock_logs

    assert response.success is True
    assert response.total == 0
    assert response.filtered == 0
    assert response.data == []


async def test_get_logs_summary_does_not_fallback_to_mock_logs_when_db_is_empty():
    module = _load_module()

    def fake_get_system_logs_from_db(**kwargs):
        return [], 0

    def fail_if_mock_called(*args, **kwargs):
        raise AssertionError("mock log fallback should not be used")

    original_get_logs = module.get_system_logs_from_db
    original_get_mock_logs = module.get_mock_system_logs
    module.get_system_logs_from_db = fake_get_system_logs_from_db
    module.get_mock_system_logs = fail_if_mock_called

    try:
        response = await module.get_logs_summary()
    finally:
        module.get_system_logs_from_db = original_get_logs
        module.get_mock_system_logs = original_get_mock_logs

    assert response["success"] is True
    assert response["data"]["total_logs"] == 0
    assert response["data"]["recent_errors_1h"] == 0
    assert response["data"]["category_counts"] == {}
