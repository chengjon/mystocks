"""
Trading cash reservation stores.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import Lock
from typing import Dict, Optional

from src.utils.trading_runtime_config import get_trading_cash_reservation_sqlite_path


class InMemoryPortfolioCashReservationStore:
    """
    Process-local reservation store for pending BUY cash.
    """

    def __init__(self) -> None:
        self._lock = Lock()
        self._portfolio_reservations: Dict[str, Dict[str, float]] = {}
        self._order_portfolio_context: Dict[str, str] = {}
        self._order_updated_at: Dict[str, str] = {}

    def upsert(
        self,
        portfolio_id: str,
        order_id: str,
        reserved_notional: float,
        updated_at: Optional[str] = None,
    ) -> None:
        with self._lock:
            self._order_portfolio_context[order_id] = portfolio_id
            portfolio_reservations = self._portfolio_reservations.setdefault(portfolio_id, {})
            portfolio_reservations[order_id] = float(reserved_notional)
            self._order_updated_at[order_id] = updated_at or datetime.now(timezone.utc).isoformat()

    def release(self, order_id: str) -> None:
        with self._lock:
            portfolio_id = self._order_portfolio_context.pop(order_id, None)
            if portfolio_id is None:
                return

            portfolio_reservations = self._portfolio_reservations.get(portfolio_id)
            if portfolio_reservations is None:
                return

            portfolio_reservations.pop(order_id, None)
            self._order_updated_at.pop(order_id, None)
            if not portfolio_reservations:
                self._portfolio_reservations.pop(portfolio_id, None)

    def get_order_reservation(self, order_id: str) -> Optional[Dict[str, float | str]]:
        with self._lock:
            portfolio_id = self._order_portfolio_context.get(order_id)
            if portfolio_id is None:
                return None

            reserved_notional = self._portfolio_reservations.get(portfolio_id, {}).get(order_id)
            if reserved_notional is None:
                return None

            return {
                "portfolio_id": portfolio_id,
                "order_id": order_id,
                "reserved_notional": float(reserved_notional),
                "updated_at": self._order_updated_at.get(order_id),
            }

    def get_portfolio_reserved_notional(self, portfolio_id: str) -> float:
        with self._lock:
            reservations = self._portfolio_reservations.get(portfolio_id, {})
            return float(sum(reservations.values()))

    def fetch_stale(self, max_age_seconds: int) -> list[Dict[str, float | str]]:
        stale_before = _utc_now() - timedelta(seconds=max_age_seconds)
        records: list[Dict[str, float | str]] = []

        with self._lock:
            for order_id, portfolio_id in self._order_portfolio_context.items():
                updated_at = self._order_updated_at.get(order_id)
                if updated_at is None:
                    continue

                updated_at_dt = _parse_utc_timestamp(updated_at)
                if updated_at_dt >= stale_before:
                    continue

                reserved_notional = self._portfolio_reservations.get(portfolio_id, {}).get(order_id)
                if reserved_notional is None:
                    continue

                records.append(
                    {
                        "portfolio_id": portfolio_id,
                        "order_id": order_id,
                        "reserved_notional": float(reserved_notional),
                        "updated_at": updated_at,
                    }
                )

        return records


class SqlitePortfolioCashReservationStore:
    """
    Local SQLite reservation ledger for pending BUY cash.

    The store is intentionally local and lightweight. It provides restart
    recovery for the canonical single-process runtime without claiming
    distributed reservation consistency.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._initialize_schema()

    def upsert(
        self,
        portfolio_id: str,
        order_id: str,
        reserved_notional: float,
        updated_at: Optional[str] = None,
    ) -> None:
        persisted_at = updated_at or _utc_now().isoformat()
        with self._lock:
            with sqlite3.connect(self.path) as conn:
                conn.execute(
                    """
                    INSERT INTO portfolio_cash_reservations (
                        portfolio_id,
                        order_id,
                        reserved_notional,
                        updated_at
                    ) VALUES (?, ?, ?, ?)
                    ON CONFLICT(order_id) DO UPDATE SET
                        portfolio_id = excluded.portfolio_id,
                        reserved_notional = excluded.reserved_notional,
                        updated_at = excluded.updated_at
                    """,
                    (portfolio_id, order_id, float(reserved_notional), persisted_at),
                )
                conn.commit()

    def release(self, order_id: str) -> None:
        with self._lock:
            with sqlite3.connect(self.path) as conn:
                conn.execute(
                    """
                    DELETE FROM portfolio_cash_reservations
                    WHERE order_id = ?
                    """,
                    (order_id,),
                )
                conn.commit()

    def get_order_reservation(self, order_id: str) -> Optional[Dict[str, float | str]]:
        with self._lock:
            with sqlite3.connect(self.path) as conn:
                conn.row_factory = sqlite3.Row
                row = conn.execute(
                    """
                    SELECT portfolio_id, order_id, reserved_notional, updated_at
                    FROM portfolio_cash_reservations
                    WHERE order_id = ?
                    """,
                    (order_id,),
                ).fetchone()

        if row is None:
            return None

        return {
            "portfolio_id": row["portfolio_id"],
            "order_id": row["order_id"],
            "reserved_notional": float(row["reserved_notional"]),
            "updated_at": row["updated_at"],
        }

    def get_portfolio_reserved_notional(self, portfolio_id: str) -> float:
        with self._lock:
            with sqlite3.connect(self.path) as conn:
                row = conn.execute(
                    """
                    SELECT COALESCE(SUM(reserved_notional), 0.0)
                    FROM portfolio_cash_reservations
                    WHERE portfolio_id = ?
                    """,
                    (portfolio_id,),
                ).fetchone()

        return float(row[0] if row is not None else 0.0)

    def fetch_all(self) -> list[Dict[str, float | str]]:
        with self._lock:
            with sqlite3.connect(self.path) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    """
                    SELECT portfolio_id, order_id, reserved_notional, updated_at
                    FROM portfolio_cash_reservations
                    ORDER BY id ASC
                    """
                ).fetchall()

        return [
            {
                "portfolio_id": row["portfolio_id"],
                "order_id": row["order_id"],
                "reserved_notional": float(row["reserved_notional"]),
                "updated_at": row["updated_at"],
            }
            for row in rows
        ]

    def fetch_stale(self, max_age_seconds: int) -> list[Dict[str, float | str]]:
        stale_before = (_utc_now() - timedelta(seconds=max_age_seconds)).isoformat()
        with self._lock:
            with sqlite3.connect(self.path) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    """
                    SELECT portfolio_id, order_id, reserved_notional, updated_at
                    FROM portfolio_cash_reservations
                    WHERE updated_at < ?
                    ORDER BY updated_at ASC
                    """,
                    (stale_before,),
                ).fetchall()

        return [
            {
                "portfolio_id": row["portfolio_id"],
                "order_id": row["order_id"],
                "reserved_notional": float(row["reserved_notional"]),
                "updated_at": row["updated_at"],
            }
            for row in rows
        ]

    def _initialize_schema(self) -> None:
        with self._lock:
            with sqlite3.connect(self.path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS portfolio_cash_reservations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        portfolio_id TEXT NOT NULL,
                        order_id TEXT NOT NULL UNIQUE,
                        reserved_notional REAL NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                    """
                )
                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_portfolio_cash_reservations_portfolio
                    ON portfolio_cash_reservations (portfolio_id)
                    """
                )
                conn.commit()


def build_default_portfolio_cash_reservation_store(
    path: Optional[str | Path] = None,
) -> SqlitePortfolioCashReservationStore:
    target_path = Path(path) if path is not None else get_trading_cash_reservation_sqlite_path()
    return SqlitePortfolioCashReservationStore(target_path)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_utc_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value)
