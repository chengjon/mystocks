from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class WorkflowDefinition:
    """Parsed `WORKFLOW.md` payload."""

    config: dict[str, Any]
    prompt_template: str


@dataclass(frozen=True)
class Workspace:
    """Filesystem workspace assigned to one issue identifier."""

    path: Path
    workspace_key: str
    issue_identifier: str
    created_now: bool


@dataclass(frozen=True)
class BlockerRef:
    """Best-effort blocker reference derived from tracker payloads."""

    id: str | None
    identifier: str | None
    state: str | None


@dataclass(frozen=True)
class Issue:
    """Normalized issue record used by Symphony orchestration."""

    id: str
    identifier: str
    title: str
    description: str | None
    priority: int | None
    state: str
    branch_name: str | None
    url: str | None
    labels: list[str]
    blocked_by: list[BlockerRef]
    created_at: datetime | None
    updated_at: datetime | None


@dataclass
class LiveCodexSession:
    """Live app-server session metadata."""

    process: Any
    workspace_path: Path
    thread_id: str
    pid: int | None
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    last_turn_id: str | None = None


@dataclass(frozen=True)
class CodexTurnResult:
    """Outcome of a single app-server turn."""

    status: str
    turn_id: str
    session_id: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    error_code: str | None = None
    message: str | None = None


@dataclass(frozen=True)
class RunAttemptResult:
    """Outcome of a Symphony worker attempt."""

    status: str
    turn_count: int
    session_id: str | None
    workspace_path: Path
    error_code: str | None = None
