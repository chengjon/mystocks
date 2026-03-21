from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class GraphitiQueryBundle:
    entity_queries: list[str]
    fact_queries: list[str]


@dataclass(frozen=True)
class GraphitiServerStatus:
    server_status: str
    message: str | None
    details: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GraphitiWriteResult:
    episode_uuid: str | None
    group_id: str | None
    queue_position: int | None
    message: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GraphitiIngestStatus:
    ingest_status: str
    episode_uuid: str | None
    group_id: str | None
    queue_depth: int | None
    queue_position: int | None
    processed_at: str | None
    last_error: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GraphitiSearchResult:
    search_outcome: str
    search_summary: str
    matched_nodes_count: int
    matched_facts_count: int
    nodes: list[dict[str, Any]] = field(default_factory=list)
    facts: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GraphitiPreflightResult:
    work_item_id: str
    server_status: str
    ingest_status: str
    search_outcome: str
    search_summary: str
    matched_nodes_count: int
    matched_facts_count: int
    wait_seconds: int
    timings: dict[str, float]
    queries: dict[str, list[str]]
    errors: list[str]
    episode_uuid: str | None = None
    group_id: str | None = None
    queue_position: int | None = None
    processed_at: str | None = None

    def to_event_payload(self, *, actor_cli: str, branch: str) -> dict[str, Any]:
        payload = self.to_dict()
        payload.update(
            {
                "source": "graphiti_preflight",
                "actor_cli": actor_cli,
                "branch": branch,
            }
        )
        return payload

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GraphitiMemoryRecordResult:
    work_item_id: str | None
    server_status: str
    ingest_status: str
    episode_uuid: str | None
    group_id: str | None
    queue_position: int | None
    processed_at: str | None
    wait_seconds: int
    timings: dict[str, float]
    message: str | None
    errors: list[str]

    def to_event_payload(self, *, actor_cli: str, branch: str) -> dict[str, Any]:
        payload = self.to_dict()
        payload.update(
            {
                "source": "graphiti_memory_record",
                "actor_cli": actor_cli,
                "branch": branch,
            }
        )
        return payload

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GraphitiMemorySearchResult:
    server_status: str
    query: str
    group_ids: list[str]
    query_type: str
    search_outcome: str
    search_summary: str
    matched_nodes_count: int
    matched_facts_count: int
    timings: dict[str, float]
    nodes: list[dict[str, Any]] = field(default_factory=list)
    facts: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
