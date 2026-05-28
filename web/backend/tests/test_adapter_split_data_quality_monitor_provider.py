from __future__ import annotations

import importlib


class FakeDataQualityMonitor:
    def __init__(self) -> None:
        self.check_calls = []
        self.evaluate_calls = []

    def check_data_quality(self, data, source_or_context):
        self.check_calls.append((data, source_or_context))
        return {"is_valid": True}

    async def evaluate_data_quality(self, *args, **kwargs):
        self.evaluate_calls.append((args, kwargs))
        return {"is_valid": True}


def _fail_global_getter():
    raise AssertionError("global get_data_quality_monitor() should not be called when a monitor is injected")


def test_adapter_split_constructors_accept_injected_quality_monitor(monkeypatch):
    base_module = importlib.import_module("app.services.adapters_split.base_adapter")
    adapter_modules = [
        importlib.import_module("app.services.adapters_split.baostock_adapter"),
        importlib.import_module("app.services.adapters_split.tushare_adapter"),
        importlib.import_module("app.services.adapters_split.customer_adapter"),
        importlib.import_module("app.services.adapters_split.byapi_adapter"),
        importlib.import_module("app.services.adapters_split.akshare_adapter"),
        importlib.import_module("app.services.adapters_split.efinance_adapter"),
        importlib.import_module("app.services.adapters_split.tdx_adapter"),
    ]

    monkeypatch.setattr(base_module, "get_data_quality_monitor", _fail_global_getter)
    for module in adapter_modules:
        monkeypatch.setattr(module, "get_data_quality_monitor", _fail_global_getter, raising=False)

    customer_module = adapter_modules[2]
    monkeypatch.setattr(customer_module.asyncio, "create_task", lambda coro: coro.close() or object())

    fake = FakeDataQualityMonitor()
    adapter_specs = [
        (adapter_modules[0].BaostockAdapter, {}),
        (adapter_modules[1].TushareAdapter, {}),
        (adapter_modules[2].CustomerAdapter, {"ws_url": "ws://localhost:8020/ws"}),
        (adapter_modules[3].BYAPIAdapter, {}),
        (adapter_modules[4].AkshareAdapter, {}),
        (adapter_modules[5].EfinanceAdapter, {}),
        (adapter_modules[6].TDXAdapter, {}),
    ]
    for adapter_cls, _ in adapter_specs:
        monkeypatch.setattr(adapter_cls, "__abstractmethods__", frozenset())

    adapters = [adapter_cls(quality_monitor=fake, **kwargs) for adapter_cls, kwargs in adapter_specs]

    assert all(adapter.quality_monitor is fake for adapter in adapters)

    adapters[0]._log_data_quality([{"symbol": "000001"}], "probe")

    assert fake.check_calls == [([{"symbol": "000001"}], "Baostock.probe")]
