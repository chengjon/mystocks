from __future__ import annotations

import importlib
from pathlib import Path

import pytest

module = importlib.import_module("app.api.system.system_health")


def test_system_health_source_contains_no_direct_use_mock_env_reads():
    source = Path(module.__file__).read_text(encoding="utf-8")

    assert 'os.getenv("USE_MOCK_DATA"' not in source


@pytest.mark.asyncio
async def test_system_health_uses_settings_backed_mock_switch(monkeypatch):
    monkeypatch.setattr(module.settings, "use_mock_apis", True, raising=False)

    result = await module.system_health()

    assert result["status"] == "healthy"
    assert result["mock_mode"] is True
