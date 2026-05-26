from __future__ import annotations

import app.services.stock_search_service as stock_search_service_package
from app.services.stock_search_service import stock_search_service as stock_search_service_module


def test_legacy_getter_and_module_singleton_are_retired():
    for target in (stock_search_service_package, stock_search_service_module):
        assert hasattr(target, "StockSearchService")
        assert hasattr(target, "install_stock_search_service")
        assert hasattr(target, "get_stock_search_service_dependency")
        assert not hasattr(target, "get_stock_search_service")

    assert not hasattr(stock_search_service_module, "_stock_search_service")
