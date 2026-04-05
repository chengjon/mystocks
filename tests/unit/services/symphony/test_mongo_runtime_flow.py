from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from src.services.maestro.collab.runtime_registry import MongoCollaborationRegistry
from src.services.symphony.config import ServiceConfig
from src.services.symphony.models import WorkflowDefinition
from src.services.symphony.mongo_tracker import MongoWorkItemTrackerClient
from src.services.symphony.orchestrator import SymphonyOrchestrator
from src.services.symphony.status_api import create_status_app


class DummyRunnerFactory:
    def __call__(self, issue, attempt):
        return {"issue": issue.identifier, "attempt": attempt}


def test_mongo_runtime_flow_updates_control_plane_and_status_api() -> None:
    database = _FakeDatabase()
    database["work_items"].docs.append(
        {
            "work_item_id": "MT-900",
            "task_key": "mongo-runtime-flow",
            "title": "Mongo runtime flow",
            "objective": "dispatch from mongo and sync control plane",
            "branch": "feat/mongo-runtime-flow",
            "owner_cli": "cli-9",
            "status": "dispatched",
            "allowed_paths": ["src/services/maestro/collab"],
            "forbidden_paths": [],
            "acceptance_checks": [],
            "openspec": None,
            "created_at": "2026-03-14T10:00:00+00:00",
            "updated_at": "2026-03-14T10:00:00+00:00",
        }
    )

    workflow_definition = WorkflowDefinition(
        config={
            "tracker": {
                "kind": "mongo",
                "mongo_uri": "mongodb://localhost:27017",
                "mongo_db": "mystocks_coord",
                "active_states": ["created", "dispatched", "in_progress", "ready_for_review"],
                "terminal_states": ["verified", "merged", "archived"],
            },
            "runtime": {
                "cli_name": "cli-9",
            },
        },
        prompt_template="Prompt",
    )
    service_config = ServiceConfig.from_workflow_definition(workflow_definition)
    tracker_client = MongoWorkItemTrackerClient(service_config.tracker, database)
    collab_registry = MongoCollaborationRegistry(database)
    orchestrator = SymphonyOrchestrator(
        workflow_definition=workflow_definition,
        service_config=service_config,
        tracker_client=tracker_client,
        runner_factory=DummyRunnerFactory(),
        collab_registry=collab_registry,
    )

    orchestrator.tick_once()
    running_entry = orchestrator.state.running["MT-900"]
    assert running_entry.issue.identifier == "MT-900"

    orchestrator.record_event(
        "MT-900",
        {
            "event": "turn.completed",
            "message": "implemented runtime synchronization",
            "session_id": "session-900",
        },
    )
    orchestrator.on_worker_exit("MT-900", reason="normal")

    assignment = collab_registry.get_assignment_state("MT-900")
    control_plane = collab_registry.list_control_plane_status_views()
    client = TestClient(create_status_app(orchestrator))
    state_response = client.get("/api/v1/state")
    control_plane_response = client.get("/api/v1/collab/control-plane")

    assert assignment is not None
    assert assignment["status"] == "retrying"
    assert control_plane[0]["work_item_id"] == "MT-900"
    assert control_plane[0]["status"] == "ready_for_review"
    assert control_plane[0]["latest_update"] == "implemented runtime synchronization"
    assert state_response.status_code == 200
    assert state_response.json()["control_plane"]["items"][0]["work_item_id"] == "MT-900"
    assert control_plane_response.status_code == 200
    assert control_plane_response.json()["items"][0]["status"] == "ready_for_review"


class _FakeDatabase:
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
        self._docs.sort(key=lambda document: str(document[key]))
        return self

    def __iter__(self):
        return iter(self._docs)


def _matches(document: dict, filter_query: dict) -> bool:
    for key, value in filter_query.items():
        expected = value
        actual = document.get(key)
        if isinstance(expected, dict) and "$in" in expected:
            if actual not in expected["$in"]:
                return False
        elif actual != expected:
            return False
    return True
