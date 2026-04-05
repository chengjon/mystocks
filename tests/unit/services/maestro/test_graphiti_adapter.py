from __future__ import annotations

import pytest

from src.services.maestro.collab.integrations.graphiti_adapter import (
    GraphitiMcpTransport,
    GraphitiTransportError,
    _extract_content_text,
)


def test_graphiti_mcp_transport_rejects_non_http_urls() -> None:
    with pytest.raises(GraphitiTransportError, match="http"):
        GraphitiMcpTransport(url="file:///tmp/graphiti-mcp")


def test_extract_content_text_rejects_non_string_payload() -> None:
    with pytest.raises(GraphitiTransportError, match="Unexpected MCP payload"):
        _extract_content_text({"result": {"content": [{"text": 123}]}})
