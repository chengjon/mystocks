from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable

from .config import TrackerConfig
from .errors import TrackerRequestError

DynamicToolHandler = Callable[[dict[str, Any]], "DynamicToolResult"]


@dataclass(frozen=True)
class DynamicToolDefinition:
    name: str
    description: str
    input_schema: dict[str, Any]
    handler: DynamicToolHandler

    def to_payload(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
        }


@dataclass(frozen=True)
class DynamicToolResult:
    success: bool
    content_items: list[dict[str, str]]
    error: str | None = None

    @classmethod
    def text(cls, text: str, success: bool = True, error: str | None = None) -> "DynamicToolResult":
        return cls(success=success, content_items=[{"type": "inputText", "text": text}], error=error)

    @classmethod
    def json(cls, payload: Any, success: bool = True, error: str | None = None) -> "DynamicToolResult":
        return cls.text(json.dumps(payload, ensure_ascii=False), success=success, error=error)

    def to_protocol_result(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "success": self.success,
            "contentItems": self.content_items,
        }
        if self.error is not None:
            payload["error"] = self.error
        return payload


def build_dynamic_tools(tracker_config: TrackerConfig, tracker_client: Any) -> dict[str, DynamicToolDefinition]:
    dynamic_tools: dict[str, DynamicToolDefinition] = {}

    if tracker_config.kind == "linear" and tracker_config.enable_linear_graphql_tool:
        dynamic_tools["linear_graphql"] = DynamicToolDefinition(
            name="linear_graphql",
            description=(
                "Run raw GraphQL requests against the configured Linear workspace. "
                "Accepts a GraphQL query and optional variables."
            ),
            input_schema={
                "type": "object",
                "required": ["query"],
                "properties": {
                    "query": {"type": "string"},
                    "variables": {"type": "object"},
                    "operationName": {"type": "string"},
                },
                "additionalProperties": False,
            },
            handler=_build_linear_graphql_handler(tracker_client),
        )

    return dynamic_tools


def _build_linear_graphql_handler(tracker_client: Any) -> DynamicToolHandler:
    def handler(arguments: dict[str, Any]) -> DynamicToolResult:
        query = arguments.get("query")
        variables = arguments.get("variables", {})
        operation_name = arguments.get("operationName")

        if not isinstance(query, str) or not query.strip():
            return DynamicToolResult.json(
                {"error": {"code": "invalid_dynamic_tool_arguments", "message": "Expected a non-empty GraphQL query."}},
                success=False,
                error="invalid_dynamic_tool_arguments",
            )

        if variables is None:
            variables = {}
        if not isinstance(variables, dict):
            return DynamicToolResult.json(
                {"error": {"code": "invalid_dynamic_tool_arguments", "message": "Expected variables to be an object."}},
                success=False,
                error="invalid_dynamic_tool_arguments",
            )

        if operation_name is not None and not isinstance(operation_name, str):
            return DynamicToolResult.json(
                {
                    "error": {
                        "code": "invalid_dynamic_tool_arguments",
                        "message": "Expected operationName to be a string.",
                    }
                },
                success=False,
                error="invalid_dynamic_tool_arguments",
            )

        try:
            payload = tracker_client.execute_raw_graphql(query, variables, operation_name=operation_name)
        except TrackerRequestError as exc:
            return DynamicToolResult.json(
                {"error": {"code": "linear_graphql_failed", "message": str(exc)}},
                success=False,
                error="linear_graphql_failed",
            )

        return DynamicToolResult.json({"data": payload})

    return handler
