from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from src.services.maestro.collab.store.models import WorkItemRecord

ActorRole = Literal["main_cli", "worker_cli", "system"]


class AuthorizationError(PermissionError):
    """Raised when an actor crosses the coordination scope boundary."""


@dataclass(frozen=True)
class ActorIdentity:
    cli_name: str
    role: ActorRole


class CoordinationAuthorizer:
    def require_can_upsert_work_item(self, actor: ActorIdentity) -> None:
        self._require_main_or_system(actor, action="upsert work item")

    def require_can_view_work_item(self, actor: ActorIdentity, work_item: WorkItemRecord) -> None:
        if actor.role in {"main_cli", "system"}:
            return
        if actor.role == "worker_cli" and actor.cli_name == work_item.owner_cli:
            return
        raise AuthorizationError(f"{actor.cli_name} cannot view work item {work_item.work_item_id}")

    def require_can_append_update(self, actor: ActorIdentity, work_item: WorkItemRecord, *, actor_cli: str) -> None:
        self._require_owned_worker_write(
            actor,
            work_item,
            actor_cli=actor_cli,
            action="append update",
        )

    def require_can_create_request(self, actor: ActorIdentity, work_item: WorkItemRecord, *, actor_cli: str) -> None:
        self._require_owned_worker_write(
            actor,
            work_item,
            actor_cli=actor_cli,
            action="create request",
        )

    def require_can_append_transcript(self, actor: ActorIdentity, work_item: WorkItemRecord, *, actor_cli: str) -> None:
        self._require_owned_worker_write(
            actor,
            work_item,
            actor_cli=actor_cli,
            action="append transcript",
        )

    def require_can_export_transcript(self, actor: ActorIdentity, work_item: WorkItemRecord) -> None:
        self.require_can_view_work_item(actor, work_item)

    def require_can_upsert_status_view(self, actor: ActorIdentity) -> None:
        self._require_main_or_system(actor, action="upsert worker status view")

    @staticmethod
    def _require_owned_worker_write(
        actor: ActorIdentity,
        work_item: WorkItemRecord,
        *,
        actor_cli: str,
        action: str,
    ) -> None:
        if actor.role in {"main_cli", "system"}:
            return
        if actor.role == "worker_cli" and actor.cli_name == work_item.owner_cli and actor.cli_name == actor_cli:
            return
        raise AuthorizationError(f"{actor.cli_name} cannot {action} for work item {work_item.work_item_id}")

    @staticmethod
    def _require_main_or_system(actor: ActorIdentity, *, action: str) -> None:
        if actor.role in {"main_cli", "system"}:
            return
        raise AuthorizationError(f"{actor.cli_name} cannot {action}")
