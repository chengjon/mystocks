from __future__ import annotations

import inspect

import app.services.data_adapters.dashboard as legacy_dashboard_module
import app.services.data_adapters.data_source as legacy_data_source_module
from app.services.adapters.dashboard_adapter import DashboardDataSourceAdapter as CanonicalDashboardDataSourceAdapter
from app.services.adapters.data_adapter import DataDataSourceAdapter as CanonicalDataDataSourceAdapter
from app.services.data_adapters.dashboard import DashboardDataSourceAdapter as LegacyDashboardDataSourceAdapter
from app.services.data_adapters.data_source import DataDataSourceAdapter as LegacyDataDataSourceAdapter


def test_legacy_data_adapter_modules_reexport_canonical_adapter_classes():
    assert LegacyDashboardDataSourceAdapter is CanonicalDashboardDataSourceAdapter
    assert LegacyDataDataSourceAdapter is CanonicalDataDataSourceAdapter


def test_legacy_data_adapter_modules_do_not_keep_monitor_getter_calls():
    assert "get_data_quality_monitor" not in inspect.getsource(legacy_dashboard_module)
    assert "get_data_quality_monitor" not in inspect.getsource(legacy_data_source_module)
