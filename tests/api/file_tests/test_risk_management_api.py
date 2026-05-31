"""
File-level compatibility contract tests for risk_management.py.

当前文件已经退化为兼容 shim，这里验证它是否仍然正确重导出
`app.api.risk` 的路由面，并保留弃用提示。
"""

from __future__ import annotations

import importlib
import inspect
import sys
import warnings
from pathlib import Path

import pytest
from fastapi.params import Depends as DependsParam


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture
def risk_management_module(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("POSTGRESQL_HOST", "localhost")
    monkeypatch.setenv("POSTGRESQL_USER", "postgres")
    monkeypatch.setenv("POSTGRESQL_PASSWORD", "password")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("BACKEND_PORT", "8020")
    monkeypatch.setenv("BACKEND_BACKUP_PORT", "8021")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return importlib.import_module("app.api.risk_management")


class TestRiskManagementAPIFile:
    @pytest.mark.file_test
    @pytest.mark.contract_test
    def test_compat_shim_emits_deprecation_warning_on_reload(self, risk_management_module):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            importlib.reload(risk_management_module)

        try:
            assert any("deprecated" in str(item.message) for item in caught)
        finally:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                importlib.reload(risk_management_module)

    @pytest.mark.file_test
    def test_router_exports_expected_number_of_http_and_websocket_routes(self, risk_management_module):
        http_routes = [route for route in risk_management_module.router.routes if getattr(route, "methods", None)]
        websocket_routes = [route for route in risk_management_module.router.routes if not getattr(route, "methods", None)]

        assert len(http_routes) == 36
        assert len(websocket_routes) == 1

    @pytest.mark.file_test
    def test_router_contains_core_risk_metric_routes(self, risk_management_module):
        route_methods = {(route.path, tuple(sorted(route.methods or []))) for route in risk_management_module.router.routes if getattr(route, "methods", None)}

        assert ("/api/v1/risk/var-cvar", ("POST",)) in route_methods
        assert ("/api/v1/risk/beta", ("POST",)) in route_methods
        assert ("/api/v1/risk/dashboard", ("GET",)) in route_methods
        assert ("/api/v1/risk/metrics/history", ("GET",)) in route_methods
        assert ("/api/v1/risk/metrics/calculate", ("POST",)) in route_methods
        assert ("/api/v1/risk/position/assess", ("POST",)) in route_methods

    @pytest.mark.file_test
    def test_router_contains_stop_loss_and_alert_routes(self, risk_management_module):
        route_methods = {(route.path, tuple(sorted(route.methods or []))) for route in risk_management_module.router.routes if getattr(route, "methods", None)}

        assert ("/api/v1/risk/v31/stop-loss/add-position", ("POST",)) in route_methods
        assert ("/api/v1/risk/v31/stop-loss/update-price", ("POST",)) in route_methods
        assert ("/api/v1/risk/v31/stop-loss/remove-position/{position_id}", ("DELETE",)) in route_methods
        assert ("/api/v1/risk/v31/stop-loss/status/{position_id}", ("GET",)) in route_methods
        assert ("/api/v1/risk/v31/alert/send", ("POST",)) in route_methods
        assert ("/api/v1/risk/v31/alert/statistics", ("GET",)) in route_methods
        assert ("/api/v1/risk/alerts", ("GET",)) in route_methods
        assert ("/api/v1/risk/alerts", ("POST",)) in route_methods

    @pytest.mark.file_test
    def test_router_contains_v31_health_and_realtime_routes(self, risk_management_module):
        route_methods = {(route.path, tuple(sorted(route.methods or []))) for route in risk_management_module.router.routes if getattr(route, "methods", None)}

        assert ("/api/v1/risk/v31/risk/realtime/{symbol}", ("GET",)) in route_methods
        assert ("/api/v1/risk/v31/stock/{symbol}", ("GET",)) in route_methods
        assert ("/api/v1/risk/v31/portfolio/{portfolio_id}", ("GET",)) in route_methods
        assert ("/api/v1/risk/v31/health", ("GET",)) in route_methods

    @pytest.mark.file_test
    def test_route_names_remain_stable_for_key_operations(self, risk_management_module):
        route_names = {
            (route.path, tuple(sorted(route.methods or []))): route.name
            for route in risk_management_module.router.routes
            if getattr(route, "methods", None)
        }

        assert route_names[("/api/v1/risk/var-cvar", ("POST",))] == "calculate_var_cvar"
        assert route_names[("/api/v1/risk/beta", ("POST",))] == "calculate_beta"
        assert route_names[("/api/v1/risk/dashboard", ("GET",))] == "get_risk_dashboard"
        assert route_names[("/api/v1/risk/v31/alerts/{alert_id}/acknowledge", ("POST",))] == "acknowledge_alert_v31"

    @pytest.mark.file_test
    def test_router_contains_expected_response_models_for_core_metrics(self, risk_management_module):
        response_models = {
            (route.path, tuple(sorted(route.methods or []))): route.response_model
            for route in risk_management_module.router.routes
            if getattr(route, "methods", None)
        }

        assert response_models[("/api/v1/risk/var-cvar", ("POST",))].__name__ == "VaRCVaRResult"
        assert response_models[("/api/v1/risk/beta", ("POST",))].__name__ == "BetaResult"
        assert response_models[("/api/v1/risk/dashboard", ("GET",))].__name__ == "RiskDashboardResponse"
        assert response_models[("/api/v1/risk/alerts", ("POST",))].__name__ == "RiskAlertResponse"

    @pytest.mark.file_test
    def test_risk_monitoring_db_uses_route_dependency_provider(self):
        from app.api.risk import _shared, alerts, metrics

        assert hasattr(_shared, "get_risk_monitoring_db")
        provider = _shared.get_risk_monitoring_db

        target_handlers = [
            alerts.create_risk_alert,
            metrics.calculate_var_cvar,
            metrics.calculate_beta,
        ]

        for handler in target_handlers:
            signature = inspect.signature(handler)
            dependency = signature.parameters["monitoring_db"].default
            assert isinstance(dependency, DependsParam)
            assert dependency.dependency is provider
            assert "get_monitoring_db()" not in inspect.getsource(handler)

    @pytest.mark.file_test
    def test_module_docstring_describes_compatibility_shim_and_split_targets(self, risk_management_module):
        doc = risk_management_module.__doc__ or ""

        assert "Compatibility shim" in doc
        assert "risk/metrics.py" in doc
        assert "risk/stop_loss.py" in doc
        assert "risk/alerts.py" in doc
        assert "risk/v31.py" in doc

    @pytest.mark.file_test
    def test_module_exports_only_router(self, risk_management_module):
        assert risk_management_module.__all__ == ["router"]

    @pytest.mark.file_test
    @pytest.mark.contract_test
    def test_contract_fixture_still_covers_risk_management_domain(self, contract_specs):
        spec = contract_specs["risk-management"]

        assert spec["info"]["version"] == "1.0.0"
        assert spec["openapi"] == "3.0.3"
        assert "/var-cvar" in spec["paths"]
        assert "/beta" in spec["paths"]
        assert "/dashboard" in spec["paths"]
