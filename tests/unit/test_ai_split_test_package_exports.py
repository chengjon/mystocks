import importlib


def test_ai_assisted_testing_package_re_exports_split_symbols():
    package = importlib.import_module("tests.ai.test_ai_assisted_testing")
    helpers = importlib.import_module("tests.ai.test_ai_assisted_testing.helpers")
    utils = importlib.import_module("tests.ai.test_ai_assisted_testing.utils")

    assert package.TestPriority is helpers.TestPriority
    assert package.TestCategory is helpers.TestCategory
    assert package.AITestAssistant is utils.AITestAssistant
    assert package.IntelligentTestOptimizer is utils.IntelligentTestOptimizer


def test_ai_data_analyzer_package_re_exports_split_symbols():
    package = importlib.import_module("tests.ai.test_data_analyzer")
    pattern_module = importlib.import_module("tests.ai.test_data_analyzer.test_pattern")
    recognizer_module = importlib.import_module("tests.ai.test_data_analyzer.pattern_recognizer")

    assert package.TestPattern is pattern_module.TestPattern
    assert package.AITestDataAnalyzer is pattern_module.AITestDataAnalyzer
    assert package.PatternRecognizer is recognizer_module.PatternRecognizer
    assert package.TestDataAnalyzer is recognizer_module.TestDataAnalyzer
