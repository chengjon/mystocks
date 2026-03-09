from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from src.services.symphony.config import ServiceConfig
from src.services.symphony.models import Issue, WorkflowDefinition
from src.services.symphony.orchestrator import SymphonyOrchestrator
from src.services.symphony.status_api import create_status_app


class EmptyTracker:
    def fetch_candidate_issues(self) -> list[Issue]:
        return []

    def fetch_issue_states_by_ids(self, _: list[str]) -> list[Issue]:
        return []

    def fetch_issues_by_states(self, _: list[str]) -> list[Issue]:
        return []


class DummyRunnerFactory:
    def __call__(self, issue: Issue, attempt: int | None):
        return {"issue": issue.identifier, "attempt": attempt}


class DummyCollabRegistry:
    def get_issue_state(self, issue_identifier: str) -> dict:
        return {
            "assignment": {"issue_identifier": issue_identifier, "assigned_worker_cli": "cli-1", "status": "assigned"},
            "workspace": {"issue_identifier": issue_identifier, "workspace_key": issue_identifier},
            "heartbeat": {"issue_identifier": issue_identifier, "stale": False},
        }

    def list_workspaces(self) -> list[dict]:
        return [{"issue_identifier": "MT-1", "workspace_key": "MT-1"}]

    def list_stale_heartbeats(self, now=None) -> list[dict]:
        return [{"issue_identifier": "MT-9", "stale": True}]


def _make_orchestrator() -> SymphonyOrchestrator:
    workflow_definition = WorkflowDefinition(
        config={"tracker": {"kind": "linear", "project_slug": "mystocks", "api_key": "token"}},
        prompt_template="Prompt",
    )
    config = ServiceConfig.from_workflow_definition(workflow_definition)
    orchestrator = SymphonyOrchestrator(
        workflow_definition=workflow_definition,
        service_config=config,
        tracker_client=EmptyTracker(),
        runner_factory=DummyRunnerFactory(),
        collab_registry=DummyCollabRegistry(),
    )
    issue = Issue(
        id="issue-1",
        identifier="MT-1",
        title="Status",
        description="Body",
        priority=1,
        state="In Progress",
        branch_name=None,
        url=None,
        labels=[],
        blocked_by=[],
        created_at=datetime.now(timezone.utc),
        updated_at=None,
    )
    orchestrator.dispatch_issue(issue)
    orchestrator.schedule_retry(
        issue_id="retry-1", identifier="MT-2", attempt=3, error="no available orchestrator slots"
    )
    return orchestrator


def test_status_api_returns_state_and_issue_details() -> None:
    orchestrator = _make_orchestrator()
    client = TestClient(create_status_app(orchestrator))

    state_response = client.get("/api/v1/state")
    issue_response = client.get("/api/v1/MT-1")
    missing_response = client.get("/api/v1/UNKNOWN")

    assert state_response.status_code == 200
    assert state_response.json()["counts"]["running"] == 1
    assert state_response.json()["counts"]["retrying"] == 1
    assert issue_response.status_code == 200
    assert issue_response.json()["issue_identifier"] == "MT-1"
    assert missing_response.status_code == 404
    assert missing_response.json()["error"]["code"] == "issue_not_found"


def test_status_api_refresh_endpoint_queues_refresh() -> None:
    orchestrator = _make_orchestrator()
    client = TestClient(create_status_app(orchestrator))

    response = client.post("/api/v1/refresh", json={})

    assert response.status_code == 202
    assert response.json()["queued"] is True
    assert orchestrator.refresh_requested is True


def test_status_api_exposes_heartbeat_and_stale_metadata() -> None:
    orchestrator = _make_orchestrator()
    running_entry = orchestrator.state.running["issue-1"]
    stale_at = datetime.now(timezone.utc) - timedelta(minutes=5)
    running_entry.started_at = stale_at
    running_entry.last_event_at = stale_at
    client = TestClient(create_status_app(orchestrator))

    response = client.get("/api/v1/state")

    assert response.status_code == 200
    heartbeat = response.json()["running"][0]["heartbeat"]
    assert heartbeat["last_seen_at"] is not None
    assert heartbeat["stale"] is True
    assert heartbeat["source"] == "event"


def test_status_api_exposes_collaboration_views() -> None:
    orchestrator = _make_orchestrator()
    client = TestClient(create_status_app(orchestrator))

    issue_response = client.get("/api/v1/collab/issues/MT-1")
    workspaces_response = client.get("/api/v1/collab/workspaces")
    stale_response = client.get("/api/v1/collab/stale")

    assert issue_response.status_code == 200
    assert issue_response.json()["assignment"]["assigned_worker_cli"] == "cli-1"
    assert workspaces_response.status_code == 200
    assert workspaces_response.json()["items"][0]["workspace_key"] == "MT-1"
    assert stale_response.status_code == 200
    assert stale_response.json()["items"][0]["issue_identifier"] == "MT-9"
