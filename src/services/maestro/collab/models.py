from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class AssignmentState:
    issue_id: str | None
    issue_identifier: str
    assigned_worker_cli: str | None
    assigned_by: str | None
    status: str
    acceptance_summary: str | None
    updated_at: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class WorkspaceBinding:
    issue_id: str | None
    issue_identifier: str
    workspace_key: str
    workspace_path: str
    branch_name: str | None
    owner_cli: str | None
    created_at: str
    updated_at: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class WorkerHeartbeat:
    issue_id: str | None
    issue_identifier: str
    session_id: str | None
    worker_cli: str | None
    last_event: str | None
    last_message: str | None
    heartbeat_at: str
    stale_after_seconds: int
    updated_at: str
    stale: bool = False

    def to_dict(self) -> dict:
        return asdict(self)
