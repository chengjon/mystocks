"""
Durable submission-attempt ledgers for broker-facing runtime handoff.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Optional

from src.utils.trading_runtime_config import get_trading_broker_submission_attempt_sqlite_path


class InMemoryTradingBrokerSubmissionAttemptStore:
    """
    Process-local submission-attempt ledger.

    This preserves the distinction between local submission, transport receipt, and later
    broker acknowledgement without claiming that broker truth has already been proven.
    """

    def __init__(self) -> None:
        self._lock = Lock()
        self._next_id = 1
        self._records: list[Dict[str, Any]] = []

    def append(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            record = _build_record(payload, record_id=self._next_id)
            self._records.append(record)
            self._next_id += 1
        return dict(record)

    def fetch_recent(self, limit: int = 100) -> list[Dict[str, Any]]:
        with self._lock:
            return [dict(record) for record in reversed(self._records[-limit:])]

    def get_latest_for_order(
        self,
        order_id: str,
        *,
        broker_channel: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        with self._lock:
            for record in reversed(self._records):
                if record["order_id"] != order_id:
                    continue
                if broker_channel is not None and record["broker_channel"] != broker_channel:
                    continue
                return dict(record)
        return None

    def get_by_bridge_task_id(
        self,
        bridge_task_id: str,
        *,
        broker_channel: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        with self._lock:
            for record in reversed(self._records):
                if record.get("bridge_task_id") != bridge_task_id:
                    continue
                if broker_channel is not None and record["broker_channel"] != broker_channel:
                    continue
                return dict(record)
        return None


class SqliteTradingBrokerSubmissionAttemptStore:
    """
    Local SQLite ledger for broker-facing submission attempts.

    The ledger records immediate runtime outcomes such as transport acceptance, immediate
    acknowledgement, and pre-acknowledgement submission failure.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._initialize_schema()

    def append(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        record = _build_record(payload)

        with self._lock:
            with sqlite3.connect(self.path) as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO trading_broker_submission_attempt (
                        order_id,
                        local_submission_id,
                        broker_channel,
                        adapter_path,
                        account_scope,
                        session_scope,
                        submission_status,
                        transport_status,
                        bridge_task_id,
                        external_order_id,
                        source_name,
                        failure_reason,
                        handoff_status,
                        handoff_reason,
                        updated_at,
                        payload_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record["order_id"],
                        record["local_submission_id"],
                        record["broker_channel"],
                        record["adapter_path"],
                        record["account_scope"],
                        record["session_scope"],
                        record["submission_status"],
                        record.get("transport_status"),
                        record.get("bridge_task_id"),
                        record.get("external_order_id"),
                        record.get("source_name"),
                        record.get("failure_reason"),
                        record.get("handoff_status"),
                        record.get("handoff_reason"),
                        record["updated_at"],
                        json.dumps(record, ensure_ascii=True, sort_keys=True),
                    ),
                )
                conn.commit()
                record["attempt_id"] = int(cursor.lastrowid)

        return record

    def fetch_recent(self, limit: int = 100) -> list[Dict[str, Any]]:
        with self._lock:
            with sqlite3.connect(self.path) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    """
                    SELECT payload_json
                    FROM trading_broker_submission_attempt
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (limit,),
                ).fetchall()

        return [json.loads(row["payload_json"]) for row in rows]

    def get_latest_for_order(
        self,
        order_id: str,
        *,
        broker_channel: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        query = """
            SELECT payload_json
            FROM trading_broker_submission_attempt
            WHERE order_id = ?
        """
        params: list[Any] = [order_id]
        if broker_channel is not None:
            query += " AND broker_channel = ?"
            params.append(broker_channel)
        query += " ORDER BY id DESC LIMIT 1"

        with self._lock:
            with sqlite3.connect(self.path) as conn:
                row = conn.execute(query, params).fetchone()

        if row is None:
            return None

        return json.loads(row[0])

    def get_by_bridge_task_id(
        self,
        bridge_task_id: str,
        *,
        broker_channel: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        query = """
            SELECT payload_json
            FROM trading_broker_submission_attempt
            WHERE bridge_task_id = ?
        """
        params: list[Any] = [bridge_task_id]
        if broker_channel is not None:
            query += " AND broker_channel = ?"
            params.append(broker_channel)
        query += " ORDER BY id DESC LIMIT 1"

        with self._lock:
            with sqlite3.connect(self.path) as conn:
                row = conn.execute(query, params).fetchone()

        if row is None:
            return None

        return json.loads(row[0])

    def _initialize_schema(self) -> None:
        with self._lock:
            with sqlite3.connect(self.path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS trading_broker_submission_attempt (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        order_id TEXT NOT NULL,
                        local_submission_id TEXT NOT NULL,
                        broker_channel TEXT NOT NULL,
                        adapter_path TEXT NOT NULL,
                        account_scope TEXT NOT NULL,
                        session_scope TEXT,
                        submission_status TEXT NOT NULL,
                        transport_status TEXT,
                        bridge_task_id TEXT,
                        external_order_id TEXT,
                        source_name TEXT,
                        failure_reason TEXT,
                        handoff_status TEXT,
                        handoff_reason TEXT,
                        updated_at TEXT NOT NULL,
                        payload_json TEXT NOT NULL
                    )
                    """
                )
                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_trading_broker_submission_attempt_order_id
                    ON trading_broker_submission_attempt (order_id)
                    """
                )
                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_trading_broker_submission_attempt_channel_status
                    ON trading_broker_submission_attempt (broker_channel, submission_status)
                    """
                )
                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_trading_broker_submission_attempt_bridge_task_id
                    ON trading_broker_submission_attempt (bridge_task_id)
                    """
                )
                conn.commit()


def build_default_trading_broker_submission_attempt_store(
    path: str | Path | None = None,
) -> SqliteTradingBrokerSubmissionAttemptStore:
    target_path = Path(path) if path is not None else get_trading_broker_submission_attempt_sqlite_path()
    return SqliteTradingBrokerSubmissionAttemptStore(target_path)


def _build_record(payload: Dict[str, Any], *, record_id: int | None = None) -> Dict[str, Any]:
    updated_at = payload.get("updated_at") or _utc_now().isoformat()
    record = {
        **payload,
        "attempt_id": record_id,
        "updated_at": updated_at,
    }
    raw_response = record.get("raw_response")
    if raw_response is not None and not isinstance(raw_response, dict):
        record["raw_response"] = {"value": raw_response}
    return record


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)
