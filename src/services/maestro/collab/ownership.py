from __future__ import annotations

from dataclasses import asdict, dataclass
from fnmatch import fnmatch
from pathlib import Path
import re


@dataclass(frozen=True)
class OwnershipEntry:
    pattern: str
    owner: str
    note: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return asdict(self)


class FileOwnershipIndex:
    """Rule index for `.FILE_OWNERSHIP` path ownership matching."""

    def __init__(self, entries: list[OwnershipEntry]) -> None:
        self.entries = list(entries)

    def match(self, candidate_path: str) -> OwnershipEntry | None:
        normalized_path = _normalize_path(candidate_path)
        best_entry: OwnershipEntry | None = None
        best_score: tuple[int, int, int] | None = None

        for entry in self.entries:
            if not _matches(entry.pattern, normalized_path):
                continue

            score = _pattern_score(entry.pattern)
            if best_score is None or score > best_score:
                best_entry = entry
                best_score = score

        return best_entry

    def owner_for_path(self, candidate_path: str) -> str | None:
        entry = self.match(candidate_path)
        return entry.owner if entry else None


def load_file_ownership(path: str | Path) -> list[OwnershipEntry]:
    ownership_path = Path(path)
    entries: list[OwnershipEntry] = []

    for raw_line in ownership_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        body, separator, note = line.partition("|")
        note_value = note.strip() if separator else None
        parsed = _parse_body(body.strip(), note_value)
        if parsed is not None:
            entries.append(parsed)

    return entries


def _parse_body(body: str, note: str | None) -> OwnershipEntry | None:
    if not body:
        return None

    tokens = body.split()
    if len(tokens) < 2:
        return None

    owner = tokens[-1].strip()
    pattern = " ".join(tokens[:-1]).strip()
    if pattern.endswith(":"):
        pattern = pattern[:-1].strip()

    if not pattern or not owner:
        return None

    return OwnershipEntry(pattern=pattern, owner=owner, note=note)


def _matches(pattern: str, candidate_path: str) -> bool:
    normalized_pattern = _normalize_path(pattern)

    if any(token in normalized_pattern for token in "*?["):
        return fnmatch(candidate_path, normalized_pattern)

    if normalized_pattern.endswith("/"):
        return candidate_path.startswith(normalized_pattern)

    return candidate_path == normalized_pattern


def _pattern_score(pattern: str) -> tuple[int, int, int]:
    normalized_pattern = _normalize_path(pattern)
    literal_length = len(re.sub(r"[*?\[]", "", normalized_pattern.rstrip("/")))

    if not any(token in normalized_pattern for token in "*?[") and not normalized_pattern.endswith("/"):
        kind_rank = 3
    elif normalized_pattern.endswith("/"):
        kind_rank = 2
    else:
        kind_rank = 1

    return literal_length, kind_rank, len(normalized_pattern)


def _normalize_path(value: str) -> str:
    normalized = value.strip().replace("\\", "/")
    normalized = re.sub(r"^(?:\./)+", "", normalized)
    return normalized
