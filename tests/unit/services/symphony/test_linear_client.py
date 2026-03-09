import json
from datetime import datetime, timezone

import httpx

from src.services.symphony.config import TrackerConfig
from src.services.symphony.linear_client import LinearIssueTrackerClient


def _make_tracker_config() -> TrackerConfig:
    return TrackerConfig(
        kind="linear",
        endpoint="https://api.linear.app/graphql",
        api_key="token",
        project_slug="mystocks",
        active_states=["todo", "in progress"],
        terminal_states=["done", "cancelled"],
    )


def test_fetch_candidate_issues_preserves_pagination_order_and_project_filter() -> None:
    requests: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content.decode("utf-8"))
        requests.append(payload)
        page_number = len(requests)

        if page_number == 1:
            body = {
                "data": {
                    "issues": {
                        "nodes": [
                            {
                                "id": "issue-1",
                                "identifier": "MT-1",
                                "title": "First",
                                "description": "Body",
                                "priority": 1,
                                "branchName": "feature/mt-1",
                                "url": "https://linear.app/mt-1",
                                "labels": {"nodes": [{"name": "Ops"}]},
                                "state": {"name": "Todo"},
                                "relations": {"nodes": []},
                                "createdAt": "2026-03-01T00:00:00Z",
                                "updatedAt": "2026-03-01T00:00:00Z",
                            },
                            {
                                "id": "issue-2",
                                "identifier": "MT-2",
                                "title": "Second",
                                "description": None,
                                "priority": 2,
                                "branchName": None,
                                "url": None,
                                "labels": {"nodes": [{"name": "Feature"}]},
                                "state": {"name": "In Progress"},
                                "relations": {"nodes": []},
                                "createdAt": "2026-03-02T00:00:00Z",
                                "updatedAt": "2026-03-02T00:00:00Z",
                            },
                        ],
                        "pageInfo": {"hasNextPage": True, "endCursor": "cursor-1"},
                    }
                }
            }
        else:
            body = {
                "data": {
                    "issues": {
                        "nodes": [
                            {
                                "id": "issue-3",
                                "identifier": "MT-3",
                                "title": "Third",
                                "description": "Tail",
                                "priority": None,
                                "branchName": None,
                                "url": None,
                                "labels": {"nodes": []},
                                "state": {"name": "Todo"},
                                "relations": {"nodes": []},
                                "createdAt": "2026-03-03T00:00:00Z",
                                "updatedAt": "2026-03-03T00:00:00Z",
                            }
                        ],
                        "pageInfo": {"hasNextPage": False, "endCursor": "cursor-2"},
                    }
                }
            }

        return httpx.Response(status_code=200, json=body)

    client = LinearIssueTrackerClient(tracker=_make_tracker_config(), transport=httpx.MockTransport(handler))

    issues = client.fetch_candidate_issues()

    assert [issue.identifier for issue in issues] == ["MT-1", "MT-2", "MT-3"]
    assert len(requests) == 2
    assert "slugId" in requests[0]["query"]
    assert requests[0]["variables"]["projectSlug"] == "mystocks"
    assert requests[0]["variables"]["stateNames"] == ["todo", "in progress"]


def test_fetch_candidate_issues_prefers_tracker_state_names_for_graphql_filters() -> None:
    requests: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(json.loads(request.content.decode("utf-8")))
        return httpx.Response(
            status_code=200,
            json={
                "data": {
                    "issues": {
                        "nodes": [],
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                    }
                }
            },
        )

    tracker = TrackerConfig(
        kind="linear",
        endpoint="https://api.linear.app/graphql",
        api_key="token",
        project_slug="mystocks",
        active_states=["todo", "in progress"],
        terminal_states=["done", "cancelled"],
        active_state_names=["Todo", "In Progress"],
        terminal_state_names=["Done", "Cancelled"],
    )
    client = LinearIssueTrackerClient(tracker=tracker, transport=httpx.MockTransport(handler))

    client.fetch_candidate_issues()

    assert requests[0]["variables"]["stateNames"] == ["Todo", "In Progress"]


def test_fetch_candidate_issues_normalizes_labels_blockers_and_priority() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json={
                "data": {
                    "issues": {
                        "nodes": [
                            {
                                "id": "issue-1",
                                "identifier": "MT-1",
                                "title": "Blocked issue",
                                "description": "Body",
                                "priority": "high",
                                "branchName": None,
                                "url": "https://linear.app/mt-1",
                                "labels": {"nodes": [{"name": "Feature"}, {"name": "Urgent"}]},
                                "state": {"name": "Todo"},
                                "relations": {
                                    "nodes": [
                                        {
                                            "type": "blocks",
                                            "relatedIssue": {
                                                "id": "issue-2",
                                                "identifier": "MT-2",
                                                "state": {"name": "In Progress"},
                                            },
                                        }
                                    ]
                                },
                                "createdAt": "2026-03-01T12:30:00Z",
                                "updatedAt": "2026-03-02T12:30:00Z",
                            }
                        ],
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                    }
                }
            },
        )

    client = LinearIssueTrackerClient(tracker=_make_tracker_config(), transport=httpx.MockTransport(handler))

    issue = client.fetch_candidate_issues()[0]

    assert issue.labels == ["feature", "urgent"]
    assert issue.priority is None
    assert issue.blocked_by[0].identifier == "MT-2"
    assert issue.blocked_by[0].state == "In Progress"
    assert issue.created_at == datetime(2026, 3, 1, 12, 30, tzinfo=timezone.utc)
    assert issue.updated_at == datetime(2026, 3, 2, 12, 30, tzinfo=timezone.utc)


def test_fetch_issues_by_states_short_circuits_on_empty_input() -> None:
    called = False

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal called
        called = True
        return httpx.Response(status_code=200, json={"data": {}})

    client = LinearIssueTrackerClient(tracker=_make_tracker_config(), transport=httpx.MockTransport(handler))

    issues = client.fetch_issues_by_states([])

    assert issues == []
    assert called is False
