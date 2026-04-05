from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from pymongo.errors import OperationFailure

from src.services.maestro.collab.backends.mongo.store import MongoCollaborationStore
from src.services.maestro.collab.models import AssignmentState
from src.services.maestro.collab.registry import SQLiteCollaborationRegistry
from src.services.maestro.collab.runtime_registry import MongoCollaborationRegistry
from src.services.maestro.collab.store.models import WorkItemRecord, WorkUpdateRecord

from scripts.runtime.export_collab_snapshots import (
    export_work_item_snapshots,
    render_task_markdown,
    render_task_report_markdown,
)
from scripts.runtime import export_collab_snapshots
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


def test_migrate_markdown_contract_imports_legacy_work_blocks_into_structured_updates(tmp_path: Path) -> None:
    task_path = tmp_path / "TASK.md"
    report_path = tmp_path / "TASK-REPORT.md"
    task_path.write_text(
        "\n".join(
            [
                "# TASK",
                "- Issue Identifier: `MT-802`",
                "- Issue Title: `Legacy import`",
                "- Assigned Worker CLI: `main`",
            ]
        ),
        encoding="utf-8",
    )
    report_path.write_text(
        "\n".join(
            [
                "# TASK REPORT",
                "",
                "## [WORK] 2026-04-03 Legacy Recovery（dev-mainline）",
                "- Scope:",
                "  - Continue real track",
                "  - Recover backend runtime",
                "- Root Cause:",
                "  - Redis readiness was not green",
                "- Completed:",
                "  - Fixed PM2 env drift",
                "- Verification Evidence:",
                "  - `curl http://localhost:8020/health/ready`",
                "- Current Status:",
                "  - Phase 1 real track passed",
                "- Next:",
                "  - Enter phase 2",
                "",
                "## [WORK] 2026-04-03 Readiness Closure",
                "- Scope:",
                "  - Remove last readiness stub",
                "- Completed:",
                "  - Switched backend Redis host to localhost",
                "- Current Status:",
                "  - Full readiness is green",
                "",
            ]
        ),
        encoding="utf-8",
    )
    database = _FakeMongoDatabase()

    migrated = migrate_markdown_contract(task_path=task_path, report_path=report_path, mongo_database=database)
    migrated_again = migrate_markdown_contract(task_path=task_path, report_path=report_path, mongo_database=database)
    store = MongoCollaborationStore(database)
    updates = store.list_work_updates("MT-802")

    assert migrated == {"work_items": 1, "work_updates": 2}
    assert migrated_again == {"work_items": 1, "work_updates": 2}
    assert [update.summary for update in updates] == ["Legacy Recovery", "Readiness Closure"]
    assert updates[0].actor_cli == "dev-mainline"
    assert updates[1].actor_cli == "main"
    assert updates[0].details == {
        "scope": ["Continue real track", "Recover backend runtime"],
        "root_cause": ["Redis readiness was not green"],
        "completed": ["Fixed PM2 env drift"],
        "verification_evidence": ["`curl http://localhost:8020/health/ready`"],
        "current_status": ["Phase 1 real track passed"],
        "next": ["Enter phase 2"],
    }
    assert updates[1].details == {
        "scope": ["Remove last readiness stub"],
        "completed": ["Switched backend Redis host to localhost"],
        "current_status": ["Full readiness is green"],
    }


def test_migrate_markdown_contract_supports_heading_style_legacy_sections(tmp_path: Path) -> None:
    task_path = tmp_path / "TASK.md"
    report_path = tmp_path / "TASK-REPORT.md"
    task_path.write_text(
        "\n".join(
            [
                "# TASK",
                "- Issue Identifier: `MT-803`",
                "- Assigned Worker CLI: `main`",
            ]
        ),
        encoding="utf-8",
    )
    report_path.write_text(
        "\n".join(
            [
                "# TASK REPORT",
                "",
                "## [WORK] 2026-04-03 Runtime Drift Fixes（dev-runtime）",
                "### Implemented Fixes",
                "- Fixed backend proxy target",
                "### Verification Evidence",
                "- `curl http://localhost:3020/api/health`",
                "### Current Status",
                "- Services are healthy",
                "### Additional Observation",
                "- Static frontend process is still online",
                "",
            ]
        ),
        encoding="utf-8",
    )
    database = _FakeMongoDatabase()

    migrated = migrate_markdown_contract(task_path=task_path, report_path=report_path, mongo_database=database)
    store = MongoCollaborationStore(database)
    updates = store.list_work_updates("MT-803")

    assert migrated == {"work_items": 1, "work_updates": 1}
    assert len(updates) == 1
    assert updates[0].summary == "Runtime Drift Fixes"
    assert updates[0].actor_cli == "dev-runtime"
    assert updates[0].details == {
        "completed": ["Fixed backend proxy target"],
        "verification_evidence": ["`curl http://localhost:3020/api/health`"],
        "current_status": ["Services are healthy"],
        "notes": ["Static frontend process is still online"],
    }


def test_migrate_markdown_contract_splits_nested_status_subsections_into_details(tmp_path: Path) -> None:
    task_path = tmp_path / "TASK.md"
    report_path = tmp_path / "TASK-REPORT.md"
    task_path.write_text(
        "\n".join(
            [
                "# TASK",
                "- Issue Identifier: `MT-804`",
                "- Assigned Worker CLI: `main`",
            ]
        ),
        encoding="utf-8",
    )
    report_path.write_text(
        "\n".join(
            [
                "# TASK REPORT",
                "",
                "## [WORK] 2026-04-03 Phase Status Split",
                "- Current Status:",
                "  - Phase 2 all green",
                "  - 质量门禁状态：",
                "    - `mystocks-backend`: `online`",
                "  - Additional Observation:",
                "    - Static frontend process remained online",
                "  - Next:",
                "    - Consume phase 2 matrix artifacts",
                "",
            ]
        ),
        encoding="utf-8",
    )
    database = _FakeMongoDatabase()

    migrated = migrate_markdown_contract(task_path=task_path, report_path=report_path, mongo_database=database)
    store = MongoCollaborationStore(database)
    updates = store.list_work_updates("MT-804")

    assert migrated == {"work_items": 1, "work_updates": 1}
    assert len(updates) == 1
    assert updates[0].details == {
        "current_status": ["Phase 2 all green"],
        "quality_gate": ["`mystocks-backend`: `online`"],
        "notes": ["Static frontend process remained online"],
        "next": ["Consume phase 2 matrix artifacts"],
    }


def test_migrate_cli_can_optionally_import_markdown_contract(monkeypatch, tmp_path: Path, capsys) -> None:
    task_path = tmp_path / "TASK.md"
    report_path = tmp_path / "TASK-REPORT.md"
    task_path.write_text("- Issue Identifier: `MT-801`", encoding="utf-8")
    report_path.write_text("- Latest Progress: imported", encoding="utf-8")
    fake_database = _FakeMongoDatabase()

    monkeypatch.setattr("scripts.runtime.migrate_collab_to_mongo.build_runtime_mongo_client", lambda *_args, **_kwargs: _FakeMongoClient(fake_database))

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


def test_migrate_cli_can_inject_local_docker_credentials_for_default_local_uri(monkeypatch, tmp_path: Path, capsys) -> None:
    fake_database = _FakeMongoDatabase()
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        "scripts.runtime.migrate_collab_to_mongo.build_runtime_mongo_client",
        lambda mongo_uri, **_kwargs: captured.update({"mongo_uri": mongo_uri}) or _FakeMongoClient(fake_database),
    )

    exit_code = migrate_collab_to_mongo.main(
        [
            "--sqlite-path",
            str(tmp_path / "tracker.db"),
        ]
    )

    assert exit_code == 0
    assert captured["mongo_uri"] == "mongodb://localhost:27017"
    assert "assignments" in capsys.readouterr().out


def test_export_collab_snapshots_cli_can_inject_local_docker_credentials_for_default_local_uri(
    monkeypatch, tmp_path: Path, capsys
) -> None:
    fake_database = _FakeMongoDatabase()
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        "scripts.runtime.export_collab_snapshots.build_runtime_mongo_client",
        lambda mongo_uri, **_kwargs: captured.update({"mongo_uri": mongo_uri}) or _FakeMongoClient(fake_database),
    )

    exit_code = export_collab_snapshots.main(
        [
            "--output-dir",
            str(tmp_path),
        ]
    )

    assert exit_code == 0
    assert captured["mongo_uri"] == "mongodb://localhost:27017"
    assert capsys.readouterr().out == ""


def test_export_collab_snapshots_parser_prefers_env_mongo_uri(monkeypatch) -> None:
    monkeypatch.setenv("MAESTRO_COLLAB_MONGO_URI", "mongodb://coord-user:coord-pass@mongo-host:27017/admin?authSource=admin")

    args = export_collab_snapshots.build_parser().parse_args([])

    assert args.mongo_uri == "mongodb://coord-user:coord-pass@mongo-host:27017/admin?authSource=admin"


def test_migrate_cli_parser_prefers_env_mongo_uri(monkeypatch) -> None:
    monkeypatch.setenv("MAESTRO_COLLAB_MONGO_URI", "mongodb://coord-user:coord-pass@mongo-host:27017/admin?authSource=admin")
    monkeypatch.setenv("MAESTRO_COLLAB_MONGO_DB", "coord_runtime")

    args = migrate_collab_to_mongo.build_parser().parse_args([])

    assert args.mongo_uri == "mongodb://coord-user:coord-pass@mongo-host:27017/admin?authSource=admin"
    assert args.mongo_db == "coord_runtime"


def test_migrate_cli_emits_structured_json_error_when_mongo_auth_fails(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        "scripts.runtime.migrate_collab_to_mongo.build_runtime_mongo_client",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            OperationFailure(
                "Authentication failed.",
                18,
                {"ok": 0.0, "errmsg": "Authentication failed.", "code": 18, "codeName": "AuthenticationFailed"},
            )
        ),
    )

    exit_code = migrate_collab_to_mongo.main([])

    assert exit_code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["error_code"] == "RuntimeError"
    assert "Mongo migration requires writable credentials" in payload["message"]


def test_export_collab_snapshots_cli_emits_structured_json_error_when_mongo_auth_fails(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        "scripts.runtime.export_collab_snapshots.build_runtime_mongo_client",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            OperationFailure(
                "createIndexes requires authentication",
                13,
                {"ok": 0.0, "errmsg": "createIndexes requires authentication", "code": 13, "codeName": "Unauthorized"},
            )
        ),
    )

    exit_code = export_collab_snapshots.main([])

    assert exit_code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["error_code"] == "RuntimeError"
    assert "Mongo export requires writable credentials" in payload["message"]


def test_render_task_artifacts_from_mongo_records() -> None:
    work_item = {
        "work_item_id": "MT-900",
        "title": "Mongo export",
        "objective": "Export task markdown from Mongo state",
        "branch": "feat/mongo-export",
        "owner_cli": "mystocks_spec1",
        "status": "ready_for_review",
        "allowed_paths": ["scripts/runtime", "src/services/maestro/collab"],
        "forbidden_paths": ["docs/archive"],
        "acceptance_checks": ["pytest tests/unit/runtime -q"],
        "openspec": {"change_id": "update-mongo-task-artifact-export"},
        "metadata": {
            "final_owner": "mystocks_spec1",
            "scope_paths": ["scripts/runtime/export_collab_snapshots.py"],
            "next_steps": ["Export the latest worker snapshot"],
        },
    }
    status_view = {
        "status": "ready_for_review",
        "latest_update": "Export verified",
        "has_pending_request": True,
    }
    updates = [
        {
            "created_at": "2026-03-17T00:00:00+00:00",
            "status": "in_progress",
            "actor_cli": "mystocks_spec1",
            "summary": "Export verified",
            "details": {
                "scope": ["Compare legacy and exported task artifacts"],
                "completed": ["Rendered richer report sections"],
                "quality_gate": {"exporter_tests": "pass"},
            },
        }
    ]
    requests = [
        {
            "created_at": "2026-03-17T00:01:00+00:00",
            "status": "pending",
            "request_type": "review",
            "actor_cli": "mystocks_spec1",
            "summary": "Need final approval",
        }
    ]

    task_markdown = render_task_markdown(work_item=work_item, status_view=status_view)
    report_markdown = render_task_report_markdown(
        work_item=work_item,
        updates=updates,
        requests=requests,
        status_view=status_view,
        transcripts=[
            {
                "session_id": "sess-900",
                "actor_cli": "mystocks_spec1",
                "transcript_kind": "AUTO",
                "started_at": "2026-04-03T00:00:00+00:00",
                "hot_body_available": True,
                "archive_locator": "archive/MT-900/sess-900/transcript.txt",
            }
        ],
    )

    assert "Issue Identifier: `MT-900`" in task_markdown
    assert "Assigned Worker CLI: `mystocks_spec1`" in task_markdown
    assert "Exported from Mongo control plane" in task_markdown
    assert "## Owner Decision" in task_markdown
    assert "## Next Steps" in task_markdown
    assert "Latest Progress: Export verified" in report_markdown
    assert "Need final approval" in report_markdown
    assert "## Detailed Updates" in report_markdown
    assert "#### Quality Gate" in report_markdown
    assert "## Transcripts" in report_markdown
    assert "sess-900" in report_markdown
    assert "archive/MT-900/sess-900/transcript.txt" in report_markdown


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
            "work_requests": _FakeCollection(),
            "work_events": _FakeCollection(),
            "worker_status_views": _FakeCollection(),
            "transcript_sessions": _FakeCollection(),
            "transcript_events": _FakeCollection(),
            "transcript_hot_bodies": _FakeCollection(),
            "transcript_legacy_indexes": _FakeCollection(),
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
