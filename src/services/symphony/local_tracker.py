from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .config import TrackerConfig
from .models import BlockerRef, Issue


class LocalIssueTrackerClient:
    """SQLite-backed local issue tracker for Symphony."""

    def __init__(self, tracker: TrackerConfig) -> None:
        if tracker.sqlite_path is None:
            raise ValueError("Local tracker requires a sqlite_path.")

        self.tracker = tracker
        self._db_path = tracker.sqlite_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def close(self) -> None:
        return None

    def create_issue(
        self,
        title: str,
        description: str | None = None,
        state: str = "Todo",
        priority: int | None = None,
        labels: list[str] | None = None,
        blocked_by: list[BlockerRef] | None = None,
        identifier: str | None = None,
        branch_name: str | None = None,
        url: str | None = None,
    ) -> Issue:
        issue_id = str(uuid4())
        issue_identifier = identifier or self._next_identifier()
        now = _utcnow()
        normalized_labels = _normalize_labels(labels or [])
        serialized_blockers = _serialize_blockers(blocked_by or [])

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO issues (
                    id, identifier, title, description, state, state_normalized, priority,
                    branch_name, url, labels_json, blocked_by_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    issue_id,
                    issue_identifier,
                    title,
                    description,
                    state,
                    state.strip().lower(),
                    priority,
                    branch_name,
                    url,
                    json.dumps(normalized_labels, ensure_ascii=False),
                    json.dumps(serialized_blockers, ensure_ascii=False),
                    now,
                    now,
                ),
            )
            self._append_event(
                connection,
                issue_id=issue_id,
                event_type="issue_created",
                payload={
                    "issue_id": issue_id,
                    "identifier": issue_identifier,
                    "title": title,
                    "state": state,
                },
            )

        return self.fetch_issue_states_by_ids([issue_id])[0]

    def update_issue_state(self, identifier: str, state: str) -> Issue:
        now = _utcnow()
        with self._connect() as connection:
            row = connection.execute(
                "SELECT id FROM issues WHERE identifier = ?",
                (identifier,),
            ).fetchone()
            if row is None:
                raise KeyError(f"Unknown local tracker issue: {identifier}")

            issue_id = str(row["id"])
            connection.execute(
                """
                UPDATE issues
                SET state = ?, state_normalized = ?, updated_at = ?
                WHERE identifier = ?
                """,
                (state, state.strip().lower(), now, identifier),
            )
            self._append_event(
                connection,
                issue_id=issue_id,
                event_type="issue_state_updated",
                payload={"issue_id": issue_id, "identifier": identifier, "state": state},
            )

        return self.fetch_issue_states_by_ids([issue_id])[0]

    def list_issues(self) -> list[Issue]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM issues ORDER BY created_at ASC, identifier ASC").fetchall()
        return [self._row_to_issue(row) for row in rows]

    def list_events(self, issue_id: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT issue_id, event_type, payload_json, created_at
                FROM issue_events
                WHERE issue_id = ?
                ORDER BY id ASC
                """,
                (issue_id,),
            ).fetchall()

        return [
            {
                "issue_id": str(row["issue_id"]),
                "event_type": str(row["event_type"]),
                "payload": _safe_json_loads(row["payload_json"], default={}),
                "created_at": str(row["created_at"]),
            }
            for row in rows
        ]

    def fetch_candidate_issues(self) -> list[Issue]:
        return self.fetch_issues_by_states(self.tracker.active_states)

    def fetch_issues_by_states(self, state_names: list[str]) -> list[Issue]:
        if not state_names:
            return []

        normalized_states = [_normalize_state_name(state_name) for state_name in state_names if state_name.strip()]
        if not normalized_states:
            return []

        placeholders = ", ".join("?" for _ in normalized_states)
        with self._connect() as connection:
            rows = connection.execute(
                f"""
                SELECT *
                FROM issues
                WHERE state_normalized IN ({placeholders})
                ORDER BY created_at ASC, identifier ASC
                """,
                tuple(normalized_states),
            ).fetchall()
        return [self._row_to_issue(row) for row in rows]

    def fetch_issue_states_by_ids(self, issue_ids: list[str]) -> list[Issue]:
        if not issue_ids:
            return []

        placeholders = ", ".join("?" for _ in issue_ids)
        with self._connect() as connection:
            rows = connection.execute(
                f"SELECT * FROM issues WHERE id IN ({placeholders})",
                tuple(issue_ids),
            ).fetchall()

        issues_by_id = {issue.id: issue for issue in (self._row_to_issue(row) for row in rows)}
        return [issues_by_id[issue_id] for issue_id in issue_ids if issue_id in issues_by_id]

    def _ensure_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS issues (
                    id TEXT PRIMARY KEY,
                    identifier TEXT NOT NULL UNIQUE,
                    title TEXT NOT NULL,
                    description TEXT,
                    state TEXT NOT NULL,
                    state_normalized TEXT NOT NULL,
                    priority INTEGER,
                    branch_name TEXT,
                    url TEXT,
                    labels_json TEXT NOT NULL DEFAULT '[]',
                    blocked_by_json TEXT NOT NULL DEFAULT '[]',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS issue_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    issue_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute("CREATE INDEX IF NOT EXISTS idx_issues_state_normalized ON issues(state_normalized)")
            connection.execute("CREATE INDEX IF NOT EXISTS idx_issue_events_issue_id ON issue_events(issue_id)")

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _next_identifier(self) -> str:
        with self._connect() as connection:
            rows = connection.execute("SELECT identifier FROM issues WHERE identifier LIKE 'LOCAL-%'").fetchall()

        max_suffix = 0
        for row in rows:
            identifier = str(row["identifier"])
            prefix, _, suffix = identifier.partition("-")
            if prefix != "LOCAL":
                continue
            try:
                max_suffix = max(max_suffix, int(suffix))
            except ValueError:
                continue

        return f"LOCAL-{max_suffix + 1}"

    def _append_event(
        self, connection: sqlite3.Connection, issue_id: str, event_type: str, payload: dict[str, Any]
    ) -> None:
        connection.execute(
            """
            INSERT INTO issue_events (issue_id, event_type, payload_json, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                issue_id,
                event_type,
                json.dumps(payload, ensure_ascii=False),
                _utcnow(),
            ),
        )

    def _row_to_issue(self, row: sqlite3.Row) -> Issue:
        blocked_by_payload = _safe_json_loads(row["blocked_by_json"], default=[])
        blocked_by = [
            BlockerRef(
                id=blocker.get("id"),
                identifier=blocker.get("identifier"),
                state=blocker.get("state"),
            )
            for blocker in blocked_by_payload
            if isinstance(blocker, dict)
        ]

        return Issue(
            id=str(row["id"]),
            identifier=str(row["identifier"]),
            title=str(row["title"]),
            description=row["description"],
            priority=int(row["priority"]) if row["priority"] is not None else None,
            state=str(row["state"]),
            branch_name=row["branch_name"],
            url=row["url"],
            labels=_safe_json_loads(row["labels_json"], default=[]),
            blocked_by=blocked_by,
            created_at=_parse_timestamp(row["created_at"]),
            updated_at=_parse_timestamp(row["updated_at"]),
        )


def _normalize_state_name(value: str) -> str:
    return value.strip().lower()


def _normalize_labels(labels: list[str]) -> list[str]:
    normalized_labels: list[str] = []
    for label in labels:
        normalized = str(label).strip().lower()
        if normalized:
            normalized_labels.append(normalized)
    return normalized_labels


def _serialize_blockers(blockers: list[BlockerRef]) -> list[dict[str, str | None]]:
    return [
        {
            "id": blocker.id,
            "identifier": blocker.identifier,
            "state": blocker.state,
        }
        for blocker in blockers
    ]


def _safe_json_loads(value: Any, default: Any) -> Any:
    if not value:
        return default
    if isinstance(value, (list, dict)):
        return value
    try:
        return json.loads(str(value))
    except json.JSONDecodeError:
        return default


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_timestamp(value: Any) -> datetime | None:
    if not value:
        return None
    normalized = str(value).replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None
