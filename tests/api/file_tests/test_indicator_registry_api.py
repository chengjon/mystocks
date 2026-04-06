"""
File-level route and model contract tests for indicator_registry.py.

这里对齐当前真实的 3 个端点、工厂单例和请求/响应模型，
替换掉生成式占位断言。
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture
def indicator_registry_module(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("POSTGRESQL_HOST", "localhost")
    monkeypatch.setenv("POSTGRESQL_USER", "postgres")
    monkeypatch.setenv("POSTGRESQL_PASSWORD", "password")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("BACKEND_PORT", "8020")
    monkeypatch.setenv("BACKEND_BACKUP_PORT", "8021")
    return importlib.import_module("app.api.indicator_registry")


class TestIndicatorRegistryAPIFile:
    @pytest.mark.file_test
    def test_router_registers_expected_indicator_registry_routes(self, indicator_registry_module):
        route_methods = {(route.path, tuple(sorted(route.methods or []))) for route in indicator_registry_module.router.routes}

        assert indicator_registry_module.router.prefix == "/api/indicator-registry"
        assert indicator_registry_module.router.tags == ["Indicator Registry"]
        assert ("/api/indicator-registry/indicators", ("GET",)) in route_methods
        assert ("/api/indicator-registry/indicators/{indicator_id}", ("GET",)) in route_methods
        assert ("/api/indicator-registry/calculate", ("POST",)) in route_methods

    @pytest.mark.file_test
    def test_router_contains_expected_number_of_routes(self, indicator_registry_module):
        route_pairs = [(route.path, tuple(sorted(route.methods or []))) for route in indicator_registry_module.router.routes]

        assert len(route_pairs) == 3
        assert len(route_pairs) == len(set(route_pairs))

    @pytest.mark.file_test
    def test_response_models_remain_stable(self, indicator_registry_module):
        response_models = {(route.path, tuple(sorted(route.methods or []))): route.response_model for route in indicator_registry_module.router.routes}

        assert response_models[("/api/indicator-registry/indicators", ("GET",))] == indicator_registry_module.List[
            indicator_registry_module.IndicatorInfo
        ]
        assert response_models[("/api/indicator-registry/indicators/{indicator_id}", ("GET",))] is None
        assert response_models[("/api/indicator-registry/calculate", ("POST",))] is indicator_registry_module.CalculationResponse

    @pytest.mark.file_test
    def test_route_names_remain_stable(self, indicator_registry_module):
        route_names = {(route.path, tuple(sorted(route.methods or []))): route.name for route in indicator_registry_module.router.routes}

        assert route_names[("/api/indicator-registry/indicators", ("GET",))] == "list_indicators"
        assert route_names[("/api/indicator-registry/indicators/{indicator_id}", ("GET",))] == "get_indicator_details"
        assert route_names[("/api/indicator-registry/calculate", ("POST",))] == "calculate_indicator"

    @pytest.mark.file_test
    def test_get_factory_behaves_as_singleton(self, indicator_registry_module, monkeypatch):
        fake_factory = Mock()
        factory_class = Mock(return_value=fake_factory)
        monkeypatch.setattr(indicator_registry_module, "IndicatorFactory", factory_class)
        monkeypatch.setattr(indicator_registry_module, "_factory", None)

        first = indicator_registry_module.get_factory()
        second = indicator_registry_module.get_factory()

        assert first is fake_factory
        assert second is fake_factory
        factory_class.assert_called_once_with()

    @pytest.mark.file_test
    def test_indicator_info_model_fields_remain_stable(self, indicator_registry_module):
        fields = set(indicator_registry_module.IndicatorInfo.model_fields)

        assert fields == {
            "indicator_id",
            "indicator_name",
            "indicator_category",
            "use_case",
            "description",
            "status",
        }

    @pytest.mark.file_test
    def test_calculation_models_expose_expected_fields(self, indicator_registry_module):
        request_fields = set(indicator_registry_module.CalculationRequest.model_fields)
        response_fields = set(indicator_registry_module.CalculationResponse.model_fields)

        assert request_fields == {"indicator_id", "data", "parameters"}
        assert response_fields == {"indicator_id", "result", "length"}

    @pytest.mark.file_test
    def test_calculation_request_default_parameters_is_empty_mapping(self, indicator_registry_module):
        req = indicator_registry_module.CalculationRequest(indicator_id="sma", data=[{"close": 1.0}])

        assert req.parameters == {}

    @pytest.mark.file_test
    def test_docstrings_cover_listing_details_and_calculation(self, indicator_registry_module):
        assert "List all registered indicators." in (indicator_registry_module.list_indicators.__doc__ or "")
        assert "Get detailed configuration" in (indicator_registry_module.get_indicator_details.__doc__ or "")
        assert "Run a batch calculation." in (indicator_registry_module.calculate_indicator.__doc__ or "")

    @pytest.mark.file_test
    def test_module_prefix_implies_all_routes_share_same_namespace(self, indicator_registry_module):
        assert all(route.path.startswith("/api/indicator-registry") for route in indicator_registry_module.router.routes)
