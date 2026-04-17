from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from app.api import data_quality as module


def test_data_quality_source_contains_no_direct_use_mock_env_reads():
    source = Path(module.__file__).read_text(encoding="utf-8")

    assert 'os.getenv("USE_MOCK_DATA"' not in source


@pytest.mark.asyncio
async def test_data_quality_mode_snapshot_uses_settings_backed_mock_flag(monkeypatch):
    monkeypatch.setattr(module.settings, "use_mock_apis", True, raising=False)
    monkeypatch.setattr(module, "get_factory_mode", lambda: SimpleNamespace(value="hybrid"))
    monkeypatch.setattr(module, "is_fallback_enabled", lambda: False)

    response = await module.get_data_source_mode()

    assert response.success is True
    assert response.data["current_mode"] == "hybrid"
    assert response.data["environment_variables"]["USE_MOCK_DATA"] == "true"
    assert response.data["environment_variables"]["REAL_DATA_AVAILABLE"] == "true"
    assert response.data["environment_variables"]["FALLBACK_ENABLED"] == "false"
