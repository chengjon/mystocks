from __future__ import annotations

from typing import Any, TypeVar

from pymongo import ASCENDING

from src.services.maestro.collab.backends.mongo.indexes import build_collaboration_index_models
from src.services.maestro.collab.store.base import CollaborationStore
from src.services.maestro.collab.store.models import (
    TranscriptEventRecord,
    TranscriptHotBodyRecord,
    TranscriptLegacyIndexRecord,
    TranscriptSessionRecord,
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
    TranscriptSessionRecord,
    TranscriptEventRecord,
    TranscriptHotBodyRecord,
    TranscriptLegacyIndexRecord,
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
        self._transcript_sessions = database["transcript_sessions"]
        self._transcript_events = database["transcript_events"]
        self._transcript_hot_bodies = database["transcript_hot_bodies"]
        self._transcript_legacy_indexes = database["transcript_legacy_indexes"]
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
        existing = self._work_updates.find_one({"work_item_id": update.work_item_id, "update_id": update.update_id})
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

    def upsert_transcript_session(self, session: TranscriptSessionRecord) -> TranscriptSessionRecord:
        self._transcript_sessions.replace_one(
            {"session_id": session.session_id},
            _document_for(session),
            upsert=True,
        )
        return session

    def get_transcript_session(self, session_id: str) -> TranscriptSessionRecord | None:
        document = self._transcript_sessions.find_one({"session_id": session_id})
        return _load_optional(document, TranscriptSessionRecord)

    def list_transcript_sessions(self, work_item_id: str) -> list[TranscriptSessionRecord]:
        cursor = self._transcript_sessions.find({"work_item_id": work_item_id})
        sessions = [_load_required(document, TranscriptSessionRecord) for document in cursor]
        return sorted(sessions, key=lambda item: (item.started_at, item.session_id))

    def append_transcript_event(self, event: TranscriptEventRecord) -> TranscriptEventRecord:
        existing = self._transcript_events.find_one({"session_id": event.session_id, "event_id": event.event_id})
        if existing is None:
            self._transcript_events.insert_one(_document_for(event))
        return event

    def list_transcript_events(self, session_id: str) -> list[TranscriptEventRecord]:
        cursor = self._transcript_events.find({"session_id": session_id})
        events = [_load_required(document, TranscriptEventRecord) for document in cursor]
        return sorted(events, key=lambda item: (item.sequence_no, item.occurred_at, item.event_id))

    def upsert_transcript_hot_body(self, hot_body: TranscriptHotBodyRecord) -> TranscriptHotBodyRecord:
        self._transcript_hot_bodies.replace_one(
            {"session_id": hot_body.session_id},
            _document_for(hot_body),
            upsert=True,
        )
        return hot_body

    def get_transcript_hot_body(self, session_id: str) -> TranscriptHotBodyRecord | None:
        document = self._transcript_hot_bodies.find_one({"session_id": session_id})
        return _load_optional(document, TranscriptHotBodyRecord)

    def append_transcript_legacy_index(self, legacy_index: TranscriptLegacyIndexRecord) -> TranscriptLegacyIndexRecord:
        existing = self._transcript_legacy_indexes.find_one({"legacy_index_id": legacy_index.legacy_index_id})
        if existing is None:
            self._transcript_legacy_indexes.insert_one(_document_for(legacy_index))
        return legacy_index

    def list_transcript_legacy_indexes(self, work_item_id: str) -> list[TranscriptLegacyIndexRecord]:
        cursor = self._transcript_legacy_indexes.find({"work_item_id": work_item_id})
        records = [_load_required(document, TranscriptLegacyIndexRecord) for document in cursor]
        return sorted(records, key=lambda item: (item.captured_at, item.legacy_index_id))


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
