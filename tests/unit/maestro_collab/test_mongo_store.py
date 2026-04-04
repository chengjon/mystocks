from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pymongo import ASCENDING, DESCENDING

from src.services.maestro.collab.backends.mongo.indexes import build_collaboration_index_models
from src.services.maestro.collab.backends.mongo.store import MongoCollaborationStore
from src.services.maestro.collab.store.models import (
    WorkerStatusViewRecord,
    WorkEventRecord,
    WorkItemRecord,
    WorkRequestRecord,
    WorkUpdateRecord,
)


def test_build_collaboration_index_models_exposes_expected_unique_indexes() -> None:
    index_models = build_collaboration_index_models()

    work_item_indexes = index_models["work_items"]
    assert any(index.document["name"] == "ux_work_items_work_item_id" for index in work_item_indexes)
    assert any(index.document["unique"] is True for index in work_item_indexes)

    work_update_indexes = index_models["work_updates"]
    assert any(index.document["name"] == "ux_work_updates_work_item_id_update_id" for index in work_update_indexes)


def test_mongo_collaboration_store_round_trips_work_item_and_status_view() -> None:
    store = MongoCollaborationStore(_FakeDatabase())
    work_item = WorkItemRecord(
        work_item_id="MT-100",
        task_key="api-availability",
        title="API availability hardening",
        objective="Track availability implementation in Mongo control plane",
        branch="dev-api-availability-gemini",
        owner_cli="gemini",
        status="in_progress",
        allowed_paths=["web/backend/app/api"],
        forbidden_paths=["web/frontend/src"],
        acceptance_checks=["pytest tests/api -q"],
        openspec={"change_id": "mongodb-multicli"},
        created_at=_ts("2026-03-14T08:00:00Z"),
        updated_at=_ts("2026-03-14T08:00:00Z"),
    )
    status_view = WorkerStatusViewRecord(
        work_item_id="MT-100",
        branch="dev-api-availability-gemini",
        owner_cli="gemini",
        status="in_progress",
        latest_update="Investigating API path regressions",
        blocker=None,
        has_pending_request=False,
        updated_at=_ts("2026-03-14T08:05:00Z"),
    )

    store.upsert_work_item(work_item)
    store.upsert_worker_status_view(status_view)

    assert store.get_work_item("MT-100") == work_item
    assert store.get_worker_status_view("MT-100") == status_view


def test_mongo_collaboration_store_ignores_mongo_internal_id_on_read() -> None:
    database = _FakeDatabase()
    database["work_items"].docs.append(
        {
            "_id": "mongo-object-id",
            "work_item_id": "MT-100A",
            "task_key": "api-availability",
            "title": "API availability hardening",
            "objective": "Track availability implementation in Mongo control plane",
            "branch": "dev-api-availability-gemini",
            "owner_cli": "gemini",
            "status": "in_progress",
            "allowed_paths": ["web/backend/app/api"],
            "forbidden_paths": ["web/frontend/src"],
            "acceptance_checks": ["pytest tests/api -q"],
            "openspec": {"change_id": "mongodb-multicli"},
            "created_at": _ts("2026-03-14T08:00:00Z"),
            "updated_at": _ts("2026-03-14T08:00:00Z"),
        }
    )
    store = MongoCollaborationStore(database)

    work_item = store.get_work_item("MT-100A")

    assert work_item is not None
    assert work_item.work_item_id == "MT-100A"


def test_mongo_collaboration_store_accepts_work_item_metadata_from_existing_documents() -> None:
    database = _FakeDatabase()
    database["work_items"].docs.append(
        {
            "work_item_id": "MT-100B",
            "task_key": "api-availability",
            "title": "API availability hardening",
            "objective": "Track availability implementation in Mongo control plane",
            "branch": "dev-api-availability-gemini",
            "owner_cli": "gemini",
            "status": "in_progress",
            "allowed_paths": ["web/backend/app/api"],
            "forbidden_paths": ["web/frontend/src"],
            "acceptance_checks": ["pytest tests/api -q"],
            "openspec": {"change_id": "mongodb-multicli"},
            "metadata": {"source": "legacy-runtime", "worktree": "root-dirty"},
            "created_at": _ts("2026-03-14T08:00:00Z"),
            "updated_at": _ts("2026-03-14T08:00:00Z"),
        }
    )
    store = MongoCollaborationStore(database)

    work_items = store.list_work_items()

    assert [item.work_item_id for item in work_items] == ["MT-100B"]
    assert work_items[0].model_dump(mode="python")["metadata"] == {
        "source": "legacy-runtime",
        "worktree": "root-dirty",
    }


def test_mongo_collaboration_store_ignores_duplicate_update_ids() -> None:
    store = MongoCollaborationStore(_FakeDatabase())
    first_update = WorkUpdateRecord(
        work_item_id="MT-101",
        update_id="upd-1",
        actor_cli="gemini",
        status="in_progress",
        summary="Collected failing API checks",
        details={"count": 3},
        created_at=_ts("2026-03-14T09:00:00Z"),
    )

    duplicate_update = first_update.model_copy(update={"summary": "This should be ignored"})
    later_update = WorkUpdateRecord(
        work_item_id="MT-101",
        update_id="upd-2",
        actor_cli="gemini",
        status="ready_for_review",
        summary="Patched API availability checks",
        details={"count": 4},
        created_at=_ts("2026-03-14T09:30:00Z"),
    )

    store.append_work_update(first_update)
    store.append_work_update(duplicate_update)
    store.append_work_update(later_update)

    updates = store.list_work_updates("MT-101")
    assert [update.update_id for update in updates] == ["upd-1", "upd-2"]
    assert updates[0].summary == "Collected failing API checks"


def test_mongo_collaboration_store_lists_requests_and_events_in_created_order() -> None:
    store = MongoCollaborationStore(_FakeDatabase())
    request = WorkRequestRecord(
        work_item_id="MT-102",
        request_id="req-1",
        actor_cli="gemini",
        status="pending",
        request_type="definition_change",
        summary="Need to widen allowed backend paths",
        payload={"path": "web/backend/app/services"},
        created_at=_ts("2026-03-14T10:00:00Z"),
        reviewed_at=None,
        reviewed_by=None,
    )
    earlier_event = WorkEventRecord(
        work_item_id="MT-102",
        event_id="evt-1",
        actor_cli="main",
        event_type="work_dispatched",
        payload={"status": "dispatched"},
        created_at=_ts("2026-03-14T09:00:00Z"),
    )
    later_event = WorkEventRecord(
        work_item_id="MT-102",
        event_id="evt-2",
        actor_cli="gemini",
        event_type="request_created",
        payload={"request_id": "req-1"},
        created_at=_ts("2026-03-14T10:00:00Z"),
    )

    store.create_work_request(request)
    store.append_work_event(later_event)
    store.append_work_event(earlier_event)

    assert store.list_work_requests("MT-102") == [request]
    assert [event.event_id for event in store.list_work_events("MT-102")] == ["evt-1", "evt-2"]


def _ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


class _FakeDatabase:
    def __init__(self) -> None:
        self._collections = {
            "work_items": _FakeCollection(),
            "work_updates": _FakeCollection(),
            "work_requests": _FakeCollection(),
            "work_events": _FakeCollection(),
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
        match_index = self._find_index(filter_query)
        if match_index is not None:
            self.docs[match_index] = document.copy()
            return
        if upsert:
            self.docs.append(document.copy())

    def insert_one(self, document: dict) -> None:
        self.docs.append(document.copy())

    def update_one(self, filter_query: dict, update: dict, *, upsert: bool = False) -> None:
        match_index = self._find_index(filter_query)
        if match_index is None:
            if not upsert:
                return
            base_document = filter_query.copy()
            self.docs.append(base_document)
            match_index = len(self.docs) - 1

        document = self.docs[match_index]
        for key, value in update.get("$set", {}).items():
            document[key] = value
        for key, value in update.get("$setOnInsert", {}).items():
            document.setdefault(key, value)

    def find_one(self, filter_query: dict) -> dict | None:
        match_index = self._find_index(filter_query)
        if match_index is None:
            return None
        return self.docs[match_index].copy()

    def find(self, filter_query: dict):
        results = [doc.copy() for doc in self.docs if _matches(doc, filter_query)]
        return _FakeCursor(results)

    def _find_index(self, filter_query: dict) -> int | None:
        for index, document in enumerate(self.docs):
            if _matches(document, filter_query):
                return index
        return None


class _FakeCursor:
    def __init__(self, docs: list[dict]) -> None:
        self._docs = docs

    def sort(self, key: str, direction: int) -> "_FakeCursor":
        reverse = direction == DESCENDING
        self._docs.sort(key=lambda doc: doc[key], reverse=reverse)
        return self

    def __iter__(self):
        return iter(self._docs)


def _matches(document: dict, filter_query: dict) -> bool:
    for key, value in filter_query.items():
        if document.get(key) != value:
            return False
    return True
