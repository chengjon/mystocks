from __future__ import annotations

import json

import pytest

from src.services.maestro.collab.transcript_archive import (
    FilesystemTranscriptArchiveBackend,
    TranscriptArchiveRetryableError,
)


def test_filesystem_transcript_archive_backend_seals_session_to_deterministic_locator(tmp_path) -> None:
    backend = FilesystemTranscriptArchiveBackend(tmp_path)

    result = backend.seal_session(
        "sess-300",
        chunks=["operator summary", "assistant response"],
        metadata={"work_item_id": "MT-300", "transcript_kind": "AUTO"},
    )

    assert result.archive_locator == "MT-300/sess-300/transcript.txt"
    assert result.manifest_locator == "MT-300/sess-300/manifest.json"
    assert (tmp_path / result.archive_locator).read_text(encoding="utf-8") == "operator summary\nassistant response"
    assert backend.stat(result.archive_locator).exists is True


def test_filesystem_transcript_archive_backend_writes_manifest_with_checksum(tmp_path) -> None:
    backend = FilesystemTranscriptArchiveBackend(tmp_path)

    result = backend.seal_session(
        "sess-301",
        chunks=["manual note"],
        metadata={"work_item_id": "MT-301", "transcript_kind": "MANUAL"},
    )

    manifest = json.loads((tmp_path / result.manifest_locator).read_text(encoding="utf-8"))
    assert manifest["checksum"] == result.checksum
    assert manifest["metadata"]["work_item_id"] == "MT-301"
    assert backend.retrieve_metadata(result.manifest_locator)["archive_locator"] == result.archive_locator


def test_filesystem_transcript_archive_backend_wraps_retryable_write_failures(tmp_path, monkeypatch) -> None:
    backend = FilesystemTranscriptArchiveBackend(tmp_path)
    monkeypatch.setattr(
        backend,
        "_write_text",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(OSError("disk full")),
    )

    with pytest.raises(TranscriptArchiveRetryableError, match="disk full"):
        backend.seal_session(
            "sess-302",
            chunks=["operator summary"],
            metadata={"work_item_id": "MT-302", "transcript_kind": "AUTO"},
        )
