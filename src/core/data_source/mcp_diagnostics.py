from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Mapping

from src.core.data_source.client import (
    DataSourceClient,
    DataSourceRequest,
    DataSourceTransport,
    RemoteDataSourceClient,
    RouteDecision,
    create_data_source_client,
)

DATA_SOURCE_MCP_ACCESS_MODES = ("stdio", "standalone_remote", "mounted")
DATA_SOURCE_MCP_TOOL_NAMES = (
    "get_data_source_health",
    "explain_route_decision",
)
DATA_SOURCE_MCP_HOT_PATH_TOOL_DENYLIST = (
    "fetch_snapshot",
    "fetch_batch",
    "stream_market",
    "subscribe_market",
)


class MCPDiagnosticsError(RuntimeError):
    """Raised when a diagnostics MCP tool request violates the access contract."""


@dataclass(frozen=True)
class DataSourceMCPDiagnostics:
    """Diagnostic/admin tool surface shared by future MCP transports."""

    access_mode: str
    transport: str
    client: DataSourceClient
    runtime_identity: int | str

    def tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": "get_data_source_health",
                "description": "Return diagnostics-plane health without fetching market data.",
                "access_mode": self.access_mode,
                "transport": self.transport,
                "hot_path": False,
                "input_schema": {
                    "type": "object",
                    "properties": {"request_id": {"type": "string"}},
                },
            },
            {
                "name": "explain_route_decision",
                "description": "Resolve and explain the route decision for a data category.",
                "access_mode": self.access_mode,
                "transport": self.transport,
                "hot_path": False,
                "input_schema": {
                    "type": "object",
                    "required": ["data_category"],
                    "properties": {
                        "data_category": {"type": "string"},
                        "params": {"type": "object"},
                        "request_id": {"type": "string"},
                        "timeout_ms": {"type": "integer"},
                    },
                },
            },
        ]

    def call_tool(self, tool_name: str, arguments: Mapping[str, Any] | None = None) -> dict[str, Any]:
        args = arguments or {}
        if tool_name in DATA_SOURCE_MCP_HOT_PATH_TOOL_DENYLIST:
            raise MCPDiagnosticsError(f"MCP diagnostics do not expose hot-path tool: {tool_name}")
        if tool_name == "get_data_source_health":
            return self._health_result(args)
        if tool_name == "explain_route_decision":
            return self._route_result(args)
        raise MCPDiagnosticsError(f"Unsupported MCP diagnostics tool: {tool_name}")

    def _health_result(self, arguments: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "tool": "get_data_source_health",
            "access_mode": self.access_mode,
            "transport": self.transport,
            "diagnostic": {
                "status": "ready",
                "scope": "diagnostics",
                "request_id": _text(arguments.get("request_id"), "mcp-health"),
                "runtime_identity": self.runtime_identity,
                "hot_path": False,
            },
        }

    def _route_result(self, arguments: Mapping[str, Any]) -> dict[str, Any]:
        request = _request_from_arguments(arguments)
        decision = self.client.resolve_route(request)
        return {
            "tool": "explain_route_decision",
            "access_mode": self.access_mode,
            "transport": self.transport,
            "diagnostic": _route_decision_payload(decision),
        }


def create_data_source_mcp_diagnostics(
    *,
    access_mode: str,
    client: DataSourceClient | None = None,
    base_url: str | None = None,
    transport: DataSourceTransport | None = None,
) -> DataSourceMCPDiagnostics:
    mode = access_mode.strip().lower()
    if mode == "stdio":
        diagnostics_client = client or create_data_source_client(mode="local")
        return DataSourceMCPDiagnostics(
            access_mode=mode,
            transport="stdio",
            client=diagnostics_client,
            runtime_identity=id(diagnostics_client),
        )
    if mode == "standalone_remote":
        resolved_base_url = base_url or os.getenv("OPENSTOCK_BASE_URL") or "http://localhost:8031"
        diagnostics_client = client or RemoteDataSourceClient(
            base_url=resolved_base_url,
            transport=transport,
        )
        return DataSourceMCPDiagnostics(
            access_mode=mode,
            transport="streamable_http",
            client=diagnostics_client,
            runtime_identity=resolved_base_url,
        )
    if mode == "mounted":
        if client is None:
            raise MCPDiagnosticsError("mounted MCP diagnostics require a runtime client")
        return DataSourceMCPDiagnostics(
            access_mode=mode,
            transport="mounted",
            client=client,
            runtime_identity=id(client),
        )
    raise MCPDiagnosticsError(f"Unsupported MCP diagnostics access mode: {access_mode}")


def _request_from_arguments(arguments: Mapping[str, Any]) -> DataSourceRequest:
    params = arguments.get("params")
    return DataSourceRequest(
        data_category=_text(arguments.get("data_category")),
        params=params if isinstance(params, Mapping) else {},
        request_id=_text(arguments.get("request_id"), "mcp-route"),
        timeout_ms=_optional_int(arguments.get("timeout_ms")),
    )


def _route_decision_payload(decision: RouteDecision) -> dict[str, Any]:
    return {
        "data_category": decision.data_category,
        "source": decision.source,
        "endpoint_name": decision.endpoint_name,
        "route_decision_id": decision.route_decision_id,
        "fallback_candidates": list(decision.fallback_candidates),
        "reason": decision.reason,
    }


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _text(value: Any, default: str = "") -> str:
    text = str(value or "").strip()
    return text or default
