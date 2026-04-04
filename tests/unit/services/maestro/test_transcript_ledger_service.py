from __future__ import annotations

from datetime import timedelta

import pytest

from src.services.maestro.collab.authz import ActorIdentity, AuthorizationError
from src.services.maestro.collab.transcript_archive import TranscriptArchiveRetryableError
from src.services.maestro.collab.services.transcript_ledger import TranscriptLedgerService
from src.services.maestro.collab.store.models import TranscriptSessionRecord
from tests.unit.maestro_collab.test_coordination_service import _InMemoryCollaborationStore, _ts, _work_item


def test_transcript_ledger_rejects_ingest_without_work_item() -> None:
    store = _InMemoryCollaborationStore()
    service = TranscriptLedgerService(store)

    with pytest.raises(KeyError):
        service.start_session(ActorIdentity(cli_name="gemini", role="worker_cli"), _session(work_item_id="MT-missing"))

    assert store.get_transcript_session("sess-200") is None
    assert store.list_transcript_events("sess-200") == []


def test_transcript_ledger_allows_session_started_only_once_per_session_id() -> None:
    store = _InMemoryCollaborationStore()
    store.upsert_work_item(_work_item(owner_cli="gemini"))
    service = TranscriptLedgerService(store)
    actor = ActorIdentity(cli_name="gemini", role="worker_cli")

    started = service.start_session(actor, _session())

    assert started == _session()
    events = service.list_session_events(actor, "sess-200")
    assert len(events) == 1
    assert events[0].event_type == "transcript.session_started"
    assert events[0].sequence_no == 1

    with pytest.raises(ValueError, match="already exists"):
        service.start_session(actor, _session())


def test_transcript_ledger_appends_blocks_with_increasing_sequence_numbers() -> None:
    store = _InMemoryCollaborationStore()
    store.upsert_work_item(_work_item(owner_cli="gemini"))
    service = TranscriptLedgerService(store)
    actor = ActorIdentity(cli_name="gemini", role="worker_cli")
    service.start_session(actor, _session())

    first = service.append_block(
        actor,
        session_id="sess-200",
        event_id="tevt-2",
        occurred_at=_ts("2026-04-03T03:05:00Z"),
        content="operator summary",
    )
    second = service.append_block(
        actor,
        session_id="sess-200",
        event_id="tevt-3",
        occurred_at=_ts("2026-04-03T03:06:00Z"),
        content="assistant answer",
    )

    assert (first.sequence_no, second.sequence_no) == (2, 3)
    assert [event.sequence_no for event in service.list_session_events(actor, "sess-200")] == [1, 2, 3]

    hot_body = store.get_transcript_hot_body("sess-200")
    assert hot_body is not None
    assert hot_body.content == "operator summary\nassistant answer"
    assert hot_body.event_id == "tevt-3"
    assert hot_body.available_until == _ts("2026-04-03T03:06:00Z") + timedelta(days=90)
    assert hot_body.purge_after is None


def test_transcript_ledger_rejects_block_append_after_session_closed() -> None:
    store = _InMemoryCollaborationStore()
    store.upsert_work_item(_work_item(owner_cli="gemini"))
    service = TranscriptLedgerService(store)
    actor = ActorIdentity(cli_name="gemini", role="worker_cli")
    service.start_session(actor, _session())
    service.append_block(
        actor,
        session_id="sess-200",
        event_id="tevt-2",
        occurred_at=_ts("2026-04-03T03:05:00Z"),
        content="operator summary",
    )

    closed = service.close_session(
        actor,
        session_id="sess-200",
        event_id="tevt-3",
        occurred_at=_ts("2026-04-03T03:10:00Z"),
    )

    assert closed.closed_at == _ts("2026-04-03T03:10:00Z")
    assert service.list_session_events(actor, "sess-200")[-1].event_type == "transcript.session_closed"

    with pytest.raises(ValueError, match="closed"):
        service.append_block(
            actor,
            session_id="sess-200",
            event_id="tevt-4",
            occurred_at=_ts("2026-04-03T03:11:00Z"),
            content="late block",
        )


def test_transcript_ledger_appends_compensation_without_mutating_prior_events() -> None:
    store = _InMemoryCollaborationStore()
    store.upsert_work_item(_work_item(owner_cli="gemini"))
    service = TranscriptLedgerService(store)
    actor = ActorIdentity(cli_name="gemini", role="worker_cli")
    service.start_session(actor, _session())
    original_event = service.append_block(
        actor,
        session_id="sess-200",
        event_id="tevt-2",
        occurred_at=_ts("2026-04-03T03:05:00Z"),
        content="secret token 123",
    )

    compensation = service.record_compensation(
        actor,
        session_id="sess-200",
        event_id="tevt-3",
        occurred_at=_ts("2026-04-03T03:06:00Z"),
        target_event_id=original_event.event_id,
        payload={"reason": "redact"},
    )

    events = service.list_session_events(actor, "sess-200")
    assert events[1] == original_event
    assert compensation.event_type == "transcript.compensation_recorded"
    assert compensation.payload["compensates_event_id"] == original_event.event_id
    assert events[-1] == compensation


def test_transcript_ledger_reuses_owned_write_scope_for_append() -> None:
    store = _InMemoryCollaborationStore()
    store.upsert_work_item(_work_item(owner_cli="gemini"))
    service = TranscriptLedgerService(store)

    with pytest.raises(AuthorizationError):
        service.start_session(ActorIdentity(cli_name="codex", role="worker_cli"), _session(actor_cli="codex"))


def test_transcript_ledger_reuses_work_item_visibility_for_export() -> None:
    store = _InMemoryCollaborationStore()
    store.upsert_work_item(_work_item(owner_cli="gemini"))
    service = TranscriptLedgerService(store)
    service.start_session(ActorIdentity(cli_name="gemini", role="worker_cli"), _session())

    with pytest.raises(AuthorizationError):
        service.get_session(ActorIdentity(cli_name="codex", role="worker_cli"), "sess-200")

    with pytest.raises(AuthorizationError):
        service.list_session_events(ActorIdentity(cli_name="codex", role="worker_cli"), "sess-200")


def test_transcript_ledger_close_session_records_archive_pending_and_body_archived() -> None:
    store = _InMemoryCollaborationStore()
    store.upsert_work_item(_work_item(owner_cli="gemini"))
    archive_backend = _SuccessfulArchiveBackend()
    service = TranscriptLedgerService(store, archive_backend=archive_backend)
    actor = ActorIdentity(cli_name="gemini", role="worker_cli")
    service.start_session(actor, _session())
    service.append_block(
        actor,
        session_id="sess-200",
        event_id="tevt-2",
        occurred_at=_ts("2026-04-03T03:05:00Z"),
        content="operator summary",
    )

    service.close_session(
        actor,
        session_id="sess-200",
        event_id="tevt-3",
        occurred_at=_ts("2026-04-03T03:10:00Z"),
    )

    event_types = [event.event_type for event in service.list_session_events(actor, "sess-200")]
    assert event_types[-2:] == ["transcript.archive_pending", "transcript.body_archived"]
    assert archive_backend.calls[0]["session_id"] == "sess-200"
    assert archive_backend.calls[0]["chunks"] == ["operator summary"]
    hot_body = store.get_transcript_hot_body("sess-200")
    assert hot_body is not None
    assert hot_body.purge_after == hot_body.available_until


def test_transcript_ledger_records_archive_write_failed_when_archive_backend_retries_needed() -> None:
    store = _InMemoryCollaborationStore()
    store.upsert_work_item(_work_item(owner_cli="gemini"))
    service = TranscriptLedgerService(store, archive_backend=_FailingArchiveBackend())
    actor = ActorIdentity(cli_name="gemini", role="worker_cli")
    service.start_session(actor, _session())
    service.append_block(
        actor,
        session_id="sess-200",
        event_id="tevt-2",
        occurred_at=_ts("2026-04-03T03:05:00Z"),
        content="operator summary",
    )

    service.close_session(
        actor,
        session_id="sess-200",
        event_id="tevt-3",
        occurred_at=_ts("2026-04-03T03:10:00Z"),
    )

    events = service.list_session_events(actor, "sess-200")
    assert events[-2].event_type == "transcript.archive_pending"
    assert events[-1].event_type == "transcript.archive_write_failed"
    assert "disk full" in events[-1].payload["error"]
    hot_body = store.get_transcript_hot_body("sess-200")
    assert hot_body is not None
    assert hot_body.purge_after is None


def test_transcript_ledger_rejects_hot_body_expiry_without_archive_reference() -> None:
    store = _InMemoryCollaborationStore()
    store.upsert_work_item(_work_item(owner_cli="gemini"))
    service = TranscriptLedgerService(store)
    actor = ActorIdentity(cli_name="gemini", role="worker_cli")
    service.start_session(actor, _session())
    service.append_block(
        actor,
        session_id="sess-200",
        event_id="tevt-2",
        occurred_at=_ts("2026-04-03T03:05:00Z"),
        content="operator summary",
    )

    with pytest.raises(ValueError, match="archive reference"):
        service.expire_hot_body(
            ActorIdentity(cli_name="main", role="main_cli"),
            session_id="sess-200",
            occurred_at=_ts("2026-07-03T03:06:00Z"),
        )

    hot_body = store.get_transcript_hot_body("sess-200")
    assert hot_body is not None
    assert hot_body.content == "operator summary"


def test_transcript_ledger_appends_hot_body_expired_event_without_mutating_hot_body() -> None:
    store = _InMemoryCollaborationStore()
    store.upsert_work_item(_work_item(owner_cli="gemini"))
    service = TranscriptLedgerService(store, archive_backend=_SuccessfulArchiveBackend())
    actor = ActorIdentity(cli_name="gemini", role="worker_cli")
    service.start_session(actor, _session())
    service.append_block(
        actor,
        session_id="sess-200",
        event_id="tevt-2",
        occurred_at=_ts("2026-04-03T03:05:00Z"),
        content="operator summary",
    )
    service.close_session(
        actor,
        session_id="sess-200",
        event_id="tevt-3",
        occurred_at=_ts("2026-04-03T03:10:00Z"),
    )

    expired = service.expire_hot_body(
        ActorIdentity(cli_name="main", role="main_cli"),
        session_id="sess-200",
        occurred_at=_ts("2026-07-03T03:06:00Z"),
    )

    assert expired.event_type == "transcript.hot_body_expired"
    assert store.get_transcript_hot_body("sess-200") is not None
    assert store.get_transcript_hot_body("sess-200").content == "operator summary"


def _session(
    *,
    work_item_id: str = "MT-200",
    session_id: str = "sess-200",
    actor_cli: str = "gemini",
) -> TranscriptSessionRecord:
    return TranscriptSessionRecord(
        session_id=session_id,
        work_item_id=work_item_id,
        actor_cli=actor_cli,
        branch="dev-api-availability-gemini",
        transcript_kind="AUTO",
        started_at=_ts("2026-04-03T03:00:00Z"),
        closed_at=None,
        archive_policy_version="v1",
    )


class _SuccessfulArchiveBackend:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def seal_session(self, session_id: str, chunks: list[str], metadata: dict) -> object:
        self.calls.append({"session_id": session_id, "chunks": list(chunks), "metadata": dict(metadata)})

        class _Result:
            archive_locator = "archive/MT-200/sess-200/transcript.txt"
            manifest_locator = "archive/MT-200/sess-200/manifest.json"
            checksum = "sha256:sealed"
            chunk_count = 1
            byte_count = len("operator summary".encode("utf-8"))
            sealed_at = _ts("2026-04-03T03:10:00Z")
            backend_kind = "filesystem"

        return _Result()

    def stat(self, locator: str) -> object:
        return {"locator": locator}

    def retrieve_metadata(self, locator: str) -> dict:
        return {"locator": locator}


class _FailingArchiveBackend:
    def seal_session(self, session_id: str, chunks: list[str], metadata: dict) -> object:
        raise TranscriptArchiveRetryableError(f"disk full: {session_id}")

    def stat(self, locator: str) -> object:
        return {"locator": locator}

    def retrieve_metadata(self, locator: str) -> dict:
        return {"locator": locator}
