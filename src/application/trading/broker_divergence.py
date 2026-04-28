"""
Durable divergence evidence stores for local-versus-broker reconciliation review.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Dict

from src.utils.trading_runtime_config import get_trading_broker_divergence_sqlite_path


class InMemoryTradingBrokerDivergenceStore:
    """
    Process-local divergence incident ledger.
    """

    def __init__(self) -> None:
        self._lock = Lock()
        self._records: list[Dict[str, Any]] = []

    def append(self, payload: Dict[str, Any]) -> None:
        with self._lock:
            record = {
                **payload,
                "persisted_at": payload.get("persisted_at") or _utc_now().isoformat(),
            }
            self._records.append(record)

    def fetch_recent(self, limit: int = 100) -> list[Dict[str, Any]]:
        with self._lock:
            return [dict(record) for record in self._records[-limit:]][::-1]


class SqliteTradingBrokerDivergenceStore:
    """
    Local SQLite ledger for reconciliation divergence incidents.

    This preserves durable review-required evidence without claiming that the current runtime
    already performs automatic broker reconciliation or resolution.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._initialize_schema()

    def append(self, payload: Dict[str, Any]) -> None:
        record = self._build_record(payload)

        with self._lock:
            with sqlite3.connect(self.path) as conn:
                conn.execute(
                    """
                    INSERT INTO trading_broker_divergence_incidents (
                        persisted_at,
                        divergence_category,
                        review_status,
                        review_owner,
                        next_action,
                        required_evidence,
                        order_id,
                        event_type,
                        external_order_id,
                        local_submission_id,
                        local_order_id,
                        local_order_status,
                        identity_status,
                        sequencing_status,
                        reported_filled_quantity,
                        reported_fill_price,
                        reason_code,
                        reason_detail,
                        adapter_path,
                        account_scope,
                        session_scope,
                        payload_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record["persisted_at"],
                        record["divergence_category"],
                        record["review_status"],
                        record["review_owner"],
                        record["next_action"],
                        record["required_evidence"],
                        record.get("order_id"),
                        record["event_type"],
                        record.get("external_order_id"),
                        record.get("local_submission_id"),
                        record.get("local_order_id"),
                        record.get("local_order_status"),
                        record["identity_status"],
                        record["sequencing_status"],
                        record.get("reported_filled_quantity"),
                        record.get("reported_fill_price"),
                        record.get("reason_code"),
                        record.get("reason_detail"),
                        record.get("adapter_path"),
                        record.get("account_scope"),
                        record.get("session_scope"),
                        json.dumps(record, ensure_ascii=True, sort_keys=True),
                    ),
                )
                conn.commit()

    def fetch_recent(self, limit: int = 100) -> list[Dict[str, Any]]:
        with self._lock:
            with sqlite3.connect(self.path) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    """
                    SELECT payload_json
                    FROM trading_broker_divergence_incidents
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (limit,),
                ).fetchall()

        return [json.loads(row["payload_json"]) for row in rows]

    def _initialize_schema(self) -> None:
        with self._lock:
            with sqlite3.connect(self.path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS trading_broker_divergence_incidents (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        persisted_at TEXT NOT NULL,
                        divergence_category TEXT NOT NULL,
                        review_status TEXT NOT NULL,
                        review_owner TEXT NOT NULL,
                        next_action TEXT NOT NULL,
                        required_evidence TEXT NOT NULL,
                        order_id TEXT,
                        event_type TEXT NOT NULL,
                        external_order_id TEXT,
                        local_submission_id TEXT,
                        local_order_id TEXT,
                        local_order_status TEXT,
                        identity_status TEXT NOT NULL,
                        sequencing_status TEXT NOT NULL,
                        reported_filled_quantity INTEGER,
                        reported_fill_price REAL,
                        reason_code TEXT,
                        reason_detail TEXT,
                        adapter_path TEXT,
                        account_scope TEXT,
                        session_scope TEXT,
                        payload_json TEXT NOT NULL
                    )
                    """
                )
                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_trading_broker_divergence_order_id
                    ON trading_broker_divergence_incidents (order_id)
                    """
                )
                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_trading_broker_divergence_category
                    ON trading_broker_divergence_incidents (divergence_category)
                    """
                )
                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_trading_broker_divergence_external_order_id
                    ON trading_broker_divergence_incidents (external_order_id)
                    """
                )
                conn.commit()

    @staticmethod
    def _build_record(payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            **payload,
            "persisted_at": payload.get("persisted_at") or _utc_now().isoformat(),
        }


def build_default_trading_broker_divergence_store(path: str | Path | None = None) -> SqliteTradingBrokerDivergenceStore:
    target_path = Path(path) if path is not None else get_trading_broker_divergence_sqlite_path()
    return SqliteTradingBrokerDivergenceStore(target_path)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)
