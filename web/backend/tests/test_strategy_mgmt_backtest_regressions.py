from __future__ import annotations

import importlib
import os
import sys
import threading
from datetime import date, datetime
from pathlib import Path
from types import SimpleNamespace

from fastapi import BackgroundTasks
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql.elements import TextClause


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


def test_tdengine_timeseries_source_satisfies_factory_interface_contract():
    from src.data_sources.real.tdengine_timeseries import TDengineTimeSeriesDataSource
    from src.interfaces.timeseries_data_source import ITimeSeriesDataSource

    assert issubclass(TDengineTimeSeriesDataSource, ITimeSeriesDataSource)


def test_postgresql_relational_source_satisfies_factory_interface_contract():
    from src.data_sources.real.postgresql_relational import PostgreSQLRelationalDataSource
    from src.interfaces.relational_data_source import IRelationalDataSource

    assert issubclass(PostgreSQLRelationalDataSource, IRelationalDataSource)


def test_business_source_factory_construction_allows_nested_source_lookup():
    from src.data_sources.factory import DataSourceFactory
    from src.data_sources.mock.business_mock import MockBusinessDataSource

    factory = DataSourceFactory()
    constructed = []

    class _NestedFactoryBusinessSource(MockBusinessDataSource):
        def __init__(self):
            self.ts = factory.get_timeseries_source(source_type="mock")
            constructed.append(type(self.ts).__name__)

    factory.register_business_source("composite", _NestedFactoryBusinessSource)
    result = {}

    def _build_source():
        try:
            result["source"] = factory.get_business_source(source_type="composite")
        except Exception as exc:  # pragma: no cover - surfaced by assertions below
            result["error"] = exc

    thread = threading.Thread(target=_build_source, daemon=True)
    thread.start()
    thread.join(timeout=1)

    assert not thread.is_alive()
    assert "error" not in result
    assert isinstance(result["source"], _NestedFactoryBusinessSource)
    assert constructed == ["MockTimeSeriesDataSource"]


class _FakeAsyncResult:
    id = "celery-task-456"


async def test_strategy_health_database_probe_uses_sqlalchemy_text_clause(monkeypatch):
    module = _load_module()
    captured = {}
    monkeypatch.setattr(
        module,
        "ensure_strategy_runtime_schema_ready",
        lambda db: {"created_tables": [], "added_columns": []},
    )

    class _FakeDb:
        def execute(self, statement):
            captured["statement"] = statement

        def query(self, model):
            return SimpleNamespace(count=lambda: 0)

    class _FakeDataSource:
        def health_check(self):
            return {"status": "healthy"}

    payload = await module.health_check(db=_FakeDb(), data_source=_FakeDataSource())

    assert isinstance(captured["statement"], TextClause)
    assert str(captured["statement"]) == "SELECT 1"
    assert payload["database"] == "connected"


def test_strategy_runtime_schema_readiness_is_additive_and_idempotent(monkeypatch):
    module = _load_module()
    from app.repositories.backtest_repository import BacktestResultModel
    from app.repositories.strategy_repository import UserStrategyModel

    created_tables = []
    executed = []
    commits = []

    monkeypatch.setattr(
        UserStrategyModel.__table__,
        "create",
        lambda bind, checkfirst=True: created_tables.append(("user_strategies", checkfirst)),
    )
    monkeypatch.setattr(
        BacktestResultModel.__table__,
        "create",
        lambda bind, checkfirst=True: created_tables.append(("backtest_results", checkfirst)),
    )

    class _FakeInspector:
        def has_table(self, table_name):
            return table_name == "backtest_results"

        def get_columns(self, table_name):
            if table_name == "backtest_results":
                return [{"name": "backtest_id"}, {"name": "strategy_id"}, {"name": "created_at"}]
            return []

    class _FakeDb:
        def get_bind(self):
            return SimpleNamespace(dialect=postgresql.dialect())

        def execute(self, statement):
            executed.append(str(statement))

        def commit(self):
            commits.append(True)

    monkeypatch.setattr(module, "inspect", lambda bind: _FakeInspector(), raising=False)

    result = module.ensure_strategy_runtime_schema_ready(_FakeDb())

    assert created_tables == [("user_strategies", True)]
    assert any("ALTER TABLE backtest_results ADD COLUMN IF NOT EXISTS user_id" in sql for sql in executed)
    assert any("ALTER TABLE backtest_results ADD COLUMN IF NOT EXISTS status" in sql for sql in executed)
    assert all("DROP TABLE" not in sql.upper() for sql in executed)
    assert commits == [True]
    assert result["created_tables"] == ["user_strategies"]
    assert "backtest_results.user_id" in result["added_columns"]


async def test_strategy_health_runs_schema_readiness_before_table_counts(monkeypatch):
    module = _load_module()
    calls = []

    def _ready(db):
        calls.append(db)
        return {"created_tables": [], "added_columns": []}

    class _FakeDb:
        def execute(self, statement):
            pass

        def query(self, model):
            return SimpleNamespace(count=lambda: 0)

    class _FakeDataSource:
        def health_check(self):
            return {"status": "healthy"}

    monkeypatch.setattr(module, "ensure_strategy_runtime_schema_ready", _ready, raising=False)

    db = _FakeDb()
    payload = await module.health_check(db=db, data_source=_FakeDataSource())

    assert calls == [db]
    assert payload["database"] == "connected"


def test_strategy_repository_dependencies_prepare_runtime_schema(monkeypatch):
    module = _load_module()
    calls = []

    def _ready(db):
        calls.append(db)
        return {"created_tables": [], "added_columns": []}

    monkeypatch.setattr(module, "ensure_strategy_runtime_schema_ready", _ready)

    db = object()
    strategy_repo = module.get_strategy_repository(db=db)
    backtest_repo = module.get_backtest_repository(db=db)

    assert isinstance(strategy_repo, module.StrategyRepository)
    assert isinstance(backtest_repo, module.BacktestRepository)
    assert calls == [db, db]


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
