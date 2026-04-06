"""
File-level route aggregation tests for the active cache API.

这里覆盖缓存聚合入口的真实路由面，以及清缓存入口的关键行为。
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture
def cache_module(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("POSTGRESQL_HOST", "localhost")
    monkeypatch.setenv("POSTGRESQL_USER", "postgres")
    monkeypatch.setenv("POSTGRESQL_PASSWORD", "password")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("BACKEND_PORT", "8020")
    monkeypatch.setenv("BACKEND_BACKUP_PORT", "8021")
    return importlib.import_module("app.api.cache")


class TestCacheAPIFile:
    @pytest.mark.file_test
    def test_router_registers_expected_cache_routes(self, cache_module):
        route_methods = {(route.path, tuple(sorted(route.methods or []))) for route in cache_module.router.routes}

        assert cache_module.router.prefix == "/cache"
        assert cache_module.router.tags == ["cache"]
        assert ("/cache", ("DELETE",)) in route_methods
        assert ("/cache/status", ("GET",)) in route_methods
        assert ("/cache/{symbol}/{data_type}", ("GET",)) in route_methods
        assert ("/cache/{symbol}/{data_type}", ("POST",)) in route_methods
        assert ("/cache/{symbol}", ("DELETE",)) in route_methods
        assert ("/cache/{symbol}/{data_type}/fresh", ("GET",)) in route_methods
        assert ("/cache/evict/manual", ("POST",)) in route_methods
        assert ("/cache/eviction/stats", ("GET",)) in route_methods
        assert ("/cache/prewarming/trigger", ("POST",)) in route_methods
        assert ("/cache/prewarming/status", ("GET",)) in route_methods
        assert ("/cache/monitoring/metrics", ("GET",)) in route_methods
        assert ("/cache/monitoring/health", ("GET",)) in route_methods

    @pytest.mark.file_test
    def test_router_contains_expected_number_of_route_method_pairs(self, cache_module):
        route_pairs = [(route.path, tuple(sorted(route.methods or []))) for route in cache_module.router.routes]

        assert len(route_pairs) == 12
        assert len(route_pairs) == len(set(route_pairs))

    @pytest.mark.file_test
    def test_clear_all_cache_rejects_missing_confirmation(self, cache_module):
        user = SimpleNamespace(username="tester")

        with pytest.raises(cache_module.BusinessException) as excinfo:
            import asyncio

            asyncio.run(cache_module.clear_all_cache(confirm=False, current_user=user))

        assert excinfo.value.status_code == 400
        assert excinfo.value.error_code == "INVALID_CACHE_REQUEST"

    @pytest.mark.file_test
    def test_clear_all_cache_returns_deleted_count_when_confirmed(self, cache_module, monkeypatch):
        cache_manager = Mock()
        cache_manager.invalidate_cache.return_value = 7
        monkeypatch.setattr(cache_module, "get_cache_manager", Mock(return_value=cache_manager))
        monkeypatch.setattr(cache_module, "_timestamp", Mock(return_value="2026-04-01T00:00:00+00:00"))
        user = SimpleNamespace(username="tester")

        import asyncio

        payload = asyncio.run(cache_module.clear_all_cache(confirm=True, current_user=user))

        assert payload == {
            "success": True,
            "message": "所有缓存已清除",
            "deleted_count": 7,
            "timestamp": "2026-04-01T00:00:00+00:00",
        }

    @pytest.mark.file_test
    def test_timestamp_helper_returns_iso8601_string(self, cache_module):
        value = cache_module._timestamp()

        assert "T" in value
        assert value.endswith("+00:00")

    @pytest.mark.file_test
    def test_router_contains_manual_eviction_and_prewarming_domains(self, cache_module):
        route_paths = {route.path for route in cache_module.router.routes}

        assert any(path.startswith("/cache/evict/") for path in route_paths)
        assert any(path.startswith("/cache/prewarming/") for path in route_paths)
        assert any(path.startswith("/cache/monitoring/") for path in route_paths)

    @pytest.mark.file_test
    def test_route_names_remain_stable_for_key_operations(self, cache_module):
        route_names = {(route.path, tuple(sorted(route.methods or []))): route.name for route in cache_module.router.routes}

        assert route_names[("/cache", ("DELETE",))] == "clear_all_cache"
        assert route_names[("/cache/status", ("GET",))] == "get_cache_status"
        assert route_names[("/cache/prewarming/trigger", ("POST",))] == "trigger_cache_prewarming"

    @pytest.mark.file_test
    def test_package_exports_router_in___all__(self, cache_module):
        assert cache_module.__all__ == ["router"]

    @pytest.mark.file_test
    def test_docstring_mentions_cache_aggregation_entry(self, cache_module):
        assert "聚合入口" in (cache_module.__doc__ or "")

    @pytest.mark.file_test
    def test_symbol_data_type_path_supports_read_and_write(self, cache_module):
        methods = [tuple(sorted(route.methods or [])) for route in cache_module.router.routes if route.path == "/cache/{symbol}/{data_type}"]

        assert sorted(methods) == [("GET",), ("POST",)]
