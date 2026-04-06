from __future__ import annotations

import time
from pathlib import Path
from typing import Iterable

from src.services.maestro.collab.authz import ActorIdentity
from src.services.maestro.collab.integrations import (
    GraphitiAdapter,
    GraphitiIngestStatus,
    GraphitiMemoryRecordResult,
    GraphitiMemorySearchResult,
    GraphitiPreflightResult,
    GraphitiQueryBundle,
    GraphitiSearchResult,
    GraphitiWriteResult,
)
from src.services.maestro.collab.services.coordination import CoordinationService
from src.services.maestro.collab.store.models import WorkItemRecord

DEFAULT_QUERY_GROUP_IDS = [
    "mystocks_spec_main",
    "mystocks_spec_workers",
    "mystocks_spec_review",
    "mystocks_spec_docs",
]
DEFAULT_WRITE_GROUP_ID = "mystocks_spec_workers"


class GraphitiPreflightService:
    def __init__(self, *, service: CoordinationService | None, adapter: GraphitiAdapter | None = None) -> None:
        self._service = service
        self._adapter = adapter or GraphitiAdapter()

    def run(
        self,
        *,
        actor: ActorIdentity,
        work_item_id: str,
        task_path: Path | None = None,
        write_memory: bool = False,
        max_wait_seconds: int = 60,
    ) -> GraphitiPreflightResult:
        work_item = self._require_service().get_work_item(actor, work_item_id)
        if work_item is None:
            raise KeyError(f"Unknown work item: {work_item_id}")

        query_bundle = self._build_query_bundle(work_item, task_path)
        errors: list[str] = []

        status_started = time.perf_counter()
        server_status = self._adapter.get_server_status()
        status_ms = round((time.perf_counter() - status_started) * 1000, 2)

        ingest_status = GraphitiIngestStatus(
            ingest_status="not_applicable",
            episode_uuid=None,
            group_id=None,
            queue_depth=None,
            queue_position=None,
            processed_at=None,
            last_error=None,
        )
        write_result: GraphitiWriteResult | None = None

        if write_memory and server_status.server_status == "ok":
            write_result, ingest_status, wait_ms, write_errors = self._write_memory_for_work_item(
                work_item=work_item,
                task_path=task_path,
                max_wait_seconds=max_wait_seconds,
                name=f"work preflight {work_item.work_item_id}",
                source_description="repo-local work preflight",
            )
            errors.extend(write_errors)
        else:
            wait_ms = 0.0

        search_started = time.perf_counter()
        if server_status.server_status == "ok":
            search_result = self._adapter.search_context(query_bundle, group_ids=DEFAULT_QUERY_GROUP_IDS)
        else:
            search_result = GraphitiSearchResult(
                search_outcome="error",
                search_summary=server_status.message or "Graphiti server unavailable",
                matched_nodes_count=0,
                matched_facts_count=0,
                nodes=[],
                facts=[],
                errors=[server_status.message or "Graphiti server unavailable"],
            )
        search_ms = round((time.perf_counter() - search_started) * 1000, 2)

        if ingest_status.ingest_status in {"warming", "best_effort"} and search_result.search_outcome == "miss":
            search_result = GraphitiSearchResult(
                search_outcome="best_effort",
                search_summary=f"{search_result.search_summary}, ingest_status={ingest_status.ingest_status}",
                matched_nodes_count=search_result.matched_nodes_count,
                matched_facts_count=search_result.matched_facts_count,
                nodes=search_result.nodes,
                facts=search_result.facts,
                errors=search_result.errors,
            )

        errors.extend(search_result.errors)
        if ingest_status.last_error:
            errors.append(ingest_status.last_error)

        result = GraphitiPreflightResult(
            work_item_id=work_item.work_item_id,
            server_status=server_status.server_status,
            ingest_status=ingest_status.ingest_status,
            search_outcome=search_result.search_outcome,
            search_summary=search_result.search_summary,
            matched_nodes_count=search_result.matched_nodes_count,
            matched_facts_count=search_result.matched_facts_count,
            wait_seconds=max_wait_seconds,
            timings={
                "status_ms": status_ms,
                "wait_ms": wait_ms,
                "search_ms": search_ms,
            },
            queries={
                "entity_queries": query_bundle.entity_queries,
                "fact_queries": query_bundle.fact_queries,
            },
            errors=_dedupe_preserve_order(errors),
            episode_uuid=(ingest_status.episode_uuid or (write_result.episode_uuid if write_result else None)),
            group_id=(ingest_status.group_id or (write_result.group_id if write_result else None)),
            queue_position=(
                ingest_status.queue_position
                if ingest_status.queue_position is not None
                else (write_result.queue_position if write_result else None)
            ),
            processed_at=ingest_status.processed_at,
        )

        self._service.record_automation_event(
            actor,
            work_item_id=work_item.work_item_id,
            event_type="automation.graphiti_preflight_checked",
            payload=result.to_event_payload(actor_cli=actor.cli_name, branch=work_item.branch),
        )
        return result

    def remember(
        self,
        *,
        actor: ActorIdentity,
        work_item_id: str,
        task_path: Path | None = None,
        max_wait_seconds: int = 60,
    ) -> GraphitiMemoryRecordResult:
        work_item = self._require_service().get_work_item(actor, work_item_id)
        if work_item is None:
            raise KeyError(f"Unknown work item: {work_item_id}")

        status_started = time.perf_counter()
        server_status = self._adapter.get_server_status()
        status_ms = round((time.perf_counter() - status_started) * 1000, 2)
        wait_ms = 0.0
        write_result: GraphitiWriteResult | None = None
        errors: list[str] = []

        if server_status.server_status == "ok":
            write_result, ingest_status, wait_ms, write_errors = self._write_memory(
                name=f"task record {work_item.work_item_id}",
                episode_body=self._build_memory_body(work_item, task_path),
                group_id=DEFAULT_WRITE_GROUP_ID,
                max_wait_seconds=max_wait_seconds,
                source_description="explicit task memory record",
            )
            errors.extend(write_errors)
        else:
            ingest_status = GraphitiIngestStatus(
                ingest_status="failed",
                episode_uuid=None,
                group_id=DEFAULT_WRITE_GROUP_ID,
                queue_depth=None,
                queue_position=None,
                processed_at=None,
                last_error=server_status.message or "Graphiti server unavailable",
            )
            errors.append(server_status.message or "Graphiti server unavailable")

        if ingest_status.last_error:
            errors.append(ingest_status.last_error)

        result = GraphitiMemoryRecordResult(
            work_item_id=work_item.work_item_id,
            server_status=server_status.server_status,
            ingest_status=ingest_status.ingest_status,
            episode_uuid=(ingest_status.episode_uuid or (write_result.episode_uuid if write_result else None)),
            group_id=(ingest_status.group_id or (write_result.group_id if write_result else None)),
            queue_position=(
                ingest_status.queue_position
                if ingest_status.queue_position is not None
                else (write_result.queue_position if write_result else None)
            ),
            processed_at=ingest_status.processed_at,
            wait_seconds=max_wait_seconds,
            timings={
                "status_ms": status_ms,
                "wait_ms": wait_ms,
            },
            message=write_result.message if write_result else None,
            errors=_dedupe_preserve_order(errors),
        )

        self._service.record_automation_event(
            actor,
            work_item_id=work_item.work_item_id,
            event_type="automation.graphiti_memory_recorded",
            payload=result.to_event_payload(actor_cli=actor.cli_name, branch=work_item.branch),
        )
        return result

    def remember_generic(
        self,
        *,
        actor_cli: str,
        group_id: str,
        name: str,
        body: str,
        max_wait_seconds: int = 60,
    ) -> GraphitiMemoryRecordResult:
        status_started = time.perf_counter()
        server_status = self._adapter.get_server_status()
        status_ms = round((time.perf_counter() - status_started) * 1000, 2)
        wait_ms = 0.0
        write_result: GraphitiWriteResult | None = None
        errors: list[str] = []

        if server_status.server_status == "ok":
            write_result, ingest_status, wait_ms, write_errors = self._write_memory(
                name=name,
                episode_body=body,
                group_id=group_id,
                max_wait_seconds=max_wait_seconds,
                source_description=f"generic memory record by {actor_cli}",
            )
            errors.extend(write_errors)
        else:
            ingest_status = GraphitiIngestStatus(
                ingest_status="failed",
                episode_uuid=None,
                group_id=group_id,
                queue_depth=None,
                queue_position=None,
                processed_at=None,
                last_error=server_status.message or "Graphiti server unavailable",
            )
            errors.append(server_status.message or "Graphiti server unavailable")

        if ingest_status.last_error:
            errors.append(ingest_status.last_error)

        result = GraphitiMemoryRecordResult(
            work_item_id=None,
            server_status=server_status.server_status,
            ingest_status=ingest_status.ingest_status,
            episode_uuid=(ingest_status.episode_uuid or (write_result.episode_uuid if write_result else None)),
            group_id=(ingest_status.group_id or (write_result.group_id if write_result else None)),
            queue_position=(
                ingest_status.queue_position
                if ingest_status.queue_position is not None
                else (write_result.queue_position if write_result else None)
            ),
            processed_at=ingest_status.processed_at,
            wait_seconds=max_wait_seconds,
            timings={
                "status_ms": status_ms,
                "wait_ms": wait_ms,
            },
            message=write_result.message if write_result else None,
            errors=_dedupe_preserve_order(errors),
        )
        return result

    def search_generic(
        self,
        *,
        actor_cli: str,
        query: str,
        group_ids: list[str],
        query_type: str = "all",
        max_nodes: int = 5,
        max_facts: int = 5,
    ) -> GraphitiMemorySearchResult:
        status_started = time.perf_counter()
        server_status = self._adapter.get_server_status()
        status_ms = round((time.perf_counter() - status_started) * 1000, 2)

        if query_type == "nodes":
            query_bundle = GraphitiQueryBundle(entity_queries=[query], fact_queries=[])
        elif query_type == "facts":
            query_bundle = GraphitiQueryBundle(entity_queries=[], fact_queries=[query])
        else:
            query_bundle = GraphitiQueryBundle(entity_queries=[query], fact_queries=[query])

        search_started = time.perf_counter()
        if server_status.server_status == "ok":
            search_result = self._adapter.search_context(
                query_bundle,
                group_ids=group_ids,
                max_nodes=max_nodes,
                max_facts=max_facts,
            )
        else:
            search_result = GraphitiSearchResult(
                search_outcome="error",
                search_summary=server_status.message or "Graphiti server unavailable",
                matched_nodes_count=0,
                matched_facts_count=0,
                nodes=[],
                facts=[],
                errors=[server_status.message or "Graphiti server unavailable"],
            )
        search_ms = round((time.perf_counter() - search_started) * 1000, 2)

        return GraphitiMemorySearchResult(
            server_status=server_status.server_status,
            query=query,
            group_ids=group_ids,
            query_type=query_type,
            search_outcome=search_result.search_outcome,
            search_summary=search_result.search_summary,
            matched_nodes_count=search_result.matched_nodes_count,
            matched_facts_count=search_result.matched_facts_count,
            timings={
                "status_ms": status_ms,
                "search_ms": search_ms,
            },
            nodes=search_result.nodes,
            facts=search_result.facts,
            errors=_dedupe_preserve_order(search_result.errors),
        )

    def _build_query_bundle(self, work_item: WorkItemRecord, task_path: Path | None) -> GraphitiQueryBundle:
        task_excerpt = _read_task_excerpt(task_path)
        entity_queries = _dedupe_preserve_order(
            [
                work_item.title,
                work_item.task_key,
                *[Path(path).name for path in work_item.allowed_paths[:3]],
            ]
        )
        fact_queries = _dedupe_preserve_order(
            [
                work_item.objective,
                f"{work_item.title} why this change",
                f"{work_item.task_key} known risks",
                task_excerpt,
            ]
        )
        return GraphitiQueryBundle(entity_queries=entity_queries, fact_queries=fact_queries)

    def _build_memory_body(self, work_item: WorkItemRecord, task_path: Path | None) -> str:
        task_excerpt = _read_task_excerpt(task_path)
        lines = [
            f"Issue Identifier: {work_item.work_item_id}",
            f"Issue Title: {work_item.title}",
            f"Objective: {work_item.objective}",
            f"Branch: {work_item.branch}",
            f"Owner CLI: {work_item.owner_cli}",
        ]
        if task_excerpt:
            lines.append(f"TASK excerpt: {task_excerpt}")
        return "\n".join(lines)

    def _require_service(self) -> CoordinationService:
        if self._service is None:
            raise RuntimeError("Mongo-backed coordination service is required for this Graphiti operation")
        return self._service

    def _write_memory_for_work_item(
        self,
        *,
        work_item: WorkItemRecord,
        task_path: Path | None,
        max_wait_seconds: int,
        name: str,
        source_description: str,
    ) -> tuple[GraphitiWriteResult | None, GraphitiIngestStatus, float, list[str]]:
        return self._write_memory(
            name=name,
            episode_body=self._build_memory_body(work_item, task_path),
            group_id=DEFAULT_WRITE_GROUP_ID,
            max_wait_seconds=max_wait_seconds,
            source_description=source_description,
        )

    def _write_memory(
        self,
        *,
        name: str,
        episode_body: str,
        group_id: str,
        max_wait_seconds: int,
        source_description: str,
    ) -> tuple[GraphitiWriteResult | None, GraphitiIngestStatus, float, list[str]]:
        wait_started = time.perf_counter()
        errors: list[str] = []

        try:
            write_result = self._adapter.add_memory(
                name=name,
                episode_body=episode_body,
                group_id=group_id,
                source_description=source_description,
            )
            if write_result.episode_uuid:
                ingest_status = self._adapter.wait_for_ingest(
                    episode_uuid=write_result.episode_uuid,
                    group_id=write_result.group_id or group_id,
                    max_wait_seconds=max_wait_seconds,
                )
            else:
                ingest_status = GraphitiIngestStatus(
                    ingest_status="best_effort",
                    episode_uuid=None,
                    group_id=write_result.group_id or group_id,
                    queue_depth=None,
                    queue_position=write_result.queue_position,
                    processed_at=None,
                    last_error="Graphiti add_memory did not return an episode_uuid",
                )
        except Exception as exc:
            write_result = None
            ingest_status = GraphitiIngestStatus(
                ingest_status="failed",
                episode_uuid=None,
                group_id=group_id,
                queue_depth=None,
                queue_position=None,
                processed_at=None,
                last_error=str(exc),
            )
            errors.append(str(exc))

        wait_ms = round((time.perf_counter() - wait_started) * 1000, 2)
        return write_result, ingest_status, wait_ms, errors


def _read_task_excerpt(task_path: Path | None) -> str:
    if task_path is None or not task_path.exists():
        return ""
    try:
        content = task_path.read_text(encoding="utf-8")
    except OSError:
        return ""

    lines = [line.strip() for line in content.splitlines() if line.strip()]
    if not lines:
        return ""
    return " | ".join(lines[:3])


def _dedupe_preserve_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    results: list[str] = []
    for value in values:
        cleaned = value.strip()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        results.append(cleaned)
    return results
