import importlib


def test_quality_metrics_module_imports_after_split():
    module = importlib.import_module("tests.metrics.test_quality_metrics.test_quality_metrics")

    assert hasattr(module, "MetricCategory")
    assert hasattr(module, "TestSuiteMetrics")
    assert hasattr(module, "TestQualityMetrics")


def test_report_generator_module_imports_after_split():
    module = importlib.import_module("tests.reporting.test_report_generator.test_report_generator")

    assert hasattr(module, "ReportFormat")
    assert hasattr(module, "TestMetrics")
    assert hasattr(module, "TestReportGenerator")


def test_enhanced_monitor_module_imports_after_split():
    module = importlib.import_module("tests.monitoring.test_monitoring_alerts.enhanced_test_monitor")

    assert hasattr(module, "TestAlertManager")
    assert hasattr(module, "DynamicPerformanceOptimizer")
    assert hasattr(module, "EnhancedTestMonitor")
