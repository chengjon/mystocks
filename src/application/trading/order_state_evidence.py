"""
Local order-state evidence stores for trading runtime hardening.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Dict, Optional

from src.utils.trading_runtime_config import get_trading_order_state_sqlite_path


class InMemoryTradingOrderStateStore:
    """
    Process-local order-state evidence store.
    """

    def __init__(self) -> None:
        self._lock = Lock()
        self._records: Dict[str, Dict[str, str]] = {}

    def upsert(
        self,
        portfolio_id: str | None,
        order_id: str,
        symbol: str,
        status: str,
        updated_at: Optional[str] = None,
    ) -> None:
        with self._lock:
            existing = self._records.get(order_id, {})
            self._records[order_id] = {
                "portfolio_id": portfolio_id if portfolio_id is not None else existing.get("portfolio_id"),
                "order_id": order_id,
                "symbol": symbol,
                "status": status,
                "updated_at": updated_at or _utc_now().isoformat(),
            }

    def get_order_state(self, order_id: str) -> Optional[Dict[str, str]]:
        with self._lock:
            record = self._records.get(order_id)
            if record is None:
                return None
            return dict(record)


class SqliteTradingOrderStateStore:
    """
    Local SQLite store for order-state evidence.

    This is intentionally local and reconstruction-oriented. It does not claim
    broker truth, but it gives the runtime and operator tooling a durable local
    view of whether an order was last seen as active or terminal.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._initialize_schema()

    def upsert(
        self,
        portfolio_id: str | None,
        order_id: str,
        symbol: str,
        status: str,
        updated_at: Optional[str] = None,
    ) -> None:
        persisted_at = updated_at or _utc_now().isoformat()
        with self._lock:
            with sqlite3.connect(self.path) as conn:
                conn.execute(
                    """
                    INSERT INTO trading_order_state_evidence (
                        portfolio_id,
                        order_id,
                        symbol,
                        status,
                        updated_at
                    ) VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(order_id) DO UPDATE SET
                        portfolio_id = COALESCE(excluded.portfolio_id, trading_order_state_evidence.portfolio_id),
                        symbol = excluded.symbol,
                        status = excluded.status,
                        updated_at = excluded.updated_at
                    """,
                    (portfolio_id, order_id, symbol, status, persisted_at),
                )
                conn.commit()

    def get_order_state(self, order_id: str) -> Optional[Dict[str, str]]:
        with self._lock:
            with sqlite3.connect(self.path) as conn:
                conn.row_factory = sqlite3.Row
                row = conn.execute(
                    """
                    SELECT portfolio_id, order_id, symbol, status, updated_at
                    FROM trading_order_state_evidence
                    WHERE order_id = ?
                    """,
                    (order_id,),
                ).fetchone()

        if row is None:
            return None

        return {
            "portfolio_id": row["portfolio_id"],
            "order_id": row["order_id"],
            "symbol": row["symbol"],
            "status": row["status"],
            "updated_at": row["updated_at"],
        }

    def _initialize_schema(self) -> None:
        with self._lock:
            with sqlite3.connect(self.path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS trading_order_state_evidence (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        portfolio_id TEXT,
                        order_id TEXT NOT NULL UNIQUE,
                        symbol TEXT NOT NULL,
                        status TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                    """
                )
                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_trading_order_state_status
                    ON trading_order_state_evidence (status)
                    """
                )
                conn.commit()


def build_default_trading_order_state_store(path: str | Path | None = None) -> SqliteTradingOrderStateStore:
    target_path = Path(path) if path is not None else get_trading_order_state_sqlite_path()
    return SqliteTradingOrderStateStore(target_path)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)
