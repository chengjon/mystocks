from __future__ import annotations

from datetime import UTC, datetime

import pytest

from src.services.maestro.collab.authz.policy import ActorIdentity, AuthorizationError
from src.services.maestro.collab.services.coordination import CoordinationService
from src.services.maestro.collab.store.models import (
    WorkPlanItemRecord,
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


def test_claim_work_item_refreshes_claim_metadata_and_owned_status() -> None:
    store = _InMemoryCollaborationStore()
    service = CoordinationService(store)
    work_item = _work_item(owner_cli="gemini")
    service.upsert_work_item(ActorIdentity(cli_name="main", role="main_cli"), work_item)

    claimed = service.claim_work_item(
        ActorIdentity(cli_name="gemini", role="worker_cli"),
        work_item_id=work_item.work_item_id,
        actor_cli="gemini",
        summary="Accepted task and started execution",
    )

    updated_work_item = store.get_work_item(work_item.work_item_id)
    status_view = store.get_worker_status_view(work_item.work_item_id)

    assert claimed.status == "in_progress"
    assert claimed.details["kind"] == "claim"
    assert updated_work_item is not None
    assert updated_work_item.status == "in_progress"
    assert status_view is not None
    assert status_view.status == "in_progress"
    assert status_view.claimed_by == "gemini"
    assert status_view.claimed_at == claimed.created_at
    assert status_view.latest_update == "Accepted task and started execution"


def test_plan_items_refresh_progress_and_current_focus() -> None:
    store = _InMemoryCollaborationStore()
    service = CoordinationService(store)
    work_item = _work_item(owner_cli="gemini")
    service.upsert_work_item(ActorIdentity(cli_name="main", role="main_cli"), work_item)
    service.claim_work_item(
        ActorIdentity(cli_name="gemini", role="worker_cli"),
        work_item_id=work_item.work_item_id,
        actor_cli="gemini",
        summary="Accepted task",
    )

    first = service.add_plan_item(
        ActorIdentity(cli_name="gemini", role="worker_cli"),
        WorkPlanItemRecord(
            work_item_id=work_item.work_item_id,
            plan_item_id="plan-1",
            title="Inspect current schema",
            order=10,
            status="todo",
            evidence_summary=None,
            updated_at=_ts("2026-03-14T01:11:00Z"),
        ),
    )
    second = service.add_plan_item(
        ActorIdentity(cli_name="gemini", role="worker_cli"),
        WorkPlanItemRecord(
            work_item_id=work_item.work_item_id,
            plan_item_id="plan-2",
            title="Implement board aggregation",
            order=20,
            status="todo",
            evidence_summary=None,
            updated_at=_ts("2026-03-14T01:12:00Z"),
        ),
    )

    initial_status_view = store.get_worker_status_view(work_item.work_item_id)
    assert initial_status_view is not None
    assert initial_status_view.plan_total == 2
    assert initial_status_view.plan_done == 0
    assert initial_status_view.progress_percent == 0
    assert initial_status_view.current_focus == first.title

    service.mark_plan_item(
        ActorIdentity(cli_name="gemini", role="worker_cli"),
        work_item_id=work_item.work_item_id,
        plan_item_id=first.plan_item_id,
        actor_cli="gemini",
        status="done",
        evidence_summary="Schema reviewed",
    )

    completed_status_view = store.get_worker_status_view(work_item.work_item_id)
    assert completed_status_view is not None
    assert completed_status_view.plan_total == 2
    assert completed_status_view.plan_done == 1
    assert completed_status_view.progress_percent == 50
    assert completed_status_view.current_focus == second.title


def test_submit_work_item_records_delivery_metadata_and_ready_for_review() -> None:
    store = _InMemoryCollaborationStore()
    service = CoordinationService(store)
    work_item = _work_item(owner_cli="gemini")
    service.upsert_work_item(ActorIdentity(cli_name="main", role="main_cli"), work_item)
    service.claim_work_item(
        ActorIdentity(cli_name="gemini", role="worker_cli"),
        work_item_id=work_item.work_item_id,
        actor_cli="gemini",
        summary="Accepted task",
    )

    submitted = service.submit_work_item(
        ActorIdentity(cli_name="gemini", role="worker_cli"),
        work_item_id=work_item.work_item_id,
        actor_cli="gemini",
        summary="Ready for review",
        commit_sha="abc123def",
        branch="feat/mongo-worker-lifecycle",
        remote="origin",
        verification_summary="pytest tests/unit/maestro_collab -q",
    )

    updated_work_item = store.get_work_item(work_item.work_item_id)
    status_view = store.get_worker_status_view(work_item.work_item_id)

    assert submitted.status == "ready_for_review"
    assert submitted.details["kind"] == "submit"
    assert submitted.details["commit_sha"] == "abc123def"
    assert updated_work_item is not None
    assert updated_work_item.status == "ready_for_review"
    assert status_view is not None
    assert status_view.status == "ready_for_review"
    assert status_view.submitted_at == submitted.created_at
    assert status_view.delivery_commit == "abc123def"
    assert status_view.delivery_branch == "feat/mongo-worker-lifecycle"


def test_non_owner_cannot_claim_plan_or_submit_work_item() -> None:
    store = _InMemoryCollaborationStore()
    service = CoordinationService(store)
    work_item = _work_item(owner_cli="gemini")
    service.upsert_work_item(ActorIdentity(cli_name="main", role="main_cli"), work_item)

    with pytest.raises(AuthorizationError):
        service.claim_work_item(
            ActorIdentity(cli_name="codex", role="worker_cli"),
            work_item_id=work_item.work_item_id,
            actor_cli="codex",
            summary="Trying to steal the task",
        )

    with pytest.raises(AuthorizationError):
        service.submit_work_item(
            ActorIdentity(cli_name="codex", role="worker_cli"),
            work_item_id=work_item.work_item_id,
            actor_cli="codex",
            summary="Illegitimate submit",
            commit_sha="badc0de",
            branch="feat/invalid",
            remote="origin",
            verification_summary="none",
        )


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
        self.work_plan_items: dict[str, list[WorkPlanItemRecord]] = {}
        self.work_requests: dict[str, list[WorkRequestRecord]] = {}
        self.work_events: dict[str, list[WorkEventRecord]] = {}
        self.worker_status_views: dict[str, WorkerStatusViewRecord] = {}

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

    def upsert_work_plan_item(self, plan_item: WorkPlanItemRecord) -> WorkPlanItemRecord:
        items = self.work_plan_items.setdefault(plan_item.work_item_id, [])
        items = [existing for existing in items if existing.plan_item_id != plan_item.plan_item_id] + [plan_item]
        items.sort(key=lambda item: (item.order, item.updated_at))
        self.work_plan_items[plan_item.work_item_id] = items
        return plan_item

    def list_work_plan_items(self, work_item_id: str) -> list[WorkPlanItemRecord]:
        return list(self.work_plan_items.get(work_item_id, []))

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
