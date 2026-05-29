from __future__ import annotations

import importlib
from pathlib import Path

import pytest

from app.mock.mock_data.core import UnifiedMockDataManager


def test_mock_data_core_source_contains_no_direct_use_mock_env_reads():
    source = Path("web/backend/app/mock/mock_data/core.py").read_text(encoding="utf-8")

    assert 'os.getenv("USE_MOCK_DATA"' not in source


def test_mock_data_manager_uses_settings_when_flag_not_explicit(monkeypatch):
    monkeypatch.setattr("app.mock.mock_data.core.settings.use_mock_apis", True)

    manager = UnifiedMockDataManager()

    assert manager.use_mock_data is True


def test_mock_data_manager_explicit_flag_overrides_settings(monkeypatch):
    monkeypatch.setattr("app.mock.mock_data.core.settings.use_mock_apis", True)

    manager = UnifiedMockDataManager(use_mock_data=False)

    assert manager.use_mock_data is False


def test_mock_data_manager_uses_settings_backed_fallback_flag(monkeypatch):
    monkeypatch.setattr("app.mock.mock_data.core.settings.fallback_enabled", False)

    manager = UnifiedMockDataManager()

    assert manager.fallback_enabled is False


def test_mock_data_manager_does_not_silently_fallback_when_disabled(monkeypatch):
    manager = UnifiedMockDataManager(use_mock_data=False, fallback_enabled=False)
    monkeypatch.setattr(manager, "_is_cache_valid", lambda _key: False)
    monkeypatch.setattr(manager, "_get_real_data", lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("real failed")))
    monkeypatch.setattr(manager, "_get_mock_data", lambda *_args, **_kwargs: {"mock": True})

    with pytest.raises(RuntimeError) as exc_info:
        manager.get_data("watchlist")

    assert str(exc_info.value) == "real failed"


def test_mock_data_manager_allows_fallback_when_enabled(monkeypatch):
    manager = UnifiedMockDataManager(use_mock_data=False, fallback_enabled=True)
    monkeypatch.setattr(manager, "_is_cache_valid", lambda _key: False)
    monkeypatch.setattr(manager, "_get_real_data", lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("real failed")))
    monkeypatch.setattr(manager, "_get_mock_data", lambda *_args, **_kwargs: {"mock": True})

    result = manager.get_data("watchlist")

    assert result["mock"] is True


def test_mock_data_manager_provider_can_be_overridden_and_reset():
    factory = importlib.import_module("app.mock.mock_data.factory")

    class TestDoubleManager:
        def get_data(self, data_type, **kwargs):
            return {"source": "test-double", "data_type": data_type, "kwargs": kwargs}

    factory.set_mock_data_manager_provider(lambda: TestDoubleManager())

    try:
        manager = factory.get_mock_data_manager()

        assert manager.get_data("watchlist", user_id=1) == {
            "source": "test-double",
            "data_type": "watchlist",
            "kwargs": {"user_id": 1},
        }
    finally:
        factory.reset_mock_data_manager_provider()

    assert not isinstance(factory.get_mock_data_manager(), TestDoubleManager)
