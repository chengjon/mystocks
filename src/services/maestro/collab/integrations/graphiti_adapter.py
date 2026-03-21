from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Protocol

from .models import (
    GraphitiIngestStatus,
    GraphitiQueryBundle,
    GraphitiSearchResult,
    GraphitiServerStatus,
    GraphitiWriteResult,
)

PROJECT_ROOT = Path(__file__).resolve().parents[6]
DEFAULT_GRAPHITI_MCP_URL = "http://192.168.123.104:8011/mcp"
DEFAULT_MAX_WAIT_SECONDS = 60
DEFAULT_POLL_INTERVAL_SECONDS = 5


class GraphitiTransportError(RuntimeError):
    """Raised when repo-local Graphiti transport fails."""


class GraphitiTransport(Protocol):
    def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]: ...


class GraphitiMcpTransport:
    def __init__(self, url: str | None = None, timeout_seconds: int = 90) -> None:
        self._url = url or _resolve_graphiti_mcp_url()
        self._timeout_seconds = timeout_seconds
        self._session_id: str | None = None
        self._request_id = 1

    def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        self._ensure_initialized()
        response = self._post(
            {
                "jsonrpc": "2.0",
                "id": self._next_request_id(),
                "method": "tools/call",
                "params": {"name": name, "arguments": arguments or {}},
            }
        )
        return _extract_content_object(response)

    def _ensure_initialized(self) -> None:
        if self._session_id is not None:
            return
        self._post(
            {
                "jsonrpc": "2.0",
                "id": self._next_request_id(),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {},
                    "clientInfo": {"name": "mystocks-graphiti-adapter", "version": "1.0"},
                },
            }
        )

    def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self._session_id:
            headers["mcp-session-id"] = self._session_id
        request = urllib.request.Request(self._url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self._timeout_seconds) as response:
                self._session_id = response.headers.get("mcp-session-id") or self._session_id
                response_text = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            response_text = exc.read().decode("utf-8", errors="replace")
            self._session_id = exc.headers.get("mcp-session-id") or self._session_id
            raise GraphitiTransportError(f"HTTP {exc.code}: {_best_effort_error_text(response_text)}") from exc
        except urllib.error.URLError as exc:
            raise GraphitiTransportError(str(exc.reason)) from exc

        try:
            return json.loads(_parse_sse_data(response_text))
        except (json.JSONDecodeError, ValueError) as exc:
            raise GraphitiTransportError(f"Invalid MCP response: {response_text[:200]}") from exc

    def _next_request_id(self) -> int:
        self._request_id += 1
        return self._request_id


class GraphitiAdapter:
    def __init__(
        self,
        *,
        transport: GraphitiTransport | None = None,
        time_fn=time.monotonic,
        sleep_fn=time.sleep,
    ) -> None:
        self._transport = transport or GraphitiMcpTransport()
        self._time_fn = time_fn
        self._sleep_fn = sleep_fn

    def get_server_status(self) -> GraphitiServerStatus:
        try:
            payload = self._transport.call_tool("get_status")
            return GraphitiServerStatus(
                server_status="ok" if payload.get("status") == "ok" else "error",
                message=payload.get("message"),
                details=payload.get("details"),
            )
        except Exception as exc:
            return GraphitiServerStatus(
                server_status="error",
                message=str(exc),
                details=None,
            )

    def add_memory(
        self,
        *,
        name: str,
        episode_body: str,
        group_id: str,
        source: str = "text",
        source_description: str = "",
    ) -> GraphitiWriteResult:
        payload = self._transport.call_tool(
            "add_memory",
            {
                "name": name,
                "episode_body": episode_body,
                "group_id": group_id,
                "source": source,
                "source_description": source_description,
            },
        )
        return GraphitiWriteResult(
            episode_uuid=payload.get("episode_uuid"),
            group_id=payload.get("group_id", group_id),
            queue_position=payload.get("queue_position"),
            message=payload.get("message"),
        )

    def wait_for_ingest(
        self,
        *,
        episode_uuid: str,
        group_id: str,
        max_wait_seconds: int = DEFAULT_MAX_WAIT_SECONDS,
        poll_interval_seconds: int = DEFAULT_POLL_INTERVAL_SECONDS,
    ) -> GraphitiIngestStatus:
        deadline = self._time_fn() + max_wait_seconds
        last_payload: dict[str, Any] | None = None

        while True:
            try:
                last_payload = self._transport.call_tool(
                    "get_ingest_status",
                    {
                        "episode_uuid": episode_uuid,
                        "group_id": group_id,
                    },
                )
            except GraphitiTransportError as exc:
                if "Unknown tool" in str(exc) or "not found" in str(exc):
                    return GraphitiIngestStatus(
                        ingest_status="best_effort",
                        episode_uuid=episode_uuid,
                        group_id=group_id,
                        queue_depth=None,
                        queue_position=None,
                        processed_at=None,
                        last_error=str(exc),
                    )
                return GraphitiIngestStatus(
                    ingest_status="failed",
                    episode_uuid=episode_uuid,
                    group_id=group_id,
                    queue_depth=None,
                    queue_position=None,
                    processed_at=None,
                    last_error=str(exc),
                )

            state = last_payload.get("state")
            if state == "completed":
                return GraphitiIngestStatus(
                    ingest_status="completed",
                    episode_uuid=last_payload.get("episode_uuid", episode_uuid),
                    group_id=last_payload.get("group_id", group_id),
                    queue_depth=last_payload.get("queue_depth"),
                    queue_position=last_payload.get("queue_position"),
                    processed_at=last_payload.get("processed_at"),
                    last_error=last_payload.get("last_error"),
                )
            if state == "failed":
                return GraphitiIngestStatus(
                    ingest_status="failed",
                    episode_uuid=last_payload.get("episode_uuid", episode_uuid),
                    group_id=last_payload.get("group_id", group_id),
                    queue_depth=last_payload.get("queue_depth"),
                    queue_position=last_payload.get("queue_position"),
                    processed_at=last_payload.get("processed_at"),
                    last_error=last_payload.get("last_error"),
                )

            if self._time_fn() >= deadline:
                return GraphitiIngestStatus(
                    ingest_status="warming",
                    episode_uuid=last_payload.get("episode_uuid", episode_uuid),
                    group_id=last_payload.get("group_id", group_id),
                    queue_depth=last_payload.get("queue_depth"),
                    queue_position=last_payload.get("queue_position"),
                    processed_at=last_payload.get("processed_at"),
                    last_error=last_payload.get("last_error"),
                )

            self._sleep_fn(min(poll_interval_seconds, max(0.0, deadline - self._time_fn())))

    def search_context(
        self,
        query_bundle: GraphitiQueryBundle,
        *,
        group_ids: list[str] | None = None,
        max_nodes: int = 5,
        max_facts: int = 5,
    ) -> GraphitiSearchResult:
        node_map: dict[str, dict[str, Any]] = {}
        fact_map: dict[str, dict[str, Any]] = {}
        errors: list[str] = []

        for query in query_bundle.entity_queries:
            if not query.strip():
                continue
            try:
                payload = self._transport.call_tool(
                    "search_nodes",
                    {"query": query, "group_ids": group_ids or [], "max_nodes": max_nodes},
                )
                for node in payload.get("nodes", []) or []:
                    key = str(node.get("uuid") or node.get("name") or query)
                    node_map[key] = node
            except Exception as exc:
                errors.append(f"search_nodes({query}): {exc}")

        for query in query_bundle.fact_queries:
            if not query.strip():
                continue
            try:
                payload = self._transport.call_tool(
                    "search_memory_facts",
                    {"query": query, "group_ids": group_ids or [], "max_facts": max_facts},
                )
                for fact in payload.get("facts", []) or []:
                    key = str(fact.get("uuid") or fact.get("fact") or query)
                    fact_map[key] = fact
            except Exception as exc:
                errors.append(f"search_memory_facts({query}): {exc}")

        matched_nodes = list(node_map.values())
        matched_facts = list(fact_map.values())
        if matched_nodes or matched_facts:
            outcome = "hit"
        elif errors:
            outcome = "best_effort"
        else:
            outcome = "miss"

        summary = f"nodes hit={len(matched_nodes)}, facts hit={len(matched_facts)}"
        if errors:
            summary = f"{summary}, errors={len(errors)}"

        return GraphitiSearchResult(
            search_outcome=outcome,
            search_summary=summary,
            matched_nodes_count=len(matched_nodes),
            matched_facts_count=len(matched_facts),
            nodes=matched_nodes,
            facts=matched_facts,
            errors=errors,
        )


def _parse_sse_data(response_text: str) -> str:
    for line in response_text.splitlines():
        if line.startswith("data: "):
            return line[6:]
    raise ValueError("No SSE data line found")


def _extract_content_object(payload: dict[str, Any]) -> dict[str, Any]:
    if "error" in payload and "result" not in payload:
        error = payload["error"]
        raise GraphitiTransportError(str(error.get("message") or payload))

    structured_result = payload.get("result", {}).get("structuredContent", {}).get("result")
    if isinstance(structured_result, dict):
        return structured_result

    text = _extract_content_text(payload)
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        return {"message": text}
    return value if isinstance(value, dict) else {"value": value}


def _extract_content_text(payload: dict[str, Any]) -> str:
    try:
        return payload["result"]["content"][0]["text"]
    except Exception as exc:
        raise GraphitiTransportError(f"Unexpected MCP payload: {payload}") from exc


def _best_effort_error_text(response_text: str) -> str:
    match = re.search(r'"message"\s*:\s*"([^"]+)"', response_text)
    if match:
        return match.group(1)
    return response_text[:200]


def _resolve_graphiti_mcp_url() -> str:
    env_url = os.getenv("GRAPHITI_MCP_URL")
    if env_url:
        return env_url

    for candidate in (PROJECT_ROOT / ".mcp.json", PROJECT_ROOT / "config/.mcp.json"):
        if not candidate.exists():
            continue
        try:
            payload = json.loads(candidate.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        url = payload.get("mcpServers", {}).get("graphiti-memory", {}).get("url")
        if isinstance(url, str) and url:
            return url

    return DEFAULT_GRAPHITI_MCP_URL
