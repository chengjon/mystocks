from __future__ import annotations

from datetime import datetime

import pytest


def test_resolve_backtest_data_source_uses_task_local_provider(monkeypatch):
    from app.tasks import backtest_tasks as module

    fake_data_source = object()
    fallback_data_source = object()

    monkeypatch.setattr(
        module,
        "_get_strategy_data_source",
        lambda: fake_data_source,
        raising=False,
    )

    import app.services.strategy_service as strategy_service_module

    monkeypatch.setattr(
        strategy_service_module,
        "get_strategy_service",
        lambda: fallback_data_source,
    )

    assert module._resolve_backtest_data_source({"data_source_mode": "auto"}) is fake_data_source


def test_run_backtest_task_uses_data_service_singleton(monkeypatch):
    from app.tasks import backtest_tasks as module

    captured = {}
    fake_data_source = object()

    class FakeEngine:
        def __init__(self, strategy_config, backtest_config, data_source, progress_callback):
            captured["strategy_config"] = strategy_config
            captured["backtest_config"] = backtest_config
            captured["data_source"] = data_source
            captured["progress_callback"] = progress_callback

        def run(self):
            return {
                "final_capital": 100000,
                "performance_metrics": {},
                "equity_curve": [],
                "trades": [],
            }

    monkeypatch.setattr(module, "BacktestEngine", FakeEngine)
    monkeypatch.setattr(
        module,
        "_save_backtest_results",
        lambda backtest_id, results: captured.setdefault("saved", results),
    )
    monkeypatch.setattr(module, "_update_backtest_status", lambda *args, **kwargs: None)
    monkeypatch.setattr(module, "get_progress_callback", lambda backtest_id: None)
    monkeypatch.setattr(
        module.run_backtest_task,
        "update_state",
        lambda **kwargs: captured.setdefault("states", []).append(kwargs),
    )

    import app.services.strategy_service as strategy_service_module

    monkeypatch.setattr(strategy_service_module, "get_strategy_service", lambda: fake_data_source)

    result = module.run_backtest_task.run(
        backtest_id=7,
        strategy_config={"name": "demo"},
        backtest_config={"start_date": "2025-01-01", "end_date": "2025-01-31"},
    )

    assert result["final_capital"] == 100000
    assert captured["data_source"] is fake_data_source
    assert captured["backtest_config"]["start_date"] == datetime(2025, 1, 1)
    assert captured["backtest_config"]["end_date"] == datetime(2025, 1, 31)


def test_run_backtest_task_rejects_unsupported_data_source_mode(monkeypatch):
    from app.tasks import backtest_tasks as module

    captured = {}

    monkeypatch.setattr(module, "_save_backtest_results", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        module,
        "_update_backtest_status",
        lambda *args, **kwargs: captured.setdefault("failed", args),
    )
    monkeypatch.setattr(module, "get_progress_callback", lambda backtest_id: None)
    monkeypatch.setattr(
        module.run_backtest_task,
        "update_state",
        lambda **kwargs: captured.setdefault("states", []).append(kwargs),
    )

    with pytest.raises(ValueError, match="不支持的回测数据源策略"):
        module.run_backtest_task.run(
            backtest_id=8,
            strategy_config={"name": "demo"},
            backtest_config={
                "start_date": "2025-01-01",
                "end_date": "2025-01-31",
                "data_source_mode": "mock",
            },
        )

    assert captured["states"][-1]["state"] == "FAILURE"
