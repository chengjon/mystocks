from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class _FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class WorkItemRecord(_FrozenModel):
    work_item_id: str
    task_key: str
    title: str
    objective: str
    branch: str
    owner_cli: str
    status: str
    allowed_paths: list[str]
    forbidden_paths: list[str]
    acceptance_checks: list[str]
    openspec: dict[str, Any] | None
    metadata: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


class WorkUpdateRecord(_FrozenModel):
    work_item_id: str
    update_id: str
    actor_cli: str
    status: str
    summary: str
    details: dict[str, Any]
    created_at: datetime


class WorkRequestRecord(_FrozenModel):
    work_item_id: str
    request_id: str
    actor_cli: str
    status: str
    request_type: str
    summary: str
    payload: dict[str, Any]
    created_at: datetime
    reviewed_at: datetime | None
    reviewed_by: str | None


class WorkEventRecord(_FrozenModel):
    work_item_id: str
    event_id: str
    actor_cli: str
    event_type: str
    payload: dict[str, Any]
    created_at: datetime


class WorkerStatusViewRecord(_FrozenModel):
    work_item_id: str
    branch: str
    owner_cli: str
    status: str
    latest_update: str | None
    blocker: str | None
    has_pending_request: bool
    updated_at: datetime


class TranscriptSessionRecord(_FrozenModel):
    session_id: str
    work_item_id: str
    actor_cli: str
    branch: str
    transcript_kind: str
    started_at: datetime
    closed_at: datetime | None
    archive_policy_version: str


class TranscriptEventRecord(_FrozenModel):
    work_item_id: str
    session_id: str
    event_id: str
    event_type: str
    sequence_no: int
    occurred_at: datetime
    payload: dict[str, Any]


class TranscriptHotBodyRecord(_FrozenModel):
    body_id: str
    session_id: str
    event_id: str
    content: str
    checksum: str
    available_until: datetime
    purge_after: datetime | None = None


class TranscriptLegacyIndexRecord(_FrozenModel):
    legacy_index_id: str
    work_item_id: str
    source_artifact: str
    legacy_block_kind: str
    legacy_session_label: str
    captured_at: datetime
    source_anchor: str
    archive_locator: str
    checksum: str
    migration_batch_id: str
    migration_recorded_at: datetime
