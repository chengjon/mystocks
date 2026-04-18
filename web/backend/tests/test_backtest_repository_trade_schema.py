from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.repositories.backtest_repository import BacktestRepository


class _FakeDB:
    def __init__(self, rows=None):
        self.rows = rows or []
        self.saved_objects = None
        self.committed = False
        self.rolled_back = False

    def bulk_save_objects(self, objects):
        self.saved_objects = objects

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def query(self, _model):
        return _FakeQuery(self.rows)


class _FakeQuery:
    def __init__(self, rows):
        self.rows = rows

    def filter(self, *_args, **_kwargs):
        return self

    def order_by(self, *_args, **_kwargs):
        return self

    def all(self):
        return list(self.rows)


def test_save_trades_maps_legacy_trade_payload_to_current_schema():
    db = _FakeDB()
    repository = BacktestRepository(db)

    saved = repository.save_trades(
        7,
        [
            {
                "symbol": "600519",
                "trade_date": date(2026, 4, 8),
                "action": "BUY",
                "price": Decimal("1750.00"),
                "quantity": 100,
                "amount": Decimal("175000.00"),
                "commission": Decimal("52.50"),
                "profit_loss": None,
            }
        ],
    )

    assert saved is True
    assert db.committed is True
    assert db.saved_objects is not None
    assert len(db.saved_objects) == 1

    trade = db.saved_objects[0]
    assert trade.symbol == "600519"
    assert trade.trade_date == date(2026, 4, 8)
    assert trade.direction == "buy"
    assert trade.amount == 100
    assert trade.total_cost == Decimal("175000.00")
    assert trade.commission == Decimal("52.50")


def test_get_trades_restores_api_trade_record_shape_from_current_schema():
    db = _FakeDB(
        rows=[
            SimpleNamespace(
                id=101,
                symbol="600519",
                trade_date=date(2026, 4, 8),
                direction="buy",
                price=Decimal("1750.00"),
                amount=100,
                total_cost=Decimal("175000.00"),
                commission=Decimal("52.50"),
            )
        ]
    )
    repository = BacktestRepository(db)

    trades = repository.get_trades(7)

    assert len(trades) == 1
    trade = trades[0]
    assert trade.trade_id == 101
    assert trade.symbol == "600519"
    assert trade.trade_date == date(2026, 4, 8)
    assert trade.action == "buy"
    assert trade.quantity == 100
    assert trade.amount == 175000.0
    assert trade.commission == 52.5
    assert trade.profit_loss is None


def test_save_trades_rejects_dict_payload_without_quantity():
    db = _FakeDB()
    repository = BacktestRepository(db)

    with pytest.raises(ValueError, match="quantity"):
        repository.save_trades(
            7,
            [
                {
                    "symbol": "600519",
                    "trade_date": date(2026, 4, 8),
                    "action": "BUY",
                    "price": Decimal("1750.00"),
                    "amount": Decimal("175000.00"),
                    "commission": Decimal("52.50"),
                }
            ],
        )


def test_backtest_trade_model_backtest_id_keeps_cascade_foreign_key():
    from app.repositories.backtest_repository import BacktestTradeModel

    foreign_keys = list(BacktestTradeModel.__table__.c.backtest_id.foreign_keys)

    assert len(foreign_keys) == 1
    assert foreign_keys[0].column.table.name == "backtest_results"
    assert foreign_keys[0].column.name == "backtest_id"
    assert foreign_keys[0].ondelete == "CASCADE"


@pytest.mark.parametrize(
    "sql_path",
    [
        Path(__file__).resolve().parents[1] / "init_tables.sql",
        Path(__file__).resolve().parents[1] / "init_tables_simple.sql",
    ],
)
def test_backtest_trade_bootstrap_sql_matches_current_schema(sql_path: Path):
    sql = sql_path.read_text(encoding="utf-8")

    assert "CREATE TABLE IF NOT EXISTS backtest_trades" in sql
    assert "backtest_id BIGINT NOT NULL REFERENCES backtest_results(backtest_id) ON DELETE CASCADE" in sql
    assert "trade_date DATE NOT NULL" in sql
    assert "direction VARCHAR(10) NOT NULL" in sql
    assert "amount INT" in sql
    assert "stamp_tax DECIMAL(20, 2)" in sql
    assert "total_cost DECIMAL(20, 2)" in sql
    assert "created_at TIMESTAMPTZ DEFAULT NOW()" in sql
    assert "action VARCHAR(10) NOT NULL" not in sql
    assert "shares INT" not in sql
    assert "profit DECIMAL(20, 2)" not in sql
    assert "return_rate DECIMAL(10, 4)" not in sql
