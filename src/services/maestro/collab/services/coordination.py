from __future__ import annotations

from datetime import UTC, datetime
from typing import Callable
from uuid import uuid4

from src.services.maestro.collab.authz.policy import ActorIdentity, CoordinationAuthorizer
from src.services.maestro.collab.store.base import CollaborationStore
from src.services.maestro.collab.store.models import (
    WorkerStatusViewRecord,
    WorkEventRecord,
    WorkItemRecord,
    WorkRequestRecord,
    WorkUpdateRecord,
)


class CoordinationService:
    def __init__(
        self,
        store: CollaborationStore,
        *,
        authorizer: CoordinationAuthorizer | None = None,
        clock: Callable[[], datetime] | None = None,
        event_id_factory: Callable[[], str] | None = None,
    ) -> None:
        self._store = store
        self._authorizer = authorizer or CoordinationAuthorizer()
        self._clock = clock or _utcnow
        self._event_id_factory = event_id_factory or _event_id

    def upsert_work_item(self, actor: ActorIdentity, work_item: WorkItemRecord) -> WorkItemRecord:
        self._authorizer.require_can_upsert_work_item(actor)
        stored = self._store.upsert_work_item(work_item)
        self._refresh_status_view(work_item.work_item_id)
        self._append_audit_event(
            actor=actor,
            work_item_id=work_item.work_item_id,
            branch=work_item.branch,
            action="upsert_work_item",
            event_type="audit.work_item_upserted",
        )
        return stored

    def get_work_item(self, actor: ActorIdentity, work_item_id: str) -> WorkItemRecord | None:
        work_item = self._store.get_work_item(work_item_id)
        if work_item is None:
            return None
        self._authorizer.require_can_view_work_item(actor, work_item)
        return work_item

    def list_work_items(self, actor: ActorIdentity) -> list[WorkItemRecord]:
        work_items = self._store.list_work_items()
        if actor.role in {"main_cli", "system"}:
            return work_items
        return [work_item for work_item in work_items if work_item.owner_cli == actor.cli_name]

    def append_work_update(self, actor: ActorIdentity, update: WorkUpdateRecord) -> WorkUpdateRecord:
        work_item = self._require_work_item(update.work_item_id)
        self._authorizer.require_can_append_update(actor, work_item, actor_cli=update.actor_cli)
        stored = self._store.append_work_update(update)
        self._refresh_status_view(work_item.work_item_id)
        self._append_audit_event(
            actor=actor,
            work_item_id=work_item.work_item_id,
            branch=work_item.branch,
            action="append_work_update",
            event_type="audit.work_update_appended",
        )
        return stored

    def create_work_request(self, actor: ActorIdentity, request: WorkRequestRecord) -> WorkRequestRecord:
        work_item = self._require_work_item(request.work_item_id)
        self._authorizer.require_can_create_request(actor, work_item, actor_cli=request.actor_cli)
        stored = self._store.create_work_request(request)
        self._refresh_status_view(work_item.work_item_id)
        self._append_audit_event(
            actor=actor,
            work_item_id=work_item.work_item_id,
            branch=work_item.branch,
            action="create_work_request",
            event_type="audit.work_request_created",
        )
        return stored

    def review_work_request(
        self,
        actor: ActorIdentity,
        *,
        work_item_id: str,
        request_id: str,
        reviewed_by: str,
        status: str,
    ) -> WorkRequestRecord:
        work_item = self._require_work_item(work_item_id)
        self._authorizer.require_can_upsert_work_item(actor)
        request = self._require_work_request(work_item_id, request_id)
        reviewed = request.model_copy(update={"status": status, "reviewed_by": reviewed_by, "reviewed_at": self._clock()})
        stored = self._store.create_work_request(reviewed)
        self._refresh_status_view(work_item_id)
        self._append_audit_event(
            actor=actor,
            work_item_id=work_item_id,
            branch=work_item.branch,
            action="review_work_request",
            event_type="audit.work_request_reviewed",
        )
        return stored

    def upsert_worker_status_view(self, actor: ActorIdentity, view: WorkerStatusViewRecord) -> WorkerStatusViewRecord:
        self._authorizer.require_can_upsert_status_view(actor)
        stored = self._store.upsert_worker_status_view(view)
        self._append_audit_event(
            actor=actor,
            work_item_id=view.work_item_id,
            branch=view.branch,
            action="upsert_worker_status_view",
            event_type="audit.worker_status_view_upserted",
        )
        return stored

    def _require_work_item(self, work_item_id: str) -> WorkItemRecord:
        work_item = self._store.get_work_item(work_item_id)
        if work_item is None:
            raise KeyError(f"Unknown work item: {work_item_id}")
        return work_item

    def _require_work_request(self, work_item_id: str, request_id: str) -> WorkRequestRecord:
        for request in self._store.list_work_requests(work_item_id):
            if request.request_id == request_id:
                return request
        raise KeyError(f"Unknown work request: {work_item_id}/{request_id}")

    def _refresh_status_view(self, work_item_id: str) -> None:
        work_item = self._require_work_item(work_item_id)
        updates = self._store.list_work_updates(work_item_id)
        requests = self._store.list_work_requests(work_item_id)
        latest_update = updates[-1].summary if updates else None
        derived_status = updates[-1].status if updates else work_item.status
        has_pending_request = any(request.status == "pending" for request in requests)

        self._store.upsert_worker_status_view(
            WorkerStatusViewRecord(
                work_item_id=work_item.work_item_id,
                branch=work_item.branch,
                owner_cli=work_item.owner_cli,
                status=derived_status,
                latest_update=latest_update,
                blocker=None,
                has_pending_request=has_pending_request,
                updated_at=self._clock(),
            )
        )

    def _append_audit_event(
        self,
        *,
        actor: ActorIdentity,
        work_item_id: str,
        branch: str,
        action: str,
        event_type: str,
    ) -> None:
        now = self._clock()
        self._store.append_work_event(
            WorkEventRecord(
                work_item_id=work_item_id,
                event_id=f"audit-{self._event_id_factory()}",
                actor_cli=actor.cli_name,
                event_type=event_type,
                payload={
                    "actor_cli": actor.cli_name,
                    "branch": branch,
                    "work_item_id": work_item_id,
                    "action": action,
                    "timestamp": now.isoformat(),
                },
                created_at=now,
            )
        )


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _event_id() -> str:
    return uuid4().hex
