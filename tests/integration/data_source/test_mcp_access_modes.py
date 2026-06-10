from __future__ import annotations

import pytest

from src.core.data_source.client import DataSourceRequest, RouteDecision
from src.core.data_source.mcp_diagnostics import (
    DATA_SOURCE_MCP_HOT_PATH_TOOL_DENYLIST,
    DATA_SOURCE_MCP_TOOL_NAMES,
    MCPDiagnosticsError,
    create_data_source_mcp_diagnostics,
)


class FakeDataSourceClient:
    def __init__(self) -> None:
        self.route_requests: list[DataSourceRequest] = []
        self.fetch_calls = 0
        self.batch_calls = 0

    def resolve_route(self, request: DataSourceRequest) -> RouteDecision:
        self.route_requests.append(request)
        return RouteDecision(
            data_category=request.data_category,
            endpoint_name="akshare.stock_zh_a_spot",
            source="akshare",
            endpoint_info={"transport": "rest_pull"},
            route_decision_id=f"route-{request.request_id}",
            fallback_candidates=("akshare.stock_info_a_code_name", "local_cache"),
            reason="akshare_realtime_quotes_primary",
        )

    def fetch_snapshot(self, request: DataSourceRequest):  # pragma: no cover - guard only
        self.fetch_calls += 1
        raise AssertionError("MCP diagnostics must not call hot-path fetch_snapshot")

    def fetch_batch(self, requests):  # pragma: no cover - guard only
        self.batch_calls += 1
        raise AssertionError("MCP diagnostics must not call hot-path fetch_batch")


class FakeRemoteTransport:
    def __init__(self) -> None:
        self.requests: list[tuple[str, dict]] = []

    def post_json(self, path: str, payload: dict, timeout_ms: int | None = None) -> dict:
        self.requests.append((path, payload))
        assert timeout_ms == 1500
        assert path == "/routing/best"
        return {
            "data_category": payload["data_category"],
            "endpoint_name": "akshare.stock_zh_a_spot",
            "source": "akshare",
            "endpoint_info": {"transport": "rest_pull"},
            "route_decision_id": f"route-{payload['request_id']}",
            "fallback_candidates": ["akshare.stock_info_a_code_name", "local_cache"],
            "reason": "akshare_realtime_quotes_primary",
        }


def test_mcp_diagnostics_declares_admin_tools_and_blocks_hot_path_tools():
    assert DATA_SOURCE_MCP_TOOL_NAMES == (
        "get_data_source_health",
        "explain_route_decision",
    )
    assert DATA_SOURCE_MCP_HOT_PATH_TOOL_DENYLIST == (
        "fetch_snapshot",
        "fetch_batch",
        "stream_market",
        "subscribe_market",
    )

    diagnostics = create_data_source_mcp_diagnostics(access_mode="stdio", client=FakeDataSourceClient())

    assert [tool["name"] for tool in diagnostics.tools()] == list(DATA_SOURCE_MCP_TOOL_NAMES)
    assert all(tool["hot_path"] is False for tool in diagnostics.tools())


def test_stdio_mcp_explains_route_without_fetching_data():
    client = FakeDataSourceClient()
    diagnostics = create_data_source_mcp_diagnostics(access_mode="stdio", client=client)

    result = diagnostics.call_tool(
        "explain_route_decision",
        {
            "data_category": "REALTIME_QUOTES",
            "params": {"symbol": "000001"},
            "request_id": "mcp-stdio",
            "timeout_ms": 1500,
        },
    )

    assert diagnostics.access_mode == "stdio"
    assert diagnostics.transport == "stdio"
    assert client.fetch_calls == 0
    assert client.batch_calls == 0
    assert client.route_requests[0].data_category == "REALTIME_QUOTES"
    assert result == {
        "tool": "explain_route_decision",
        "access_mode": "stdio",
        "transport": "stdio",
        "diagnostic": {
            "data_category": "REALTIME_QUOTES",
            "source": "akshare",
            "endpoint_name": "akshare.stock_zh_a_spot",
            "route_decision_id": "route-mcp-stdio",
            "fallback_candidates": [
                "akshare.stock_info_a_code_name",
                "local_cache",
            ],
            "reason": "akshare_realtime_quotes_primary",
        },
    }


def test_standalone_remote_mcp_calls_rest_route_only():
    transport = FakeRemoteTransport()
    diagnostics = create_data_source_mcp_diagnostics(
        access_mode="standalone_remote",
        base_url="http://openstock.test",
        transport=transport,
    )

    result = diagnostics.call_tool(
        "explain_route_decision",
        {
            "data_category": "REALTIME_QUOTES",
            "params": {"symbol": "000001"},
            "request_id": "mcp-remote",
            "timeout_ms": 1500,
        },
    )

    assert diagnostics.access_mode == "standalone_remote"
    assert diagnostics.transport == "streamable_http"
    assert [path for path, _payload in transport.requests] == ["/routing/best"]
    assert result["diagnostic"]["route_decision_id"] == "route-mcp-remote"


def test_mounted_mcp_reuses_supplied_runtime_client_identity():
    client = FakeDataSourceClient()
    diagnostics = create_data_source_mcp_diagnostics(access_mode="mounted", client=client)

    health = diagnostics.call_tool("get_data_source_health", {"request_id": "mcp-health"})
    route = diagnostics.call_tool(
        "explain_route_decision",
        {"data_category": "REALTIME_QUOTES", "request_id": "mcp-mounted"},
    )

    assert diagnostics.access_mode == "mounted"
    assert diagnostics.transport == "mounted"
    assert diagnostics.runtime_identity == id(client)
    assert health["diagnostic"]["runtime_identity"] == id(client)
    assert route["diagnostic"]["route_decision_id"] == "route-mcp-mounted"


@pytest.mark.parametrize("tool_name", DATA_SOURCE_MCP_HOT_PATH_TOOL_DENYLIST)
def test_mcp_diagnostics_rejects_hot_path_tools(tool_name: str):
    diagnostics = create_data_source_mcp_diagnostics(access_mode="stdio", client=FakeDataSourceClient())

    with pytest.raises(MCPDiagnosticsError, match=f"hot-path tool: {tool_name}"):
        diagnostics.call_tool(tool_name, {})
