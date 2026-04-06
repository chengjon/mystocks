from __future__ import annotations

from datetime import UTC, datetime

import pytest

from src.services.maestro.collab.authz.policy import ActorIdentity, AuthorizationError
from src.services.maestro.collab.services.coordination import CoordinationService
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


def test_main_cli_can_upsert_work_item_and_emit_audit_event() -> None:
    store = _InMemoryCollaborationStore()
    service = CoordinationService(store)
    actor = ActorIdentity(cli_name="main", role="main_cli")
    work_item = _work_item(owner_cli="gemini")

    created = service.upsert_work_item(actor, work_item)

    assert created == work_item
    assert store.get_work_item(work_item.work_item_id) == work_item
    audit_event = store.list_work_events(work_item.work_item_id)[0]
    assert audit_event.actor_cli == "main"
    assert audit_event.event_type == "audit.work_item_upserted"
    assert audit_event.payload["action"] == "upsert_work_item"
    assert audit_event.payload["branch"] == work_item.branch


def test_worker_can_only_read_owned_work_item() -> None:
    store = _InMemoryCollaborationStore()
    service = CoordinationService(store)
    owned_work_item = _work_item(owner_cli="gemini")
    store.upsert_work_item(owned_work_item)

    assert service.get_work_item(ActorIdentity(cli_name="gemini", role="worker_cli"), owned_work_item.work_item_id) == (
        owned_work_item
    )

    with pytest.raises(AuthorizationError):
        service.get_work_item(ActorIdentity(cli_name="codex", role="worker_cli"), owned_work_item.work_item_id)


def test_worker_cannot_upsert_work_item_definition_directly() -> None:
    store = _InMemoryCollaborationStore()
    service = CoordinationService(store)

    with pytest.raises(AuthorizationError):
        service.upsert_work_item(ActorIdentity(cli_name="gemini", role="worker_cli"), _work_item(owner_cli="gemini"))


def test_worker_can_append_update_only_for_owned_work_item_and_emits_audit_event() -> None:
    store = _InMemoryCollaborationStore()
    service = CoordinationService(store)
    work_item = _work_item(owner_cli="gemini")
    store.upsert_work_item(work_item)
    update = _work_update(work_item_id=work_item.work_item_id, actor_cli="gemini")

    appended = service.append_work_update(ActorIdentity(cli_name="gemini", role="worker_cli"), update)

    assert appended == update
    assert store.list_work_updates(work_item.work_item_id) == [update]
    audit_event = store.list_work_events(work_item.work_item_id)[0]
    assert audit_event.event_type == "audit.work_update_appended"
    assert audit_event.payload["action"] == "append_work_update"

    with pytest.raises(AuthorizationError):
        service.append_work_update(
            ActorIdentity(cli_name="codex", role="worker_cli"),
            _work_update(work_item_id=work_item.work_item_id, actor_cli="codex", update_id="upd-2"),
        )


def test_worker_can_create_request_only_for_owned_work_item_and_emits_audit_event() -> None:
    store = _InMemoryCollaborationStore()
    service = CoordinationService(store)
    work_item = _work_item(owner_cli="gemini")
    store.upsert_work_item(work_item)
    request = _work_request(work_item_id=work_item.work_item_id, actor_cli="gemini")

    created = service.create_work_request(ActorIdentity(cli_name="gemini", role="worker_cli"), request)

    assert created == request
    assert store.list_work_requests(work_item.work_item_id) == [request]
    audit_event = store.list_work_events(work_item.work_item_id)[0]
    assert audit_event.event_type == "audit.work_request_created"
    assert audit_event.payload["action"] == "create_work_request"

    with pytest.raises(AuthorizationError):
        service.create_work_request(
            ActorIdentity(cli_name="codex", role="worker_cli"),
            _work_request(work_item_id=work_item.work_item_id, actor_cli="codex", request_id="req-2"),
        )


def test_only_main_cli_can_upsert_worker_status_view() -> None:
    store = _InMemoryCollaborationStore()
    service = CoordinationService(store)
    work_item = _work_item(owner_cli="gemini")
    store.upsert_work_item(work_item)
    status_view = _status_view(work_item_id=work_item.work_item_id, owner_cli="gemini", branch=work_item.branch)

    service.upsert_worker_status_view(ActorIdentity(cli_name="main", role="main_cli"), status_view)
    assert store.get_worker_status_view(work_item.work_item_id) == status_view

    with pytest.raises(AuthorizationError):
        service.upsert_worker_status_view(ActorIdentity(cli_name="gemini", role="worker_cli"), status_view)


def test_upsert_work_item_initializes_status_view_summary() -> None:
    store = _InMemoryCollaborationStore()
    service = CoordinationService(store)
    work_item = _work_item(owner_cli="gemini")

    service.upsert_work_item(ActorIdentity(cli_name="main", role="main_cli"), work_item)

    status_view = store.get_worker_status_view(work_item.work_item_id)
    assert status_view is not None
    assert status_view.status == "dispatched"
    assert status_view.latest_update is None
    assert status_view.has_pending_request is False


def test_append_update_refreshes_status_view_latest_update_and_status() -> None:
    store = _InMemoryCollaborationStore()
    service = CoordinationService(store)
    work_item = _work_item(owner_cli="gemini")
    service.upsert_work_item(ActorIdentity(cli_name="main", role="main_cli"), work_item)

    service.append_work_update(
        ActorIdentity(cli_name="gemini", role="worker_cli"),
        _work_update(work_item_id=work_item.work_item_id, actor_cli="gemini"),
    )

    status_view = store.get_worker_status_view(work_item.work_item_id)
    assert status_view is not None
    assert status_view.status == "in_progress"
    assert status_view.latest_update == "Update summary"


def test_create_and_review_request_refresh_pending_request_flag() -> None:
    store = _InMemoryCollaborationStore()
    service = CoordinationService(store)
    work_item = _work_item(owner_cli="gemini")
    service.upsert_work_item(ActorIdentity(cli_name="main", role="main_cli"), work_item)

    created_request = service.create_work_request(
        ActorIdentity(cli_name="gemini", role="worker_cli"),
        _work_request(work_item_id=work_item.work_item_id, actor_cli="gemini"),
    )
    created_status_view = store.get_worker_status_view(work_item.work_item_id)
    assert created_status_view is not None
    assert created_status_view.has_pending_request is True

    reviewed_request = service.review_work_request(
        ActorIdentity(cli_name="main", role="main_cli"),
        work_item_id=work_item.work_item_id,
        request_id=created_request.request_id,
        reviewed_by="main",
        status="approved",
    )

    assert reviewed_request.status == "approved"
    reviewed_status_view = store.get_worker_status_view(work_item.work_item_id)
    assert reviewed_status_view is not None
    assert reviewed_status_view.has_pending_request is False


def _work_item(owner_cli: str) -> WorkItemRecord:
    return WorkItemRecord(
        work_item_id="MT-200",
        task_key="mongo-collab-task",
        title="Mongo collab task",
        objective="Add Mongo coordination control plane",
        branch="dev-api-availability-gemini",
        owner_cli=owner_cli,
        status="dispatched",
        allowed_paths=["web/backend/app/api"],
        forbidden_paths=["web/frontend/src"],
        acceptance_checks=["pytest tests/unit/maestro_collab -q"],
        openspec={"change_id": "mongodb-multicli"},
        created_at=_ts("2026-03-14T01:00:00Z"),
        updated_at=_ts("2026-03-14T01:00:00Z"),
    )


def _work_update(work_item_id: str, actor_cli: str, update_id: str = "upd-1") -> WorkUpdateRecord:
    return WorkUpdateRecord(
        work_item_id=work_item_id,
        update_id=update_id,
        actor_cli=actor_cli,
        status="in_progress",
        summary="Update summary",
        details={"step": 1},
        created_at=_ts("2026-03-14T01:10:00Z"),
    )


def _work_request(work_item_id: str, actor_cli: str, request_id: str = "req-1") -> WorkRequestRecord:
    return WorkRequestRecord(
        work_item_id=work_item_id,
        request_id=request_id,
        actor_cli=actor_cli,
        status="pending",
        request_type="definition_change",
        summary="Need to expand backend scope",
        payload={"path": "web/backend/app/services"},
        created_at=_ts("2026-03-14T01:15:00Z"),
        reviewed_at=None,
        reviewed_by=None,
    )


def _status_view(work_item_id: str, owner_cli: str, branch: str) -> WorkerStatusViewRecord:
    return WorkerStatusViewRecord(
        work_item_id=work_item_id,
        branch=branch,
        owner_cli=owner_cli,
        status="in_progress",
        latest_update="Collected status",
        blocker=None,
        has_pending_request=True,
        updated_at=_ts("2026-03-14T01:20:00Z"),
    )


def _ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


class _InMemoryCollaborationStore:
    def __init__(self) -> None:
        self.work_items: dict[str, WorkItemRecord] = {}
        self.work_updates: dict[str, list[WorkUpdateRecord]] = {}
        self.work_requests: dict[str, list[WorkRequestRecord]] = {}
        self.work_events: dict[str, list[WorkEventRecord]] = {}
        self.worker_status_views: dict[str, WorkerStatusViewRecord] = {}
        self.transcript_sessions: dict[str, TranscriptSessionRecord] = {}
        self.transcript_events: dict[str, list[TranscriptEventRecord]] = {}
        self.transcript_hot_bodies: dict[str, TranscriptHotBodyRecord] = {}
        self.transcript_legacy_indexes: dict[str, list[TranscriptLegacyIndexRecord]] = {}

    def ensure_indexes(self) -> None:
        return None

    def upsert_work_item(self, work_item: WorkItemRecord) -> WorkItemRecord:
        self.work_items[work_item.work_item_id] = work_item
        return work_item

    def get_work_item(self, work_item_id: str) -> WorkItemRecord | None:
        return self.work_items.get(work_item_id)

    def list_work_items(self) -> list[WorkItemRecord]:
        return [self.work_items[key] for key in sorted(self.work_items)]

    def append_work_update(self, update: WorkUpdateRecord) -> WorkUpdateRecord:
        updates = self.work_updates.setdefault(update.work_item_id, [])
        if all(existing.update_id != update.update_id for existing in updates):
            updates.append(update)
        return update

    def list_work_updates(self, work_item_id: str) -> list[WorkUpdateRecord]:
        return list(self.work_updates.get(work_item_id, []))

    def create_work_request(self, request: WorkRequestRecord) -> WorkRequestRecord:
        requests = self.work_requests.setdefault(request.work_item_id, [])
        requests = [existing for existing in requests if existing.request_id != request.request_id] + [request]
        requests.sort(key=lambda item: item.created_at)
        self.work_requests[request.work_item_id] = requests
        return request

    def list_work_requests(self, work_item_id: str) -> list[WorkRequestRecord]:
        return list(self.work_requests.get(work_item_id, []))

    def append_work_event(self, event: WorkEventRecord) -> WorkEventRecord:
        events = self.work_events.setdefault(event.work_item_id, [])
        events = [existing for existing in events if existing.event_id != event.event_id] + [event]
        events.sort(key=lambda item: item.created_at)
        self.work_events[event.work_item_id] = events
        return event

    def list_work_events(self, work_item_id: str) -> list[WorkEventRecord]:
        return list(self.work_events.get(work_item_id, []))

    def upsert_worker_status_view(self, view: WorkerStatusViewRecord) -> WorkerStatusViewRecord:
        self.worker_status_views[view.work_item_id] = view
        return view

    def get_worker_status_view(self, work_item_id: str) -> WorkerStatusViewRecord | None:
        return self.worker_status_views.get(work_item_id)

    def upsert_transcript_session(self, session: TranscriptSessionRecord) -> TranscriptSessionRecord:
        self.transcript_sessions[session.session_id] = session
        return session

    def get_transcript_session(self, session_id: str) -> TranscriptSessionRecord | None:
        return self.transcript_sessions.get(session_id)

    def list_transcript_sessions(self, work_item_id: str) -> list[TranscriptSessionRecord]:
        return sorted(
            [session for session in self.transcript_sessions.values() if session.work_item_id == work_item_id],
            key=lambda item: (item.started_at, item.session_id),
        )

    def append_transcript_event(self, event: TranscriptEventRecord) -> TranscriptEventRecord:
        events = self.transcript_events.setdefault(event.session_id, [])
        if all(existing.event_id != event.event_id for existing in events):
            events.append(event)
            events.sort(key=lambda item: (item.sequence_no, item.occurred_at, item.event_id))
        return event

    def list_transcript_events(self, session_id: str) -> list[TranscriptEventRecord]:
        return list(self.transcript_events.get(session_id, []))

    def upsert_transcript_hot_body(self, hot_body: TranscriptHotBodyRecord) -> TranscriptHotBodyRecord:
        self.transcript_hot_bodies[hot_body.session_id] = hot_body
        return hot_body

    def get_transcript_hot_body(self, session_id: str) -> TranscriptHotBodyRecord | None:
        return self.transcript_hot_bodies.get(session_id)

    def append_transcript_legacy_index(self, legacy_index: TranscriptLegacyIndexRecord) -> TranscriptLegacyIndexRecord:
        legacy_indexes = self.transcript_legacy_indexes.setdefault(legacy_index.work_item_id, [])
        if all(existing.legacy_index_id != legacy_index.legacy_index_id for existing in legacy_indexes):
            legacy_indexes.append(legacy_index)
            legacy_indexes.sort(key=lambda item: (item.captured_at, item.legacy_index_id))
        return legacy_index

    def list_transcript_legacy_indexes(self, work_item_id: str) -> list[TranscriptLegacyIndexRecord]:
        return list(self.transcript_legacy_indexes.get(work_item_id, []))
