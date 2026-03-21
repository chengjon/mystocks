from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.services.maestro.collab.authz import ActorIdentity
from src.services.maestro.collab.backends.mongo.store import MongoCollaborationStore
from src.services.maestro.collab.integrations.models import (
    GraphitiIngestStatus,
    GraphitiPreflightResult,
    GraphitiQueryBundle,
    GraphitiSearchResult,
    GraphitiServerStatus,
    GraphitiWriteResult,
)
from src.services.maestro.collab.services import CoordinationService
from src.services.maestro.collab.services.graphiti_preflight import GraphitiPreflightService
from src.services.maestro.collab.store.models import WorkItemRecord


class _FakeGraphitiAdapter:
    def __init__(self) -> None:
        self.write_calls: list[dict[str, Any]] = []
        self.wait_calls: list[dict[str, Any]] = []
        self.search_calls: list[dict[str, Any]] = []

    def get_server_status(self) -> GraphitiServerStatus:
        return GraphitiServerStatus(server_status="ok", message="ready", details={})

    def add_memory(self, **kwargs: Any) -> GraphitiWriteResult:
        self.write_calls.append(kwargs)
        return GraphitiWriteResult(
            episode_uuid="ep-123",
            group_id="mystocks_spec_workers",
            queue_position=1,
            message="queued",
        )

    def wait_for_ingest(self, **kwargs: Any) -> GraphitiIngestStatus:
        self.wait_calls.append(kwargs)
        return GraphitiIngestStatus(
            ingest_status="completed",
            episode_uuid="ep-123",
            group_id="mystocks_spec_workers",
            queue_depth=0,
            queue_position=None,
            processed_at="2026-03-20T08:00:00+00:00",
            last_error=None,
        )

    def search_context(self, query_bundle: GraphitiQueryBundle, group_ids: list[str] | None = None) -> GraphitiSearchResult:
        self.search_calls.append({"query_bundle": query_bundle, "group_ids": group_ids})
        return GraphitiSearchResult(
            search_outcome="hit",
            search_summary="nodes hit=1, facts hit=2",
            matched_nodes_count=1,
            matched_facts_count=2,
            nodes=[{"uuid": "n-1", "name": "Codex Smoke Tester"}],
            facts=[{"uuid": "f-1", "fact": "Codex Smoke Tester works at Graphiti Validation Lab"}],
            errors=[],
        )


def test_graphiti_preflight_records_audit_event_without_mutating_workflow_truth(tmp_path: Path) -> None:
    database = _FakeDatabase()
    store = MongoCollaborationStore(database)
    service = CoordinationService(store)
    now = datetime(2026, 3, 20, 8, 0, tzinfo=UTC)
    work_item = WorkItemRecord(
        work_item_id="MT-100",
        task_key="graphiti-preflight",
        title="Graphiti preflight",
        objective="Read Graphiti context before work starts",
        branch="feat/graphiti-preflight",
        owner_cli="cli-1",
        status="dispatched",
        allowed_paths=["src/services/maestro/collab"],
        forbidden_paths=[],
        acceptance_checks=[],
        openspec=None,
        created_at=now,
        updated_at=now,
    )
    actor = ActorIdentity(cli_name="cli-1", role="worker_cli")
    service.upsert_work_item(ActorIdentity(cli_name="main", role="main_cli"), work_item)

    preflight = GraphitiPreflightService(service=service, adapter=_FakeGraphitiAdapter())
    task_path = tmp_path / "TASK.md"
    task_path.write_text("- Objective: verify graphiti preflight\n", encoding="utf-8")

    result = preflight.run(
        actor=actor,
        work_item_id="MT-100",
        task_path=task_path,
        write_memory=False,
        max_wait_seconds=60,
    )

    assert result.server_status == "ok"
    assert result.ingest_status == "not_applicable"
    assert result.search_outcome == "hit"

    events = service.list_work_events(actor, "MT-100")
    assert len(events) == 2
    graphiti_event = events[-1]
    assert graphiti_event.event_type == "automation.graphiti_preflight_checked"
    assert graphiti_event.payload["server_status"] == "ok"
    assert graphiti_event.payload["search_summary"] == "nodes hit=1, facts hit=2"

    status_view = service.get_worker_status_view(actor, "MT-100")
    assert status_view is not None
    assert status_view.status == "dispatched"


def test_graphiti_preflight_can_write_memory_and_wait_for_ingest(tmp_path: Path) -> None:
    database = _FakeDatabase()
    store = MongoCollaborationStore(database)
    service = CoordinationService(store)
    now = datetime(2026, 3, 20, 8, 0, tzinfo=UTC)
    work_item = WorkItemRecord(
        work_item_id="MT-101",
        task_key="graphiti-write",
        title="Graphiti write preflight",
        objective="Write a reusable handoff summary",
        branch="feat/graphiti-write",
        owner_cli="cli-1",
        status="in_progress",
        allowed_paths=["src/services/maestro/collab"],
        forbidden_paths=[],
        acceptance_checks=[],
        openspec=None,
        created_at=now,
        updated_at=now,
    )
    adapter = _FakeGraphitiAdapter()
    service.upsert_work_item(ActorIdentity(cli_name="main", role="main_cli"), work_item)
    preflight = GraphitiPreflightService(service=service, adapter=adapter)

    result = preflight.run(
        actor=ActorIdentity(cli_name="cli-1", role="worker_cli"),
        work_item_id="MT-101",
        task_path=tmp_path / "TASK.md",
        write_memory=True,
        max_wait_seconds=60,
    )

    assert result.ingest_status == "completed"
    assert result.episode_uuid == "ep-123"
    assert result.group_id == "mystocks_spec_workers"
    assert result.processed_at == "2026-03-20T08:00:00+00:00"
    assert adapter.write_calls
    assert adapter.wait_calls


def test_graphiti_preflight_can_record_memory_as_an_explicit_action(tmp_path: Path) -> None:
    database = _FakeDatabase()
    store = MongoCollaborationStore(database)
    service = CoordinationService(store)
    now = datetime(2026, 3, 20, 8, 0, tzinfo=UTC)
    work_item = WorkItemRecord(
        work_item_id="MT-102",
        task_key="graphiti-record",
        title="Record Graphiti task memory",
        objective="Persist a reusable task summary",
        branch="feat/graphiti-record",
        owner_cli="cli-1",
        status="in_progress",
        allowed_paths=["scripts/runtime"],
        forbidden_paths=[],
        acceptance_checks=[],
        openspec=None,
        created_at=now,
        updated_at=now,
    )
    actor = ActorIdentity(cli_name="cli-1", role="worker_cli")
    adapter = _FakeGraphitiAdapter()
    service.upsert_work_item(ActorIdentity(cli_name="main", role="main_cli"), work_item)
    preflight = GraphitiPreflightService(service=service, adapter=adapter)

    task_path = tmp_path / "TASK.md"
    task_path.write_text("- Issue Identifier: `MT-102`\n", encoding="utf-8")

    result = preflight.remember(
        actor=actor,
        work_item_id="MT-102",
        task_path=task_path,
        max_wait_seconds=45,
    )

    assert result.server_status == "ok"
    assert result.ingest_status == "completed"
    assert result.episode_uuid == "ep-123"
    assert result.group_id == "mystocks_spec_workers"
    assert result.processed_at == "2026-03-20T08:00:00+00:00"
    assert adapter.write_calls
    assert adapter.wait_calls

    events = service.list_work_events(actor, "MT-102")
    graphiti_event = events[-1]
    assert graphiti_event.event_type == "automation.graphiti_memory_recorded"
    assert graphiti_event.payload["episode_uuid"] == "ep-123"


class _FakeDatabase:
    def __init__(self) -> None:
        self._collections = {
            "work_items": _FakeCollection(),
            "work_updates": _FakeCollection(),
            "work_requests": _FakeCollection(),
            "work_events": _FakeCollection(),
            "worker_status_views": _FakeCollection(),
        }

    def __getitem__(self, name: str) -> "_FakeCollection":
        return self._collections[name]


class _FakeCollection:
    def __init__(self) -> None:
        self.docs: list[dict[str, Any]] = []
        self.indexes = []

    def create_indexes(self, indexes) -> None:
        self.indexes.extend(indexes)

    def replace_one(self, filter_query: dict[str, Any], document: dict[str, Any], *, upsert: bool = False) -> None:
        for index, existing in enumerate(self.docs):
            if _matches(existing, filter_query):
                self.docs[index] = document.copy()
                return
        if upsert:
            self.docs.append(document.copy())

    def find_one(self, filter_query: dict[str, Any]) -> dict[str, Any] | None:
        for document in self.docs:
            if _matches(document, filter_query):
                return document.copy()
        return None

    def insert_one(self, document: dict[str, Any]) -> None:
        self.docs.append(document.copy())

    def find(self, filter_query: dict[str, Any]):
        return _FakeCursor([document.copy() for document in self.docs if _matches(document, filter_query)])


class _FakeCursor:
    def __init__(self, docs: list[dict[str, Any]]) -> None:
        self._docs = docs

    def sort(self, key: str, _direction: int):
        self._docs.sort(key=lambda document: str(document[key]))
        return self

    def __iter__(self):
        return iter(self._docs)


def _matches(document: dict[str, Any], filter_query: dict[str, Any]) -> bool:
    for key, value in filter_query.items():
        if document.get(key) != value:
            return False
    return True
