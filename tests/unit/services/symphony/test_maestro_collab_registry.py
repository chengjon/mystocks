from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.services.maestro.collab import SQLiteCollaborationRegistry
from src.services.symphony.models import Issue, Workspace


def _make_issue(identifier: str = "MT-1", issue_id: str = "issue-1") -> Issue:
    return Issue(
        id=issue_id,
        identifier=identifier,
        title="Task",
        description="Body",
        priority=1,
        state="In Progress",
        branch_name=None,
        url=None,
        labels=[],
        blocked_by=[],
        created_at=datetime.now(timezone.utc),
        updated_at=None,
    )


def test_sqlite_collaboration_registry_persists_assignment_workspace_and_heartbeat(tmp_path: Path) -> None:
    registry = SQLiteCollaborationRegistry(tmp_path / "tracker.db")
    issue = _make_issue()
    workspace = Workspace(
        path=(tmp_path / "workspaces" / "MT-1").resolve(),
        workspace_key="MT-1",
        issue_identifier=issue.identifier,
        created_now=True,
    )

    registry.record_assignment(
        issue,
        status="running",
        assigned_worker_cli="cli-1",
        assigned_by="main",
        acceptance_summary="ship the fix",
    )
    registry.register_workspace(issue, workspace, owner_cli="cli-1", branch_name="feat/mt-1-cli-1")
    registry.record_heartbeat(
        issue,
        session_id="session-1",
        worker_cli="cli-1",
        last_event="turn.completed",
        last_message="ok",
        stale_after_seconds=30,
    )

    snapshot = registry.get_issue_state(issue.identifier)

    assert snapshot["assignment"]["status"] == "running"
    assert snapshot["assignment"]["assigned_worker_cli"] == "cli-1"
    assert snapshot["workspace"]["workspace_key"] == "MT-1"
    assert snapshot["workspace"]["branch_name"] == "feat/mt-1-cli-1"
    assert snapshot["heartbeat"]["session_id"] == "session-1"
    assert snapshot["heartbeat"]["last_event"] == "turn.completed"


def test_sqlite_collaboration_registry_lists_stale_heartbeats(tmp_path: Path) -> None:
    registry = SQLiteCollaborationRegistry(tmp_path / "tracker.db")
    issue = _make_issue("MT-2", "issue-2")
    stale_at = datetime.now(timezone.utc) - timedelta(seconds=120)

    registry.record_heartbeat(
        issue,
        session_id="session-2",
        worker_cli="cli-2",
        last_event="turn.started",
        stale_after_seconds=30,
        heartbeat_at=stale_at,
    )

    stale = registry.list_stale_heartbeats(now=datetime.now(timezone.utc))

    assert [row["issue_identifier"] for row in stale] == ["MT-2"]
    assert stale[0]["stale"] is True
