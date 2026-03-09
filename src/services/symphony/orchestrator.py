from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

from .config import ServiceConfig, validate_dispatch_config
from .models import Issue, WorkflowDefinition


@dataclass
class RetryEntry:
    issue_id: str
    identifier: str
    attempt: int
    due_at_ms: int
    error: str | None = None


@dataclass
class RunningEntry:
    issue: Issue
    worker_handle: Any
    started_at: datetime
    session_id: str | None = None
    turn_count: int = 0
    last_event: str | None = None
    last_message: str | None = None
    last_event_at: datetime | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    retry_attempt: int | None = None


@dataclass
class OrchestratorState:
    poll_interval_ms: int
    max_concurrent_agents: int
    running: dict[str, RunningEntry] = field(default_factory=dict)
    claimed: set[str] = field(default_factory=set)
    retry_attempts: dict[str, RetryEntry] = field(default_factory=dict)
    completed: set[str] = field(default_factory=set)
    codex_totals: dict[str, float] = field(
        default_factory=lambda: {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "seconds_running": 0.0,
        }
    )
    codex_rate_limits: dict[str, Any] | None = None


class SymphonyOrchestrator:
    """Single-authority in-memory orchestration state for Symphony."""

    def __init__(
        self,
        workflow_definition: WorkflowDefinition,
        service_config: ServiceConfig,
        tracker_client: Any,
        runner_factory: Callable[[Issue, int | None], Any],
        workspace_manager: Any | None = None,
        collab_registry: Any | None = None,
    ) -> None:
        self.workflow_definition = workflow_definition
        self.service_config = service_config
        self.tracker_client = tracker_client
        self.runner_factory = runner_factory
        self.workspace_manager = workspace_manager
        self.collab_registry = collab_registry
        self.refresh_requested = False
        self.state = OrchestratorState(
            poll_interval_ms=service_config.polling.interval_ms,
            max_concurrent_agents=service_config.agent.max_concurrent_agents,
        )

    def tick_once(self) -> None:
        self.refresh_requested = False
        self.refresh_stale_assignments()
        self.reconcile_running_issues()
        validate_dispatch_config(self.service_config)
        issues = self.sort_candidate_issues(self.tracker_client.fetch_candidate_issues())

        for issue in issues:
            if self.available_slots() <= 0:
                break
            if self.should_dispatch(issue):
                self.dispatch_issue(issue)

    def dispatch_issue(self, issue: Issue, attempt: int | None = None) -> None:
        worker_handle = self.runner_factory(issue, attempt)
        self.state.running[issue.id] = RunningEntry(
            issue=issue,
            worker_handle=worker_handle,
            started_at=datetime.now(timezone.utc),
            retry_attempt=attempt,
        )
        self.state.claimed.add(issue.id)
        self.state.retry_attempts.pop(issue.id, None)
        if self.collab_registry is not None and hasattr(self.collab_registry, "record_assignment"):
            self.collab_registry.record_assignment(
                issue,
                status="running",
                assigned_worker_cli=self._resolve_runtime_assignee(issue),
                assigned_by="runtime",
            )

    def on_worker_exit(self, issue_id: str, reason: str) -> None:
        running_entry = self.state.running.pop(issue_id, None)
        if running_entry is None:
            return
        elapsed_seconds = (datetime.now(timezone.utc) - running_entry.started_at).total_seconds()
        self.state.codex_totals["seconds_running"] += elapsed_seconds
        self.state.codex_totals["input_tokens"] += running_entry.input_tokens
        self.state.codex_totals["output_tokens"] += running_entry.output_tokens
        self.state.codex_totals["total_tokens"] += running_entry.total_tokens

        if reason == "normal":
            self.state.completed.add(issue_id)
            if self.collab_registry is not None and hasattr(self.collab_registry, "record_assignment"):
                self.collab_registry.record_assignment(
                    running_entry.issue,
                    status="retrying",
                    assigned_worker_cli=self._resolve_runtime_assignee(running_entry.issue),
                    assigned_by="runtime",
                )
            self.schedule_retry(issue_id=issue_id, identifier=running_entry.issue.identifier, attempt=1, delay_ms=1000)
        else:
            next_attempt = 1 if running_entry.retry_attempt in (None, 0) else running_entry.retry_attempt + 1
            delay_ms = min(10000 * (2 ** max(next_attempt - 1, 0)), self.service_config.agent.max_retry_backoff_ms)
            if self.collab_registry is not None and hasattr(self.collab_registry, "record_assignment"):
                self.collab_registry.record_assignment(
                    running_entry.issue,
                    status="failed",
                    assigned_worker_cli=self._resolve_runtime_assignee(running_entry.issue),
                    assigned_by="runtime",
                )
            self.schedule_retry(
                issue_id=issue_id,
                identifier=running_entry.issue.identifier,
                attempt=next_attempt,
                error=f"worker exited: {reason}",
                delay_ms=delay_ms,
            )

    def schedule_retry(
        self,
        issue_id: str,
        identifier: str,
        attempt: int,
        error: str | None = None,
        delay_ms: int | None = None,
    ) -> None:
        due_at_ms = int(time.monotonic() * 1000) + (delay_ms if delay_ms is not None else 1000)
        self.state.retry_attempts[issue_id] = RetryEntry(
            issue_id=issue_id,
            identifier=identifier,
            attempt=attempt,
            due_at_ms=due_at_ms,
            error=error,
        )
        self.state.claimed.add(issue_id)

    def reconcile_running_issues(self) -> None:
        if not self.state.running:
            return

        refreshed_issues = self.tracker_client.fetch_issue_states_by_ids(list(self.state.running))
        refreshed_by_id = {issue.id: issue for issue in refreshed_issues}

        for issue_id, running_entry in list(self.state.running.items()):
            refreshed_issue = refreshed_by_id.get(issue_id)
            if refreshed_issue is None:
                continue

            normalized_state = refreshed_issue.state.strip().lower()
            if normalized_state in self.service_config.tracker.terminal_states:
                if self.collab_registry is not None and hasattr(self.collab_registry, "record_assignment"):
                    self.collab_registry.record_assignment(refreshed_issue, status="completed", assigned_by="runtime")
                self._stop_running_issue(issue_id, cleanup_workspace=True)
            elif normalized_state in self.service_config.tracker.active_states:
                running_entry.issue = refreshed_issue
            else:
                if self.collab_registry is not None and hasattr(self.collab_registry, "record_assignment"):
                    self.collab_registry.record_assignment(refreshed_issue, status="paused", assigned_by="runtime")
                self._stop_running_issue(issue_id, cleanup_workspace=False)

    def available_slots(self) -> int:
        return max(self.service_config.agent.max_concurrent_agents - len(self.state.running), 0)

    def should_dispatch(self, issue: Issue) -> bool:
        if not issue.id or not issue.identifier or not issue.title or not issue.state:
            return False

        normalized_state = issue.state.strip().lower()
        if normalized_state not in self.service_config.tracker.active_states:
            return False
        if normalized_state in self.service_config.tracker.terminal_states:
            return False
        if issue.id in self.state.running or issue.id in self.state.claimed:
            return False
        if self.available_slots() <= 0:
            return False
        if not self._assignment_allows_dispatch(issue):
            return False
        if not self._has_state_slot(normalized_state):
            return False
        if normalized_state == "todo" and any(
            blocker.state and blocker.state.strip().lower() not in self.service_config.tracker.terminal_states
            for blocker in issue.blocked_by
        ):
            return False
        return True

    def sort_candidate_issues(self, issues: list[Issue]) -> list[Issue]:
        def sort_key(issue: Issue) -> tuple[int, datetime, str]:
            priority = issue.priority if issue.priority is not None else 999999
            created_at = issue.created_at or datetime.max.replace(tzinfo=timezone.utc)
            return (priority, created_at, issue.identifier)

        return sorted(issues, key=sort_key)

    def queue_refresh(self) -> None:
        self.refresh_requested = True

    def refresh_stale_assignments(self) -> None:
        if self.collab_registry is None or not hasattr(self.collab_registry, "list_stale_heartbeats"):
            return

        for row in self.collab_registry.list_stale_heartbeats():
            if not row.get("stale"):
                continue
            issue_identifier = row.get("issue_identifier")
            if not issue_identifier or not hasattr(self.collab_registry, "get_assignment_state"):
                continue
            assignment = self.collab_registry.get_assignment_state(str(issue_identifier))
            if assignment is None:
                continue
            self.collab_registry.record_assignment(
                _CollabIssueRef(
                    id=assignment.get("issue_id"),
                    identifier=str(issue_identifier),
                ),
                status="stale",
                assigned_worker_cli=assignment.get("assigned_worker_cli"),
                assigned_by=assignment.get("assigned_by") or "runtime",
                acceptance_summary=assignment.get("acceptance_summary"),
            )

    def record_event(self, issue_id: str, event: dict[str, Any]) -> None:
        running_entry = self.state.running.get(issue_id)
        if running_entry is None:
            return
        running_entry.last_event = event.get("event")
        running_entry.last_message = event.get("message")
        running_entry.last_event_at = datetime.now(timezone.utc)
        if event.get("session_id"):
            running_entry.session_id = event["session_id"]
        if event.get("turn_id") and running_entry.session_id is None:
            running_entry.session_id = f"{running_entry.issue.id}-{event['turn_id']}"
        if event.get("input_tokens") is not None:
            running_entry.input_tokens = int(event["input_tokens"])
        if event.get("output_tokens") is not None:
            running_entry.output_tokens = int(event["output_tokens"])
        if event.get("total_tokens") is not None:
            running_entry.total_tokens = int(event["total_tokens"])
        if self.collab_registry is not None and hasattr(self.collab_registry, "record_heartbeat"):
            self.collab_registry.record_heartbeat(
                running_entry.issue,
                session_id=running_entry.session_id,
                worker_cli=self._resolve_runtime_assignee(running_entry.issue),
                last_event=running_entry.last_event,
                last_message=running_entry.last_message,
                stale_after_seconds=max(int(self.state.poll_interval_ms * 3 / 1000), 1),
            )

    def record_worker_result(self, issue_id: str, result: Any) -> None:
        running_entry = self.state.running.get(issue_id)
        if running_entry is None:
            return
        running_entry.turn_count = getattr(result, "turn_count", running_entry.turn_count)
        running_entry.session_id = getattr(result, "session_id", running_entry.session_id)

    def snapshot(self) -> dict[str, Any]:
        generated_at = datetime.now(timezone.utc).isoformat()
        running_rows = []
        for issue_id, entry in self.state.running.items():
            running_rows.append(
                {
                    "issue_id": issue_id,
                    "issue_identifier": entry.issue.identifier,
                    "state": entry.issue.state,
                    "session_id": entry.session_id,
                    "turn_count": entry.turn_count,
                    "last_event": entry.last_event,
                    "last_message": entry.last_message or "",
                    "started_at": entry.started_at.isoformat(),
                    "last_event_at": entry.last_event_at.isoformat() if entry.last_event_at else None,
                    "heartbeat": self._build_heartbeat_payload(entry, generated_at),
                    "tokens": {
                        "input_tokens": entry.input_tokens,
                        "output_tokens": entry.output_tokens,
                        "total_tokens": entry.total_tokens,
                    },
                }
            )

        retry_rows = []
        for retry in self.state.retry_attempts.values():
            retry_rows.append(
                {
                    "issue_id": retry.issue_id,
                    "issue_identifier": retry.identifier,
                    "attempt": retry.attempt,
                    "due_at": datetime.fromtimestamp(retry.due_at_ms / 1000, tz=timezone.utc).isoformat(),
                    "error": retry.error,
                }
            )

        return {
            "generated_at": generated_at,
            "counts": {"running": len(running_rows), "retrying": len(retry_rows)},
            "running": running_rows,
            "retrying": retry_rows,
            "codex_totals": self.state.codex_totals,
            "rate_limits": self.state.codex_rate_limits,
        }

    def get_issue_snapshot(self, issue_identifier: str) -> dict[str, Any] | None:
        for issue_id, entry in self.state.running.items():
            if entry.issue.identifier == issue_identifier:
                retry = self.state.retry_attempts.get(issue_id)
                return {
                    "issue_identifier": entry.issue.identifier,
                    "issue_id": issue_id,
                    "status": "running",
                    "workspace": {"path": None},
                    "attempts": {
                        "restart_count": 0,
                        "current_retry_attempt": retry.attempt if retry else None,
                    },
                    "running": {
                        "session_id": entry.session_id,
                        "turn_count": entry.turn_count,
                        "state": entry.issue.state,
                        "started_at": entry.started_at.isoformat(),
                        "last_event": entry.last_event,
                        "last_message": entry.last_message or "",
                        "last_event_at": entry.last_event_at.isoformat() if entry.last_event_at else None,
                        "heartbeat": self._build_heartbeat_payload(entry),
                        "tokens": {
                            "input_tokens": entry.input_tokens,
                            "output_tokens": entry.output_tokens,
                            "total_tokens": entry.total_tokens,
                        },
                    },
                    "retry": None,
                    "logs": {"codex_session_logs": []},
                    "recent_events": [],
                    "last_error": None,
                    "tracked": {},
                }
        return None

    def _build_heartbeat_payload(self, entry: RunningEntry, generated_at: str | None = None) -> dict[str, Any]:
        reference_time = entry.last_event_at or entry.started_at
        source = "event" if entry.last_event_at is not None else "started"
        now = datetime.fromisoformat(generated_at) if generated_at else datetime.now(timezone.utc)
        age_seconds = max((now - reference_time).total_seconds(), 0.0)
        stale_after_seconds = max(self.state.poll_interval_ms * 3 / 1000, 1.0)

        return {
            "last_seen_at": reference_time.isoformat(),
            "age_seconds": round(age_seconds, 3),
            "stale_after_seconds": round(stale_after_seconds, 3),
            "stale": age_seconds > stale_after_seconds,
            "source": source,
        }

    def get_collab_issue_state(self, issue_identifier: str) -> dict[str, Any] | None:
        if self.collab_registry is None or not hasattr(self.collab_registry, "get_issue_state"):
            return None
        return self.collab_registry.get_issue_state(issue_identifier)

    def list_collab_workspaces(self) -> list[dict[str, Any]]:
        if self.collab_registry is None or not hasattr(self.collab_registry, "list_workspaces"):
            return []
        return self.collab_registry.list_workspaces()

    def list_collab_stale(self) -> list[dict[str, Any]]:
        if self.collab_registry is None or not hasattr(self.collab_registry, "list_stale_heartbeats"):
            return []
        return self.collab_registry.list_stale_heartbeats()

    def _assignment_allows_dispatch(self, issue: Issue) -> bool:
        if self.collab_registry is None or not hasattr(self.collab_registry, "get_assignment_state"):
            return True

        assignment = self.collab_registry.get_assignment_state(issue.identifier)
        if not assignment:
            return True

        assigned_worker_cli = (assignment.get("assigned_worker_cli") or "").strip()
        if not assigned_worker_cli:
            return True

        runtime_cli_name = self.service_config.runtime.cli_name.strip()
        if runtime_cli_name and assigned_worker_cli == runtime_cli_name:
            return True

        return bool(
            assignment.get("status") == "stale"
            and runtime_cli_name
            and self.service_config.runtime.reclaim_stale_assignments
        )

    def _resolve_runtime_assignee(self, issue: Issue) -> str | None:
        runtime_cli_name = self.service_config.runtime.cli_name.strip()
        if runtime_cli_name:
            return runtime_cli_name
        if self.collab_registry is not None and hasattr(self.collab_registry, "get_assignment_state"):
            assignment = self.collab_registry.get_assignment_state(issue.identifier)
            if assignment:
                return assignment.get("assigned_worker_cli")
        return None

    def _has_state_slot(self, normalized_state: str) -> bool:
        state_limit = self.service_config.agent.max_concurrent_agents_by_state.get(
            normalized_state,
            self.service_config.agent.max_concurrent_agents,
        )
        current_state_count = sum(
            1 for entry in self.state.running.values() if entry.issue.state.strip().lower() == normalized_state
        )
        return current_state_count < state_limit

    def _stop_running_issue(self, issue_id: str, cleanup_workspace: bool) -> None:
        running_entry = self.state.running.pop(issue_id)
        if hasattr(running_entry.worker_handle, "stop"):
            running_entry.worker_handle.stop()
        self.state.claimed.discard(issue_id)
        self.state.retry_attempts.pop(issue_id, None)
        if cleanup_workspace and self.workspace_manager is not None:
            self.workspace_manager.remove_workspace(running_entry.issue.identifier)


@dataclass(frozen=True)
class _CollabIssueRef:
    id: str | None
    identifier: str
