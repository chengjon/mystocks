from __future__ import annotations

from datetime import UTC, datetime
from math import floor
from typing import Callable
from uuid import uuid4

from src.services.maestro.collab.authz.policy import ActorIdentity, CoordinationAuthorizer
from src.services.maestro.collab.store.base import CollaborationStore
from src.services.maestro.collab.store.models import (
    WorkPlanItemRecord,
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

    def claim_work_item(
        self,
        actor: ActorIdentity,
        *,
        work_item_id: str,
        actor_cli: str,
        summary: str,
    ) -> WorkUpdateRecord:
        work_item = self._require_work_item(work_item_id)
        self._authorizer.require_can_claim_work_item(actor, work_item, actor_cli=actor_cli)
        now = self._clock()
        self._store.upsert_work_item(work_item.model_copy(update={"status": "in_progress", "updated_at": now}))
        update = WorkUpdateRecord(
            work_item_id=work_item_id,
            update_id=f"upd-{self._event_id_factory()}",
            actor_cli=actor_cli,
            status="in_progress",
            summary=summary,
            details={"kind": "claim"},
            created_at=now,
        )
        stored = self._store.append_work_update(update)
        self._refresh_status_view(work_item_id)
        self._append_audit_event(
            actor=actor,
            work_item_id=work_item_id,
            branch=work_item.branch,
            action="claim_work_item",
            event_type="audit.work_item_claimed",
        )
        return stored

    def add_plan_item(self, actor: ActorIdentity, plan_item: WorkPlanItemRecord) -> WorkPlanItemRecord:
        work_item = self._require_work_item(plan_item.work_item_id)
        self._authorizer.require_can_manage_plan_item(actor, work_item, actor_cli=actor.cli_name)
        stored = self._store.upsert_work_plan_item(plan_item)
        self._refresh_status_view(plan_item.work_item_id)
        self._append_audit_event(
            actor=actor,
            work_item_id=plan_item.work_item_id,
            branch=work_item.branch,
            action="add_plan_item",
            event_type="audit.work_plan_item_upserted",
        )
        return stored

    def mark_plan_item(
        self,
        actor: ActorIdentity,
        *,
        work_item_id: str,
        plan_item_id: str,
        actor_cli: str,
        status: str,
        evidence_summary: str | None,
    ) -> WorkPlanItemRecord:
        work_item = self._require_work_item(work_item_id)
        self._authorizer.require_can_manage_plan_item(actor, work_item, actor_cli=actor_cli)
        existing = self._require_plan_item(work_item_id, plan_item_id)
        updated = existing.model_copy(
            update={"status": status, "evidence_summary": evidence_summary, "updated_at": self._clock()}
        )
        stored = self._store.upsert_work_plan_item(updated)
        self._refresh_status_view(work_item_id)
        self._append_audit_event(
            actor=actor,
            work_item_id=work_item_id,
            branch=work_item.branch,
            action="mark_plan_item",
            event_type="audit.work_plan_item_marked",
        )
        return stored

    def list_work_plan_items(self, actor: ActorIdentity, work_item_id: str) -> list[WorkPlanItemRecord]:
        work_item = self._require_work_item(work_item_id)
        self._authorizer.require_can_view_work_item(actor, work_item)
        return self._store.list_work_plan_items(work_item_id)

    def submit_work_item(
        self,
        actor: ActorIdentity,
        *,
        work_item_id: str,
        actor_cli: str,
        summary: str,
        commit_sha: str,
        branch: str,
        remote: str | None,
        verification_summary: str | None,
    ) -> WorkUpdateRecord:
        work_item = self._require_work_item(work_item_id)
        self._authorizer.require_can_submit_work_item(actor, work_item, actor_cli=actor_cli)
        now = self._clock()
        self._store.upsert_work_item(work_item.model_copy(update={"status": "ready_for_review", "updated_at": now}))
        update = WorkUpdateRecord(
            work_item_id=work_item_id,
            update_id=f"upd-{self._event_id_factory()}",
            actor_cli=actor_cli,
            status="ready_for_review",
            summary=summary,
            details={
                "kind": "submit",
                "commit_sha": commit_sha,
                "branch": branch,
                "remote": remote,
                "verification_summary": verification_summary,
            },
            created_at=now,
        )
        stored = self._store.append_work_update(update)
        self._refresh_status_view(work_item_id)
        self._append_audit_event(
            actor=actor,
            work_item_id=work_item_id,
            branch=work_item.branch,
            action="submit_work_item",
            event_type="audit.work_item_submitted",
        )
        return stored

    def get_work_item_snapshot(self, actor: ActorIdentity, work_item_id: str, *, include_plan: bool = False) -> dict:
        work_item = self.get_work_item(actor, work_item_id)
        if work_item is None:
            raise KeyError(f"Unknown work item: {work_item_id}")

        status_view = self._store.get_worker_status_view(work_item_id)
        if status_view is None:
            status_view = self._build_status_view(work_item)

        payload = {
            "work_item": work_item.model_dump(mode="json"),
            "status_view": status_view.model_dump(mode="json"),
        }
        if include_plan:
            payload["plan_items"] = [
                plan_item.model_dump(mode="json") for plan_item in self.list_work_plan_items(actor, work_item_id)
            ]
        return payload

    def list_work_board_rows(self, actor: ActorIdentity, *, active_only: bool = False) -> list[dict]:
        rows: list[dict] = []
        for work_item in self.list_work_items(actor):
            status_view = self._store.get_worker_status_view(work_item.work_item_id)
            if status_view is None:
                status_view = self._build_status_view(work_item)
            row = {
                "work_item_id": work_item.work_item_id,
                "branch": work_item.branch,
                "owner_cli": work_item.owner_cli,
                "status": status_view.status,
                "claimed_by": status_view.claimed_by,
                "claimed_at": status_view.claimed_at,
                "plan_total": status_view.plan_total,
                "plan_done": status_view.plan_done,
                "progress_percent": status_view.progress_percent,
                "current_focus": status_view.current_focus,
                "has_pending_request": status_view.has_pending_request,
                "blocker": status_view.blocker,
                "submitted_at": status_view.submitted_at,
                "delivery_commit": status_view.delivery_commit,
                "delivery_branch": status_view.delivery_branch,
                "latest_update": status_view.latest_update,
                "updated_at": status_view.updated_at,
            }
            if active_only and row["status"] in {"verified", "merged", "archived"}:
                continue
            rows.append(row)
        return rows

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

    def _require_plan_item(self, work_item_id: str, plan_item_id: str) -> WorkPlanItemRecord:
        for plan_item in self._store.list_work_plan_items(work_item_id):
            if plan_item.plan_item_id == plan_item_id:
                return plan_item
        raise KeyError(f"Unknown work plan item: {work_item_id}/{plan_item_id}")

    def _refresh_status_view(self, work_item_id: str) -> None:
        work_item = self._require_work_item(work_item_id)
        self._store.upsert_worker_status_view(self._build_status_view(work_item))

    def _build_status_view(self, work_item: WorkItemRecord) -> WorkerStatusViewRecord:
        updates = self._store.list_work_updates(work_item.work_item_id)
        plan_items = self._store.list_work_plan_items(work_item.work_item_id)
        requests = self._store.list_work_requests(work_item.work_item_id)

        latest_update = updates[-1].summary if updates else None
        derived_status = updates[-1].status if updates else work_item.status
        has_pending_request = any(request.status == "pending" for request in requests)

        claim_update = next((update for update in reversed(updates) if update.details.get("kind") == "claim"), None)
        submit_update = next((update for update in reversed(updates) if update.details.get("kind") == "submit"), None)

        sorted_plan_items = sorted(plan_items, key=lambda item: (item.order, item.updated_at))
        plan_total = len(sorted_plan_items)
        plan_done = sum(1 for item in sorted_plan_items if item.status == "done")
        progress_percent = floor((plan_done * 100) / plan_total) if plan_total else 0
        current_focus = next((item.title for item in sorted_plan_items if item.status == "doing"), None)
        if current_focus is None:
            current_focus = next((item.title for item in sorted_plan_items if item.status != "done"), None)

        blocked_item = next((item for item in sorted_plan_items if item.status == "blocked"), None)
        latest_pending_request = next((request for request in reversed(requests) if request.status == "pending"), None)
        blocker = None
        if blocked_item is not None:
            blocker = blocked_item.evidence_summary or blocked_item.title
        elif latest_pending_request is not None:
            blocker = latest_pending_request.summary

        return WorkerStatusViewRecord(
            work_item_id=work_item.work_item_id,
            branch=work_item.branch,
            owner_cli=work_item.owner_cli,
            status=derived_status,
            latest_update=latest_update,
            blocker=blocker,
            has_pending_request=has_pending_request,
            updated_at=self._clock(),
            claimed_by=claim_update.actor_cli if claim_update is not None else None,
            claimed_at=claim_update.created_at if claim_update is not None else None,
            plan_total=plan_total,
            plan_done=plan_done,
            progress_percent=progress_percent,
            current_focus=current_focus,
            submitted_at=submit_update.created_at if submit_update is not None else None,
            delivery_commit=submit_update.details.get("commit_sha") if submit_update is not None else None,
            delivery_branch=submit_update.details.get("branch") if submit_update is not None else None,
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
