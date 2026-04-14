from __future__ import annotations

import importlib
import os
import sys
from datetime import date, datetime
from pathlib import Path
from types import SimpleNamespace

from fastapi import BackgroundTasks


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

os.environ.setdefault("POSTGRESQL_HOST", "localhost")
os.environ.setdefault("POSTGRESQL_PORT", "5432")
os.environ.setdefault("POSTGRESQL_USER", "tester")
os.environ.setdefault("POSTGRESQL_PASSWORD", "tester")
os.environ.setdefault("POSTGRESQL_DATABASE", "tester")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("BACKEND_PORT", "8134")
os.environ.setdefault("BACKEND_BACKUP_PORT", "8135")
os.environ.setdefault("TESTING", "true")


def _load_module():
    sys.modules.pop("app.api.strategy_mgmt", None)
    return importlib.import_module("app.api.strategy_mgmt")


class _FakeAsyncResult:
    id = "celery-task-456"


async def test_execute_backtest_registers_runtime_task_mapping(monkeypatch):
    module = _load_module()
    captured = {}

    class _FakeStrategyRepo:
        def get_strategy(self, strategy_id):
            return module.StrategyConfig(
                strategy_id=strategy_id,
                user_id=1001,
                strategy_name="双均线突破",
                strategy_type="momentum",
                parameters=[],
                max_position_size=0.2,
                stop_loss_percent=5.0,
                take_profit_percent=12.0,
                status="active",
                created_at=datetime(2026, 4, 1, 9, 30, 0),
                updated_at=datetime(2026, 4, 1, 9, 30, 0),
                tags=["趋势"],
            )

    class _FakeBacktestRepo:
        def create_backtest(self, request):
            captured["request"] = request
            return SimpleNamespace(
                backtest_id=456,
                strategy_id=request.strategy_id,
                user_id=request.user_id,
                symbols=request.symbols,
                start_date=request.start_date,
                end_date=request.end_date,
                initial_capital=request.initial_capital,
                created_at=datetime(2026, 4, 15, 9, 0, 0),
            )

    monkeypatch.setattr(module, "_require_write_auth", lambda authorization: None)
    def _fake_delay(**kwargs):
        captured["delay_kwargs"] = kwargs
        return _FakeAsyncResult()

    monkeypatch.setattr(module.run_backtest_task, "delay", _fake_delay)
    monkeypatch.setattr(
        module,
        "register_backtest_task",
        lambda backtest_id, task_id: captured.setdefault("mapping", (backtest_id, task_id)),
    )

    request = module.BacktestRequest(
        strategy_id=123,
        user_id=1001,
        symbols=["000001.SZ"],
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
        initial_capital=100000.0,
        commission_rate=0.0003,
        slippage_rate=0.001,
        benchmark="000300.SH",
        include_analysis=True,
    )

    payload = await module.execute_backtest(
        background_tasks=BackgroundTasks(),
        backtest_req=request,
        strategy_repo=_FakeStrategyRepo(),
        backtest_repo=_FakeBacktestRepo(),
        authorization=None,
    )

    assert payload.backtest_id == 456
    assert captured["mapping"] == (456, "celery-task-456")
    assert captured["delay_kwargs"] == {
        "backtest_id": 456,
        "strategy_config": {
            "strategy_id": 123,
            "strategy_name": "双均线突破",
            "strategy_type": "momentum",
            "parameters": [],
            "max_position_size": 0.2,
            "stop_loss_percent": 5.0,
            "take_profit_percent": 12.0,
        },
        "backtest_config": {
            "backtest_id": 456,
            "symbols": ["000001.SZ"],
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "initial_capital": 100000.0,
            "commission_rate": 0.0003,
            "slippage_rate": 0.001,
            "benchmark": "000300.SH",
        },
    }
