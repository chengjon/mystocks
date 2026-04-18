import importlib


def test_dashboard_test_package_re_exports_split_symbols():
    package = importlib.import_module("tests.dashboard.test_dashboard")
    source = importlib.import_module("tests.dashboard.test_dashboard.dashboard_widget_type")

    assert package.DashboardWidgetType is source.DashboardWidgetType
    assert package.DashboardMetric is source.DashboardMetric
    assert package.TestDashboard is source.TestDashboard


def test_reporting_test_package_re_exports_split_symbols():
    package = importlib.import_module("tests.reporting.test_report_generator")
    source = importlib.import_module("tests.reporting.test_report_generator.report_format")

    assert package.ReportFormat is source.ReportFormat
    assert package.ReportType is source.ReportType
    assert package.PDFReportGenerator is source.PDFReportGenerator


def test_metrics_test_package_re_exports_split_symbols():
    package = importlib.import_module("tests.metrics.test_quality_metrics")
    source = importlib.import_module("tests.metrics.test_quality_metrics.metric_category")

    assert package.MetricCategory is source.MetricCategory
    assert package.MetricWeight is source.MetricWeight
    assert package.TestSuiteMetrics is source.TestSuiteMetrics
