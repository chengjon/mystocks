from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .errors import ConfigurationValidationError
from .models import WorkflowDefinition

LINEAR_ENDPOINT = "https://api.linear.app/graphql"
DEFAULT_ACTIVE_STATES = ["Todo", "In Progress"]
DEFAULT_TERMINAL_STATES = ["Closed", "Cancelled", "Canceled", "Duplicate", "Done"]
DEFAULT_WORKSPACE_ROOT = Path(tempfile.gettempdir()) / "symphony_workspaces"
DEFAULT_LOCAL_TRACKER_SQLITE_PATH = Path(".symphony/tracker.db")


def _normalize_state_name(value: str) -> str:
    return value.strip().lower()


def _coerce_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _coerce_positive_int(value: Any, default: int) -> int:
    coerced = _coerce_int(value, default)
    return coerced if coerced > 0 else default


def _coerce_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off"}:
            return False
    return bool(value)


def _parse_state_list(value: Any, default: list[str]) -> list[str]:
    if value is None or value == "":
        items = default
    elif isinstance(value, str):
        items = [part for part in value.split(",")]
    elif isinstance(value, list):
        items = [str(part) for part in value]
    else:
        items = default

    parsed = [str(item).strip() for item in items if str(item).strip()]
    return parsed or [str(item).strip() for item in default if str(item).strip()]


def _normalize_state_list(values: list[str]) -> list[str]:
    normalized = [_normalize_state_name(value) for value in values if value.strip()]
    return normalized


def _resolve_env_string(value: Any, env: dict[str, str], default_env_key: str | None = None) -> str:
    if value is None or value == "":
        return env.get(default_env_key, "") if default_env_key else ""
    if isinstance(value, str) and value.startswith("$"):
        return env.get(value[1:], "")
    return str(value)


def _resolve_path(value: Any, env: dict[str, str], default: Path) -> Path:
    if value is None or value == "":
        return default.resolve()

    raw_value = str(value)
    if raw_value.startswith("$"):
        raw_value = env.get(raw_value[1:], "")

    if not raw_value:
        return default.resolve()

    path = Path(raw_value).expanduser()
    has_separator = any(separator and separator in raw_value for separator in (os.sep, os.altsep))
    if raw_value.startswith("~") or path.is_absolute() or has_separator:
        return path.resolve()
    return path


@dataclass(frozen=True)
class TrackerConfig:
    kind: str
    endpoint: str
    api_key: str
    project_slug: str
    active_states: list[str]
    terminal_states: list[str]
    sqlite_path: Path | None = None
    active_state_names: list[str] = field(default_factory=list)
    terminal_state_names: list[str] = field(default_factory=list)
    enable_linear_graphql_tool: bool = False

    def __post_init__(self) -> None:
        if not self.active_state_names:
            object.__setattr__(self, "active_state_names", list(self.active_states))
        if not self.terminal_state_names:
            object.__setattr__(self, "terminal_state_names", list(self.terminal_states))


@dataclass(frozen=True)
class PollingConfig:
    interval_ms: int = 30000


@dataclass(frozen=True)
class WorkspaceConfig:
    root: Path = DEFAULT_WORKSPACE_ROOT.resolve()


@dataclass(frozen=True)
class HooksConfig:
    after_create: str | None = None
    before_run: str | None = None
    after_run: str | None = None
    before_remove: str | None = None
    timeout_ms: int = 60000


@dataclass(frozen=True)
class AgentConfig:
    max_concurrent_agents: int = 10
    max_turns: int = 20
    max_retry_backoff_ms: int = 300000
    max_concurrent_agents_by_state: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class CodexConfig:
    command: str = "codex app-server"
    approval_policy: Any = None
    thread_sandbox: Any = None
    turn_sandbox_policy: Any = None
    turn_timeout_ms: int = 3600000
    read_timeout_ms: int = 5000
    stall_timeout_ms: int = 300000


@dataclass(frozen=True)
class RuntimeConfig:
    cli_name: str = ""
    reclaim_stale_assignments: bool = False


@dataclass(frozen=True)
class ServiceConfig:
    tracker: TrackerConfig
    polling: PollingConfig
    workspace: WorkspaceConfig
    hooks: HooksConfig
    agent: AgentConfig
    codex: CodexConfig
    runtime: RuntimeConfig = field(default_factory=RuntimeConfig)
    server_port: int | None = None

    @classmethod
    def from_workflow_definition(
        cls,
        definition: WorkflowDefinition,
        env: dict[str, str] | None = None,
    ) -> "ServiceConfig":
        env_map = dict(os.environ) if env is None else env
        config = definition.config or {}

        tracker_config = config.get("tracker", {})
        polling_config = config.get("polling", {})
        workspace_config = config.get("workspace", {})
        hooks_config = config.get("hooks", {})
        agent_config = config.get("agent", {})
        codex_config = config.get("codex", {})
        runtime_config = config.get("runtime", {})
        server_config = config.get("server", {})

        active_state_names = _parse_state_list(tracker_config.get("active_states"), DEFAULT_ACTIVE_STATES)
        terminal_state_names = _parse_state_list(tracker_config.get("terminal_states"), DEFAULT_TERMINAL_STATES)
        tracker_kind = str(tracker_config.get("kind", "")).strip().lower()

        sqlite_path: Path | None = None
        if tracker_kind == "local":
            raw_sqlite_path = tracker_config.get("sqlite_path")
            if raw_sqlite_path in (None, ""):
                sqlite_path = DEFAULT_LOCAL_TRACKER_SQLITE_PATH
            else:
                sqlite_path = _resolve_path(raw_sqlite_path, env_map, DEFAULT_LOCAL_TRACKER_SQLITE_PATH)

        tracker = TrackerConfig(
            kind=tracker_kind,
            endpoint=str(tracker_config.get("endpoint") or LINEAR_ENDPOINT).strip(),
            api_key=_resolve_env_string(
                tracker_config.get("api_key"),
                env_map,
                default_env_key=("LINEAR_API_KEY" if tracker_kind == "linear" else None),
            ),
            project_slug=str(tracker_config.get("project_slug", "")).strip(),
            active_states=_normalize_state_list(active_state_names),
            terminal_states=_normalize_state_list(terminal_state_names),
            sqlite_path=sqlite_path,
            active_state_names=active_state_names,
            terminal_state_names=terminal_state_names,
            enable_linear_graphql_tool=_coerce_bool(tracker_config.get("enable_linear_graphql_tool"), False),
        )

        polling = PollingConfig(interval_ms=_coerce_positive_int(polling_config.get("interval_ms"), 30000))
        workspace = WorkspaceConfig(root=_resolve_path(workspace_config.get("root"), env_map, DEFAULT_WORKSPACE_ROOT))

        hooks_timeout = _coerce_positive_int(hooks_config.get("timeout_ms"), 60000)
        hooks = HooksConfig(
            after_create=hooks_config.get("after_create"),
            before_run=hooks_config.get("before_run"),
            after_run=hooks_config.get("after_run"),
            before_remove=hooks_config.get("before_remove"),
            timeout_ms=hooks_timeout,
        )

        per_state_limits: dict[str, int] = {}
        raw_limits = agent_config.get("max_concurrent_agents_by_state", {})
        if isinstance(raw_limits, dict):
            for state_name, limit in raw_limits.items():
                try:
                    coerced_limit = int(limit)
                except (TypeError, ValueError):
                    continue
                if coerced_limit <= 0:
                    continue
                per_state_limits[_normalize_state_name(str(state_name))] = coerced_limit

        agent = AgentConfig(
            max_concurrent_agents=_coerce_positive_int(agent_config.get("max_concurrent_agents"), 10),
            max_turns=_coerce_positive_int(agent_config.get("max_turns"), 20),
            max_retry_backoff_ms=_coerce_positive_int(agent_config.get("max_retry_backoff_ms"), 300000),
            max_concurrent_agents_by_state=per_state_limits,
        )

        codex = CodexConfig(
            command=str(codex_config.get("command") or "codex app-server"),
            approval_policy=codex_config.get("approval_policy"),
            thread_sandbox=codex_config.get("thread_sandbox"),
            turn_sandbox_policy=codex_config.get("turn_sandbox_policy"),
            turn_timeout_ms=_coerce_positive_int(codex_config.get("turn_timeout_ms"), 3600000),
            read_timeout_ms=_coerce_positive_int(codex_config.get("read_timeout_ms"), 5000),
            stall_timeout_ms=_coerce_int(codex_config.get("stall_timeout_ms"), 300000),
        )
        runtime_cli_name = _resolve_env_string(runtime_config.get("cli_name"), env_map)
        if not runtime_cli_name:
            runtime_cli_name = env_map.get("MAESTRO_CLI_NAME", env_map.get("SYMPHONY_CLI_NAME", ""))

        runtime = RuntimeConfig(
            cli_name=str(runtime_cli_name).strip(),
            reclaim_stale_assignments=_coerce_bool(runtime_config.get("reclaim_stale_assignments"), False),
        )

        server_port = server_config.get("port")
        if server_port is not None:
            server_port = _coerce_int(server_port, 0)

        return cls(
            tracker=tracker,
            polling=polling,
            workspace=workspace,
            hooks=hooks,
            agent=agent,
            codex=codex,
            runtime=runtime,
            server_port=server_port,
        )


def validate_dispatch_config(config: ServiceConfig) -> None:
    if config.tracker.kind == "linear":
        if not config.tracker.api_key:
            raise ConfigurationValidationError("Missing tracker API key.", code="missing_tracker_api_key")
        if not config.tracker.project_slug:
            raise ConfigurationValidationError("Missing tracker project slug.", code="missing_tracker_project_slug")
    elif config.tracker.kind == "local":
        if config.tracker.sqlite_path is None:
            raise ConfigurationValidationError(
                "Missing local tracker sqlite path.", code="missing_local_tracker_sqlite_path"
            )
    else:
        raise ConfigurationValidationError("Unsupported tracker kind.", code="unsupported_tracker_kind")
    if not config.codex.command.strip():
        raise ConfigurationValidationError("Missing Codex launch command.", code="missing_codex_command")
