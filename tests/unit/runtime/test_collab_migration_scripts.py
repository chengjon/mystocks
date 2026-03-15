from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from src.services.maestro.collab.backends.mongo.store import MongoCollaborationStore
from src.services.maestro.collab.models import AssignmentState
from src.services.maestro.collab.registry import SQLiteCollaborationRegistry
from src.services.maestro.collab.runtime_registry import MongoCollaborationRegistry
from src.services.maestro.collab.store.models import WorkItemRecord, WorkUpdateRecord

from scripts.runtime.export_collab_snapshots import export_work_item_snapshots
from scripts.runtime import migrate_collab_to_mongo
from scripts.runtime.migrate_collab_to_mongo import migrate_markdown_contract, migrate_runtime_registry


def test_migrate_runtime_registry_moves_sqlite_runtime_facts_into_mongo() -> None:
    sqlite_path = Path("/tmp/test-collab-runtime.db")
    if sqlite_path.exists():
        sqlite_path.unlink()

    sqlite_registry = SQLiteCollaborationRegistry(sqlite_path)
    issue = _IssueRef("MT-600", issue_id="issue-600", branch_name="feat/migrate")
    workspace = _WorkspaceRef("mt-600", Path("/tmp/mt-600"))
    sqlite_registry.record_assignment(issue, status="running", assigned_worker_cli="cli-1", assigned_by="runtime")
    sqlite_registry.register_workspace_for_issue(
        issue_identifier=issue.identifier,
        issue_id=issue.id,
        workspace=workspace,
        owner_cli="cli-1",
        branch_name=issue.branch_name,
    )
    sqlite_registry.record_heartbeat(issue, session_id="session-600", worker_cli="cli-1", last_event="turn.completed")

    mongo_database = _FakeMongoDatabase()
    counts = migrate_runtime_registry(sqlite_path=sqlite_path, mongo_database=mongo_database)
    mongo_registry = MongoCollaborationRegistry(mongo_database)

    assert counts == {"assignments": 1, "workspaces": 1, "heartbeats": 1}
    assignment = mongo_registry.get_assignment_state("MT-600")
    assert assignment == AssignmentState(
        issue_id="issue-600",
        issue_identifier="MT-600",
        assigned_worker_cli="cli-1",
        assigned_by="runtime",
        status="running",
        acceptance_summary=None,
        updated_at=assignment["updated_at"],
    ).to_dict()
    assert mongo_registry.get_issue_state("MT-600")["workspace"]["workspace_key"] == "mt-600"


def test_export_work_item_snapshots_writes_markdown_summary(tmp_path: Path) -> None:
    database = _FakeMongoDatabase()
    store = MongoCollaborationStore(database)
    work_item = WorkItemRecord(
        work_item_id="MT-601",
        task_key="snapshot",
        title="Snapshot export",
        objective="Write markdown snapshots from Mongo control plane",
        branch="feat/snapshot",
        owner_cli="gemini",
        status="ready_for_review",
        allowed_paths=["scripts/runtime"],
        forbidden_paths=[],
        acceptance_checks=["pytest tests/unit/runtime -q"],
        openspec={"change_id": "mongodb-multicli"},
        created_at=_ts("2026-03-14T03:00:00Z"),
        updated_at=_ts("2026-03-14T03:05:00Z"),
    )
    update = WorkUpdateRecord(
        work_item_id="MT-601",
        update_id="upd-1",
        actor_cli="gemini",
        status="ready_for_review",
        summary="Implemented snapshot export",
        details={},
        created_at=_ts("2026-03-14T03:06:00Z"),
    )
    store.upsert_work_item(work_item)
    store.append_work_update(update)

    written_paths = export_work_item_snapshots(database=database, output_dir=tmp_path)

    snapshot_path = tmp_path / "MT-601.md"
    assert written_paths == [snapshot_path]
    content = snapshot_path.read_text(encoding="utf-8")
    assert "# MT-601" in content
    assert "Snapshot export" in content
    assert "Implemented snapshot export" in content


def test_migrate_markdown_contract_imports_minimum_fields_into_work_item_and_update(tmp_path: Path) -> None:
    task_path = tmp_path / "TASK.md"
    report_path = tmp_path / "TASK-REPORT.md"
    task_path.write_text(
        "\n".join(
            [
                "# TASK",
                "- Issue Identifier: `MT-800`",
                "- Issue Title: `Mongo cutover task`",
                "- Assigned Worker CLI: `gemini`",
                "- Acceptance Summary: `finish mongo cutover`",
            ]
        ),
        encoding="utf-8",
    )
    report_path.write_text(
        "\n".join(
            [
                "# TASK-REPORT",
                "- Latest Progress: implemented runtime mongo tracker",
            ]
        ),
        encoding="utf-8",
    )
    database = _FakeMongoDatabase()

    migrated = migrate_markdown_contract(task_path=task_path, report_path=report_path, mongo_database=database)
    store = MongoCollaborationStore(database)
    work_item = store.get_work_item("MT-800")
    updates = store.list_work_updates("MT-800")

    assert migrated == {"work_items": 1, "work_updates": 1}
    assert work_item is not None
    assert work_item.title == "Mongo cutover task"
    assert work_item.owner_cli == "gemini"
    assert work_item.acceptance_checks == ["finish mongo cutover"]
    assert updates[0].summary == "implemented runtime mongo tracker"


def test_migrate_cli_can_optionally_import_markdown_contract(monkeypatch, tmp_path: Path, capsys) -> None:
    task_path = tmp_path / "TASK.md"
    report_path = tmp_path / "TASK-REPORT.md"
    task_path.write_text("- Issue Identifier: `MT-801`", encoding="utf-8")
    report_path.write_text("- Latest Progress: imported", encoding="utf-8")
    fake_database = _FakeMongoDatabase()

    monkeypatch.setattr("scripts.runtime.migrate_collab_to_mongo.MongoClient", lambda _uri: _FakeMongoClient(fake_database))

    exit_code = migrate_collab_to_mongo.main(
        [
            "--sqlite-path",
            str(tmp_path / "tracker.db"),
            "--mongo-uri",
            "mongodb://localhost:27017",
            "--mongo-db",
            "smoke",
            "--task-path",
            str(task_path),
            "--report-path",
            str(report_path),
        ]
    )

    assert exit_code == 0
    payload = capsys.readouterr().out
    assert "work_items" in payload


class _FakeMongoClient:
    def __init__(self, database: _FakeMongoDatabase) -> None:
        self._database = database

    def __getitem__(self, _name: str) -> _FakeMongoDatabase:
        return self._database


class _IssueRef:
    def __init__(self, identifier: str, *, issue_id: str | None = None, branch_name: str | None = None) -> None:
        self.identifier = identifier
        self.id = issue_id
        self.branch_name = branch_name


class _WorkspaceRef:
    def __init__(self, workspace_key: str, path: Path) -> None:
        self.workspace_key = workspace_key
        self.path = path


def _ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


class _FakeMongoDatabase:
    def __init__(self) -> None:
        self._collections = {
            "work_items": _FakeCollection(),
            "work_updates": _FakeCollection(),
            "work_plan_items": _FakeCollection(),
            "work_requests": _FakeCollection(),
            "work_events": _FakeCollection(),
            "worker_status_views": _FakeCollection(),
            "issue_assignments": _FakeCollection(),
            "worktree_registry": _FakeCollection(),
            "worker_heartbeats": _FakeCollection(),
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

    def insert_one(self, document: dict) -> None:
        self.docs.append(document.copy())

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
