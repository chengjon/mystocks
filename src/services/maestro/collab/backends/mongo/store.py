from __future__ import annotations

from typing import Any, TypeVar

from pymongo import ASCENDING

from src.services.maestro.collab.backends.mongo.indexes import build_collaboration_index_models
from src.services.maestro.collab.store.base import CollaborationStore
from src.services.maestro.collab.store.models import (
    WorkerStatusViewRecord,
    WorkEventRecord,
    WorkItemRecord,
    WorkRequestRecord,
    WorkUpdateRecord,
)

RecordT = TypeVar(
    "RecordT",
    WorkItemRecord,
    WorkUpdateRecord,
    WorkRequestRecord,
    WorkEventRecord,
    WorkerStatusViewRecord,
)


class MongoCollaborationStore(CollaborationStore):
    def __init__(self, database: Any) -> None:
        self._database = database
        self._work_items = database["work_items"]
        self._work_updates = database["work_updates"]
        self._work_requests = database["work_requests"]
        self._work_events = database["work_events"]
        self._worker_status_views = database["worker_status_views"]
        self.ensure_indexes()

    def ensure_indexes(self) -> None:
        for collection_name, indexes in build_collaboration_index_models().items():
            self._database[collection_name].create_indexes(indexes)

    def upsert_work_item(self, work_item: WorkItemRecord) -> WorkItemRecord:
        self._work_items.replace_one(
            {"work_item_id": work_item.work_item_id},
            _document_for(work_item),
            upsert=True,
        )
        return work_item

    def get_work_item(self, work_item_id: str) -> WorkItemRecord | None:
        document = self._work_items.find_one({"work_item_id": work_item_id})
        return _load_optional(document, WorkItemRecord)

    def list_work_items(self) -> list[WorkItemRecord]:
        cursor = self._work_items.find({}).sort("work_item_id", ASCENDING)
        return [_load_required(document, WorkItemRecord) for document in cursor]

    def append_work_update(self, update: WorkUpdateRecord) -> WorkUpdateRecord:
        existing = self._work_updates.find_one(
            {"work_item_id": update.work_item_id, "update_id": update.update_id}
        )
        if existing is None:
            self._work_updates.insert_one(_document_for(update))
        return update

    def list_work_updates(self, work_item_id: str) -> list[WorkUpdateRecord]:
        cursor = self._work_updates.find({"work_item_id": work_item_id}).sort("created_at", ASCENDING)
        return [_load_required(document, WorkUpdateRecord) for document in cursor]

    def create_work_request(self, request: WorkRequestRecord) -> WorkRequestRecord:
        self._work_requests.replace_one(
            {"work_item_id": request.work_item_id, "request_id": request.request_id},
            _document_for(request),
            upsert=True,
        )
        return request

    def list_work_requests(self, work_item_id: str) -> list[WorkRequestRecord]:
        cursor = self._work_requests.find({"work_item_id": work_item_id}).sort("created_at", ASCENDING)
        return [_load_required(document, WorkRequestRecord) for document in cursor]

    def append_work_event(self, event: WorkEventRecord) -> WorkEventRecord:
        self._work_events.replace_one(
            {"work_item_id": event.work_item_id, "event_id": event.event_id},
            _document_for(event),
            upsert=True,
        )
        return event

    def list_work_events(self, work_item_id: str) -> list[WorkEventRecord]:
        cursor = self._work_events.find({"work_item_id": work_item_id}).sort("created_at", ASCENDING)
        return [_load_required(document, WorkEventRecord) for document in cursor]

    def upsert_worker_status_view(self, view: WorkerStatusViewRecord) -> WorkerStatusViewRecord:
        self._worker_status_views.replace_one(
            {"work_item_id": view.work_item_id},
            _document_for(view),
            upsert=True,
        )
        return view

    def get_worker_status_view(self, work_item_id: str) -> WorkerStatusViewRecord | None:
        document = self._worker_status_views.find_one({"work_item_id": work_item_id})
        return _load_optional(document, WorkerStatusViewRecord)


def _document_for(record: RecordT) -> dict[str, Any]:
    return record.model_dump(mode="python")


def _load_optional(document: dict[str, Any] | None, record_type: type[RecordT]) -> RecordT | None:
    if document is None:
        return None
    return _load_required(document, record_type)


def _load_required(document: dict[str, Any], record_type: type[RecordT]) -> RecordT:
    return record_type.model_validate(_strip_mongo_internal_fields(document))


def _strip_mongo_internal_fields(document: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in document.items() if key != "_id"}
