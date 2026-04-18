from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.repositories.backtest_repository import BacktestRepository, BacktestTradeModel


def test_backtest_repository_maps_domain_trade_fields_to_runtime_trade_schema():
    engine = create_engine("sqlite:///:memory:")
    BacktestTradeModel.__table__.create(engine)

    with Session(engine) as session:
        repo = BacktestRepository(session)

        assert repo.save_trades(
            7,
            [
                {
                    "symbol": "600519",
                    "trade_date": date(2026, 4, 8),
                    "action": "buy",
                    "price": Decimal("1750.00"),
                    "quantity": 100,
                    "amount": Decimal("175000.00"),
                    "commission": Decimal("52.50"),
                    "profit_loss": None,
                }
            ],
        )

        stored_trade = session.query(BacktestTradeModel).one()
        assert stored_trade.backtest_id == 7
        assert stored_trade.direction == "buy"
        assert stored_trade.amount == 100
        assert stored_trade.total_cost == Decimal("175000.00")

        trades = repo.get_trades(7)

    assert len(trades) == 1
    assert trades[0].trade_id == 1
    assert trades[0].trade_date == date(2026, 4, 8)
    assert trades[0].action == "buy"
    assert trades[0].quantity == 100
    assert trades[0].amount == 175000.0
    assert trades[0].commission == 52.5
