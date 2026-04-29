from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ExecuteTaskRequest(BaseModel):
    provider: str
    method: str
    params: dict[str, Any] = Field(default_factory=dict)
    write_to_nas: bool = True


class HealthResponse(BaseModel):
    status: str
    node: str
    provider_mode: str
    bridge_contract_version: str
    bridge_auth_configured: bool
    source_name: str
    time: str
