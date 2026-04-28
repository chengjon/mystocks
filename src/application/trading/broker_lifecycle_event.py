"""
Local broker lifecycle event envelope and durable ledger.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from src.utils.trading_runtime_config import get_trading_broker_lifecycle_event_sqlite_path


class BrokerLifecycleEvent(BaseModel):
    """
    Minimum broker lifecycle event envelope for acknowledgement and reconciliation preparation.
    """

    event_type: str = Field(..., pattern="^(acknowledgement|reject|cancel|execution)$")
    source_timestamp: datetime
    broker_channel: Optional[str] = Field(None, min_length=1, max_length=64)
    source_name: Optional[str] = Field(None, min_length=1, max_length=128)
    external_order_id: Optional[str] = Field(None, min_length=1, max_length=128)
    local_submission_id: Optional[str] = Field(None, min_length=1, max_length=128)
    local_order_id: Optional[str] = Field(None, min_length=1, max_length=128)
    event_id: Optional[str] = Field(None, min_length=1, max_length=128)
    sequence_id: Optional[str] = Field(None, min_length=1, max_length=128)
    filled_quantity: Optional[int] = Field(None, ge=0)
    fill_price: Optional[float] = Field(None, gt=0)
    reason_code: Optional[str] = Field(None, min_length=1, max_length=128)
    reason_detail: Optional[str] = Field(None, min_length=1, max_length=512)


class InMemoryTradingBrokerLifecycleEventStore:
    """
    Process-local broker lifecycle event ledger.
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


class SqliteTradingBrokerLifecycleEventStore:
    """
    Local SQLite ledger for broker lifecycle event envelopes.

    This preserves the raw broker-facing identity surface needed for later replay-suppression
    and reconciliation work, without claiming that the current runtime already resolves those
    workflows automatically.
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
                    INSERT INTO trading_broker_lifecycle_events (
                        persisted_at,
                        event_type,
                        order_id,
                        external_order_id,
                        local_submission_id,
                        local_order_id,
                        source_timestamp,
                        source_name,
                        event_id,
                        sequence_id,
                        identity_status,
                        sequencing_status,
                        fill_quantity,
                        fill_price,
                        reason_code,
                        reason_detail,
                        adapter_path,
                        account_scope,
                        session_scope,
                        payload_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record["persisted_at"],
                        record["event_type"],
                        record.get("order_id"),
                        record.get("external_order_id"),
                        record.get("local_submission_id"),
                        record.get("local_order_id"),
                        record["source_timestamp"],
                        record.get("source_name"),
                        record.get("event_id"),
                        record.get("sequence_id"),
                        record["identity_status"],
                        record["sequencing_status"],
                        record.get("fill_quantity"),
                        record.get("fill_price"),
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
                    FROM trading_broker_lifecycle_events
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
                    CREATE TABLE IF NOT EXISTS trading_broker_lifecycle_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        persisted_at TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        order_id TEXT,
                        external_order_id TEXT,
                        local_submission_id TEXT,
                        local_order_id TEXT,
                        source_timestamp TEXT NOT NULL,
                        source_name TEXT,
                        event_id TEXT,
                        sequence_id TEXT,
                        identity_status TEXT NOT NULL,
                        sequencing_status TEXT NOT NULL,
                        fill_quantity INTEGER,
                        fill_price REAL,
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
                    CREATE INDEX IF NOT EXISTS idx_trading_broker_lifecycle_events_external_order_id
                    ON trading_broker_lifecycle_events (external_order_id)
                    """
                )
                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_trading_broker_lifecycle_events_order_id
                    ON trading_broker_lifecycle_events (order_id)
                    """
                )
                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_trading_broker_lifecycle_events_event_type
                    ON trading_broker_lifecycle_events (event_type)
                    """
                )
                conn.commit()

    @staticmethod
    def _build_record(payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            **payload,
            "persisted_at": payload.get("persisted_at") or _utc_now().isoformat(),
        }


def build_default_trading_broker_lifecycle_event_store(
    path: str | Path | None = None,
) -> SqliteTradingBrokerLifecycleEventStore:
    target_path = Path(path) if path is not None else get_trading_broker_lifecycle_event_sqlite_path()
    return SqliteTradingBrokerLifecycleEventStore(target_path)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)
