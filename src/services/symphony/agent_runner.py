from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .codex_app_server import CodexAppServerClient
from .config import ServiceConfig
from .dynamic_tools import build_dynamic_tools
from .models import Issue, RunAttemptResult, WorkflowDefinition
from .template_renderer import build_continuation_prompt, render_prompt
from .workspace_manager import WorkspaceManager


class AgentRunner:
    """Run one Symphony attempt for one issue."""

    def __init__(
        self,
        workflow_definition: WorkflowDefinition,
        service_config: ServiceConfig,
        tracker_client: Any,
        workspace_manager: WorkspaceManager | None = None,
        collab_registry: Any | None = None,
    ) -> None:
        self.workflow_definition = workflow_definition
        self.service_config = service_config
        self.tracker_client = tracker_client
        self.workspace_manager = workspace_manager or WorkspaceManager(
            workspace=service_config.workspace,
            hooks=service_config.hooks,
            collab_registry=collab_registry,
        )
        self._active_client: CodexAppServerClient | None = None
        self._active_session = None
        self.dynamic_tools = build_dynamic_tools(
            tracker_config=service_config.tracker,
            tracker_client=tracker_client,
        )

    def run_attempt(
        self,
        issue: Issue,
        attempt: int | None = None,
        on_event: Callable[[dict[str, Any]], None] | None = None,
    ) -> RunAttemptResult:
        workspace = self.workspace_manager.ensure_workspace(
            issue.identifier,
            issue_id=issue.id,
            branch_name=issue.branch_name,
        )
        self.workspace_manager.run_before_run(workspace)
        client = CodexAppServerClient(
            command=self.service_config.codex.command,
            read_timeout_ms=self.service_config.codex.read_timeout_ms,
            turn_timeout_ms=self.service_config.codex.turn_timeout_ms,
            dynamic_tools=self.dynamic_tools,
        )
        self._active_client = client
        session = client.start_session(
            workspace_path=workspace.path,
            approval_policy=self.service_config.codex.approval_policy or "never",
            thread_sandbox=self.service_config.codex.thread_sandbox or "workspace-write",
            on_event=on_event,
        )
        self._active_session = session

        current_issue = issue
        turn_count = 0
        last_session_id: str | None = None
        try:
            while turn_count < self.service_config.agent.max_turns:
                turn_count += 1
                prompt = (
                    render_prompt(self.workflow_definition.prompt_template, current_issue, attempt)
                    if turn_count == 1
                    else build_continuation_prompt(current_issue, turn_count)
                )
                result = client.run_turn(
                    session=session,
                    prompt=prompt,
                    title=f"{current_issue.identifier}: {current_issue.title}",
                    approval_policy=self.service_config.codex.approval_policy or "never",
                    sandbox_policy=self.service_config.codex.turn_sandbox_policy or {"type": "workspace-write"},
                    on_event=on_event,
                )
                last_session_id = result.session_id
                if result.status != "completed":
                    return RunAttemptResult(
                        status="failed",
                        turn_count=turn_count,
                        session_id=last_session_id,
                        workspace_path=workspace.path,
                        error_code=result.error_code,
                    )

                refreshed_issues = self.tracker_client.fetch_issue_states_by_ids([current_issue.id])
                if refreshed_issues:
                    current_issue = refreshed_issues[0]

                if current_issue.state.strip().lower() not in self.service_config.tracker.active_states:
                    break
        finally:
            client.stop_session(session)
            self.workspace_manager.run_after_run(workspace)
            self._active_client = None
            self._active_session = None

        return RunAttemptResult(
            status="succeeded",
            turn_count=turn_count,
            session_id=last_session_id,
            workspace_path=Path(workspace.path),
        )

    def stop(self) -> None:
        if self._active_client is not None and self._active_session is not None:
            self._active_client.stop_session(self._active_session)
