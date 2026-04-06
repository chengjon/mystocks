from __future__ import annotations

import hashlib
from datetime import datetime, timedelta
from typing import Any, Callable
from uuid import uuid4

from src.services.maestro.collab.authz import ActorIdentity, CoordinationAuthorizer
from src.services.maestro.collab.transcript_archive import (
    TranscriptArchiveBackend,
    TranscriptArchiveRetryableError,
)
from src.services.maestro.collab.store.base import CollaborationStore
from src.services.maestro.collab.store.models import (
    TranscriptEventRecord,
    TranscriptHotBodyRecord,
    TranscriptLegacyIndexRecord,
    TranscriptSessionRecord,
    WorkItemRecord,
)

HOT_TRANSCRIPT_RETENTION_DAYS = 90


class TranscriptLedgerService:
    def __init__(
        self,
        store: CollaborationStore,
        *,
        authorizer: CoordinationAuthorizer | None = None,
        archive_backend: TranscriptArchiveBackend | None = None,
        event_id_factory: Callable[[], str] | None = None,
        hot_retention_days: int = HOT_TRANSCRIPT_RETENTION_DAYS,
    ) -> None:
        self._store = store
        self._authorizer = authorizer or CoordinationAuthorizer()
        self._archive_backend = archive_backend
        self._event_id_factory = event_id_factory or _event_id
        self._hot_retention_days = hot_retention_days

    def start_session(self, actor: ActorIdentity, session: TranscriptSessionRecord) -> TranscriptSessionRecord:
        work_item = self._require_work_item(session.work_item_id)
        self._authorizer.require_can_append_transcript(actor, work_item, actor_cli=session.actor_cli)
        if session.closed_at is not None:
            raise ValueError(f"Transcript session must start open: {session.session_id}")
        if self._store.get_transcript_session(session.session_id) is not None:
            raise ValueError(f"Transcript session already exists: {session.session_id}")

        stored = self._store.upsert_transcript_session(session)
        self._store.append_transcript_event(
            TranscriptEventRecord(
                work_item_id=session.work_item_id,
                session_id=session.session_id,
                event_id=f"transcript-{self._event_id_factory()}",
                event_type="transcript.session_started",
                sequence_no=1,
                occurred_at=session.started_at,
                payload={
                    "actor_cli": session.actor_cli,
                    "branch": session.branch,
                    "transcript_kind": session.transcript_kind,
                    "archive_policy_version": session.archive_policy_version,
                },
            )
        )
        return stored

    def append_block(
        self,
        actor: ActorIdentity,
        *,
        session_id: str,
        event_id: str,
        occurred_at: datetime,
        content: str,
        payload: dict[str, Any] | None = None,
    ) -> TranscriptEventRecord:
        session = self._require_open_session(session_id)
        work_item = self._require_work_item(session.work_item_id)
        self._authorizer.require_can_append_transcript(actor, work_item, actor_cli=session.actor_cli)

        event = TranscriptEventRecord(
            work_item_id=session.work_item_id,
            session_id=session.session_id,
            event_id=event_id,
            event_type="transcript.block_appended",
            sequence_no=self._next_sequence_no(session.session_id),
            occurred_at=occurred_at,
            payload={"content": content, **(payload or {})},
        )
        stored = self._store.append_transcript_event(event)
        self._refresh_hot_body(session, stored, content)
        return stored

    def close_session(
        self,
        actor: ActorIdentity,
        *,
        session_id: str,
        event_id: str,
        occurred_at: datetime,
        payload: dict[str, Any] | None = None,
    ) -> TranscriptSessionRecord:
        session = self._require_open_session(session_id)
        work_item = self._require_work_item(session.work_item_id)
        self._authorizer.require_can_append_transcript(actor, work_item, actor_cli=session.actor_cli)

        closed = session.model_copy(update={"closed_at": occurred_at})
        self._store.upsert_transcript_session(closed)
        self._append_event(
            session=closed,
            event_id=event_id,
            event_type="transcript.session_closed",
            occurred_at=occurred_at,
            payload=payload or {},
        )
        self._archive_after_close(closed, occurred_at=occurred_at)
        return closed

    def record_compensation(
        self,
        actor: ActorIdentity,
        *,
        session_id: str,
        event_id: str,
        occurred_at: datetime,
        target_event_id: str,
        payload: dict[str, Any] | None = None,
    ) -> TranscriptEventRecord:
        session = self._require_session(session_id)
        work_item = self._require_work_item(session.work_item_id)
        self._authorizer.require_can_append_transcript(actor, work_item, actor_cli=session.actor_cli)
        self._require_session_event(session_id, target_event_id)

        event = TranscriptEventRecord(
            work_item_id=session.work_item_id,
            session_id=session.session_id,
            event_id=event_id,
            event_type="transcript.compensation_recorded",
            sequence_no=self._next_sequence_no(session.session_id),
            occurred_at=occurred_at,
            payload={"compensates_event_id": target_event_id, **(payload or {})},
        )
        return self._store.append_transcript_event(event)

    def get_session(self, actor: ActorIdentity, session_id: str) -> TranscriptSessionRecord | None:
        session = self._store.get_transcript_session(session_id)
        if session is None:
            return None
        work_item = self._require_work_item(session.work_item_id)
        self._authorizer.require_can_export_transcript(actor, work_item)
        return session

    def list_work_item_sessions(self, actor: ActorIdentity, work_item_id: str) -> list[TranscriptSessionRecord]:
        work_item = self._require_work_item(work_item_id)
        self._authorizer.require_can_export_transcript(actor, work_item)
        return self._store.list_transcript_sessions(work_item_id)

    def list_session_events(self, actor: ActorIdentity, session_id: str) -> list[TranscriptEventRecord]:
        session = self._require_session(session_id)
        work_item = self._require_work_item(session.work_item_id)
        self._authorizer.require_can_export_transcript(actor, work_item)
        return self._store.list_transcript_events(session_id)

    def get_hot_body(self, actor: ActorIdentity, session_id: str) -> TranscriptHotBodyRecord | None:
        session = self._require_session(session_id)
        work_item = self._require_work_item(session.work_item_id)
        self._authorizer.require_can_export_transcript(actor, work_item)
        return self._store.get_transcript_hot_body(session_id)

    def index_legacy_record(
        self,
        actor: ActorIdentity,
        legacy_index: TranscriptLegacyIndexRecord,
    ) -> TranscriptLegacyIndexRecord:
        self._require_work_item(legacy_index.work_item_id)
        self._authorizer.require_can_upsert_work_item(actor)
        return self._store.append_transcript_legacy_index(legacy_index)

    def list_legacy_indexes(self, actor: ActorIdentity, work_item_id: str) -> list[TranscriptLegacyIndexRecord]:
        work_item = self._require_work_item(work_item_id)
        self._authorizer.require_can_export_transcript(actor, work_item)
        return self._store.list_transcript_legacy_indexes(work_item_id)

    def expire_hot_body(
        self,
        actor: ActorIdentity,
        *,
        session_id: str,
        occurred_at: datetime,
    ) -> TranscriptEventRecord:
        self._authorizer.require_can_upsert_work_item(actor)
        session = self._require_session(session_id)
        hot_body = self._store.get_transcript_hot_body(session_id)
        if hot_body is None:
            raise KeyError(f"Unknown hot transcript body: {session_id}")
        if occurred_at < hot_body.available_until:
            raise ValueError(f"Transcript hot body is not yet eligible for expiry: {session_id}")
        archive_locator = self._latest_archive_locator(session_id)
        if not archive_locator:
            raise ValueError(f"Transcript hot body cannot expire without archive reference: {session_id}")
        return self._append_event(
            session=session,
            event_id=f"tevt-{self._event_id_factory()}",
            event_type="transcript.hot_body_expired",
            occurred_at=occurred_at,
            payload={
                "available_until": hot_body.available_until.isoformat(),
                "hot_body_event_id": hot_body.event_id,
                "archive_locator": archive_locator,
            },
        )

    def _require_work_item(self, work_item_id: str) -> WorkItemRecord:
        work_item = self._store.get_work_item(work_item_id)
        if work_item is None:
            raise KeyError(f"Unknown work item: {work_item_id}")
        return work_item

    def _require_session(self, session_id: str) -> TranscriptSessionRecord:
        session = self._store.get_transcript_session(session_id)
        if session is None:
            raise KeyError(f"Unknown transcript session: {session_id}")
        return session

    def _require_open_session(self, session_id: str) -> TranscriptSessionRecord:
        session = self._require_session(session_id)
        if session.closed_at is not None:
            raise ValueError(f"Transcript session is already closed: {session_id}")
        return session

    def _require_session_event(self, session_id: str, event_id: str) -> TranscriptEventRecord:
        for event in self._store.list_transcript_events(session_id):
            if event.event_id == event_id:
                return event
        raise KeyError(f"Unknown transcript event: {session_id}/{event_id}")

    def _next_sequence_no(self, session_id: str) -> int:
        events = self._store.list_transcript_events(session_id)
        if not events:
            return 1
        return events[-1].sequence_no + 1

    def _append_event(
        self,
        *,
        session: TranscriptSessionRecord,
        event_id: str,
        event_type: str,
        occurred_at: datetime,
        payload: dict[str, Any],
    ) -> TranscriptEventRecord:
        return self._store.append_transcript_event(
            TranscriptEventRecord(
                work_item_id=session.work_item_id,
                session_id=session.session_id,
                event_id=event_id,
                event_type=event_type,
                sequence_no=self._next_sequence_no(session.session_id),
                occurred_at=occurred_at,
                payload=payload,
            )
        )

    def _archive_after_close(self, session: TranscriptSessionRecord, *, occurred_at: datetime) -> None:
        hot_body = self._store.get_transcript_hot_body(session.session_id)
        if self._archive_backend is None or hot_body is None or not hot_body.content:
            return

        self._append_event(
            session=session,
            event_id=f"tevt-{self._event_id_factory()}",
            event_type="transcript.archive_pending",
            occurred_at=occurred_at,
            payload={"reason": "session_closed"},
        )

        try:
            chunks = [
                str(event.payload["content"])
                for event in self._store.list_transcript_events(session.session_id)
                if event.event_type == "transcript.block_appended" and "content" in event.payload
            ]
            result = self._archive_backend.seal_session(
                session.session_id,
                chunks=chunks,
                metadata={
                    "work_item_id": session.work_item_id,
                    "actor_cli": session.actor_cli,
                    "branch": session.branch,
                    "transcript_kind": session.transcript_kind,
                    "started_at": session.started_at,
                    "closed_at": session.closed_at,
                    "archive_policy_version": session.archive_policy_version,
                },
            )
        except TranscriptArchiveRetryableError as exc:
            self._append_event(
                session=session,
                event_id=f"tevt-{self._event_id_factory()}",
                event_type="transcript.archive_write_failed",
                occurred_at=occurred_at,
                payload={"error": str(exc)},
            )
            return

        self._append_event(
            session=session,
            event_id=f"tevt-{self._event_id_factory()}",
            event_type="transcript.body_archived",
            occurred_at=occurred_at,
            payload={
                "archive_locator": result.archive_locator,
                "manifest_locator": result.manifest_locator,
                "checksum": result.checksum,
                "chunk_count": result.chunk_count,
                "byte_count": result.byte_count,
                "sealed_at": result.sealed_at.isoformat(),
                "backend_kind": result.backend_kind,
            },
        )
        self._mark_hot_body_purge_ready(session.session_id)

    def _refresh_hot_body(
        self,
        session: TranscriptSessionRecord,
        event: TranscriptEventRecord,
        content: str,
    ) -> TranscriptHotBodyRecord:
        existing = self._store.get_transcript_hot_body(session.session_id)
        if existing is None or not existing.content:
            full_content = content
        else:
            full_content = f"{existing.content}\n{content}"

        checksum = f"sha256:{hashlib.sha256(full_content.encode('utf-8')).hexdigest()}"
        hot_body = TranscriptHotBodyRecord(
            body_id=f"hot-{session.session_id}",
            session_id=session.session_id,
            event_id=event.event_id,
            content=full_content,
            checksum=checksum,
            available_until=event.occurred_at + timedelta(days=self._hot_retention_days),
            purge_after=existing.purge_after if existing is not None else None,
        )
        return self._store.upsert_transcript_hot_body(hot_body)

    def _mark_hot_body_purge_ready(self, session_id: str) -> TranscriptHotBodyRecord | None:
        hot_body = self._store.get_transcript_hot_body(session_id)
        if hot_body is None:
            return None
        purge_ready = hot_body.model_copy(update={"purge_after": hot_body.available_until})
        return self._store.upsert_transcript_hot_body(purge_ready)

    def _latest_archive_locator(self, session_id: str) -> str | None:
        locator: str | None = None
        for event in self._store.list_transcript_events(session_id):
            if event.event_type == "transcript.body_archived":
                locator = event.payload.get("archive_locator")
            elif event.event_type == "transcript.hot_body_expired":
                locator = event.payload.get("archive_locator") or locator
        return locator


def _event_id() -> str:
    return uuid4().hex
