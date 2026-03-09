import json

from src.services.symphony.config import TrackerConfig
from src.services.symphony.dynamic_tools import build_dynamic_tools


class _FakeLinearTrackerClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict, str | None]] = []

    def execute_raw_graphql(self, query: str, variables: dict | None = None, operation_name: str | None = None) -> dict:
        self.calls.append((query, variables or {}, operation_name))
        return {"projects": {"nodes": [{"id": "p-1", "name": "mystocks"}]}}


def test_build_dynamic_tools_returns_linear_graphql_when_enabled() -> None:
    tracker_config = TrackerConfig(
        kind="linear",
        endpoint="https://api.linear.app/graphql",
        api_key="token",
        project_slug="mystocks",
        active_states=["todo"],
        terminal_states=["done"],
        active_state_names=["Todo"],
        terminal_state_names=["Done"],
        enable_linear_graphql_tool=True,
    )
    tracker_client = _FakeLinearTrackerClient()

    dynamic_tools = build_dynamic_tools(tracker_config=tracker_config, tracker_client=tracker_client)

    result = dynamic_tools["linear_graphql"].handler(
        {
            "query": "query Projects { projects { nodes { id name } } }",
            "variables": {"limit": 1},
            "operationName": "Projects",
        }
    )

    assert tracker_client.calls == [
        (
            "query Projects { projects { nodes { id name } } }",
            {"limit": 1},
            "Projects",
        )
    ]
    assert result.success is True
    assert json.loads(result.content_items[0]["text"]) == {
        "data": {"projects": {"nodes": [{"id": "p-1", "name": "mystocks"}]}}
    }


def test_build_dynamic_tools_omits_linear_graphql_when_disabled() -> None:
    tracker_config = TrackerConfig(
        kind="linear",
        endpoint="https://api.linear.app/graphql",
        api_key="token",
        project_slug="mystocks",
        active_states=["todo"],
        terminal_states=["done"],
        active_state_names=["Todo"],
        terminal_state_names=["Done"],
        enable_linear_graphql_tool=False,
    )

    dynamic_tools = build_dynamic_tools(tracker_config=tracker_config, tracker_client=_FakeLinearTrackerClient())

    assert dynamic_tools == {}
