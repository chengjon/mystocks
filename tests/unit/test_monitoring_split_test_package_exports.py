import importlib


def test_monitoring_alerts_package_re_exports_split_symbols():
    package = importlib.import_module("tests.monitoring.test_monitoring_alerts")
    alert_module = importlib.import_module("tests.monitoring.test_monitoring_alerts.alert_severity")
    manager_module = importlib.import_module("tests.monitoring.test_monitoring_alerts.test_alert_manager")

    assert package.AlertSeverity is alert_module.AlertSeverity
    assert package.TestMonitor is alert_module.TestMonitor
    assert package.TestAlertManager is manager_module.TestAlertManager
    assert package.DynamicPerformanceOptimizer is manager_module.DynamicPerformanceOptimizer


def test_unit_core_monitoring_package_re_exports_split_symbols():
    package = importlib.import_module("tests.unit.core.test_monitoring")
    severity_module = importlib.import_module("tests.unit.core.test_monitoring.test_alert_severity")
    global_module = importlib.import_module("tests.unit.core.test_monitoring.test_global_functions")

    assert package.TestAlertSeverity is severity_module.TestAlertSeverity
    assert package.TestMetricsCollector is severity_module.TestMetricsCollector
    assert package.TestGlobalFunctions is global_module.TestGlobalFunctions
    assert package.TestIntegrationScenarios is global_module.TestIntegrationScenarios
