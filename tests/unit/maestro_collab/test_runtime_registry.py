from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

from src.services.maestro.collab.models import AssignmentState, WorkerHeartbeat, WorkspaceBinding
from src.services.maestro.collab.runtime_registry import DualWriteCollaborationRegistry, MongoCollaborationRegistry


def test_mongo_runtime_registry_persists_assignment_workspace_and_heartbeat() -> None:
    registry = MongoCollaborationRegistry(_FakeDatabase())
    issue = _IssueRef("MT-500", issue_id="issue-500", branch_name="feat/runtime")
    workspace = _WorkspaceRef("mt-500", Path("/tmp/mt-500"))
    heartbeat_at = _ts("2026-03-14T02:00:00Z")

    registry.record_assignment(issue, status="running", assigned_worker_cli="cli-1", assigned_by="runtime")
    registry.register_workspace_for_issue(
        issue_identifier=issue.identifier,
        issue_id=issue.id,
        workspace=workspace,
        owner_cli="cli-1",
        branch_name=issue.branch_name,
    )
    registry.record_heartbeat(
        issue,
        session_id="session-500",
        worker_cli="cli-1",
        last_event="turn.completed",
        heartbeat_at=heartbeat_at,
        stale_after_seconds=60,
    )

    assignment = registry.get_assignment_state("MT-500")
    snapshot = registry.get_issue_state("MT-500")
    stale = registry.list_stale_heartbeats(now=heartbeat_at + timedelta(seconds=120))

    assert assignment == AssignmentState(
        issue_id="issue-500",
        issue_identifier="MT-500",
        assigned_worker_cli="cli-1",
        assigned_by="runtime",
        status="running",
        acceptance_summary=None,
        updated_at=assignment["updated_at"],
    ).to_dict()
    assert snapshot["workspace"]["workspace_key"] == "mt-500"
    assert snapshot["heartbeat"]["session_id"] == "session-500"
    assert stale[0]["issue_identifier"] == "MT-500"
    assert stale[0]["stale"] is True


def test_dual_write_registry_mirrors_writes_to_primary_and_secondary() -> None:
    primary = _RecordingRegistry()
    secondary = _RecordingRegistry()
    registry = DualWriteCollaborationRegistry(primary=primary, secondary=secondary)
    issue = _IssueRef("MT-501", issue_id="issue-501")

    registry.record_assignment(issue, status="running", assigned_worker_cli="cli-2", assigned_by="runtime")
    registry.record_heartbeat(issue, session_id="session-501", worker_cli="cli-2")

    assert primary.actions == secondary.actions


def test_mongo_runtime_registry_syncs_runtime_progress_into_control_plane_views() -> None:
    database = _FakeDatabase()
    database["work_items"].docs.append(
        {
            "work_item_id": "MT-502",
            "task_key": "runtime-progress",
            "title": "Runtime progress",
            "objective": "Sync runtime state",
            "branch": "feat/runtime-progress",
            "owner_cli": "cli-3",
            "status": "dispatched",
            "created_at": "2026-03-14T02:10:00+00:00",
            "updated_at": "2026-03-14T02:10:00+00:00",
        }
    )
    registry = MongoCollaborationRegistry(database)
    issue = _IssueRef("MT-502", issue_id="issue-502", branch_name="feat/runtime-progress")

    registry.sync_work_item_progress(issue, status="in_progress", latest_update="Runtime started")

    assert database["work_items"].find_one({"work_item_id": "MT-502"})["status"] == "in_progress"
    status_view = database["worker_status_views"].find_one({"work_item_id": "MT-502"})
    assert status_view["status"] == "in_progress"
    assert status_view["latest_update"] == "Runtime started"


def test_mongo_runtime_registry_lists_control_plane_status_views() -> None:
    database = _FakeDatabase()
    database["worker_status_views"].docs.extend(
        [
            {
                "_id": "mongo-view-1",
                "work_item_id": "MT-503",
                "branch": "feat/a",
                "owner_cli": "cli-1",
                "status": "in_progress",
                "latest_update": "alpha",
                "blocker": None,
                "has_pending_request": False,
                "updated_at": "2026-03-14T02:20:00+00:00",
            },
            {
                "_id": "mongo-view-2",
                "work_item_id": "MT-504",
                "branch": "feat/b",
                "owner_cli": "cli-2",
                "status": "ready_for_review",
                "latest_update": "beta",
                "blocker": None,
                "has_pending_request": True,
                "updated_at": "2026-03-14T02:21:00+00:00",
            },
        ]
    )
    registry = MongoCollaborationRegistry(database)

    items = registry.list_control_plane_status_views()

    assert [item["work_item_id"] for item in items] == ["MT-503", "MT-504"]
    assert items[1]["has_pending_request"] is True


@dataclass(frozen=True)
class _IssueRef:
    identifier: str
    issue_id: str | None = None
    branch_name: str | None = None

    @property
    def id(self) -> str | None:
        return self.issue_id


@dataclass(frozen=True)
class _WorkspaceRef:
    workspace_key: str
    path: Path


class _RecordingRegistry:
    def __init__(self) -> None:
        self.actions: list[tuple] = []

    def record_assignment(self, issue, **kwargs) -> None:
        self.actions.append(("assignment", issue.identifier, kwargs["status"]))

    def register_workspace_for_issue(self, **kwargs) -> None:
        self.actions.append(("workspace", kwargs["issue_identifier"], kwargs["workspace"].workspace_key))

    def record_heartbeat(self, issue, **kwargs) -> None:
        self.actions.append(("heartbeat", issue.identifier, kwargs.get("session_id")))

    def sync_work_item_progress(self, issue, **kwargs) -> None:
        self.actions.append(("sync", issue.identifier, kwargs.get("status"), kwargs.get("latest_update")))

    def get_issue_state(self, issue_identifier: str):
        return {"issue_identifier": issue_identifier}

    def get_assignment_state(self, issue_identifier: str):
        return {"issue_identifier": issue_identifier}

    def list_workspaces(self):
        return []

    def list_stale_heartbeats(self, now=None):
        return []

    def close(self) -> None:
        return None


def _ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


class _FakeDatabase:
    def __init__(self) -> None:
        self._collections = {
            "issue_assignments": _FakeCollection(),
            "worktree_registry": _FakeCollection(),
            "worker_heartbeats": _FakeCollection(),
            "work_items": _FakeCollection(),
            "worker_status_views": _FakeCollection(),
        }

    def __getitem__(self, name: str) -> _FakeCollection:
        return self._collections[name]


class _FakeCollection:
    def __init__(self) -> None:
        self.docs: list[dict] = []
        self.indexes = []

    def create_indexes(self, indexes) -> None:
        self.indexes.extend(indexes)

    def replace_one(self, filter_query: dict, document: dict, *, upsert: bool = False) -> None:
        for index, existing in enumerate(self.docs):
            if _matches(existing, filter_query):
                self.docs[index] = document.copy()
                return
        if upsert:
            self.docs.append(document.copy())

    def find_one(self, filter_query: dict) -> dict | None:
        for document in self.docs:
            if _matches(document, filter_query):
                return document.copy()
        return None

    def find(self, filter_query: dict):
        return _FakeCursor([document.copy() for document in self.docs if _matches(document, filter_query)])


class _FakeCursor:
    def __init__(self, docs: list[dict]) -> None:
        self._docs = docs

    def sort(self, key: str, _direction: int):
        self._docs.sort(key=lambda document: document[key])
        return self

    def __iter__(self):
        return iter(self._docs)


def _matches(document: dict, filter_query: dict) -> bool:
    for key, value in filter_query.items():
        if document.get(key) != value:
            return False
    return True
