from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any

from app.core.database import SessionLocal
from app.repositories.backtest_repository import BacktestTradeModel


def build_statement_account_id(backtest_id: int) -> str:
    return f"backtest:{backtest_id}"


def parse_statement_account_id(account_id: str) -> int:
    prefix, separator, raw_backtest_id = account_id.partition(":")
    if prefix != "backtest" or separator != ":" or not raw_backtest_id:
        raise ValueError(f"unsupported reconciliation account_id: {account_id}")

    try:
        return int(raw_backtest_id)
    except ValueError as exc:
        raise ValueError(f"unsupported reconciliation account_id: {account_id}") from exc


def _to_trade_time(value: date | datetime) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.combine(value, datetime.min.time())


def _resolve_trade_time(trade: BacktestTradeModel) -> datetime:
    created_at = getattr(trade, "created_at", None)
    if isinstance(created_at, datetime):
        if created_at.tzinfo is not None:
            return created_at.astimezone(timezone.utc).replace(tzinfo=None)
        return created_at
    return _to_trade_time(trade.trade_date)


def _to_trade_amount(trade: BacktestTradeModel) -> Decimal:
    quantity = int(trade.amount or 0)
    price = Decimal(str(trade.price or 0))
    if trade.total_cost is not None:
        return Decimal(str(trade.total_cost))
    return price * Decimal(str(quantity))


def _serialize_trade_row(trade: BacktestTradeModel) -> dict[str, Any]:
    return {
        "account_id": build_statement_account_id(int(trade.backtest_id)),
        "trade_id": str(trade.id),
        "order_id": f"backtest-{trade.backtest_id}-{trade.id}",
        "symbol": trade.symbol,
        "direction": trade.direction,
        "trade_time": _resolve_trade_time(trade).isoformat(),
        "price": str(Decimal(str(trade.price or 0))),
        "quantity": int(trade.amount or 0),
        "amount": str(_to_trade_amount(trade)),
        "commission": str(Decimal(str(trade.commission or 0))),
    }


def list_reconciliation_accounts() -> list[dict[str, Any]]:
    session = SessionLocal()
    try:
        backtest_ids = (
            session.query(BacktestTradeModel.backtest_id)
            .distinct()
            .order_by(BacktestTradeModel.backtest_id.desc())
            .all()
        )
        return [
            {
                "account_id": build_statement_account_id(int(backtest_id)),
                "label": f"Backtest #{int(backtest_id)}",
                "account_type": "backtest",
            }
            for (backtest_id,) in backtest_ids
        ]
    finally:
        session.close()


def query_internal_statements(
    *,
    account_id: str,
    start_date: date | None,
    end_date: date | None,
    page: int,
    page_size: int,
) -> dict[str, Any]:
    backtest_id = parse_statement_account_id(account_id)
    session = SessionLocal()
    try:
        query = session.query(BacktestTradeModel).filter(BacktestTradeModel.backtest_id == backtest_id)
        if start_date is not None:
            query = query.filter(BacktestTradeModel.trade_date >= start_date)
        if end_date is not None:
            query = query.filter(BacktestTradeModel.trade_date <= end_date)

        filtered_rows = sorted(
            query.order_by(BacktestTradeModel.trade_date.desc()).all(),
            key=lambda item: (_resolve_trade_time(item), int(item.id)),
            reverse=True,
        )
        offset = (page - 1) * page_size
        paged_rows = filtered_rows[offset : offset + page_size]

        total_amount = sum((_to_trade_amount(row) for row in filtered_rows), Decimal("0"))
        total_commission = sum((Decimal(str(row.commission or 0)) for row in filtered_rows), Decimal("0"))

        return {
            "account_id": account_id,
            "items": [_serialize_trade_row(row) for row in paged_rows],
            "summary": {
                "total_count": len(filtered_rows),
                "total_amount": str(total_amount),
                "total_commission": str(total_commission),
            },
            "total_count": len(filtered_rows),
            "page": page,
            "page_size": page_size,
            "source": "backtest_trades",
        }
    finally:
        session.close()
