from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pymongo import ASCENDING, IndexModel

from .models import AssignmentState, WorkerHeartbeat, WorkspaceBinding


class MongoCollaborationRegistry:
    """Mongo-backed runtime collaboration registry for Maestro/Symphony."""

    def __init__(self, database: Any) -> None:
        self._database = database
        self._assignments = database["issue_assignments"]
        self._workspaces = database["worktree_registry"]
        self._heartbeats = database["worker_heartbeats"]
        self._ensure_indexes()

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
        issue_identifier = _require_issue_identifier(issue)
        existing = self._assignments.find_one({"issue_identifier": issue_identifier}) or {}
        document = {
            "issue_identifier": issue_identifier,
            "issue_id": _safe_getattr(issue, "id") or existing.get("issue_id"),
            "assigned_worker_cli": assigned_worker_cli or existing.get("assigned_worker_cli"),
            "assigned_by": assigned_by or existing.get("assigned_by"),
            "status": status,
            "acceptance_summary": acceptance_summary or existing.get("acceptance_summary"),
            "updated_at": _utcnow(),
        }
        self._assignments.replace_one({"issue_identifier": issue_identifier}, document, upsert=True)

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
        existing = self._workspaces.find_one({"issue_identifier": issue_identifier}) or {}
        created_at = existing.get("created_at") or _utcnow()
        document = {
            "issue_identifier": issue_identifier,
            "issue_id": issue_id or existing.get("issue_id"),
            "workspace_key": workspace.workspace_key,
            "workspace_path": str(workspace.path),
            "branch_name": branch_name or existing.get("branch_name"),
            "owner_cli": owner_cli or existing.get("owner_cli"),
            "created_at": created_at,
            "updated_at": _utcnow(),
        }
        self._workspaces.replace_one({"issue_identifier": issue_identifier}, document, upsert=True)

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
        issue_identifier = _require_issue_identifier(issue)
        existing = self._heartbeats.find_one({"issue_identifier": issue_identifier}) or {}
        timestamp = (heartbeat_at or datetime.now(timezone.utc)).astimezone(timezone.utc).isoformat()
        document = {
            "issue_identifier": issue_identifier,
            "issue_id": _safe_getattr(issue, "id") or existing.get("issue_id"),
            "session_id": session_id or existing.get("session_id"),
            "worker_cli": worker_cli or existing.get("worker_cli"),
            "last_event": last_event or existing.get("last_event"),
            "last_message": last_message or existing.get("last_message"),
            "heartbeat_at": timestamp,
            "stale_after_seconds": max(int(stale_after_seconds), 1),
            "updated_at": _utcnow(),
        }
        self._heartbeats.replace_one({"issue_identifier": issue_identifier}, document, upsert=True)

    def get_issue_state(self, issue_identifier: str) -> dict[str, Any]:
        assignment = self.get_assignment_state(issue_identifier)
        workspace = _to_workspace_dict(self._workspaces.find_one({"issue_identifier": issue_identifier}))
        heartbeat = _to_heartbeat_dict(self._heartbeats.find_one({"issue_identifier": issue_identifier}))
        return {
            "assignment": assignment,
            "workspace": workspace,
            "heartbeat": heartbeat,
        }

    def get_assignment_state(self, issue_identifier: str) -> dict[str, Any] | None:
        return _to_assignment_dict(self._assignments.find_one({"issue_identifier": issue_identifier}))

    def list_workspaces(self) -> list[dict[str, Any]]:
        cursor = self._workspaces.find({}).sort("issue_identifier", ASCENDING)
        return [_to_workspace_dict(row) for row in cursor if row is not None]

    def list_stale_heartbeats(self, now: datetime | None = None) -> list[dict[str, Any]]:
        reference = now or datetime.now(timezone.utc)
        cursor = self._heartbeats.find({}).sort("issue_identifier", ASCENDING)
        stale_rows: list[dict[str, Any]] = []
        for row in cursor:
            if row is None:
                continue
            payload = _to_heartbeat_dict(row, now=reference)
            if payload is not None and payload["stale"]:
                stale_rows.append(payload)
        return stale_rows

    def list_control_plane_status_views(self) -> list[dict[str, Any]]:
        try:
            control_status_views = self._database["worker_status_views"]
        except Exception:
            return []
        cursor = control_status_views.find({}).sort("work_item_id", ASCENDING)
        return [_strip_mongo_internal_fields(dict(row)) for row in cursor if row is not None]

    def sync_work_item_progress(self, issue: Any, *, status: str, latest_update: str | None = None) -> None:
        try:
            control_work_items = self._database["work_items"]
            control_status_views = self._database["worker_status_views"]
        except Exception:
            return

        issue_identifier = _require_issue_identifier(issue)
        work_item = control_work_items.find_one({"work_item_id": issue_identifier})
        if work_item is None:
            return

        updated_at = _utcnow()
        updated_work_item = dict(work_item)
        updated_work_item["status"] = status
        updated_work_item["updated_at"] = updated_at
        control_work_items.replace_one({"work_item_id": issue_identifier}, updated_work_item, upsert=True)

        existing_view = control_status_views.find_one({"work_item_id": issue_identifier}) or {}
        status_view = {
            "work_item_id": issue_identifier,
            "branch": work_item.get("branch") or _safe_getattr(issue, "branch_name") or existing_view.get("branch", ""),
            "owner_cli": work_item.get("owner_cli") or existing_view.get("owner_cli", ""),
            "status": status,
            "latest_update": latest_update if latest_update is not None else existing_view.get("latest_update"),
            "blocker": existing_view.get("blocker"),
            "has_pending_request": existing_view.get("has_pending_request", False),
            "updated_at": updated_at,
        }
        control_status_views.replace_one({"work_item_id": issue_identifier}, status_view, upsert=True)

    def _ensure_indexes(self) -> None:
        self._assignments.create_indexes(
            [
                IndexModel([("issue_identifier", ASCENDING)], name="ux_issue_assignments_issue_identifier", unique=True),
            ]
        )
        self._workspaces.create_indexes(
            [
                IndexModel([("issue_identifier", ASCENDING)], name="ux_worktree_registry_issue_identifier", unique=True),
            ]
        )
        self._heartbeats.create_indexes(
            [
                IndexModel([("issue_identifier", ASCENDING)], name="ux_worker_heartbeats_issue_identifier", unique=True),
            ]
        )


class DualWriteCollaborationRegistry:
    """Write to both primary and secondary collaboration registries."""

    def __init__(self, *, primary: Any, secondary: Any) -> None:
        self.primary = primary
        self.secondary = secondary

    def close(self) -> None:
        if hasattr(self.primary, "close"):
            self.primary.close()
        if hasattr(self.secondary, "close"):
            self.secondary.close()

    def record_assignment(self, issue: Any, **kwargs) -> None:
        self.primary.record_assignment(issue, **kwargs)
        self.secondary.record_assignment(issue, **kwargs)

    def register_workspace(self, issue: Any, workspace: Any, **kwargs) -> None:
        self.primary.register_workspace(issue, workspace, **kwargs)
        self.secondary.register_workspace(issue, workspace, **kwargs)

    def register_workspace_for_issue(self, **kwargs) -> None:
        self.primary.register_workspace_for_issue(**kwargs)
        self.secondary.register_workspace_for_issue(**kwargs)

    def record_heartbeat(self, issue: Any, **kwargs) -> None:
        self.primary.record_heartbeat(issue, **kwargs)
        self.secondary.record_heartbeat(issue, **kwargs)

    def get_issue_state(self, issue_identifier: str) -> dict[str, Any]:
        return self.primary.get_issue_state(issue_identifier)

    def get_assignment_state(self, issue_identifier: str) -> dict[str, Any] | None:
        return self.primary.get_assignment_state(issue_identifier)

    def list_workspaces(self) -> list[dict[str, Any]]:
        return self.primary.list_workspaces()

    def list_stale_heartbeats(self, now: datetime | None = None) -> list[dict[str, Any]]:
        return self.primary.list_stale_heartbeats(now=now)

    def list_control_plane_status_views(self) -> list[dict[str, Any]]:
        if hasattr(self.primary, "list_control_plane_status_views"):
            return self.primary.list_control_plane_status_views()
        return []

    def sync_work_item_progress(self, issue: Any, *, status: str, latest_update: str | None = None) -> None:
        if hasattr(self.primary, "sync_work_item_progress"):
            self.primary.sync_work_item_progress(issue, status=status, latest_update=latest_update)
        if hasattr(self.secondary, "sync_work_item_progress"):
            self.secondary.sync_work_item_progress(issue, status=status, latest_update=latest_update)


def _to_assignment_dict(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    row = _strip_mongo_internal_fields(row)
    return AssignmentState(
        issue_id=row.get("issue_id"),
        issue_identifier=str(row["issue_identifier"]),
        assigned_worker_cli=row.get("assigned_worker_cli"),
        assigned_by=row.get("assigned_by"),
        status=str(row["status"]),
        acceptance_summary=row.get("acceptance_summary"),
        updated_at=str(row["updated_at"]),
    ).to_dict()


def _to_workspace_dict(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    row = _strip_mongo_internal_fields(row)
    return WorkspaceBinding(
        issue_id=row.get("issue_id"),
        issue_identifier=str(row["issue_identifier"]),
        workspace_key=str(row["workspace_key"]),
        workspace_path=str(row["workspace_path"]),
        branch_name=row.get("branch_name"),
        owner_cli=row.get("owner_cli"),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
    ).to_dict()


def _to_heartbeat_dict(row: dict[str, Any] | None, now: datetime | None = None) -> dict[str, Any] | None:
    if row is None:
        return None
    row = _strip_mongo_internal_fields(row)
    heartbeat_at = _parse_timestamp(row.get("heartbeat_at")) or datetime.now(timezone.utc)
    reference = now or datetime.now(timezone.utc)
    stale_after_seconds = int(row["stale_after_seconds"])
    stale = (reference - heartbeat_at).total_seconds() > stale_after_seconds
    return WorkerHeartbeat(
        issue_id=row.get("issue_id"),
        issue_identifier=str(row["issue_identifier"]),
        session_id=row.get("session_id"),
        worker_cli=row.get("worker_cli"),
        last_event=row.get("last_event"),
        last_message=row.get("last_message"),
        heartbeat_at=str(row["heartbeat_at"]),
        stale_after_seconds=stale_after_seconds,
        updated_at=str(row["updated_at"]),
        stale=stale,
    ).to_dict()


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


def _strip_mongo_internal_fields(document: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in document.items() if key != "_id"}
