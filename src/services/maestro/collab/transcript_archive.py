from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any, Callable, Protocol


@dataclass(frozen=True)
class TranscriptArchiveSealResult:
    session_id: str
    archive_locator: str
    manifest_locator: str
    checksum: str
    chunk_count: int
    byte_count: int
    sealed_at: datetime
    backend_kind: str


@dataclass(frozen=True)
class TranscriptArchiveStat:
    locator: str
    exists: bool
    size_bytes: int | None


class TranscriptArchiveRetryableError(RuntimeError):
    """Raised when archive sealing can be retried later."""


class TranscriptArchiveBackend(Protocol):
    def seal_session(self, session_id: str, chunks: list[str], metadata: dict[str, Any]) -> TranscriptArchiveSealResult: ...

    def stat(self, locator: str) -> TranscriptArchiveStat: ...

    def retrieve_metadata(self, locator: str) -> dict[str, Any]: ...


class FilesystemTranscriptArchiveBackend:
    def __init__(self, root: Path, *, clock: Callable[[], datetime] | None = None) -> None:
        self._root = root
        self._clock = clock or _utcnow

    def seal_session(self, session_id: str, chunks: list[str], metadata: dict[str, Any]) -> TranscriptArchiveSealResult:
        work_item_id = str(metadata["work_item_id"])
        session_dir = self._root / work_item_id / session_id
        archive_path = session_dir / "transcript.txt"
        manifest_path = session_dir / "manifest.json"
        content = "\n".join(chunks)
        checksum = f"sha256:{sha256(content.encode('utf-8')).hexdigest()}"
        sealed_at = self._clock()
        archive_locator = str(archive_path.relative_to(self._root))
        manifest_locator = str(manifest_path.relative_to(self._root))
        manifest = {
            "session_id": session_id,
            "archive_locator": archive_locator,
            "manifest_locator": manifest_locator,
            "checksum": checksum,
            "chunk_count": len(chunks),
            "byte_count": len(content.encode("utf-8")),
            "sealed_at": sealed_at.astimezone(UTC).isoformat(),
            "backend_kind": "filesystem",
            "metadata": _json_ready(metadata),
        }

        try:
            self._write_text(archive_path, content)
            self._write_text(manifest_path, json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
        except OSError as exc:
            raise TranscriptArchiveRetryableError(f"filesystem archive seal failed for {session_id}: {exc}") from exc

        return TranscriptArchiveSealResult(
            session_id=session_id,
            archive_locator=archive_locator,
            manifest_locator=manifest_locator,
            checksum=checksum,
            chunk_count=len(chunks),
            byte_count=len(content.encode("utf-8")),
            sealed_at=sealed_at,
            backend_kind="filesystem",
        )

    def stat(self, locator: str) -> TranscriptArchiveStat:
        path = self._root / locator
        if not path.exists():
            return TranscriptArchiveStat(locator=locator, exists=False, size_bytes=None)
        return TranscriptArchiveStat(locator=locator, exists=True, size_bytes=path.stat().st_size)

    def retrieve_metadata(self, locator: str) -> dict[str, Any]:
        return json.loads((self._root / locator).read_text(encoding="utf-8"))

    def _write_text(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def _json_ready(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.astimezone(UTC).isoformat()
    if isinstance(value, dict):
        return {key: _json_ready(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    return value


def _utcnow() -> datetime:
    return datetime.now(UTC)
