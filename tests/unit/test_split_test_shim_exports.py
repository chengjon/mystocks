import importlib


def test_reporting_shim_re_exports_split_package_symbols():
    shim = importlib.import_module("tests.reporting.test_report_generator")
    package = importlib.import_module("tests.reporting.test_report_generator")
    report_format = importlib.import_module("tests.reporting.test_report_generator.report_format")

    assert shim.ReportFormat is package.ReportFormat
    assert shim.PDFReportGenerator is report_format.PDFReportGenerator


def test_metrics_shim_re_exports_split_package_symbols():
    shim = importlib.import_module("tests.metrics.test_quality_metrics")
    package = importlib.import_module("tests.metrics.test_quality_metrics")
    metric_category = importlib.import_module("tests.metrics.test_quality_metrics.metric_category")

    assert shim.MetricCategory is package.MetricCategory
    assert shim.TestSuiteMetrics is metric_category.TestSuiteMetrics


def test_ai_shims_re_export_split_package_symbols():
    ai_assisted = importlib.import_module("tests.ai.test_ai_assisted_testing")
    ai_assisted_utils = importlib.import_module("tests.ai.test_ai_assisted_testing.utils")
    data_analyzer = importlib.import_module("tests.ai.test_data_analyzer")
    pattern_module = importlib.import_module("tests.ai.test_data_analyzer.test_pattern")

    assert ai_assisted.AITestAssistant is ai_assisted_utils.AITestAssistant
    assert data_analyzer.TestPattern is pattern_module.TestPattern
