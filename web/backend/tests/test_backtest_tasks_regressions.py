from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

import pandas as pd


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
    monkeypatch.setattr(module, "_save_backtest_results", lambda backtest_id, results: captured.setdefault("saved", results))
    monkeypatch.setattr(module, "_update_backtest_status", lambda *args, **kwargs: None)
    monkeypatch.setattr(module, "get_progress_callback", lambda backtest_id: None)
    monkeypatch.setattr(module.run_backtest_task, "update_state", lambda **kwargs: captured.setdefault("states", []).append(kwargs))

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
    monkeypatch.setattr(module, "_update_backtest_status", lambda *args, **kwargs: captured.setdefault("failed", args))
    monkeypatch.setattr(module, "get_progress_callback", lambda backtest_id: None)
    monkeypatch.setattr(module.run_backtest_task, "update_state", lambda **kwargs: captured.setdefault("states", []).append(kwargs))

    try:
        module.run_backtest_task.run(
            backtest_id=8,
            strategy_config={"name": "demo"},
            backtest_config={
                "start_date": "2025-01-01",
                "end_date": "2025-01-31",
                "data_source_mode": "mock",
            },
        )
    except ValueError as exc:
        assert "不支持的回测数据源策略" in str(exc)
    else:
        raise AssertionError("expected ValueError for unsupported data_source_mode")

    assert captured["states"][-1]["state"] == "FAILURE"


def test_backtest_engine_normalizes_dates_for_strategy_history_source():
    from app.backtest.backtest_engine import BacktestEngine

    captured = {}

    class FakeDataSource:
        def get_stock_history(self, *, symbol, start_date, end_date):
            captured["history_request"] = {
                "symbol": symbol,
                "start_date": start_date,
                "end_date": end_date,
            }
            return pd.DataFrame(
                [
                    {
                        "date": "2025-01-02",
                        "open": 10,
                        "high": 11,
                        "low": 9,
                        "close": 10.5,
                        "volume": 1000,
                    }
                ]
            )

    engine = BacktestEngine(
        strategy_config={"strategy_type": "custom"},
        backtest_config={
            "symbols": ["000001"],
            "start_date": datetime(2025, 1, 1),
            "end_date": datetime(2025, 1, 31),
            "initial_capital": 100000,
        },
        data_source=FakeDataSource(),
    )

    engine._load_market_data()

    assert captured["history_request"] == {
        "symbol": "000001",
        "start_date": "20250101",
        "end_date": "20250131",
    }
    assert list(engine.market_data["000001"].keys()) == [datetime(2025, 1, 2)]


def test_backtest_repository_accepts_engine_result_shapes():
    from app.repositories.backtest_repository import BacktestRepository

    saved = {}

    class FakeBacktestModel:
        final_capital = None
        performance_metrics = None
        status = None
        completed_at = None

    class FakeQuery:
        def filter(self, *_args, **_kwargs):
            return self

        def first(self):
            return FakeBacktestModel()

    class FakeDb:
        def query(self, _model):
            return FakeQuery()

        def commit(self):
            saved["commits"] = saved.get("commits", 0) + 1

        def refresh(self, obj):
            saved["refreshed"] = obj

        def rollback(self):
            saved["rolled_back"] = True

        def bulk_save_objects(self, objects):
            saved["bulk_objects"] = objects

    repo = BacktestRepository(FakeDb())
    repo._orm_to_pydantic = lambda obj: obj

    repo.save_backtest_results(
        backtest_id="smoke-1",
        final_capital=Decimal("100001.23"),
        performance_metrics={
            "total_return": 0.001,
            "annualized_return": 0.0,
            "volatility": 0.0,
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0,
            "total_trades": 0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
        },
    )
    repo.save_equity_curve(
        backtest_id="smoke-1",
        equity_curve=[
            {
                "trade_date": datetime(2025, 1, 2),
                "equity": Decimal("100001.23"),
                "drawdown": Decimal("0"),
            }
        ],
    )

    assert saved["refreshed"].performance_metrics["annualized_return"] == 0.0
    assert saved["bulk_objects"][0].trade_date == datetime(2025, 1, 2).date()


def test_backtest_repository_returns_pending_backtest_api_shape():
    from app.repositories.backtest_repository import BacktestRepository

    pending = SimpleNamespace(
        backtest_id=123,
        strategy_id=10,
        user_id=1001,
        symbols=["000001"],
        start_date=datetime(2025, 1, 1).date(),
        end_date=datetime(2025, 1, 31).date(),
        initial_capital=Decimal("100000"),
        commission_rate=Decimal("0.0003"),
        slippage_rate=Decimal("0.001"),
        benchmark=None,
        final_capital=None,
        performance_metrics=None,
        equity_curves=[],
        trades=[],
        status="pending",
        error_message=None,
        created_at=datetime(2025, 1, 1, 9, 30),
        started_at=None,
        completed_at=None,
    )

    result = BacktestRepository(SimpleNamespace())._orm_to_pydantic(pending)

    assert result.status.value == "pending"
    assert result.final_capital == 100000.0
    assert result.performance.total_return == 0.0
    assert result.performance.annual_return == 0.0


def test_backtest_repository_maps_engine_metrics_to_backtest_api_shape():
    from app.repositories.backtest_repository import BacktestRepository

    completed = SimpleNamespace(
        backtest_id=124,
        strategy_id=10,
        user_id=1001,
        symbols=["000001"],
        start_date=datetime(2025, 1, 1).date(),
        end_date=datetime(2025, 1, 31).date(),
        initial_capital=Decimal("100000"),
        commission_rate=Decimal("0.0003"),
        slippage_rate=Decimal("0.001"),
        benchmark=None,
        final_capital=Decimal("100500"),
        performance_metrics={
            "total_return": 0.005,
            "annualized_return": 0.06,
            "volatility": 0.1,
            "sharpe_ratio": 1.2,
            "max_drawdown": 0.0,
            "total_trades": 0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
        },
        equity_curves=[],
        trades=[],
        status="completed",
        error_message=None,
        created_at=datetime(2025, 1, 1, 9, 30),
        started_at=None,
        completed_at=datetime(2025, 1, 31, 15, 0),
    )

    result = BacktestRepository(SimpleNamespace())._orm_to_pydantic(completed)

    assert result.status.value == "completed"
    assert result.final_capital == 100500.0
    assert result.performance.total_return == 0.005
    assert result.performance.annual_return == 0.06


def test_create_backtest_populates_legacy_runtime_required_columns():
    from app.models.strategy_schemas import BacktestExecuteRequest
    from app.repositories.backtest_repository import BacktestRepository

    saved = {}

    class FakeDb:
        def add(self, obj):
            saved["added"] = obj

        def commit(self):
            saved["committed"] = True

        def rollback(self):
            saved["rolled_back"] = True

    repo = BacktestRepository(FakeDb())

    result = repo.create_backtest(
        BacktestExecuteRequest(
            strategy_id=10,
            user_id=1001,
            symbols=["000001"],
            start_date=datetime(2025, 1, 1).date(),
            end_date=datetime(2025, 1, 5).date(),
            initial_capital=100000,
            commission_rate=0.0003,
            slippage_rate=0.001,
        )
    )

    added = saved["added"]
    assert saved["committed"] is True
    assert result.backtest_id == added.backtest_id
    assert result.status.value == "pending"
    assert result.final_capital == 100000.0
    assert added.backtest_id is not None
    assert added.strategy_id == "10"
    assert added.strategy_name == "strategy-10"
    assert added.backtest_start_date == datetime(2025, 1, 1).date()
    assert added.backtest_end_date == datetime(2025, 1, 5).date()
    assert added.final_capital == 100000.0
    assert added.total_return == 0.0
    assert added.max_drawdown == 0.0
    assert added.total_trades == 0


def test_save_backtest_results_skips_detail_rows_when_parent_result_is_missing(monkeypatch):
    from app.tasks import backtest_tasks as module

    calls = []

    class FakeRepo:
        def __init__(self, db):
            self.db = db

        def save_backtest_results(self, **_kwargs):
            calls.append("save_backtest_results")
            return None

        def save_equity_curve(self, *_args, **_kwargs):
            calls.append("save_equity_curve")

        def save_trades(self, *_args, **_kwargs):
            calls.append("save_trades")

    class FakeDb:
        def commit(self):
            calls.append("commit")

        def close(self):
            calls.append("close")

    monkeypatch.setattr("app.core.database.SessionLocal", lambda: FakeDb())
    monkeypatch.setattr("app.repositories.backtest_repository.BacktestRepository", FakeRepo)

    module._save_backtest_results(
        backtest_id=987654321,
        results={
            "final_capital": 100000,
            "performance_metrics": {"total_return": 0},
            "equity_curve": [{"trade_date": "2025-01-02T00:00:00", "equity": 100000, "drawdown": 0}],
            "trades": [{"symbol": "000001", "trade_date": "2025-01-02T00:00:00"}],
        },
    )

    assert calls == ["save_backtest_results", "close"]
