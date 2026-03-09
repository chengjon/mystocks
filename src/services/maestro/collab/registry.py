from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import AssignmentState, WorkerHeartbeat, WorkspaceBinding


class SQLiteCollaborationRegistry:
    """Persist machine-state collaboration metadata for Maestro."""

    def __init__(self, sqlite_path: str | Path) -> None:
        self._db_path = Path(sqlite_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def close(self) -> None:
        return None

    def record_assignment(
        self,
        issue: Any,
        *,
        status: str,
        assigned_worker_cli: str | None = None,
        assigned_by: str | None = None,
        acceptance_summary: str | None = None,
    ) -> None:
        issue_id = _safe_getattr(issue, "id")
        issue_identifier = _require_issue_identifier(issue)
        now = _utcnow()

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO issue_assignments (
                    issue_identifier, issue_id, assigned_worker_cli, assigned_by, status, acceptance_summary, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(issue_identifier) DO UPDATE SET
                    issue_id = excluded.issue_id,
                    assigned_worker_cli = COALESCE(excluded.assigned_worker_cli, issue_assignments.assigned_worker_cli),
                    assigned_by = COALESCE(excluded.assigned_by, issue_assignments.assigned_by),
                    status = excluded.status,
                    acceptance_summary = COALESCE(excluded.acceptance_summary, issue_assignments.acceptance_summary),
                    updated_at = excluded.updated_at
                """,
                (
                    issue_identifier,
                    issue_id,
                    assigned_worker_cli,
                    assigned_by,
                    status,
                    acceptance_summary,
                    now,
                ),
            )

    def register_workspace(
        self,
        issue: Any,
        workspace: Any,
        *,
        owner_cli: str | None = None,
        branch_name: str | None = None,
    ) -> None:
        self.register_workspace_for_issue(
            issue_identifier=_require_issue_identifier(issue),
            workspace=workspace,
            issue_id=_safe_getattr(issue, "id"),
            owner_cli=owner_cli,
            branch_name=branch_name or _safe_getattr(issue, "branch_name"),
        )

    def register_workspace_for_issue(
        self,
        *,
        issue_identifier: str,
        workspace: Any,
        issue_id: str | None = None,
        owner_cli: str | None = None,
        branch_name: str | None = None,
    ) -> None:
        now = _utcnow()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO worktree_registry (
                    issue_identifier, issue_id, workspace_key, workspace_path, branch_name, owner_cli, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(issue_identifier) DO UPDATE SET
                    issue_id = COALESCE(excluded.issue_id, worktree_registry.issue_id),
                    workspace_key = excluded.workspace_key,
                    workspace_path = excluded.workspace_path,
                    branch_name = COALESCE(excluded.branch_name, worktree_registry.branch_name),
                    owner_cli = COALESCE(excluded.owner_cli, worktree_registry.owner_cli),
                    updated_at = excluded.updated_at
                """,
                (
                    issue_identifier,
                    issue_id,
                    workspace.workspace_key,
                    str(workspace.path),
                    branch_name,
                    owner_cli,
                    now,
                    now,
                ),
            )

    def record_heartbeat(
        self,
        issue: Any,
        *,
        session_id: str | None = None,
        worker_cli: str | None = None,
        last_event: str | None = None,
        last_message: str | None = None,
        stale_after_seconds: int = 90,
        heartbeat_at: datetime | None = None,
    ) -> None:
        issue_id = _safe_getattr(issue, "id")
        issue_identifier = _require_issue_identifier(issue)
        heartbeat_timestamp = (heartbeat_at or datetime.now(timezone.utc)).astimezone(timezone.utc).isoformat()
        now = _utcnow()

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO worker_heartbeats (
                    issue_identifier, issue_id, session_id, worker_cli, last_event, last_message,
                    heartbeat_at, stale_after_seconds, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(issue_identifier) DO UPDATE SET
                    issue_id = COALESCE(excluded.issue_id, worker_heartbeats.issue_id),
                    session_id = COALESCE(excluded.session_id, worker_heartbeats.session_id),
                    worker_cli = COALESCE(excluded.worker_cli, worker_heartbeats.worker_cli),
                    last_event = COALESCE(excluded.last_event, worker_heartbeats.last_event),
                    last_message = COALESCE(excluded.last_message, worker_heartbeats.last_message),
                    heartbeat_at = excluded.heartbeat_at,
                    stale_after_seconds = excluded.stale_after_seconds,
                    updated_at = excluded.updated_at
                """,
                (
                    issue_identifier,
                    issue_id,
                    session_id,
                    worker_cli,
                    last_event,
                    last_message,
                    heartbeat_timestamp,
                    max(int(stale_after_seconds), 1),
                    now,
                ),
            )

    def get_issue_state(self, issue_identifier: str) -> dict[str, Any]:
        with self._connect() as connection:
            assignment_row = connection.execute(
                "SELECT * FROM issue_assignments WHERE issue_identifier = ?",
                (issue_identifier,),
            ).fetchone()
            workspace_row = connection.execute(
                "SELECT * FROM worktree_registry WHERE issue_identifier = ?",
                (issue_identifier,),
            ).fetchone()
            heartbeat_row = connection.execute(
                "SELECT * FROM worker_heartbeats WHERE issue_identifier = ?",
                (issue_identifier,),
            ).fetchone()

        return {
            "assignment": self._row_to_assignment(assignment_row).to_dict() if assignment_row is not None else None,
            "workspace": self._row_to_workspace(workspace_row).to_dict() if workspace_row is not None else None,
            "heartbeat": self._row_to_heartbeat(heartbeat_row).to_dict() if heartbeat_row is not None else None,
        }

    def get_assignment_state(self, issue_identifier: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM issue_assignments WHERE issue_identifier = ?",
                (issue_identifier,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_assignment(row).to_dict()

    def list_workspaces(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM worktree_registry ORDER BY issue_identifier ASC").fetchall()
        return [self._row_to_workspace(row).to_dict() for row in rows]

    def list_stale_heartbeats(self, now: datetime | None = None) -> list[dict[str, Any]]:
        reference = now or datetime.now(timezone.utc)
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM worker_heartbeats ORDER BY issue_identifier ASC").fetchall()

        stale_rows: list[dict[str, Any]] = []
        for row in rows:
            heartbeat = self._row_to_heartbeat(row, now=reference)
            if heartbeat.stale:
                stale_rows.append(heartbeat.to_dict())
        return stale_rows

    def _ensure_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS issue_assignments (
                    issue_identifier TEXT PRIMARY KEY,
                    issue_id TEXT,
                    assigned_worker_cli TEXT,
                    assigned_by TEXT,
                    status TEXT NOT NULL,
                    acceptance_summary TEXT,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS worktree_registry (
                    issue_identifier TEXT PRIMARY KEY,
                    issue_id TEXT,
                    workspace_key TEXT NOT NULL,
                    workspace_path TEXT NOT NULL,
                    branch_name TEXT,
                    owner_cli TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS worker_heartbeats (
                    issue_identifier TEXT PRIMARY KEY,
                    issue_id TEXT,
                    session_id TEXT,
                    worker_cli TEXT,
                    last_event TEXT,
                    last_message TEXT,
                    heartbeat_at TEXT NOT NULL,
                    stale_after_seconds INTEGER NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._db_path)
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def _row_to_assignment(row: sqlite3.Row) -> AssignmentState:
        return AssignmentState(
            issue_id=row["issue_id"],
            issue_identifier=str(row["issue_identifier"]),
            assigned_worker_cli=row["assigned_worker_cli"],
            assigned_by=row["assigned_by"],
            status=str(row["status"]),
            acceptance_summary=row["acceptance_summary"],
            updated_at=str(row["updated_at"]),
        )

    @staticmethod
    def _row_to_workspace(row: sqlite3.Row) -> WorkspaceBinding:
        return WorkspaceBinding(
            issue_id=row["issue_id"],
            issue_identifier=str(row["issue_identifier"]),
            workspace_key=str(row["workspace_key"]),
            workspace_path=str(row["workspace_path"]),
            branch_name=row["branch_name"],
            owner_cli=row["owner_cli"],
            created_at=str(row["created_at"]),
            updated_at=str(row["updated_at"]),
        )

    @staticmethod
    def _row_to_heartbeat(row: sqlite3.Row, now: datetime | None = None) -> WorkerHeartbeat:
        heartbeat_at = _parse_timestamp(row["heartbeat_at"]) or datetime.now(timezone.utc)
        reference = now or datetime.now(timezone.utc)
        stale_after_seconds = int(row["stale_after_seconds"])
        stale = (reference - heartbeat_at).total_seconds() > stale_after_seconds
        return WorkerHeartbeat(
            issue_id=row["issue_id"],
            issue_identifier=str(row["issue_identifier"]),
            session_id=row["session_id"],
            worker_cli=row["worker_cli"],
            last_event=row["last_event"],
            last_message=row["last_message"],
            heartbeat_at=str(row["heartbeat_at"]),
            stale_after_seconds=stale_after_seconds,
            updated_at=str(row["updated_at"]),
            stale=stale,
        )


def _require_issue_identifier(issue: Any) -> str:
    identifier = _safe_getattr(issue, "identifier")
    if not identifier:
        raise ValueError("Expected issue identifier for collaboration registry operations.")
    return str(identifier)


def _safe_getattr(value: Any, attribute: str) -> Any:
    return getattr(value, attribute, None)


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_timestamp(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
