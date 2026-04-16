from __future__ import annotations

import importlib
from pathlib import Path

import pytest

module = importlib.import_module("app.api.strategy_management.get_monitoring_db")


class _MonitoringNoop:
    def log_operation(self, *args, **kwargs):
        return True


def test_strategy_management_source_contains_no_direct_use_mock_env_reads():
    source = Path(module.__file__).read_text(encoding="utf-8")

    assert 'os.getenv("USE_MOCK_DATA"' not in source


@pytest.mark.asyncio
async def test_list_strategies_uses_mock_helper_when_enabled(monkeypatch):
    monkeypatch.setattr(module.settings, "use_mock_apis", True, raising=False)
    monkeypatch.setattr(module, "get_monitoring_db", lambda: _MonitoringNoop())
    monkeypatch.setattr(
        module,
        "_get_mock_strategy_list",
        lambda: [{"id": 1, "strategy_id": 1, "strategy_name": "mock-strategy", "status": "draft"}],
    )

    result = await module.list_strategies(status=None, page=1, page_size=20)

    assert result.success is True
    assert result.data["total"] == 1
    assert result.data["items"][0]["strategy_name"] == "mock-strategy"


@pytest.mark.asyncio
async def test_create_strategy_uses_runtime_record_builder_when_mock_enabled(monkeypatch):
    monkeypatch.setattr(module.settings, "use_mock_apis", True, raising=False)
    monkeypatch.setattr(module, "_runtime_fallback_enabled", lambda: False)
    monkeypatch.setattr(
        module,
        "_build_runtime_strategy_record",
        lambda strategy_data, strategy_id=None: {
            "id": 900001,
            "strategy_id": 900001,
            "strategy_name": strategy_data["name"],
            "strategy_type": strategy_data["strategy_type"],
            "description": strategy_data["description"],
            "parameters": strategy_data["parameters"],
            "status": strategy_data["status"],
            "is_mock": strategy_data["is_mock"],
        },
    )

    result = await module.create_strategy(
        strategy_data={"name": "demo", "description": "desc", "strategy_type": "technical", "parameters": {}}
    )

    assert result.success is True
    assert result.data["strategy_name"] == "demo"
    assert result.data["is_mock"] is True
