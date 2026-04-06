from __future__ import annotations

import argparse
import json

import pytest
from pymongo.errors import OperationFailure

from scripts.runtime import maestro_collab


def test_build_parser_exposes_coordination_command_groups() -> None:
    parser = maestro_collab.build_parser()

    choices = parser._subparsers._group_actions[0].choices  # type: ignore[attr-defined]
    assert "work" in choices
    assert "update" in choices
    assert "request" in choices
    assert "transcript" in choices
    assert "assign" in choices
    assert "state" in choices
    assert "suggest" in choices


def test_main_can_create_show_and_transition_work_item_as_json(monkeypatch, capsys) -> None:
    service = _FakeCoordinationService()
    monkeypatch.setattr(maestro_collab, "_build_coordination_service", lambda _args: service)

    exit_code = maestro_collab.main(
        [
            "work",
            "create",
            "--work-item-id",
            "MT-300",
            "--task-key",
            "mongo-cli",
            "--title",
            "Add coordctl",
            "--objective",
            "Expose Mongo coordination CLI",
            "--branch",
            "feat/mongo-cli",
            "--owner-cli",
            "gemini",
            "--allowed-path",
            "scripts/runtime",
            "--acceptance-check",
            "pytest tests/unit/runtime -q",
            "--output",
            "json",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["work_item_id"] == "MT-300"
    assert payload["status"] == "created"

    exit_code = maestro_collab.main(["work", "show", "MT-300", "--output", "json"])
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["title"] == "Add coordctl"

    exit_code = maestro_collab.main(["work", "transition", "MT-300", "--to", "merged", "--output", "json"])
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "merged"


def test_worker_can_mark_work_and_add_update(monkeypatch, capsys) -> None:
    service = _FakeCoordinationService()
    service.create_work_item(
        {
            "work_item_id": "MT-301",
            "task_key": "worker-flow",
            "title": "Worker flow",
            "objective": "Track updates",
            "branch": "feat/worker-flow",
            "owner_cli": "gemini",
            "status": "dispatched",
            "allowed_paths": ["src/services/maestro/collab"],
            "forbidden_paths": [],
            "acceptance_checks": [],
            "openspec": None,
        }
    )
    monkeypatch.setattr(maestro_collab, "_build_coordination_service", lambda _args: service)

    exit_code = maestro_collab.main(
        ["work", "mark", "MT-301", "--status", "in_progress", "--actor-cli", "gemini", "--output", "json"]
    )
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "in_progress"

    exit_code = maestro_collab.main(
        [
            "update",
            "add",
            "MT-301",
            "--actor-cli",
            "gemini",
            "--summary",
            "Collected failures",
            "--status",
            "in_progress",
            "--output",
            "json",
        ]
    )
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["summary"] == "Collected failures"


def test_request_review_and_text_output(monkeypatch, capsys) -> None:
    service = _FakeCoordinationService()
    service.create_work_item(
        {
            "work_item_id": "MT-302",
            "task_key": "request-flow",
            "title": "Request flow",
            "objective": "Track request approvals",
            "branch": "feat/request-flow",
            "owner_cli": "gemini",
            "status": "in_progress",
            "allowed_paths": ["src/services/maestro/collab"],
            "forbidden_paths": [],
            "acceptance_checks": [],
            "openspec": None,
        }
    )
    monkeypatch.setattr(maestro_collab, "_build_coordination_service", lambda _args: service)

    exit_code = maestro_collab.main(
        [
            "request",
            "create",
            "MT-302",
            "--actor-cli",
            "gemini",
            "--request-id",
            "req-1",
            "--request-type",
            "definition_change",
            "--summary",
            "Need broader backend scope",
            "--output",
            "json",
        ]
    )
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["request_id"] == "req-1"
    assert payload["status"] == "pending"

    exit_code = maestro_collab.main(
        ["request", "review", "MT-302", "req-1", "--reviewed-by", "main", "--status", "approved", "--output", "text"]
    )
    assert exit_code == 0
    output = capsys.readouterr().out.strip()
    assert "request_id=req-1" in output
    assert "status=approved" in output


def test_work_item_can_export_task_and_task_report_snapshots(monkeypatch, tmp_path, capsys) -> None:
    service = _FakeCoordinationService()
    service.create_work_item(
        {
            "work_item_id": "MT-450",
            "task_key": "export-flow",
            "title": "Export flow",
            "objective": "Render markdown task artifacts from Mongo state",
            "branch": "feat/export-flow",
            "owner_cli": "gemini",
            "status": "in_progress",
            "allowed_paths": ["scripts/runtime"],
            "forbidden_paths": ["docs/archive"],
            "acceptance_checks": ["pytest tests/unit/runtime -q"],
            "openspec": {"change_id": "update-mongo-task-artifact-export"},
            "metadata": {
                "final_owner": "gemini",
                "worker_cli": "gemini",
                "scope_paths": ["scripts/runtime/export_collab_snapshots.py"],
                "related_plans": ["docs/plans/export-alignment.md"],
            },
        }
    )
    service.create_work_update(
        "MT-450",
        "gemini",
        "Export command implemented",
        "in_progress",
        details={
            "scope": ["Align exported markdown with legacy task sections"],
            "completed": ["Added richer task/report rendering"],
            "verification_evidence": ["pytest tests/unit/runtime -q"],
        },
    )
    service.create_work_request("MT-450", "gemini", "req-9", "review", "Need review")
    service.start_transcript_session("sess-450", "MT-450", "gemini", "AUTO")
    service.append_transcript_block("sess-450", "gemini", "full transcript body should stay out of TASK-REPORT")
    monkeypatch.setattr(maestro_collab, "_build_coordination_service", lambda _args: service)

    task_path = tmp_path / "TASK.md"
    report_path = tmp_path / "TASK-REPORT.md"

    exit_code = maestro_collab.main(
        ["work", "export-task", "MT-450", "--output-path", str(task_path), "--output", "json"]
    )
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["artifact"] == "TASK.md"
    assert payload["output_path"] == str(task_path)
    task_content = task_path.read_text(encoding="utf-8")
    assert "Issue Identifier: `MT-450`" in task_content
    assert "## Owner Decision" in task_content
    assert "## Scope Paths" in task_content

    exit_code = maestro_collab.main(
        ["work", "export-task-report", "MT-450", "--output-path", str(report_path), "--output", "json"]
    )
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["artifact"] == "TASK-REPORT.md"
    content = report_path.read_text(encoding="utf-8")
    assert "Export command implemented" in content
    assert "Need review" in content
    assert "## Detailed Updates" in content
    assert "#### Verification Evidence" in content
    assert "## Transcripts" in content
    assert "sess-450" in content
    assert "full transcript body should stay out of TASK-REPORT" not in content


def test_work_item_export_task_report_prefers_live_graphiti_projection(monkeypatch, tmp_path, capsys) -> None:
    service = _FakeCoordinationService()
    service.create_work_item(
        {
            "work_item_id": "MT-452",
            "task_key": "graphiti-live-export",
            "title": "Graphiti live export",
            "objective": "Render live Graphiti ingest status during export",
            "branch": "main",
            "owner_cli": "gemini",
            "status": "verified",
            "allowed_paths": ["scripts/runtime"],
            "forbidden_paths": [],
            "acceptance_checks": [],
            "openspec": None,
        }
    )
    graphiti_events = [
        {
            "event_type": "automation.graphiti_preflight_checked",
            "created_at": "2026-04-03T09:00:00+00:00",
            "payload": {
                "server_status": "ok",
                "ingest_status": "warming",
                "search_summary": "nodes hit=2, facts hit=3",
                "episode_uuid": "ep-452",
                "group_id": "mystocks_spec_workers",
            },
        }
    ]
    monkeypatch.setattr(maestro_collab, "_build_coordination_service", lambda _args: service)
    monkeypatch.setattr(service, "list_work_events", lambda work_item_id: graphiti_events if work_item_id == "MT-452" else [])
    monkeypatch.setattr(
        maestro_collab,
        "_build_live_graphiti_projection",
        lambda _events: {
            "server_status": "ok",
            "ingest_status": "completed",
            "search_summary": "nodes hit=2, facts hit=3",
        },
    )

    report_path = tmp_path / "TASK-REPORT.md"
    exit_code = maestro_collab.main(
        ["work", "export-task-report", "MT-452", "--output-path", str(report_path), "--output", "json"]
    )

    assert exit_code == 0
    content = report_path.read_text(encoding="utf-8")
    assert "ingest_status: `completed`" in content
    assert "ingest_status: `warming`" not in content


def test_work_commands_accept_structured_metadata_and_update_details(monkeypatch, capsys) -> None:
    service = _FakeCoordinationService()
    monkeypatch.setattr(maestro_collab, "_build_coordination_service", lambda _args: service)

    exit_code = maestro_collab.main(
        [
            "work",
            "create",
            "--work-item-id",
            "MT-451",
            "--task-key",
            "aligned-export",
            "--title",
            "Aligned export",
            "--objective",
            "Carry rich task metadata in Mongo",
            "--branch",
            "feat/aligned-export",
            "--owner-cli",
            "main",
            "--metadata-json",
            json.dumps(
                {
                    "final_owner": "main",
                    "scope_paths": ["TASK.md", "TASK-REPORT.md"],
                    "next_steps": ["Export current snapshot"],
                }
            ),
            "--output",
            "json",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["metadata"]["final_owner"] == "main"

    exit_code = maestro_collab.main(
        [
            "update",
            "add",
            "MT-451",
            "--actor-cli",
            "main",
            "--summary",
            "Captured aligned report details",
            "--status",
            "in_progress",
            "--details-json",
            json.dumps(
                {
                    "scope": ["Compare legacy and exported root artifacts"],
                    "completed": ["Defined metadata-driven alignment path"],
                    "current_status": ["Ready to re-export snapshots"],
                }
            ),
            "--output",
            "json",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["details"]["scope"] == ["Compare legacy and exported root artifacts"]


def test_transcript_commands_manage_session_lifecycle_as_json(monkeypatch, capsys) -> None:
    service = _FakeCoordinationService()
    service.create_work_item(
        {
            "work_item_id": "MT-500",
            "task_key": "transcript-cli",
            "title": "Transcript CLI",
            "objective": "Manage AUTO and MANUAL transcript sessions",
            "branch": "feat/transcript-cli",
            "owner_cli": "gemini",
            "status": "in_progress",
            "allowed_paths": ["scripts/runtime"],
            "forbidden_paths": [],
            "acceptance_checks": [],
            "openspec": None,
        }
    )
    monkeypatch.setattr(maestro_collab, "_build_coordination_service", lambda _args: service)

    exit_code = maestro_collab.main(
        [
            "transcript",
            "start",
            "sess-500",
            "--work-item-id",
            "MT-500",
            "--actor-cli",
            "gemini",
            "--transcript-kind",
            "AUTO",
            "--output",
            "json",
        ]
    )
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["session_id"] == "sess-500"
    assert payload["work_item_id"] == "MT-500"
    assert payload["transcript_kind"] == "AUTO"

    exit_code = maestro_collab.main(
        [
            "transcript",
            "append",
            "sess-500",
            "--actor-cli",
            "gemini",
            "--content",
            "operator summary",
            "--output",
            "json",
        ]
    )
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["event_type"] == "transcript.block_appended"
    assert payload["sequence_no"] == 2

    exit_code = maestro_collab.main(
        [
            "transcript",
            "close",
            "sess-500",
            "--actor-cli",
            "gemini",
            "--output",
            "json",
        ]
    )
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["session_id"] == "sess-500"
    assert payload["closed_at"] == "2026-04-03T00:02:00+00:00"


def test_transcript_commands_can_show_export_and_index_legacy(monkeypatch, capsys) -> None:
    service = _FakeCoordinationService()
    service.create_work_item(
        {
            "work_item_id": "MT-501",
            "task_key": "transcript-export",
            "title": "Transcript export",
            "objective": "Show summary and export full session payload",
            "branch": "feat/transcript-export",
            "owner_cli": "gemini",
            "status": "in_progress",
            "allowed_paths": ["scripts/runtime"],
            "forbidden_paths": [],
            "acceptance_checks": [],
            "openspec": None,
        }
    )
    service.start_transcript_session("sess-501", "MT-501", "gemini", "MANUAL")
    service.append_transcript_block("sess-501", "gemini", "manual note")
    monkeypatch.setattr(maestro_collab, "_build_coordination_service", lambda _args: service)

    exit_code = maestro_collab.main(
        [
            "transcript",
            "show-session",
            "sess-501",
            "--actor-cli",
            "gemini",
            "--output",
            "json",
        ]
    )
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["session"]["session_id"] == "sess-501"
    assert payload["event_count"] == 2
    assert payload["hot_body_available"] is True

    exit_code = maestro_collab.main(
        [
            "transcript",
            "export-session",
            "sess-501",
            "--actor-cli",
            "gemini",
            "--output",
            "json",
        ]
    )
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["session"]["session_id"] == "sess-501"
    assert payload["hot_body"]["content"] == "manual note"
    assert payload["events"][-1]["event_type"] == "transcript.block_appended"

    service.expire_transcript_session("sess-501", archive_locator="archive/MT-501/sess-501/transcript.txt")
    exit_code = maestro_collab.main(
        [
            "transcript",
            "export-session",
            "sess-501",
            "--actor-cli",
            "gemini",
            "--output",
            "json",
        ]
    )
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["hot_body"] is None
    assert payload["archive_ref"] == "archive/MT-501/sess-501/transcript.txt"
    assert payload["events"][-1]["event_type"] == "transcript.hot_body_expired"

    exit_code = maestro_collab.main(
        [
            "transcript",
            "index-legacy",
            "--work-item-id",
            "MT-501",
            "--actor-cli",
            "main",
            "--legacy-block-kind",
            "AUTO",
            "--legacy-session-label",
            "AUTO 2026-03-01",
            "--source-artifact",
            "TASK-REPORT.md",
            "--captured-at",
            "2026-03-01T08:00:00Z",
            "--source-anchor",
            "L120",
            "--archive-locator",
            "archive/MT-501/legacy-1.md",
            "--checksum",
            "sha256:legacy-1",
            "--migration-batch-id",
            "batch-1",
            "--output",
            "json",
        ]
    )
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["work_item_id"] == "MT-501"
    assert payload["legacy_block_kind"] == "AUTO"
    assert payload["archive_locator"] == "archive/MT-501/legacy-1.md"


def test_hot_body_stays_visible_when_archive_has_not_been_sealed(monkeypatch) -> None:
    monkeypatch.setattr(maestro_collab, "_utcnow", lambda: maestro_collab._parse_datetime("2026-07-03T00:00:00Z"))

    assert (
        maestro_collab._MongoCoordinationFacade._is_hot_body_available(
            hot_body={
                "available_until": "2026-07-02T00:01:00+00:00",
                "purge_after": None,
            },
            events=[],
        )
        is True
    )


def test_hot_body_hides_after_purge_deadline_once_archive_exists(monkeypatch) -> None:
    monkeypatch.setattr(maestro_collab, "_utcnow", lambda: maestro_collab._parse_datetime("2026-07-03T00:00:00Z"))

    assert (
        maestro_collab._MongoCoordinationFacade._is_hot_body_available(
            hot_body={
                "available_until": "2026-07-02T00:01:00+00:00",
                "purge_after": "2026-07-02T00:01:00+00:00",
            },
            events=[
                {
                    "event_type": "transcript.body_archived",
                    "payload": {"archive_locator": "archive/MT-501/sess-501/transcript.txt"},
                }
            ],
        )
        is False
    )


def test_transcript_commands_enforce_required_arguments() -> None:
    parser = maestro_collab.build_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(["transcript", "start", "sess-500", "--actor-cli", "gemini"])

    with pytest.raises(SystemExit):
        parser.parse_args(["transcript", "append", "sess-500", "--actor-cli", "gemini"])

    with pytest.raises(SystemExit):
        parser.parse_args(["transcript", "index-legacy", "--actor-cli", "main"])


def test_coordctl_wrapper_delegates_to_maestro_collab(monkeypatch) -> None:
    from scripts.runtime import coordctl

    captured: dict[str, list[str]] = {}

    def _fake_main(argv: list[str] | None = None) -> int:
        captured["argv"] = argv or []
        return 7

    monkeypatch.setattr(coordctl, "_delegate", _fake_main)

    assert coordctl.main(["work", "list"]) == 7
    assert captured["argv"] == ["work", "list"]


def test_build_coordination_service_uses_env_driven_mongo_client_when_uri_omitted(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class _FakeClient:
        def __getitem__(self, name: str):
            captured["mongo_db"] = name
            return object()

    monkeypatch.setattr(
        maestro_collab,
        "build_project_runtime_mongo_client",
        lambda project_root, mongo_uri, server_selection_timeout_ms=3000: captured.update(
            {"project_root": str(project_root), "mongo_uri": mongo_uri, "server_selection_timeout_ms": server_selection_timeout_ms}
        )
        or _FakeClient(),
    )
    monkeypatch.setattr(maestro_collab, "MongoCollaborationStore", lambda database: captured.update({"database": database}) or object())
    monkeypatch.setattr(maestro_collab, "CoordinationService", lambda store: captured.update({"store": store}) or object())

    facade = maestro_collab._build_coordination_service(argparse.Namespace(mongo_uri=None, mongo_db="mystocks_coord"))

    assert isinstance(facade, maestro_collab._MongoCoordinationFacade)
    assert captured["mongo_db"] == "mystocks_coord"
    assert captured["mongo_uri"] is None
    assert captured["server_selection_timeout_ms"] == 3000
    assert str(maestro_collab.PROJECT_ROOT) == captured["project_root"]


def test_build_coordination_service_can_fallback_to_local_docker_container_credentials(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class _FakeClient:
        def __getitem__(self, name: str):
            captured["mongo_db"] = name
            return object()

    monkeypatch.setattr(
        maestro_collab,
        "build_project_runtime_mongo_client",
        lambda project_root, mongo_uri, server_selection_timeout_ms=3000: captured.update(
            {"project_root": str(project_root), "mongo_uri": mongo_uri, "server_selection_timeout_ms": server_selection_timeout_ms}
        )
        or _FakeClient(),
    )
    monkeypatch.setattr(maestro_collab, "MongoCollaborationStore", lambda database: captured.update({"database": database}) or object())
    monkeypatch.setattr(maestro_collab, "CoordinationService", lambda store: captured.update({"store": store}) or object())

    facade = maestro_collab._build_coordination_service(argparse.Namespace(mongo_uri=None, mongo_db="mystocks_coord"))

    assert isinstance(facade, maestro_collab._MongoCoordinationFacade)
    assert captured["mongo_db"] == "mystocks_coord"
    assert str(maestro_collab.PROJECT_ROOT) == captured["project_root"]
    assert captured["mongo_uri"] is None
    assert captured["server_selection_timeout_ms"] == 3000


def test_build_coordination_service_can_inject_local_docker_credentials_for_default_local_uri(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class _FakeClient:
        def __getitem__(self, name: str):
            captured["mongo_db"] = name
            return object()

    monkeypatch.setattr(
        maestro_collab,
        "build_project_runtime_mongo_client",
        lambda project_root, mongo_uri, server_selection_timeout_ms=3000: captured.update(
            {"project_root": str(project_root), "mongo_uri": mongo_uri, "server_selection_timeout_ms": server_selection_timeout_ms}
        )
        or _FakeClient(),
    )
    monkeypatch.setattr(maestro_collab, "MongoCollaborationStore", lambda database: captured.update({"database": database}) or object())
    monkeypatch.setattr(maestro_collab, "CoordinationService", lambda store: captured.update({"store": store}) or object())

    facade = maestro_collab._build_coordination_service(
        argparse.Namespace(mongo_uri="mongodb://localhost:27017", mongo_db="mystocks_coord")
    )

    assert isinstance(facade, maestro_collab._MongoCoordinationFacade)
    assert captured["mongo_db"] == "mystocks_coord"
    assert str(maestro_collab.PROJECT_ROOT) == captured["project_root"]
    assert captured["mongo_uri"] == "mongodb://localhost:27017"


def test_build_coordination_service_prefers_explicit_mongo_uri(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class _FakeClient:
        def __getitem__(self, name: str):
            captured["mongo_db"] = name
            return object()

    monkeypatch.setattr(
        maestro_collab,
        "build_project_runtime_mongo_client",
        lambda project_root, mongo_uri, server_selection_timeout_ms=3000: captured.update(
            {"project_root": str(project_root), "mongo_uri": mongo_uri, "server_selection_timeout_ms": server_selection_timeout_ms}
        )
        or _FakeClient(),
    )
    monkeypatch.setattr(maestro_collab, "MongoCollaborationStore", lambda database: captured.update({"database": database}) or object())
    monkeypatch.setattr(maestro_collab, "CoordinationService", lambda store: captured.update({"store": store}) or object())

    facade = maestro_collab._build_coordination_service(
        argparse.Namespace(mongo_uri="mongodb://user:pass@mongo.example:27017/admin?authSource=admin", mongo_db="mystocks_coord")
    )

    assert isinstance(facade, maestro_collab._MongoCoordinationFacade)
    assert str(maestro_collab.PROJECT_ROOT) == captured["project_root"]
    assert captured["mongo_uri"] == "mongodb://user:pass@mongo.example:27017/admin?authSource=admin"
    assert captured["mongo_db"] == "mystocks_coord"


def test_build_coordination_service_uses_transcript_archive_defaults(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class _FakeClient:
        def __getitem__(self, name: str):
            captured["mongo_db"] = name
            return object()

    monkeypatch.setattr(
        maestro_collab,
        "build_project_runtime_mongo_client",
        lambda project_root, mongo_uri, server_selection_timeout_ms=3000: captured.update(
            {"project_root": str(project_root), "mongo_uri": mongo_uri, "server_selection_timeout_ms": server_selection_timeout_ms}
        )
        or _FakeClient(),
    )
    monkeypatch.setattr(maestro_collab, "MongoCollaborationStore", lambda database: captured.update({"database": database}) or object())
    monkeypatch.setattr(maestro_collab, "CoordinationService", lambda store: captured.update({"store": store}) or object())
    monkeypatch.setattr(
        maestro_collab,
        "FilesystemTranscriptArchiveBackend",
        lambda root: captured.update({"archive_root": str(root)}) or ("archive-backend", str(root)),
    )
    monkeypatch.setattr(
        maestro_collab,
        "TranscriptLedgerService",
        lambda store, archive_backend=None, hot_retention_days=90: captured.update(
            {
                "transcript_store": store,
                "archive_backend": archive_backend,
                "hot_retention_days": hot_retention_days,
            }
        )
        or object(),
    )

    facade = maestro_collab._build_coordination_service(argparse.Namespace(mongo_uri=None, mongo_db="mystocks_coord"))

    assert isinstance(facade, maestro_collab._MongoCoordinationFacade)
    assert captured["mongo_db"] == "mystocks_coord"
    assert captured["archive_root"] == str(maestro_collab.PROJECT_ROOT / ".maestro/transcript-archive")
    assert captured["hot_retention_days"] == 90
    assert captured["archive_backend"] == ("archive-backend", str(maestro_collab.PROJECT_ROOT / ".maestro/transcript-archive"))


def test_main_emits_structured_error_when_mongo_auth_fails(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        maestro_collab,
        "_build_coordination_service",
        lambda _args: (_ for _ in ()).throw(
            OperationFailure(
                "createIndexes requires authentication",
                13,
                {"ok": 0.0, "errmsg": "createIndexes requires authentication", "code": 13, "codeName": "Unauthorized"},
            )
        ),
    )

    exit_code = maestro_collab.main(["work", "list", "--output", "json"])

    assert exit_code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["error_code"] == "RuntimeError"
    assert "Mongo control plane requires writable credentials" in payload["message"]


def test_main_emits_structured_error_when_mongo_authentication_failed(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        maestro_collab,
        "_build_coordination_service",
        lambda _args: (_ for _ in ()).throw(
            OperationFailure(
                "Authentication failed.",
                18,
                {"ok": 0.0, "errmsg": "Authentication failed.", "code": 18, "codeName": "AuthenticationFailed"},
            )
        ),
    )

    exit_code = maestro_collab.main(["work", "list", "--output", "json"])

    assert exit_code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["error_code"] == "RuntimeError"
    assert "Mongo control plane requires writable credentials" in payload["message"]


class _FakeCoordinationService:
    def __init__(self) -> None:
        self.work_items: dict[str, dict] = {}
        self.requests: dict[tuple[str, str], dict] = {}
        self.status_views: dict[str, dict] = {}
        self.updates_by_work_item: dict[str, list[dict]] = {}
        self.transcript_sessions: dict[str, dict] = {}
        self.transcript_events: dict[str, list[dict]] = {}
        self.transcript_hot_bodies: dict[str, dict] = {}
        self.transcript_legacy_indexes: list[dict] = []
        self.transcript_archive_refs: dict[str, str] = {}
        self.update_seq = 0

    def create_work_item(self, payload: dict) -> dict:
        item = {
            **payload,
            "status": payload.get("status", "created"),
        }
        self.work_items[item["work_item_id"]] = item
        self.status_views[item["work_item_id"]] = {
            "work_item_id": item["work_item_id"],
            "branch": item["branch"],
            "owner_cli": item["owner_cli"],
            "status": item["status"],
            "latest_update": None,
            "blocker": None,
            "has_pending_request": False,
        }
        self.updates_by_work_item.setdefault(item["work_item_id"], [])
        return item

    def get_work_item(self, work_item_id: str) -> dict | None:
        return self.work_items.get(work_item_id)

    def list_work_items(self) -> list[dict]:
        return sorted(self.work_items.values(), key=lambda item: item["work_item_id"])

    def transition_work_item(self, work_item_id: str, status: str, actor_cli: str) -> dict:
        item = self.work_items[work_item_id]
        item["status"] = status
        item["last_actor_cli"] = actor_cli
        return item

    def create_work_update(
        self, work_item_id: str, actor_cli: str, summary: str, status: str, details: dict | None = None
    ) -> dict:
        self.update_seq += 1
        item = self.work_items[work_item_id]
        item["status"] = status
        item["latest_update"] = summary
        update = {
            "work_item_id": work_item_id,
            "update_id": f"upd-{self.update_seq}",
            "actor_cli": actor_cli,
            "summary": summary,
            "status": status,
            "details": details or {},
            "created_at": "2026-03-17T00:00:00+00:00",
        }
        self.updates_by_work_item.setdefault(work_item_id, []).append(update)
        self.status_views[work_item_id]["status"] = status
        self.status_views[work_item_id]["latest_update"] = summary
        return update

    def create_work_request(
        self, work_item_id: str, actor_cli: str, request_id: str, request_type: str, summary: str
    ) -> dict:
        payload = {
            "work_item_id": work_item_id,
            "request_id": request_id,
            "actor_cli": actor_cli,
            "request_type": request_type,
            "summary": summary,
            "status": "pending",
            "created_at": "2026-03-17T00:01:00+00:00",
        }
        self.requests[(work_item_id, request_id)] = payload
        self.status_views[work_item_id]["has_pending_request"] = True
        return payload

    def review_work_request(self, work_item_id: str, request_id: str, reviewed_by: str, status: str) -> dict:
        payload = self.requests[(work_item_id, request_id)]
        payload["reviewed_by"] = reviewed_by
        payload["status"] = status
        self.status_views[work_item_id]["has_pending_request"] = any(
            request["status"] == "pending" and request["work_item_id"] == work_item_id
            for request in self.requests.values()
        )
        return payload

    def list_work_updates(self, work_item_id: str) -> list[dict]:
        return self.updates_by_work_item.get(work_item_id, [])

    def list_work_requests(self, work_item_id: str) -> list[dict]:
        return [request for request in self.requests.values() if request["work_item_id"] == work_item_id]

    def list_work_events(self, work_item_id: str) -> list[dict]:
        return []

    def get_worker_status_view(self, work_item_id: str) -> dict | None:
        return self.status_views.get(work_item_id)

    def start_transcript_session(
        self,
        session_id: str,
        work_item_id: str,
        actor_cli: str,
        transcript_kind: str,
        *,
        archive_policy_version: str = "v1",
    ) -> dict:
        work_item = self.work_items[work_item_id]
        session = {
            "session_id": session_id,
            "work_item_id": work_item_id,
            "actor_cli": actor_cli,
            "branch": work_item["branch"],
            "transcript_kind": transcript_kind,
            "started_at": "2026-04-03T00:00:00+00:00",
            "closed_at": None,
            "archive_policy_version": archive_policy_version,
        }
        self.transcript_sessions[session_id] = session
        self.transcript_events[session_id] = [
            {
                "work_item_id": work_item_id,
                "session_id": session_id,
                "event_id": "tevt-1",
                "event_type": "transcript.session_started",
                "sequence_no": 1,
                "occurred_at": "2026-04-03T00:00:00+00:00",
                "payload": {
                    "actor_cli": actor_cli,
                    "transcript_kind": transcript_kind,
                },
            }
        ]
        return session

    def append_transcript_block(
        self,
        session_id: str,
        actor_cli: str,
        content: str,
        payload: dict | None = None,
    ) -> dict:
        session = self.transcript_sessions[session_id]
        events = self.transcript_events.setdefault(session_id, [])
        event = {
            "work_item_id": session["work_item_id"],
            "session_id": session_id,
            "event_id": f"tevt-{len(events) + 1}",
            "event_type": "transcript.block_appended",
            "sequence_no": len(events) + 1,
            "occurred_at": "2026-04-03T00:01:00+00:00",
            "payload": {"content": content, **(payload or {})},
        }
        events.append(event)
        existing = self.transcript_hot_bodies.get(session_id, {}).get("content")
        full_content = content if not existing else f"{existing}\n{content}"
        self.transcript_hot_bodies[session_id] = {
            "body_id": f"hot-{session_id}",
            "session_id": session_id,
            "event_id": event["event_id"],
            "content": full_content,
            "checksum": "sha256:fake-hot-body",
            "available_until": "2026-07-02T00:01:00+00:00",
        }
        return event

    def close_transcript_session(self, session_id: str, actor_cli: str, payload: dict | None = None) -> dict:
        session = self.transcript_sessions[session_id]
        session["actor_cli"] = actor_cli
        session["closed_at"] = "2026-04-03T00:02:00+00:00"
        events = self.transcript_events.setdefault(session_id, [])
        events.append(
            {
                "work_item_id": session["work_item_id"],
                "session_id": session_id,
                "event_id": f"tevt-{len(events) + 1}",
                "event_type": "transcript.session_closed",
                "sequence_no": len(events) + 1,
                "occurred_at": "2026-04-03T00:02:00+00:00",
                "payload": payload or {},
            }
        )
        return session

    def show_transcript_session(self, session_id: str, actor_cli: str) -> dict:
        session = self.transcript_sessions[session_id]
        return {
            "session": {**session, "actor_cli": actor_cli},
            "event_count": len(self.transcript_events.get(session_id, [])),
            "hot_body_available": session_id in self.transcript_hot_bodies,
        }

    def export_transcript_session(self, session_id: str, actor_cli: str) -> dict:
        session = self.transcript_sessions[session_id]
        archive_ref = self.transcript_archive_refs.get(session_id)
        return {
            "session": {**session, "actor_cli": actor_cli},
            "events": list(self.transcript_events.get(session_id, [])),
            "hot_body": None if archive_ref else self.transcript_hot_bodies.get(session_id),
            "archive_ref": archive_ref,
        }

    def expire_transcript_session(self, session_id: str, archive_locator: str) -> None:
        session = self.transcript_sessions[session_id]
        self.transcript_archive_refs[session_id] = archive_locator
        events = self.transcript_events.setdefault(session_id, [])
        events.append(
            {
                "work_item_id": session["work_item_id"],
                "session_id": session_id,
                "event_id": f"tevt-{len(events) + 1}",
                "event_type": "transcript.hot_body_expired",
                "sequence_no": len(events) + 1,
                "occurred_at": "2026-07-03T00:00:00+00:00",
                "payload": {"archive_locator": archive_locator},
            }
        )

    def index_legacy_transcript(
        self,
        *,
        work_item_id: str,
        actor_cli: str,
        legacy_block_kind: str,
        legacy_session_label: str,
        source_artifact: str,
        captured_at: str,
        source_anchor: str,
        archive_locator: str,
        checksum: str,
        migration_batch_id: str,
    ) -> dict:
        payload = {
            "legacy_index_id": f"legacy-{len(self.transcript_legacy_indexes) + 1}",
            "work_item_id": work_item_id,
            "actor_cli": actor_cli,
            "legacy_block_kind": legacy_block_kind,
            "legacy_session_label": legacy_session_label,
            "source_artifact": source_artifact,
            "captured_at": captured_at if isinstance(captured_at, str) else captured_at.isoformat(),
            "source_anchor": source_anchor,
            "archive_locator": archive_locator,
            "checksum": checksum,
            "migration_batch_id": migration_batch_id,
            "migration_recorded_at": "2026-04-03T00:03:00+00:00",
        }
        self.transcript_legacy_indexes.append(payload)
        return payload

    def list_work_item_transcripts(self, work_item_id: str) -> list[dict]:
        summaries: list[dict] = []
        for session_id, session in self.transcript_sessions.items():
            if session["work_item_id"] != work_item_id:
                continue
            summaries.append(
                {
                    "session_id": session_id,
                    "actor_cli": session["actor_cli"],
                    "transcript_kind": session["transcript_kind"],
                    "started_at": session["started_at"],
                    "hot_body_available": session_id in self.transcript_hot_bodies and session_id not in self.transcript_archive_refs,
                    "archive_locator": self.transcript_archive_refs.get(session_id),
                }
            )
        return summaries
