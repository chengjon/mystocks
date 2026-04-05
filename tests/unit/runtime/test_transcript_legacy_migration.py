from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from scripts.runtime.migrate_transcript_legacy_indexes import migrate_legacy_transcript_indexes
from src.services.maestro.collab.backends.mongo.store import MongoCollaborationStore
from src.services.maestro.collab.store.models import TranscriptSessionRecord, WorkItemRecord


def test_migrate_legacy_transcript_indexes_creates_only_legacy_indexes_without_body_backfill(tmp_path: Path) -> None:
    database = _FakeMongoDatabase()
    store = MongoCollaborationStore(database)
    work_item = _work_item("MT-980")
    store.upsert_work_item(work_item)

    artifact_path = tmp_path / "TASK-REPORT.md"
    artifact_path.write_text(
        "\n".join(
            [
                "# TASK-REPORT",
                "",
                "- Issue Identifier: `MT-980`",
                "",
                "## AUTO 2026-03-01 Sync Review",
                "operator summary line",
                "assistant response line",
                "",
                "## MANUAL 2026-03-02 Follow-up",
                "manual transcript line",
            ]
        ),
        encoding="utf-8",
    )

    counts = migrate_legacy_transcript_indexes(
        artifact_paths=[artifact_path],
        mongo_database=database,
        migration_batch_id="batch-legacy-1",
    )

    legacy_indexes = store.list_transcript_legacy_indexes("MT-980")
    assert counts == {"legacy_indexes": 2, "artifacts_scanned": 1, "skipped_missing_work_item": 0}
    assert [record.legacy_block_kind for record in legacy_indexes] == ["AUTO", "MANUAL"]
    assert all(record.archive_locator.startswith(str(artifact_path)) for record in legacy_indexes)
    assert all(record.migration_batch_id == "batch-legacy-1" for record in legacy_indexes)
    assert store.list_transcript_sessions("MT-980") == []


def test_migrate_legacy_transcript_indexes_keeps_legacy_indexes_distinct_from_ledger_sessions(tmp_path: Path) -> None:
    database = _FakeMongoDatabase()
    store = MongoCollaborationStore(database)
    work_item = _work_item("MT-981")
    store.upsert_work_item(work_item)
    store.upsert_transcript_session(
        TranscriptSessionRecord(
            session_id="sess-981",
            work_item_id="MT-981",
            actor_cli="gemini",
            branch="feat/transcript-ledger",
            transcript_kind="AUTO",
            started_at=_ts("2026-04-03T00:00:00Z"),
            closed_at=None,
            archive_policy_version="v1",
        )
    )

    artifact_path = tmp_path / "TASK.md"
    artifact_path.write_text(
        "\n".join(
            [
                "# TASK",
                "",
                "- Issue Identifier: `MT-981`",
                "",
                "### MANUAL 2026-03-01 Historical Review",
                "legacy transcript body",
            ]
        ),
        encoding="utf-8",
    )

    migrate_legacy_transcript_indexes(
        artifact_paths=[artifact_path],
        mongo_database=database,
        migration_batch_id="batch-legacy-2",
    )

    sessions = store.list_transcript_sessions("MT-981")
    legacy_indexes = store.list_transcript_legacy_indexes("MT-981")
    assert [session.session_id for session in sessions] == ["sess-981"]
    assert [record.legacy_block_kind for record in legacy_indexes] == ["MANUAL"]
    assert legacy_indexes[0].legacy_session_label == "MANUAL 2026-03-01 Historical Review"


def test_migrate_legacy_transcript_indexes_reports_only_new_indexes_on_repeat_runs(tmp_path: Path) -> None:
    database = _FakeMongoDatabase()
    store = MongoCollaborationStore(database)
    store.upsert_work_item(_work_item("MT-982"))

    artifact_path = tmp_path / "TASK-REPORT.md"
    artifact_path.write_text(
        "\n".join(
            [
                "# TASK-REPORT",
                "",
                "- Issue Identifier: `MT-982`",
                "",
                "## AUTO 2026-03-01 Sync Review",
                "operator summary line",
            ]
        ),
        encoding="utf-8",
    )

    first_counts = migrate_legacy_transcript_indexes(
        artifact_paths=[artifact_path],
        mongo_database=database,
        migration_batch_id="batch-legacy-repeat",
    )
    second_counts = migrate_legacy_transcript_indexes(
        artifact_paths=[artifact_path],
        mongo_database=database,
        migration_batch_id="batch-legacy-repeat",
    )

    assert first_counts == {"legacy_indexes": 1, "artifacts_scanned": 1, "skipped_missing_work_item": 0}
    assert second_counts == {"legacy_indexes": 0, "artifacts_scanned": 1, "skipped_missing_work_item": 0}
    assert len(store.list_transcript_legacy_indexes("MT-982")) == 1


def _work_item(work_item_id: str) -> WorkItemRecord:
    now = _ts("2026-04-03T00:00:00Z")
    return WorkItemRecord(
        work_item_id=work_item_id,
        task_key=work_item_id.lower(),
        title=f"Work item {work_item_id}",
        objective="Legacy transcript migration",
        branch="feat/transcript-ledger",
        owner_cli="gemini",
        status="in_progress",
        allowed_paths=["scripts/runtime"],
        forbidden_paths=[],
        acceptance_checks=[],
        openspec=None,
        created_at=now,
        updated_at=now,
    )


def _ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


class _FakeMongoDatabase:
    def __init__(self) -> None:
        self._collections = {
            "work_items": _FakeCollection(),
            "work_updates": _FakeCollection(),
            "work_requests": _FakeCollection(),
            "work_events": _FakeCollection(),
            "worker_status_views": _FakeCollection(),
            "transcript_sessions": _FakeCollection(),
            "transcript_events": _FakeCollection(),
            "transcript_hot_bodies": _FakeCollection(),
            "transcript_legacy_indexes": _FakeCollection(),
        }

    def __getitem__(self, name: str) -> "_FakeCollection":
        return self._collections[name]


class _FakeCollection:
    def __init__(self) -> None:
        self.docs: list[dict] = []
        self.indexes = []

    def create_indexes(self, indexes) -> None:
        self.indexes.extend(indexes)

    def replace_one(self, filter_query: dict, document: dict, *, upsert: bool = False) -> None:
        for index, existing in enumerate(self.docs):
            if _matches(existing, filter_query):
                self.docs[index] = document.copy()
                return
        if upsert:
            self.docs.append(document.copy())

    def find_one(self, filter_query: dict) -> dict | None:
        for document in self.docs:
            if _matches(document, filter_query):
                return document.copy()
        return None

    def insert_one(self, document: dict) -> None:
        self.docs.append(document.copy())

    def find(self, filter_query: dict):
        return _FakeCursor([document.copy() for document in self.docs if _matches(document, filter_query)])


class _FakeCursor:
    def __init__(self, docs: list[dict]) -> None:
        self._docs = docs

    def sort(self, key: str, _direction: int):
        self._docs.sort(key=lambda document: str(document.get(key, "")))
        return self

    def __iter__(self):
        return iter(self._docs)


def _matches(document: dict, filter_query: dict) -> bool:
    for key, value in filter_query.items():
        if document.get(key) != value:
            return False
    return True
