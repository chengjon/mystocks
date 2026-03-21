from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from src.services.maestro.collab.integrations.models import (
    GraphitiIngestStatus,
    GraphitiSearchResult,
    GraphitiServerStatus,
    GraphitiWriteResult,
)
from src.services.maestro.collab.services.graphiti_preflight import GraphitiPreflightService


class _FakeGraphitiAdapter:
    def __init__(self) -> None:
        self.write_calls: list[dict[str, Any]] = []
        self.wait_calls: list[dict[str, Any]] = []
        self.search_calls: list[dict[str, Any]] = []

    def get_server_status(self) -> GraphitiServerStatus:
        return GraphitiServerStatus(server_status="ok", message="ready", details={})

    def add_memory(self, **kwargs: Any) -> GraphitiWriteResult:
        self.write_calls.append(kwargs)
        return GraphitiWriteResult(
            episode_uuid="ep-500",
            group_id=kwargs["group_id"],
            queue_position=2,
            message="queued",
        )

    def wait_for_ingest(self, **kwargs: Any) -> GraphitiIngestStatus:
        self.wait_calls.append(kwargs)
        return GraphitiIngestStatus(
            ingest_status="completed",
            episode_uuid=kwargs["episode_uuid"],
            group_id=kwargs["group_id"],
            queue_depth=0,
            queue_position=None,
            processed_at="2026-03-21T09:00:00+00:00",
            last_error=None,
        )

    def search_context(self, query_bundle, group_ids: list[str] | None = None, max_nodes: int = 5, max_facts: int = 5) -> GraphitiSearchResult:
        self.search_calls.append(
            {
                "query_bundle": query_bundle,
                "group_ids": group_ids,
                "max_nodes": max_nodes,
                "max_facts": max_facts,
            }
        )
        return GraphitiSearchResult(
            search_outcome="hit",
            search_summary="nodes hit=1, facts hit=1",
            matched_nodes_count=1,
            matched_facts_count=1,
            nodes=[{"uuid": "n-1", "name": "Graphiti workflow guide"}],
            facts=[{"uuid": "f-1", "fact": "Graphiti is used as long-term memory"}],
            errors=[],
        )


def test_graphiti_generic_remember_does_not_require_work_item() -> None:
    adapter = _FakeGraphitiAdapter()
    service = GraphitiPreflightService(service=None, adapter=adapter)

    result = service.remember_generic(
        actor_cli="cli-5",
        group_id="mystocks_spec_docs",
        name="Architecture Note",
        body="Graphiti generic memory should bypass Mongo work-item lookup.",
        max_wait_seconds=30,
    )

    assert result.episode_uuid == "ep-500"
    assert result.group_id == "mystocks_spec_docs"
    assert result.ingest_status == "completed"
    assert adapter.write_calls
    assert adapter.wait_calls


def test_graphiti_generic_remember_returns_durable_audit_metadata() -> None:
    adapter = _FakeGraphitiAdapter()
    service = GraphitiPreflightService(service=None, adapter=adapter)

    result = service.remember_generic(
        actor_cli="cli-7",
        group_id="mystocks_spec_review",
        name="Review Note",
        body="Record durable Graphiti metadata.",
        max_wait_seconds=45,
    )

    assert result.episode_uuid is not None
    assert result.group_id == "mystocks_spec_review"
    assert result.processed_at == "2026-03-21T09:00:00+00:00"
    assert "status_ms" in result.timings
    assert "wait_ms" in result.timings


def test_graphiti_generic_search_uses_explicit_group_ids() -> None:
    adapter = _FakeGraphitiAdapter()
    service = GraphitiPreflightService(service=None, adapter=adapter)

    result = service.search_generic(
        actor_cli="cli-8",
        query="Graphiti workflow guide",
        group_ids=["mystocks_spec_docs"],
        query_type="all",
    )

    assert result.server_status == "ok"
    assert result.search_outcome == "hit"
    assert result.group_ids == ["mystocks_spec_docs"]
    assert adapter.search_calls[0]["group_ids"] == ["mystocks_spec_docs"]
