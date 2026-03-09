from __future__ import annotations

from pathlib import Path
import re

from .ownership import FileOwnershipIndex

_BACKTICK_PATH_PATTERN = re.compile(r"`([^`\n]+)`")
_BARE_PATH_PATTERN = re.compile(r"(?<![\w`])(?:[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+|[A-Za-z0-9_.-]+\.[A-Za-z0-9_.-]+)")
_STRIP_EDGE_CHARS = "\"'()[]{}<>,;:。！？、"
_REPO_PATH_PREFIXES = (
    "src/",
    "tests/",
    "docs/",
    "scripts/",
    "web/",
    "config/",
    "openspec/",
    "architecture/",
    "reports/",
    ".github/",
    ".claude/",
)
_KNOWN_ROOT_FILES = {
    "TASK.md",
    "TASK-REPORT.md",
    "WORKFLOW.md",
    "README.md",
    "AGENTS.md",
    "CLAUDE.md",
    ".FILE_OWNERSHIP",
    "pyproject.toml",
}


class OwnershipSuggestionEngine:
    """Advisory owner suggester for main CLI dispatch decisions."""

    def __init__(self, ownership_index: FileOwnershipIndex, *, fallback_owner: str = "main") -> None:
        self._ownership_index = ownership_index
        self._fallback_owner = fallback_owner

    def suggest(
        self,
        *,
        candidate_paths: list[str] | None = None,
        task_path_hints: list[str] | None = None,
    ) -> dict[str, object]:
        all_paths = _unique_paths([*(candidate_paths or []), *(task_path_hints or [])])
        matched_paths: dict[str, list[str]] = {}
        matched_rules: dict[str, list[str]] = {}
        unowned_paths: list[str] = []
        owner_scores: dict[str, int] = {}

        for candidate_path in all_paths:
            entry = self._ownership_index.match(candidate_path)
            if entry is None:
                unowned_paths.append(candidate_path)
                continue

            suggestable_owner = _normalize_owner(entry.owner, fallback_owner=self._fallback_owner)
            matched_paths.setdefault(suggestable_owner, []).append(candidate_path)
            matched_rules.setdefault(suggestable_owner, []).append(entry.pattern)
            owner_scores[suggestable_owner] = owner_scores.get(suggestable_owner, 0) + 1

        suggested_owner = self._select_owner(owner_scores)
        reasons = _build_reasons(
            suggested_owner=suggested_owner,
            matched_paths=matched_paths,
            unowned_paths=unowned_paths,
            fallback_owner=self._fallback_owner,
        )

        return {
            "suggested_owner": suggested_owner,
            "fallback_owner": self._fallback_owner,
            "candidate_paths": all_paths,
            "matched_paths": matched_paths,
            "matched_rules": matched_rules,
            "owner_scores": owner_scores,
            "unowned_paths": unowned_paths,
            "reasons": reasons,
        }

    def _select_owner(self, owner_scores: dict[str, int]) -> str:
        if not owner_scores:
            return self._fallback_owner

        top_score = max(owner_scores.values())
        top_owners = sorted(owner for owner, score in owner_scores.items() if score == top_score)
        if len(top_owners) > 1:
            return self._fallback_owner
        return top_owners[0]


def extract_task_path_hints(path: str | Path) -> list[str]:
    task_path = Path(path)
    content = task_path.read_text(encoding="utf-8")
    hints: list[str] = []

    for matched in _BACKTICK_PATH_PATTERN.findall(content):
        normalized = _normalize_candidate_path(matched)
        if _looks_like_path(normalized):
            hints.append(normalized)

    content_without_backticks = _BACKTICK_PATH_PATTERN.sub(" ", content)
    for matched in _BARE_PATH_PATTERN.findall(content_without_backticks):
        normalized = _normalize_candidate_path(matched)
        if _looks_like_path(normalized):
            hints.append(normalized)

    return _unique_paths(hints)


def _normalize_candidate_path(value: str) -> str:
    normalized = value.strip().strip(_STRIP_EDGE_CHARS).replace("\\", "/")
    return re.sub(r"^(?:\./)+", "", normalized)


def _looks_like_path(value: str) -> bool:
    if not value:
        return False

    if value in _KNOWN_ROOT_FILES:
        return True

    if "/" in value:
        if any(value.startswith(prefix) for prefix in _REPO_PATH_PREFIXES):
            return True

        first_segment = value.split("/", 1)[0]
        tail_segment = value.rsplit("/", 1)[-1]
        return bool(re.fullmatch(r"[a-z0-9._-]+", first_segment)) and bool(
            re.search(r"\.[A-Za-z0-9_-]+$", tail_segment)
        )

    return bool(re.search(r"\.[A-Za-z0-9_-]+$", value))


def _unique_paths(values: list[str]) -> list[str]:
    unique_values: list[str] = []
    seen: set[str] = set()

    for value in values:
        normalized = _normalize_candidate_path(value)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        unique_values.append(normalized)

    return unique_values


def _normalize_owner(owner: str, *, fallback_owner: str) -> str:
    normalized = owner.strip()
    if normalized == "main+clis":
        return fallback_owner
    return normalized


def _build_reasons(
    *,
    suggested_owner: str,
    matched_paths: dict[str, list[str]],
    unowned_paths: list[str],
    fallback_owner: str,
) -> list[str]:
    reasons: list[str] = []

    if matched_paths.get(suggested_owner):
        reasons.append(f"{suggested_owner} matched {len(matched_paths[suggested_owner])} path(s)")

    if unowned_paths:
        reasons.append(f"{len(unowned_paths)} path(s) fallback to {fallback_owner}")

    if not reasons:
        reasons.append(f"no owned paths found; fallback to {fallback_owner}")

    return reasons
