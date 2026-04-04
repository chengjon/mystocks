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
