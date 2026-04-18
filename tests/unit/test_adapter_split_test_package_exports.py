import importlib


def test_akshare_adapter_package_re_exports_split_symbols():
    package = importlib.import_module("tests.adapters.test_akshare_adapter")
    helpers = importlib.import_module("tests.adapters.test_akshare_adapter.helpers")
    market_adapter = importlib.import_module("tests.adapters.test_akshare_adapter.test_akshare_market_data_adapter")

    assert package.TestAkshareDataSourceInit is helpers.TestAkshareDataSourceInit
    assert package.TestAkshareDataSourceMinuteKline is helpers.TestAkshareDataSourceMinuteKline
    assert package.TestAkshareMarketDataAdapter is market_adapter.TestAkshareMarketDataAdapter


def test_akshare_market_data_adapter_methods_package_exports_composed_class():
    package = importlib.import_module("tests.adapters.test_akshare_adapter.test_akshare_market_data_adapter_methods")
    part1 = importlib.import_module("tests.adapters.test_akshare_adapter.test_akshare_market_data_adapter_methods.part1")
    part2 = importlib.import_module("tests.adapters.test_akshare_adapter.test_akshare_market_data_adapter_methods.part2")
    part3 = importlib.import_module("tests.adapters.test_akshare_adapter.test_akshare_market_data_adapter_methods.part3")

    adapter_cls = package.TestAkshareMarketDataAdapter

    assert issubclass(adapter_cls, part1.TestAkshareMarketDataAdapterCoreMixin)
    assert issubclass(adapter_cls, part2.TestAkshareMarketDataAdapterTestGetStockMixin)
    assert issubclass(adapter_cls, part3.TestAkshareMarketDataAdapterAnalyticsMixin)
