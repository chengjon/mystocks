"""
Local broker-order correlation ledgers for acknowledgement and reconciliation preparation.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Dict, Optional

from src.utils.trading_runtime_config import get_trading_broker_order_correlation_sqlite_path

LOCAL_ANCHOR_BROKER_CHANNEL = "local_anchor"
MINIQMT_BROKER_CHANNEL = "miniqmt"
TDX_MANUAL_BROKER_CHANNEL = "tdx_manual"


class InMemoryTradingBrokerOrderCorrelationStore:
    """
    Process-local broker-order correlation ledger.

    This does not claim external broker truth. It preserves the local order id and the
    submission attempt identity while the path is still awaiting broker acknowledgement.
    """

    def __init__(self) -> None:
        self._lock = Lock()
        self._records: Dict[str, Dict[str, Optional[str]]] = {}
        self._external_to_order_id: Dict[tuple[str, str], str] = {}
        self._submission_to_order_id: Dict[tuple[str, str], str] = {}

    def upsert_submission(
        self,
        *,
        order_id: str,
        local_submission_id: str,
        broker_channel: str = LOCAL_ANCHOR_BROKER_CHANNEL,
        adapter_path: str,
        account_scope: str,
        session_scope: Optional[str],
        acknowledgement_status: str,
        external_order_id: Optional[str] = None,
        updated_at: Optional[str] = None,
    ) -> None:
        persisted_at = updated_at or _utc_now().isoformat()
        with self._lock:
            existing = self._records.get(order_id, {})
            existing_channel = existing.get("broker_channel")
            existing_submission_id = existing.get("local_submission_id")
            existing_external_order_id = existing.get("external_order_id")
            resolved_external_order_id = external_order_id or existing.get("external_order_id")
            submission_key = (broker_channel, local_submission_id)
            bound_order_id = self._submission_to_order_id.get(submission_key)
            if bound_order_id is not None and bound_order_id != order_id:
                raise ValueError(
                    f"Broker order correlation already exists for channel-scoped submission: {broker_channel}:{local_submission_id}"
                )

            if resolved_external_order_id is not None:
                external_key = (broker_channel, resolved_external_order_id)
                bound_order_id = self._external_to_order_id.get(external_key)
                if bound_order_id is not None and bound_order_id != order_id:
                    raise ValueError(
                        f"Broker order correlation already exists for channel-scoped external order: {broker_channel}:{resolved_external_order_id}"
                    )

            record = {
                "order_id": order_id,
                "local_submission_id": local_submission_id,
                "broker_channel": broker_channel,
                "adapter_path": adapter_path,
                "account_scope": account_scope,
                "session_scope": session_scope,
                "acknowledgement_status": acknowledgement_status,
                "external_order_id": resolved_external_order_id,
                "updated_at": persisted_at,
            }
            self._records[order_id] = record
            if existing_channel is not None and existing_submission_id is not None:
                self._submission_to_order_id.pop((existing_channel, existing_submission_id), None)
            if existing_channel is not None and existing_external_order_id is not None:
                self._external_to_order_id.pop((existing_channel, existing_external_order_id), None)
            if resolved_external_order_id:
                self._external_to_order_id[(broker_channel, resolved_external_order_id)] = order_id
            self._submission_to_order_id[submission_key] = order_id

    def bind_external_order_id(
        self,
        *,
        order_id: str,
        external_order_id: str,
        acknowledgement_status: str,
        updated_at: Optional[str] = None,
    ) -> None:
        persisted_at = updated_at or _utc_now().isoformat()
        with self._lock:
            existing = self._records.get(order_id)
            if existing is None:
                raise ValueError(f"Broker order correlation not found: {order_id}")

            broker_channel = existing["broker_channel"]
            external_key = (broker_channel, external_order_id)
            bound_order_id = self._external_to_order_id.get(external_key)
            if bound_order_id is not None and bound_order_id != order_id:
                raise ValueError(
                    f"Broker order correlation already exists for channel-scoped external order: {broker_channel}:{external_order_id}"
                )

            previous_external_order_id = existing.get("external_order_id")
            if previous_external_order_id is not None:
                self._external_to_order_id.pop((broker_channel, previous_external_order_id), None)
            existing["external_order_id"] = external_order_id
            existing["acknowledgement_status"] = acknowledgement_status
            existing["updated_at"] = persisted_at
            self._external_to_order_id[external_key] = order_id

    def get_order_correlation(self, order_id: str) -> Optional[Dict[str, Optional[str]]]:
        with self._lock:
            record = self._records.get(order_id)
            if record is None:
                return None
            return dict(record)

    def get_by_external_order_id(
        self,
        external_order_id: str,
        broker_channel: Optional[str] = None,
    ) -> Optional[Dict[str, Optional[str]]]:
        with self._lock:
            if broker_channel is not None:
                order_id = self._external_to_order_id.get((broker_channel, external_order_id))
                if order_id is None:
                    return None
                record = self._records.get(order_id)
                if record is None:
                    return None
                return dict(record)
            return self._get_unique_record_by_field_locked(
                field_name="external_order_id",
                field_value=external_order_id,
            )

    def get_by_local_submission_id(
        self,
        local_submission_id: str,
        broker_channel: Optional[str] = None,
    ) -> Optional[Dict[str, Optional[str]]]:
        with self._lock:
            if broker_channel is not None:
                order_id = self._submission_to_order_id.get((broker_channel, local_submission_id))
                if order_id is None:
                    return None
                record = self._records.get(order_id)
                if record is None:
                    return None
                return dict(record)
            return self._get_unique_record_by_field_locked(
                field_name="local_submission_id",
                field_value=local_submission_id,
            )

    def _get_unique_record_by_field_locked(
        self,
        *,
        field_name: str,
        field_value: str,
    ) -> Optional[Dict[str, Optional[str]]]:
        matched_records = [
            record
            for record in self._records.values()
            if record.get(field_name) == field_value
        ]
        if len(matched_records) != 1:
            return None
        return dict(matched_records[0])


class SqliteTradingBrokerOrderCorrelationStore:
    """
    Local SQLite ledger for local-to-external order identity correlation.

    The ledger remains repository-local and reconstruction-oriented. It preserves a durable
    waiting-for-acknowledgement surface without claiming that the current runtime already has
    a verified broker-facing adapter truth.
    """

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._initialize_schema()

    def upsert_submission(
        self,
        *,
        order_id: str,
        local_submission_id: str,
        broker_channel: str = LOCAL_ANCHOR_BROKER_CHANNEL,
        adapter_path: str,
        account_scope: str,
        session_scope: Optional[str],
        acknowledgement_status: str,
        external_order_id: Optional[str] = None,
        updated_at: Optional[str] = None,
    ) -> None:
        persisted_at = updated_at or _utc_now().isoformat()
        with self._lock:
            with sqlite3.connect(self.path) as conn:
                conn.execute(
                    """
                    INSERT INTO trading_broker_order_correlation (
                        order_id,
                        local_submission_id,
                        broker_channel,
                        adapter_path,
                        account_scope,
                        session_scope,
                        acknowledgement_status,
                        external_order_id,
                        updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(order_id) DO UPDATE SET
                        local_submission_id = excluded.local_submission_id,
                        broker_channel = excluded.broker_channel,
                        adapter_path = excluded.adapter_path,
                        account_scope = excluded.account_scope,
                        session_scope = excluded.session_scope,
                        acknowledgement_status = excluded.acknowledgement_status,
                        external_order_id = COALESCE(excluded.external_order_id, trading_broker_order_correlation.external_order_id),
                        updated_at = excluded.updated_at
                    """,
                    (
                        order_id,
                        local_submission_id,
                        broker_channel,
                        adapter_path,
                        account_scope,
                        session_scope,
                        acknowledgement_status,
                        external_order_id,
                        persisted_at,
                    ),
                )
                conn.commit()

    def bind_external_order_id(
        self,
        *,
        order_id: str,
        external_order_id: str,
        acknowledgement_status: str,
        updated_at: Optional[str] = None,
    ) -> None:
        persisted_at = updated_at or _utc_now().isoformat()
        with self._lock:
            with sqlite3.connect(self.path) as conn:
                cursor = conn.execute(
                    """
                    UPDATE trading_broker_order_correlation
                    SET external_order_id = ?, acknowledgement_status = ?, updated_at = ?
                    WHERE order_id = ?
                    """,
                    (external_order_id, acknowledgement_status, persisted_at, order_id),
                )
                if cursor.rowcount == 0:
                    raise ValueError(f"Broker order correlation not found: {order_id}")
                conn.commit()

    def get_order_correlation(self, order_id: str) -> Optional[Dict[str, Optional[str]]]:
        with self._lock:
            with sqlite3.connect(self.path) as conn:
                conn.row_factory = sqlite3.Row
                row = conn.execute(
                    """
                    SELECT
                        order_id,
                        local_submission_id,
                        broker_channel,
                        adapter_path,
                        account_scope,
                        session_scope,
                        acknowledgement_status,
                        external_order_id,
                        updated_at
                    FROM trading_broker_order_correlation
                    WHERE order_id = ?
                    """,
                    (order_id,),
                ).fetchone()

        if row is None:
            return None

        return _row_to_record(row)

    def get_by_external_order_id(
        self,
        external_order_id: str,
        broker_channel: Optional[str] = None,
    ) -> Optional[Dict[str, Optional[str]]]:
        with self._lock:
            with sqlite3.connect(self.path) as conn:
                conn.row_factory = sqlite3.Row
                row = _select_unique_row(
                    conn=conn,
                    field_name="external_order_id",
                    field_value=external_order_id,
                    broker_channel=broker_channel,
                )

        if row is None:
            return None

        return _row_to_record(row)

    def get_by_local_submission_id(
        self,
        local_submission_id: str,
        broker_channel: Optional[str] = None,
    ) -> Optional[Dict[str, Optional[str]]]:
        with self._lock:
            with sqlite3.connect(self.path) as conn:
                conn.row_factory = sqlite3.Row
                row = _select_unique_row(
                    conn=conn,
                    field_name="local_submission_id",
                    field_value=local_submission_id,
                    broker_channel=broker_channel,
                )

        if row is None:
            return None

        return _row_to_record(row)

    def _initialize_schema(self) -> None:
        with self._lock:
            with sqlite3.connect(self.path) as conn:
                columns = {
                    row[1]
                    for row in conn.execute("PRAGMA table_info(trading_broker_order_correlation)").fetchall()
                }
                if not columns:
                    _create_channel_scoped_correlation_schema(conn)
                elif "broker_channel" not in columns:
                    _migrate_to_channel_scoped_correlation_schema(conn)
                else:
                    _ensure_channel_scoped_correlation_indexes(conn)
                conn.commit()


def build_default_trading_broker_order_correlation_store(
    path: str | Path | None = None,
) -> SqliteTradingBrokerOrderCorrelationStore:
    target_path = Path(path) if path is not None else get_trading_broker_order_correlation_sqlite_path()
    return SqliteTradingBrokerOrderCorrelationStore(target_path)


def _row_to_record(row: sqlite3.Row) -> Dict[str, Optional[str]]:
    return {
        "order_id": row["order_id"],
        "local_submission_id": row["local_submission_id"],
        "broker_channel": row["broker_channel"],
        "adapter_path": row["adapter_path"],
        "account_scope": row["account_scope"],
        "session_scope": row["session_scope"],
        "acknowledgement_status": row["acknowledgement_status"],
        "external_order_id": row["external_order_id"],
        "updated_at": row["updated_at"],
    }


def _select_unique_row(
    *,
    conn: sqlite3.Connection,
    field_name: str,
    field_value: str,
    broker_channel: Optional[str],
) -> Optional[sqlite3.Row]:
    selected_columns = """
        SELECT
            order_id,
            local_submission_id,
            broker_channel,
            adapter_path,
            account_scope,
            session_scope,
            acknowledgement_status,
            external_order_id,
            updated_at
        FROM trading_broker_order_correlation
    """
    if broker_channel is not None:
        row = conn.execute(
            f"""
            {selected_columns}
            WHERE {field_name} = ? AND broker_channel = ?
            """,
            (field_value, broker_channel),
        ).fetchone()
        return row

    rows = conn.execute(
        f"""
        {selected_columns}
        WHERE {field_name} = ?
        ORDER BY updated_at DESC
        LIMIT 2
        """,
        (field_value,),
    ).fetchall()
    if len(rows) != 1:
        return None
    return rows[0]


def _create_channel_scoped_correlation_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS trading_broker_order_correlation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL UNIQUE,
            local_submission_id TEXT NOT NULL,
            broker_channel TEXT NOT NULL,
            adapter_path TEXT NOT NULL,
            account_scope TEXT NOT NULL,
            session_scope TEXT,
            acknowledgement_status TEXT NOT NULL,
            external_order_id TEXT,
            updated_at TEXT NOT NULL
        )
        """
    )
    _ensure_channel_scoped_correlation_indexes(conn)


def _ensure_channel_scoped_correlation_indexes(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS ux_trading_broker_order_correlation_channel_submission
        ON trading_broker_order_correlation (broker_channel, local_submission_id)
        """
    )
    conn.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS ux_trading_broker_order_correlation_channel_external_order_id
        ON trading_broker_order_correlation (broker_channel, external_order_id)
        WHERE external_order_id IS NOT NULL
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_trading_broker_order_correlation_ack_status
        ON trading_broker_order_correlation (acknowledgement_status)
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_trading_broker_order_correlation_channel_external_lookup
        ON trading_broker_order_correlation (broker_channel, external_order_id)
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_trading_broker_order_correlation_channel_submission_lookup
        ON trading_broker_order_correlation (broker_channel, local_submission_id)
        """
    )


def _migrate_to_channel_scoped_correlation_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        "ALTER TABLE trading_broker_order_correlation RENAME TO trading_broker_order_correlation_legacy"
    )
    _create_channel_scoped_correlation_schema(conn)
    conn.execute(
        """
        INSERT INTO trading_broker_order_correlation (
            order_id,
            local_submission_id,
            broker_channel,
            adapter_path,
            account_scope,
            session_scope,
            acknowledgement_status,
            external_order_id,
            updated_at
        )
        SELECT
            order_id,
            local_submission_id,
            ?,
            adapter_path,
            account_scope,
            session_scope,
            acknowledgement_status,
            external_order_id,
            updated_at
        FROM trading_broker_order_correlation_legacy
        """,
        (LOCAL_ANCHOR_BROKER_CHANNEL,),
    )
    conn.execute("DROP TABLE trading_broker_order_correlation_legacy")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)
