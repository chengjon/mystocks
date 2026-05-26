"""Regression tests for retiring unused IntegratedServices facade getters."""

from __future__ import annotations

import importlib


REMOVED_SERVICE_FACADE_GETTERS = (
    "get_trading_data_service",
    "get_analysis_data_service",
    "get_data_api_service",
    "get_database_service",
    "get_websocket_service",
    "get_cache_service",
)

LOCKED_FACADE_GETTERS = (
    "get_integrated_services",
    "get_market_data_service",
    "get_risk_calculator",
    "get_risk_monitoring",
    "get_risk_alerts",
    "get_risk_settings",
    "get_risk_dashboard",
)


def test_unused_integrated_services_facade_getters_are_retired() -> None:
    services = importlib.import_module("app.services")

    for getter_name in REMOVED_SERVICE_FACADE_GETTERS:
        assert not hasattr(services, getter_name), f"{getter_name} should not remain on app.services"


def test_locked_integrated_services_facade_getters_remain_available() -> None:
    services = importlib.import_module("app.services")

    for getter_name in LOCKED_FACADE_GETTERS:
        assert callable(getattr(services, getter_name, None)), f"{getter_name} should remain callable"
