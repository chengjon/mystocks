from __future__ import annotations

import argparse
import json

import pytest

from scripts.runtime import maestro_collab


def test_build_parser_exposes_coordination_command_groups() -> None:
    parser = maestro_collab.build_parser()

    choices = parser._subparsers._group_actions[0].choices  # type: ignore[attr-defined]
    assert "work" in choices
    assert "plan" in choices
    assert "update" in choices
    assert "request" in choices
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


def test_worker_can_claim_plan_submit_and_inspect_board(monkeypatch, capsys) -> None:
    service = _FakeCoordinationService()
    service.create_work_item(
        {
            "work_item_id": "MT-303",
            "task_key": "mongo-lifecycle",
            "title": "Mongo lifecycle",
            "objective": "Track claim, plan, and submit",
            "branch": "feat/mongo-lifecycle",
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
        ["work", "claim", "MT-303", "--actor-cli", "gemini", "--summary", "Accepted task", "--output", "json"]
    )
    assert exit_code == 0
    claim_payload = json.loads(capsys.readouterr().out)
    assert claim_payload["details"]["kind"] == "claim"

    exit_code = maestro_collab.main(
        ["plan", "add", "MT-303", "--actor-cli", "gemini", "--title", "Inspect schema", "--order", "10", "--output", "json"]
    )
    assert exit_code == 0
    added_plan = json.loads(capsys.readouterr().out)
    assert added_plan["title"] == "Inspect schema"

    exit_code = maestro_collab.main(
        [
            "plan",
            "mark",
            "MT-303",
            added_plan["plan_item_id"],
            "--actor-cli",
            "gemini",
            "--status",
            "done",
            "--evidence",
            "Schema captured",
            "--output",
            "json",
        ]
    )
    assert exit_code == 0
    marked_plan = json.loads(capsys.readouterr().out)
    assert marked_plan["status"] == "done"

    exit_code = maestro_collab.main(
        [
            "work",
            "submit",
            "MT-303",
            "--actor-cli",
            "gemini",
            "--summary",
            "Ready for review",
            "--commit",
            "abc123",
            "--branch",
            "feat/mongo-lifecycle",
            "--verify",
            "pytest tests/unit/runtime -q",
            "--output",
            "json",
        ]
    )
    assert exit_code == 0
    submit_payload = json.loads(capsys.readouterr().out)
    assert submit_payload["details"]["kind"] == "submit"
    assert submit_payload["status"] == "ready_for_review"

    exit_code = maestro_collab.main(["work", "board", "--active-only", "--output", "json"])
    assert exit_code == 0
    board_payload = json.loads(capsys.readouterr().out)
    assert board_payload[0]["work_item_id"] == "MT-303"
    assert board_payload[0]["plan_total"] == 1
    assert board_payload[0]["plan_done"] == 1
    assert board_payload[0]["delivery_commit"] == "abc123"

    exit_code = maestro_collab.main(["work", "show", "MT-303", "--include-plan", "--output", "json"])
    assert exit_code == 0
    show_payload = json.loads(capsys.readouterr().out)
    assert show_payload["work_item"]["work_item_id"] == "MT-303"
    assert len(show_payload["plan_items"]) == 1


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

    monkeypatch.setattr(maestro_collab, "load_dotenv", lambda path, override=False: captured.update({"dotenv_path": str(path)}))
    monkeypatch.setattr(
        maestro_collab,
        "get_mongo_connection_kwargs",
        lambda **kwargs: {
            "host": "mongo.local",
            "port": 27017,
            "username": "coord",
            "password": "secret",
            "authSource": "admin",
            "serverSelectionTimeoutMS": kwargs["server_selection_timeout_ms"],
        },
    )
    monkeypatch.setattr(maestro_collab, "MongoClient", lambda **kwargs: captured.update({"client_kwargs": kwargs}) or _FakeClient())
    monkeypatch.setattr(maestro_collab, "MongoCollaborationStore", lambda database: captured.update({"database": database}) or object())
    monkeypatch.setattr(maestro_collab, "CoordinationService", lambda store: captured.update({"store": store}) or object())

    facade = maestro_collab._build_coordination_service(argparse.Namespace(mongo_uri=None, mongo_db="mystocks_coord"))

    assert isinstance(facade, maestro_collab._MongoCoordinationFacade)
    assert captured["mongo_db"] == "mystocks_coord"
    assert captured["client_kwargs"] == {
        "host": "mongo.local",
        "port": 27017,
        "username": "coord",
        "password": "secret",
        "authSource": "admin",
        "serverSelectionTimeoutMS": 3000,
    }
    assert str(maestro_collab.PROJECT_ROOT / ".env") == captured["dotenv_path"]


def test_build_coordination_service_prefers_explicit_mongo_uri(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class _FakeClient:
        def __getitem__(self, name: str):
            captured["mongo_db"] = name
            return object()

    monkeypatch.setattr(maestro_collab, "load_dotenv", lambda *_args, **_kwargs: pytest.fail("load_dotenv should not run"))
    monkeypatch.setattr(
        maestro_collab,
        "get_mongo_connection_kwargs",
        lambda **_kwargs: pytest.fail("env-driven mongo kwargs should not be used when uri is explicit"),
    )
    monkeypatch.setattr(maestro_collab, "MongoClient", lambda uri: captured.update({"mongo_uri": uri}) or _FakeClient())
    monkeypatch.setattr(maestro_collab, "MongoCollaborationStore", lambda database: captured.update({"database": database}) or object())
    monkeypatch.setattr(maestro_collab, "CoordinationService", lambda store: captured.update({"store": store}) or object())

    facade = maestro_collab._build_coordination_service(
        argparse.Namespace(mongo_uri="mongodb://user:pass@mongo.example:27017/admin?authSource=admin", mongo_db="mystocks_coord")
    )

    assert isinstance(facade, maestro_collab._MongoCoordinationFacade)
    assert captured["mongo_uri"] == "mongodb://user:pass@mongo.example:27017/admin?authSource=admin"
    assert captured["mongo_db"] == "mystocks_coord"


class _FakeCoordinationService:
    def __init__(self) -> None:
        self.work_items: dict[str, dict] = {}
        self.requests: dict[tuple[str, str], dict] = {}
        self.plan_items: dict[str, list[dict]] = {}
        self.board_rows: dict[str, dict] = {}
        self.update_seq = 0
        self.plan_seq = 0

    def create_work_item(self, payload: dict) -> dict:
        item = {
            **payload,
            "status": payload.get("status", "created"),
        }
        self.work_items[item["work_item_id"]] = item
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

    def claim_work_item(self, work_item_id: str, actor_cli: str, summary: str) -> dict:
        self.update_seq += 1
        item = self.work_items[work_item_id]
        item["status"] = "in_progress"
        board = self.board_rows.setdefault(work_item_id, {"work_item_id": work_item_id, "plan_total": 0, "plan_done": 0})
        board["status"] = "in_progress"
        board["claimed_by"] = actor_cli
        board["latest_update"] = summary
        return {
            "work_item_id": work_item_id,
            "update_id": f"upd-{self.update_seq}",
            "actor_cli": actor_cli,
            "summary": summary,
            "status": "in_progress",
            "details": {"kind": "claim"},
        }

    def create_work_update(self, work_item_id: str, actor_cli: str, summary: str, status: str) -> dict:
        self.update_seq += 1
        item = self.work_items[work_item_id]
        item["status"] = status
        item["latest_update"] = summary
        return {
            "work_item_id": work_item_id,
            "update_id": f"upd-{self.update_seq}",
            "actor_cli": actor_cli,
            "summary": summary,
            "status": status,
        }

    def add_plan_item(self, work_item_id: str, actor_cli: str, title: str, order: int) -> dict:
        self.plan_seq += 1
        payload = {
            "work_item_id": work_item_id,
            "plan_item_id": f"plan-{self.plan_seq}",
            "actor_cli": actor_cli,
            "title": title,
            "order": order,
            "status": "todo",
            "evidence_summary": None,
        }
        self.plan_items.setdefault(work_item_id, []).append(payload)
        self.plan_items[work_item_id].sort(key=lambda item: item["order"])
        board = self.board_rows.setdefault(work_item_id, {"work_item_id": work_item_id, "plan_done": 0})
        board["plan_total"] = len(self.plan_items[work_item_id])
        board["current_focus"] = self.plan_items[work_item_id][0]["title"]
        return payload

    def mark_plan_item(self, work_item_id: str, plan_item_id: str, actor_cli: str, status: str, evidence: str | None) -> dict:
        for plan_item in self.plan_items[work_item_id]:
            if plan_item["plan_item_id"] == plan_item_id:
                plan_item["status"] = status
                plan_item["evidence_summary"] = evidence
                break
        board = self.board_rows.setdefault(work_item_id, {"work_item_id": work_item_id, "plan_total": 0})
        board["plan_total"] = len(self.plan_items[work_item_id])
        board["plan_done"] = sum(1 for item in self.plan_items[work_item_id] if item["status"] == "done")
        board["current_focus"] = next(
            (item["title"] for item in self.plan_items[work_item_id] if item["status"] != "done"),
            None,
        )
        return next(item for item in self.plan_items[work_item_id] if item["plan_item_id"] == plan_item_id)

    def submit_work_item(
        self,
        work_item_id: str,
        actor_cli: str,
        summary: str,
        commit_sha: str,
        branch: str,
        remote: str | None,
        verification_summary: str | None,
    ) -> dict:
        self.update_seq += 1
        item = self.work_items[work_item_id]
        item["status"] = "ready_for_review"
        board = self.board_rows.setdefault(work_item_id, {"work_item_id": work_item_id})
        board["status"] = "ready_for_review"
        board["delivery_commit"] = commit_sha
        board["delivery_branch"] = branch
        board["latest_update"] = summary
        return {
            "work_item_id": work_item_id,
            "update_id": f"upd-{self.update_seq}",
            "actor_cli": actor_cli,
            "summary": summary,
            "status": "ready_for_review",
            "details": {
                "kind": "submit",
                "commit_sha": commit_sha,
                "branch": branch,
                "remote": remote,
                "verification_summary": verification_summary,
            },
        }

    def get_work_item_snapshot(self, work_item_id: str, include_plan: bool = False) -> dict:
        payload = {
            "work_item": self.work_items[work_item_id],
            "status_view": self.board_rows.get(work_item_id, {"work_item_id": work_item_id, "status": self.work_items[work_item_id]["status"]}),
        }
        if include_plan:
            payload["plan_items"] = self.plan_items.get(work_item_id, [])
        return payload

    def list_work_board_rows(self, active_only: bool = False) -> list[dict]:
        rows = list(self.board_rows.values())
        if active_only:
            rows = [row for row in rows if row.get("status") not in {"verified", "merged", "archived"}]
        return rows

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
        }
        self.requests[(work_item_id, request_id)] = payload
        return payload

    def review_work_request(self, work_item_id: str, request_id: str, reviewed_by: str, status: str) -> dict:
        payload = self.requests[(work_item_id, request_id)]
        payload["reviewed_by"] = reviewed_by
        payload["status"] = status
        return payload
