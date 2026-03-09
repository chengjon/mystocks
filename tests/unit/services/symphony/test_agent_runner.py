from __future__ import annotations

import shlex
import sys
from dataclasses import replace
from pathlib import Path

from src.services.symphony.agent_runner import AgentRunner
from src.services.symphony.config import ServiceConfig
from src.services.symphony.models import Issue, WorkflowDefinition


def _command_for(scenario: str, log_path: Path) -> str:
    fixture = Path(__file__).parent / "fixtures" / "fake_codex_app_server.py"
    return f"{shlex.quote(sys.executable)} {shlex.quote(str(fixture))} {shlex.quote(scenario)} {shlex.quote(str(log_path))}"


class FakeTrackerClient:
    def __init__(self, issues: list[Issue]) -> None:
        self._issues = issues
        self._index = 0

    def fetch_issue_states_by_ids(self, _: list[str]) -> list[Issue]:
        issue = self._issues[min(self._index, len(self._issues) - 1)]
        self._index += 1
        return [issue]


def test_agent_runner_reuses_thread_for_continuation_turns(tmp_path: Path) -> None:
    log_path = tmp_path / "runner.log"
    workflow_definition = WorkflowDefinition(
        config={
            "tracker": {"kind": "linear", "project_slug": "mystocks", "api_key": "token"},
            "workspace": {"root": str(tmp_path / "workspaces")},
            "agent": {"max_turns": 3},
            "codex": {"command": _command_for("multi_turn", log_path)},
        },
        prompt_template="Work on {{ issue.identifier }}.",
    )
    config = ServiceConfig.from_workflow_definition(workflow_definition)
    initial_issue = Issue(
        id="issue-1",
        identifier="MT-1",
        title="Runner test",
        description="Body",
        priority=1,
        state="Todo",
        branch_name=None,
        url=None,
        labels=[],
        blocked_by=[],
        created_at=None,
        updated_at=None,
    )
    tracker = FakeTrackerClient(
        [
            replace(initial_issue, state="Todo"),
            replace(initial_issue, state="Done"),
        ]
    )

    runner = AgentRunner(workflow_definition=workflow_definition, service_config=config, tracker_client=tracker)
    result = runner.run_attempt(initial_issue)

    assert result.status == "succeeded"
    assert result.turn_count == 2
    assert result.session_id == "thread-1-turn-2"
    assert (tmp_path / "workspaces" / "MT-1").exists()
