from __future__ import annotations

import shlex
import sys
from pathlib import Path

from src.services.symphony.codex_app_server import CodexAppServerClient
from src.services.symphony.dynamic_tools import DynamicToolDefinition, DynamicToolResult


def _command_for(scenario: str, log_path: Path) -> str:
    fixture = Path(__file__).parent / "fixtures" / "fake_codex_app_server.py"
    return f"{shlex.quote(sys.executable)} {shlex.quote(str(fixture))} {shlex.quote(scenario)} {shlex.quote(str(log_path))}"


def test_codex_client_starts_session_runs_turn_and_tracks_usage(tmp_path: Path) -> None:
    log_path = tmp_path / "success.log"
    events: list[dict] = []
    client = CodexAppServerClient(command=_command_for("success", log_path))

    session = client.start_session(
        workspace_path=tmp_path,
        approval_policy="never",
        thread_sandbox="workspace-write",
        on_event=events.append,
    )
    result = client.run_turn(
        session=session,
        prompt="Implement the ticket.",
        title="MT-1: Test",
        approval_policy="never",
        sandbox_policy={"type": "workspace-write"},
        on_event=events.append,
    )
    client.stop_session(session)

    assert session.thread_id == "thread-1"
    assert result.turn_id == "turn-1"
    assert result.status == "completed"
    assert result.total_tokens == 5
    assert any(event["event"] == "session_started" for event in events)
    assert any(event["event"] == "turn_completed" for event in events)
    assert log_path.read_text(encoding="utf-8").splitlines()[:4] == [
        "initialize",
        "initialized",
        "thread/start",
        "turn/start",
    ]


def test_codex_client_auto_approves_and_rejects_unsupported_tool_calls(tmp_path: Path) -> None:
    log_path = tmp_path / "approval.log"
    events: list[dict] = []
    client = CodexAppServerClient(command=_command_for("approval_and_tool", log_path))

    session = client.start_session(
        workspace_path=tmp_path,
        approval_policy="never",
        thread_sandbox="workspace-write",
        on_event=events.append,
    )
    result = client.run_turn(
        session=session,
        prompt="Continue working.",
        title="MT-2: Test",
        approval_policy="never",
        sandbox_policy={"type": "workspace-write"},
        on_event=events.append,
    )
    client.stop_session(session)

    assert result.status == "completed"
    log_lines = log_path.read_text(encoding="utf-8").splitlines()
    assert "approval:approved_for_session" in log_lines
    assert "tool:unsupported_tool_call" in log_lines
    assert any(event["event"] == "approval_auto_approved" for event in events)
    assert any(event["event"] == "unsupported_tool_call" for event in events)


def test_codex_client_fails_when_user_input_is_requested(tmp_path: Path) -> None:
    log_path = tmp_path / "input.log"
    client = CodexAppServerClient(command=_command_for("request_user_input", log_path))

    session = client.start_session(
        workspace_path=tmp_path,
        approval_policy="never",
        thread_sandbox="workspace-write",
    )
    result = client.run_turn(
        session=session,
        prompt="Need input.",
        title="MT-3: Test",
        approval_policy="never",
        sandbox_policy={"type": "workspace-write"},
    )
    client.stop_session(session)

    assert result.status == "input_required"
    assert result.error_code == "turn_input_required"


def test_codex_client_registers_and_serves_supported_dynamic_tools(tmp_path: Path) -> None:
    log_path = tmp_path / "dynamic-tool.log"

    def handler(arguments: dict) -> DynamicToolResult:
        assert arguments["variables"] == {"limit": 1}
        return DynamicToolResult.json({"data": {"projects": [{"id": "p-1"}]}})

    client = CodexAppServerClient(
        command=_command_for("supported_tool", log_path),
        dynamic_tools={
            "linear_graphql": DynamicToolDefinition(
                name="linear_graphql",
                description="Run Linear GraphQL calls.",
                input_schema={
                    "type": "object",
                    "required": ["query"],
                    "properties": {
                        "query": {"type": "string"},
                        "variables": {"type": "object"},
                    },
                },
                handler=handler,
            )
        },
    )

    session = client.start_session(
        workspace_path=tmp_path,
        approval_policy="never",
        thread_sandbox="workspace-write",
    )
    result = client.run_turn(
        session=session,
        prompt="Inspect Linear.",
        title="MT-4: Dynamic tool test",
        approval_policy="never",
        sandbox_policy={"type": "workspace-write"},
    )
    client.stop_session(session)

    assert result.status == "completed"
    log_lines = log_path.read_text(encoding="utf-8").splitlines()
    assert "dynamic_tools:linear_graphql" in log_lines
    assert "tool_success:True" in log_lines
    assert 'tool_text:{"data": {"projects": [{"id": "p-1"}]}}' in log_lines
