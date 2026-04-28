"""
Trading decision audit sinks.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Optional

from src.utils.trading_runtime_config import (
    get_trading_decision_audit_jsonl_path,
    get_trading_decision_audit_sqlite_path,
)


class JsonlTradingDecisionAuditSink:
    """
    Append-only JSONL sink for trading decision audits.

    This is a low-risk durable sink for Wave 3 runtime hardening.
    It is process-local and file-backed, so it improves reconstructability
    without pretending to be a full distributed audit pipeline.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def __call__(self, payload: Dict[str, Any]) -> None:
        record = {
            **payload,
            "persisted_at": datetime.now(timezone.utc).isoformat(),
        }
        encoded = json.dumps(record, ensure_ascii=True, sort_keys=True)

        with self._lock:
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(encoded)
                handle.write("\n")
                handle.flush()


class SqliteTradingDecisionAuditSink:
    """
    Local SQLite ledger for trading decision audits.

    This complements the JSONL sink with a lightweight query surface while
    staying process-local and dependency-free.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._initialize_schema()

    def __call__(self, payload: Dict[str, Any]) -> None:
        record = self._build_record(payload)

        with self._lock:
            with sqlite3.connect(self.path) as conn:
                conn.execute(
                    """
                    INSERT INTO trading_decision_audit (
                        persisted_at,
                        request_identity,
                        request_id,
                        actor_id,
                        strategy_id,
                        source_id,
                        execution_path_classification,
                        symbol,
                        side,
                        quantity,
                        price,
                        order_type,
                        decision_outcome,
                        decision_reason,
                        order_id,
                        payload_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record["persisted_at"],
                        record.get("request_identity"),
                        record.get("request_id"),
                        record.get("actor_id"),
                        record.get("strategy_id"),
                        record.get("source_id"),
                        record.get("execution_path_classification"),
                        record.get("symbol"),
                        record.get("side"),
                        record.get("quantity"),
                        record.get("price"),
                        record.get("order_type"),
                        record.get("decision_outcome"),
                        record.get("decision_reason"),
                        record.get("order_id"),
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
                    FROM trading_decision_audit
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
                    CREATE TABLE IF NOT EXISTS trading_decision_audit (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        persisted_at TEXT NOT NULL,
                        request_identity TEXT,
                        request_id TEXT,
                        actor_id TEXT,
                        strategy_id TEXT,
                        source_id TEXT,
                        execution_path_classification TEXT,
                        symbol TEXT,
                        side TEXT,
                        quantity INTEGER,
                        price REAL,
                        order_type TEXT,
                        decision_outcome TEXT NOT NULL,
                        decision_reason TEXT,
                        order_id TEXT,
                        payload_json TEXT NOT NULL
                    )
                    """
                )
                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_trading_decision_audit_request_identity
                    ON trading_decision_audit (request_identity)
                    """
                )
                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_trading_decision_audit_decision_outcome
                    ON trading_decision_audit (decision_outcome)
                    """
                )
                conn.commit()

    @staticmethod
    def _build_record(payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            **payload,
            "persisted_at": datetime.now(timezone.utc).isoformat(),
        }


class CompositeTradingDecisionAuditSink:
    """
    Fan-out sink for keeping a hot-path ledger and a queryable local index in sync.
    """

    def __init__(self, *sinks: Any):
        self._sinks = [sink for sink in sinks if sink is not None]

    def __call__(self, payload: Dict[str, Any]) -> None:
        for sink in self._sinks:
            sink(payload)

    def fetch_recent(self, limit: int = 100) -> list[Dict[str, Any]]:
        for sink in self._sinks:
            if hasattr(sink, "fetch_recent"):
                return sink.fetch_recent(limit=limit)
        return []


def build_default_trading_decision_audit_sink(
    path: Optional[str | Path] = None,
    sqlite_path: Optional[str | Path] = None,
) -> CompositeTradingDecisionAuditSink:
    target_path = Path(path) if path is not None else get_trading_decision_audit_jsonl_path()
    target_sqlite_path = Path(sqlite_path) if sqlite_path is not None else get_trading_decision_audit_sqlite_path()
    return CompositeTradingDecisionAuditSink(
        JsonlTradingDecisionAuditSink(target_path),
        SqliteTradingDecisionAuditSink(target_sqlite_path),
    )
