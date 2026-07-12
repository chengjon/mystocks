from __future__ import annotations

import importlib.util
import logging
import sys
from pathlib import Path
from types import ModuleType


def load_stock_search_service_module():
    package_name = "app.services.stock_search_service"
    module_name = "app.services.stock_search_service.stock_search_service"
    module_paths = {
        "app.services.stock_search_service.parse_datetime_to_timestamp": Path(
            "web/backend/app/services/stock_search_service/parse_datetime_to_timestamp.py",
        ),
        "app.services.stock_search_service.kline_fallback": Path(
            "web/backend/app/services/stock_search_service/kline_fallback.py",
        ),
        "app.services.stock_search_service._stock_search_cn": Path(
            "web/backend/app/services/stock_search_service/_stock_search_cn.py",
        ),
        "app.services.stock_search_service._stock_search_hk": Path(
            "web/backend/app/services/stock_search_service/_stock_search_hk.py",
        ),
        "app.services.stock_search_service._stock_search_finnhub": Path(
            "web/backend/app/services/stock_search_service/_stock_search_finnhub.py",
        ),
    }

    fake_app = ModuleType("app")
    fake_services = ModuleType("app.services")
    fake_package = ModuleType(package_name)
    fake_app.__path__ = []
    fake_services.__path__ = []
    fake_package.__path__ = [str(Path("web/backend/app/services/stock_search_service").resolve())]

    previous = {
        "app": sys.modules.get("app"),
        "app.services": sys.modules.get("app.services"),
        package_name: sys.modules.get(package_name),
        module_name: sys.modules.get(module_name),
    }

    for dotted_name in module_paths:
        previous[dotted_name] = sys.modules.get(dotted_name)

    sys.modules["app"] = fake_app
    sys.modules["app.services"] = fake_services
    sys.modules[package_name] = fake_package

    for dotted_name, module_path in module_paths.items():
        spec = importlib.util.spec_from_file_location(dotted_name, module_path)
        module = importlib.util.module_from_spec(spec)
        assert spec is not None and spec.loader is not None
        sys.modules[dotted_name] = module
        spec.loader.exec_module(module)

    spec = importlib.util.spec_from_file_location(
        module_name,
        Path("web/backend/app/services/stock_search_service/stock_search_service.py"),
    )
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    for name, previous_module in previous.items():
        if previous_module is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = previous_module

    return module


def test_stock_search_service_source_contains_no_print_statements():
    source = Path("web/backend/app/services/stock_search_service/stock_search_service.py").read_text(encoding="utf-8")

    assert "print(" not in source


def test_stock_search_service_split_helpers_load():
    module = load_stock_search_service_module()

    assert callable(module.StockSearchService)
    assert callable(module.get_stock_search_service)


def test_search_stocks_logs_finnhub_errors(monkeypatch, caplog):
    module = load_stock_search_service_module()
    service = module.StockSearchService()

    def raise_api_error(_endpoint, _params=None):
        raise module.FinnhubAPIError("upstream exploded")

    monkeypatch.setattr(service, "_make_request", raise_api_error)

    with caplog.at_level(logging.ERROR, logger=module.__name__):
        result = service.search_stocks("AAPL")

    assert result == []
    assert any("搜索股票时发生错误" in record.getMessage() for record in caplog.records)
    assert any(record.exc_info is not None for record in caplog.records)


def test_search_a_stocks_logs_warning_when_akshare_unavailable(caplog):
    module = load_stock_search_service_module()
    service = module.StockSearchService()
    service.akshare_available = False

    with caplog.at_level(logging.WARNING, logger=module.__name__):
        result = service.search_a_stocks("平安")

    assert result == []
    assert any(record.levelno == logging.WARNING and "A股搜索失败" in record.getMessage() for record in caplog.records)


def test_get_a_stock_kline_logs_warning_for_invalid_period(caplog):
    module = load_stock_search_service_module()
    service = module.StockSearchService()

    with caplog.at_level(logging.WARNING, logger=module.__name__):
        result = service.get_a_stock_kline("600519", period="hourly")

    assert result is None
    assert any(record.levelno == logging.WARNING and "无效的时间周期" in record.getMessage() for record in caplog.records)
