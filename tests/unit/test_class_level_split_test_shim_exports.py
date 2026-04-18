import importlib


def test_akshare_market_data_adapter_shim_re_exports_composed_class():
    shim = importlib.import_module("tests.adapters.test_akshare_adapter.test_akshare_market_data_adapter")
    methods_package = importlib.import_module("tests.adapters.test_akshare_adapter.test_akshare_market_data_adapter_methods")
    part1 = importlib.import_module("tests.adapters.test_akshare_adapter.test_akshare_market_data_adapter_methods.part1")
    part2 = importlib.import_module("tests.adapters.test_akshare_adapter.test_akshare_market_data_adapter_methods.part2")
    part3 = importlib.import_module("tests.adapters.test_akshare_adapter.test_akshare_market_data_adapter_methods.part3")

    adapter_cls = shim.TestAkshareMarketDataAdapter

    assert adapter_cls is methods_package.TestAkshareMarketDataAdapter
    assert issubclass(adapter_cls, part1.TestAkshareMarketDataAdapterCoreMixin)
    assert issubclass(adapter_cls, part2.TestAkshareMarketDataAdapterTestGetStockMixin)
    assert issubclass(adapter_cls, part3.TestAkshareMarketDataAdapterAnalyticsMixin)


def test_ai_test_generator_shim_re_exports_composed_class():
    shim = importlib.import_module("tests.ai.test_ai_assisted_testing.ai_test_generator")
    methods_package = importlib.import_module("tests.ai.test_ai_assisted_testing.ai_test_generator_methods")
    part1 = importlib.import_module("tests.ai.test_ai_assisted_testing.ai_test_generator_methods.part1")
    part2 = importlib.import_module("tests.ai.test_ai_assisted_testing.ai_test_generator_methods.part2")

    generator_cls = shim.AITestGenerator

    assert generator_cls is methods_package.AITestGenerator
    assert issubclass(generator_cls, part1.AITestGeneratorCoreMixin)
    assert issubclass(generator_cls, part2.AITestGeneratorCreatePatternSpecificMixin)
