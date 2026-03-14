from pathlib import Path

import pytest

from src.services.symphony.config import ServiceConfig, validate_dispatch_config
from src.services.symphony.errors import ConfigurationValidationError
from src.services.symphony.models import WorkflowDefinition


def test_service_config_applies_defaults_and_env_resolution(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("LINEAR_API_KEY", "linear-token")
    monkeypatch.setenv("SYMPHONY_WORKSPACE_ROOT", str(tmp_path / "workspaces"))

    definition = WorkflowDefinition(
        config={
            "tracker": {
                "kind": "linear",
                "project_slug": "mystocks",
                "api_key": "$LINEAR_API_KEY",
            },
            "workspace": {"root": "$SYMPHONY_WORKSPACE_ROOT"},
        },
        prompt_template="Prompt",
    )

    config = ServiceConfig.from_workflow_definition(definition)

    assert config.tracker.kind == "linear"
    assert config.tracker.endpoint == "https://api.linear.app/graphql"
    assert config.tracker.api_key == "linear-token"
    assert config.tracker.active_states == ["todo", "in progress"]
    assert config.tracker.active_state_names == ["Todo", "In Progress"]
    assert "done" in config.tracker.terminal_states
    assert "Done" in config.tracker.terminal_state_names
    assert config.polling.interval_ms == 30000
    assert config.workspace.root == (tmp_path / "workspaces").resolve()
    assert config.hooks.timeout_ms == 60000
    assert config.agent.max_concurrent_agents == 10
    assert config.agent.max_turns == 20
    assert config.agent.max_retry_backoff_ms == 300000
    assert config.codex.command == "codex app-server"
    assert config.codex.read_timeout_ms == 5000
    assert config.codex.turn_timeout_ms == 3600000
    assert config.codex.stall_timeout_ms == 300000


def test_service_config_normalizes_states_and_ignores_invalid_per_state_limits() -> None:
    definition = WorkflowDefinition(
        config={
            "tracker": {
                "kind": "linear",
                "project_slug": "mystocks",
                "api_key": "token",
                "active_states": " Todo, In Progress ",
                "terminal_states": [" Done ", " Cancelled "],
            },
            "agent": {
                "max_concurrent_agents_by_state": {
                    " Todo ": "2",
                    "In Progress": 3,
                    "Broken": 0,
                    "Ignored": "abc",
                }
            },
        },
        prompt_template="Prompt",
    )

    config = ServiceConfig.from_workflow_definition(definition)

    assert config.tracker.active_states == ["todo", "in progress"]
    assert config.tracker.active_state_names == ["Todo", "In Progress"]
    assert config.tracker.terminal_states == ["done", "cancelled"]
    assert config.tracker.terminal_state_names == ["Done", "Cancelled"]
    assert config.agent.max_concurrent_agents_by_state == {"todo": 2, "in progress": 3}


def test_service_config_can_enable_linear_graphql_tool() -> None:
    definition = WorkflowDefinition(
        config={
            "tracker": {
                "kind": "linear",
                "project_slug": "mystocks",
                "api_key": "token",
                "enable_linear_graphql_tool": True,
            }
        },
        prompt_template="Prompt",
    )

    config = ServiceConfig.from_workflow_definition(definition)

    assert config.tracker.enable_linear_graphql_tool is True


def test_service_config_supports_local_tracker_with_default_sqlite_path() -> None:
    definition = WorkflowDefinition(
        config={
            "tracker": {
                "kind": "local",
            }
        },
        prompt_template="Prompt",
    )

    config = ServiceConfig.from_workflow_definition(definition)

    assert config.tracker.kind == "local"
    assert config.tracker.sqlite_path == Path(".symphony/tracker.db")
    validate_dispatch_config(config)


def test_service_config_resolves_local_tracker_sqlite_path_from_env(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("SYMPHONY_TRACKER_DB", str(tmp_path / "tracker.db"))
    definition = WorkflowDefinition(
        config={
            "tracker": {
                "kind": "local",
                "sqlite_path": "$SYMPHONY_TRACKER_DB",
            }
        },
        prompt_template="Prompt",
    )

    config = ServiceConfig.from_workflow_definition(definition)

    assert config.tracker.sqlite_path == (tmp_path / "tracker.db").resolve()


def test_service_config_reads_runtime_cli_identity_and_reclaim_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MAESTRO_CLI_NAME", "cli-env")
    definition = WorkflowDefinition(
        config={
            "tracker": {"kind": "local"},
            "runtime": {
                "reclaim_stale_assignments": True,
            },
        },
        prompt_template="Prompt",
    )

    config = ServiceConfig.from_workflow_definition(definition)

    assert config.runtime.cli_name == "cli-env"
    assert config.runtime.reclaim_stale_assignments is True


def test_service_config_supports_mongo_tracker_settings() -> None:
    definition = WorkflowDefinition(
        config={
            "tracker": {
                "kind": "mongo",
                "mongo_uri": "mongodb://mongo:27017",
                "mongo_db": "mystocks_coord",
                "active_states": ["created", "dispatched", "in_progress"],
                "terminal_states": ["verified", "merged"],
            }
        },
        prompt_template="Prompt",
    )

    config = ServiceConfig.from_workflow_definition(definition)

    assert config.tracker.kind == "mongo"
    assert config.tracker.mongo_uri == "mongodb://mongo:27017"
    assert config.tracker.mongo_db == "mystocks_coord"
    validate_dispatch_config(config)


def test_service_config_expands_home_but_preserves_bare_relative_roots(monkeypatch: pytest.MonkeyPatch) -> None:
    definition_home = WorkflowDefinition(
        config={
            "tracker": {"kind": "linear", "project_slug": "mystocks", "api_key": "token"},
            "workspace": {"root": "~/symfony_workspaces"},
        },
        prompt_template="Prompt",
    )
    definition_relative = WorkflowDefinition(
        config={
            "tracker": {"kind": "linear", "project_slug": "mystocks", "api_key": "token"},
            "workspace": {"root": "relative_workspaces"},
        },
        prompt_template="Prompt",
    )

    home_config = ServiceConfig.from_workflow_definition(definition_home)
    relative_config = ServiceConfig.from_workflow_definition(definition_relative)

    assert home_config.workspace.root == Path.home().joinpath("symfony_workspaces").resolve()
    assert relative_config.workspace.root == Path("relative_workspaces")


def test_validate_dispatch_config_requires_supported_tracker_kind() -> None:
    definition = WorkflowDefinition(
        config={"tracker": {"kind": "jira", "project_slug": "mystocks", "api_key": "token"}},
        prompt_template="Prompt",
    )

    config = ServiceConfig.from_workflow_definition(definition)

    with pytest.raises(ConfigurationValidationError):
        validate_dispatch_config(config)


def test_validate_dispatch_config_requires_tracker_auth_and_project_slug() -> None:
    definition = WorkflowDefinition(
        config={"tracker": {"kind": "linear", "project_slug": "", "api_key": ""}},
        prompt_template="Prompt",
    )

    config = ServiceConfig.from_workflow_definition(definition)

    with pytest.raises(ConfigurationValidationError):
        validate_dispatch_config(config)
