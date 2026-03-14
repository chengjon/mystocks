from __future__ import annotations

import json

import pytest

from scripts.runtime import maestro_collab


def test_build_parser_exposes_coordination_command_groups() -> None:
    parser = maestro_collab.build_parser()

    choices = parser._subparsers._group_actions[0].choices  # type: ignore[attr-defined]
    assert "work" in choices
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


class _FakeCoordinationService:
    def __init__(self) -> None:
        self.work_items: dict[str, dict] = {}
        self.requests: dict[tuple[str, str], dict] = {}
        self.update_seq = 0

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
