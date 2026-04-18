import importlib


def test_monitoring_alerts_shim_re_exports_split_package_symbols():
    shim = importlib.import_module("tests.monitoring.test_monitoring_alerts")
    alert_module = importlib.import_module("tests.monitoring.test_monitoring_alerts.alert_severity")
    manager_module = importlib.import_module("tests.monitoring.test_monitoring_alerts.test_alert_manager")

    assert shim.AlertSeverity is alert_module.AlertSeverity
    assert shim.TestMonitor is alert_module.TestMonitor
    assert shim.TestAlertManager is manager_module.TestAlertManager


def test_unit_core_monitoring_shim_re_exports_split_package_symbols():
    shim = importlib.import_module("tests.unit.core.test_monitoring")
    severity_module = importlib.import_module("tests.unit.core.test_monitoring.test_alert_severity")
    global_module = importlib.import_module("tests.unit.core.test_monitoring.test_global_functions")

    assert shim.TestAlertSeverity is severity_module.TestAlertSeverity
    assert shim.TestMetricsCollector is severity_module.TestMetricsCollector
    assert shim.TestGlobalFunctions is global_module.TestGlobalFunctions
