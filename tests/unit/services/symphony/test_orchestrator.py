from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone

from src.services.symphony.config import ServiceConfig
from src.services.symphony.models import BlockerRef, Issue, WorkflowDefinition
from src.services.symphony.orchestrator import SymphonyOrchestrator


def _make_issue(
    identifier: str,
    *,
    issue_id: str | None = None,
    title: str = "Task",
    state: str = "In Progress",
    priority: int | None = 1,
    blocked_by: list[BlockerRef] | None = None,
    created_at: datetime | None = None,
) -> Issue:
    return Issue(
        id=issue_id or identifier.lower(),
        identifier=identifier,
        title=title,
        description="Body",
        priority=priority,
        state=state,
        branch_name=None,
        url=None,
        labels=[],
        blocked_by=blocked_by or [],
        created_at=created_at or datetime.now(timezone.utc),
        updated_at=None,
    )


class FakeTracker:
    def __init__(self, candidates: list[Issue], refresh: list[Issue] | None = None) -> None:
        self._candidates = candidates
        self._refresh = refresh or []

    def fetch_candidate_issues(self) -> list[Issue]:
        return list(self._candidates)

    def fetch_issue_states_by_ids(self, _: list[str]) -> list[Issue]:
        return list(self._refresh)

    def fetch_issues_by_states(self, _: list[str]) -> list[Issue]:
        return []


class FakeWorkerHandle:
    def __init__(self, issue: Issue) -> None:
        self.issue = issue
        self.stopped = 0

    def stop(self) -> None:
        self.stopped += 1


class FakeRunnerFactory:
    def __init__(self) -> None:
        self.calls: list[tuple[str, int | None]] = []
        self.handles: dict[str, FakeWorkerHandle] = {}

    def __call__(self, issue: Issue, attempt: int | None) -> FakeWorkerHandle:
        handle = FakeWorkerHandle(issue)
        self.calls.append((issue.identifier, attempt))
        self.handles[issue.id] = handle
        return handle


class FakeWorkspaceManager:
    def __init__(self) -> None:
        self.removed: list[str] = []

    def remove_workspace(self, issue_identifier: str) -> None:
        self.removed.append(issue_identifier)


class FakeCollabRegistry:
    def __init__(self, assignments: dict[str, dict] | None = None, stale: list[dict] | None = None) -> None:
        self.actions: list[tuple] = []
        self.assignments = assignments or {}
        self.stale = stale or []

    def record_assignment(
        self,
        issue: Issue,
        *,
        status: str,
        assigned_worker_cli: str | None = None,
        assigned_by: str | None = None,
        acceptance_summary: str | None = None,
    ) -> None:
        self.actions.append(("assignment", issue.identifier, status, assigned_worker_cli, assigned_by))

    def record_heartbeat(
        self,
        issue: Issue,
        *,
        session_id: str | None = None,
        worker_cli: str | None = None,
        last_event: str | None = None,
        last_message: str | None = None,
        stale_after_seconds: int = 90,
        heartbeat_at: datetime | None = None,
    ) -> None:
        self.actions.append(("heartbeat", issue.identifier, session_id, last_event, worker_cli))

    def sync_work_item_progress(
        self,
        issue: Issue,
        *,
        status: str,
        latest_update: str | None = None,
    ) -> None:
        self.actions.append(("sync", issue.identifier, status, latest_update))

    def get_assignment_state(self, issue_identifier: str):
        return self.assignments.get(issue_identifier)

    def list_stale_heartbeats(self, now: datetime | None = None) -> list[dict]:
        return list(self.stale)

    def list_workspaces(self) -> list[dict]:
        return []


def test_orchestrator_dispatches_highest_priority_eligible_issue() -> None:
    workflow_definition = WorkflowDefinition(
        config={"tracker": {"kind": "linear", "project_slug": "mystocks", "api_key": "token"}},
        prompt_template="Prompt",
    )
    config = ServiceConfig.from_workflow_definition(workflow_definition)
    blocked_issue = _make_issue(
        "MT-1",
        state="Todo",
        priority=1,
        blocked_by=[BlockerRef(id="x", identifier="MT-9", state="In Progress")],
    )
    lower_priority_issue = _make_issue("MT-2", priority=2, created_at=datetime.now(timezone.utc) - timedelta(days=2))
    higher_priority_issue = _make_issue("MT-3", priority=1, created_at=datetime.now(timezone.utc) - timedelta(days=1))
    tracker = FakeTracker([blocked_issue, lower_priority_issue, higher_priority_issue])
    runner_factory = FakeRunnerFactory()

    orchestrator = SymphonyOrchestrator(
        workflow_definition=workflow_definition,
        service_config=replace(config, agent=replace(config.agent, max_concurrent_agents=1)),
        tracker_client=tracker,
        runner_factory=runner_factory,
    )
    orchestrator.tick_once()

    assert runner_factory.calls == [("MT-3", None)]
    assert "mt-3" in orchestrator.state.claimed
    assert "mt-3" in orchestrator.state.running


def test_orchestrator_schedules_continuation_retry_after_normal_exit() -> None:
    workflow_definition = WorkflowDefinition(
        config={"tracker": {"kind": "linear", "project_slug": "mystocks", "api_key": "token"}},
        prompt_template="Prompt",
    )
    config = ServiceConfig.from_workflow_definition(workflow_definition)
    issue = _make_issue("MT-10", issue_id="issue-10")
    runner_factory = FakeRunnerFactory()
    orchestrator = SymphonyOrchestrator(
        workflow_definition=workflow_definition,
        service_config=config,
        tracker_client=FakeTracker([issue]),
        runner_factory=runner_factory,
    )

    orchestrator.dispatch_issue(issue)
    orchestrator.on_worker_exit(issue.id, reason="normal")

    retry = orchestrator.state.retry_attempts[issue.id]
    assert retry.attempt == 1
    assert retry.identifier == issue.identifier
    assert issue.id in orchestrator.state.claimed
    assert issue.id not in orchestrator.state.running


def test_orchestrator_reconciliation_stops_terminal_runs_and_cleans_workspace() -> None:
    workflow_definition = WorkflowDefinition(
        config={"tracker": {"kind": "linear", "project_slug": "mystocks", "api_key": "token"}},
        prompt_template="Prompt",
    )
    config = ServiceConfig.from_workflow_definition(workflow_definition)
    active_issue = _make_issue("MT-20", issue_id="issue-20", state="In Progress")
    terminal_issue = replace(active_issue, state="Done")
    runner_factory = FakeRunnerFactory()
    workspace_manager = FakeWorkspaceManager()
    orchestrator = SymphonyOrchestrator(
        workflow_definition=workflow_definition,
        service_config=config,
        tracker_client=FakeTracker([active_issue], refresh=[terminal_issue]),
        runner_factory=runner_factory,
        workspace_manager=workspace_manager,
    )

    orchestrator.dispatch_issue(active_issue)
    handle = runner_factory.handles[active_issue.id]
    orchestrator.reconcile_running_issues()

    assert handle.stopped == 1
    assert workspace_manager.removed == ["MT-20"]
    assert active_issue.id not in orchestrator.state.running


def test_orchestrator_updates_collab_registry_on_dispatch_event_and_exit() -> None:
    workflow_definition = WorkflowDefinition(
        config={"tracker": {"kind": "linear", "project_slug": "mystocks", "api_key": "token"}},
        prompt_template="Prompt",
    )
    config = ServiceConfig.from_workflow_definition(workflow_definition)
    issue = _make_issue("MT-30", issue_id="issue-30")
    collab_registry = FakeCollabRegistry()
    orchestrator = SymphonyOrchestrator(
        workflow_definition=workflow_definition,
        service_config=config,
        tracker_client=FakeTracker([issue]),
        runner_factory=FakeRunnerFactory(),
        collab_registry=collab_registry,
    )

    orchestrator.dispatch_issue(issue)
    orchestrator.record_event(
        issue.id,
        {"event": "turn.completed", "message": "ok", "session_id": "session-30"},
    )
    orchestrator.on_worker_exit(issue.id, reason="normal")

    assert ("assignment", "MT-30", "running", None, "runtime") in collab_registry.actions
    assert ("sync", "MT-30", "in_progress", None) in collab_registry.actions
    assert ("sync", "MT-30", "in_progress", "ok") in collab_registry.actions
    assert ("heartbeat", "MT-30", "session-30", "turn.completed", None) in collab_registry.actions
    assert ("sync", "MT-30", "ready_for_review", "ok") in collab_registry.actions
    assert ("assignment", "MT-30", "retrying", None, "runtime") in collab_registry.actions


def test_orchestrator_skips_issue_assigned_to_other_cli() -> None:
    workflow_definition = WorkflowDefinition(
        config={
            "tracker": {"kind": "linear", "project_slug": "mystocks", "api_key": "token"},
            "runtime": {"cli_name": "cli-1"},
        },
        prompt_template="Prompt",
    )
    config = ServiceConfig.from_workflow_definition(workflow_definition)
    issue = _make_issue("MT-40", issue_id="issue-40")
    runner_factory = FakeRunnerFactory()
    collab_registry = FakeCollabRegistry(
        assignments={
            "MT-40": {
                "issue_identifier": "MT-40",
                "assigned_worker_cli": "cli-2",
                "status": "assigned",
            }
        }
    )
    orchestrator = SymphonyOrchestrator(
        workflow_definition=workflow_definition,
        service_config=config,
        tracker_client=FakeTracker([issue]),
        runner_factory=runner_factory,
        collab_registry=collab_registry,
    )

    orchestrator.tick_once()

    assert runner_factory.calls == []


def test_orchestrator_can_reclaim_stale_assignment_when_enabled() -> None:
    workflow_definition = WorkflowDefinition(
        config={
            "tracker": {"kind": "linear", "project_slug": "mystocks", "api_key": "token"},
            "runtime": {"cli_name": "cli-1", "reclaim_stale_assignments": True},
        },
        prompt_template="Prompt",
    )
    config = ServiceConfig.from_workflow_definition(workflow_definition)
    issue = _make_issue("MT-41", issue_id="issue-41")
    runner_factory = FakeRunnerFactory()
    collab_registry = FakeCollabRegistry(
        assignments={
            "MT-41": {
                "issue_identifier": "MT-41",
                "assigned_worker_cli": "cli-2",
                "status": "stale",
            }
        },
        stale=[{"issue_identifier": "MT-41", "stale": True}],
    )
    orchestrator = SymphonyOrchestrator(
        workflow_definition=workflow_definition,
        service_config=config,
        tracker_client=FakeTracker([issue]),
        runner_factory=runner_factory,
        collab_registry=collab_registry,
    )

    orchestrator.tick_once()

    assert runner_factory.calls == [("MT-41", None)]
    assert ("assignment", "MT-41", "running", "cli-1", "runtime") in collab_registry.actions
