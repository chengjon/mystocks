from pathlib import Path

import pytest

from src.services.maestro.collab import SQLiteCollaborationRegistry
from src.services.symphony.config import HooksConfig, WorkspaceConfig
from src.services.symphony.errors import HookExecutionError, WorkspaceSafetyError
from src.services.symphony.workspace_manager import WorkspaceManager


def test_workspace_manager_creates_sanitized_workspace_and_reuses_it(tmp_path: Path) -> None:
    manager = WorkspaceManager(
        workspace=WorkspaceConfig(root=tmp_path / "workspaces"),
        hooks=HooksConfig(after_create="printf created >> hook.log", timeout_ms=1000),
    )

    first = manager.ensure_workspace("ABC/123")
    second = manager.ensure_workspace("ABC/123")

    assert first.workspace_key == "ABC_123"
    assert first.path == (tmp_path / "workspaces" / "ABC_123").resolve()
    assert first.created_now is True
    assert first.path.is_dir()
    assert second.path == first.path
    assert second.created_now is False
    assert (first.path / "hook.log").read_text(encoding="utf-8") == "created"


def test_workspace_manager_rejects_paths_outside_root(tmp_path: Path) -> None:
    manager = WorkspaceManager(
        workspace=WorkspaceConfig(root=tmp_path / "workspaces"),
        hooks=HooksConfig(timeout_ms=1000),
    )

    with pytest.raises(WorkspaceSafetyError):
        manager.validate_workspace_path((tmp_path / "escape").resolve())


def test_workspace_manager_raises_on_before_run_failure(tmp_path: Path) -> None:
    manager = WorkspaceManager(
        workspace=WorkspaceConfig(root=tmp_path / "workspaces"),
        hooks=HooksConfig(before_run="exit 9", timeout_ms=1000),
    )
    workspace = manager.ensure_workspace("ABC-9")

    with pytest.raises(HookExecutionError):
        manager.run_before_run(workspace)


def test_workspace_manager_ignores_after_run_and_before_remove_failures(tmp_path: Path) -> None:
    manager = WorkspaceManager(
        workspace=WorkspaceConfig(root=tmp_path / "workspaces"),
        hooks=HooksConfig(after_run="exit 7", before_remove="exit 5", timeout_ms=1000),
    )
    workspace = manager.ensure_workspace("ABC-10")

    manager.run_after_run(workspace)
    manager.remove_workspace("ABC-10")

    assert not workspace.path.exists()


def test_workspace_manager_injects_hook_context_environment(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo-root"
    repo_root.mkdir()
    manager = WorkspaceManager(
        workspace=WorkspaceConfig(root=tmp_path / "workspaces"),
        hooks=HooksConfig(
            after_create=(
                "printf '%s|%s|%s|%s' "
                '"$SYMPHONY_REPO_ROOT" '
                '"$SYMPHONY_WORKSPACE_PATH" '
                '"$SYMPHONY_WORKSPACE_KEY" '
                '"$SYMPHONY_ISSUE_IDENTIFIER" '
                "> hook-context.log"
            ),
            timeout_ms=1000,
        ),
        repo_root=repo_root,
    )

    workspace = manager.ensure_workspace("ISSUE/42")
    hook_context = (workspace.path / "hook-context.log").read_text(encoding="utf-8")

    assert hook_context == f"{repo_root.resolve()}|{workspace.path}|ISSUE_42|ISSUE/42"


def test_workspace_manager_registers_workspace_in_collab_registry(tmp_path: Path) -> None:
    registry = SQLiteCollaborationRegistry(tmp_path / "tracker.db")
    manager = WorkspaceManager(
        workspace=WorkspaceConfig(root=tmp_path / "workspaces"),
        hooks=HooksConfig(timeout_ms=1000),
        collab_registry=registry,
    )

    workspace = manager.ensure_workspace("ISSUE-43")
    snapshot = registry.get_issue_state("ISSUE-43")

    assert workspace.path == (tmp_path / "workspaces" / "ISSUE-43").resolve()
    assert snapshot["workspace"]["workspace_key"] == "ISSUE-43"
    assert snapshot["workspace"]["workspace_path"] == str(workspace.path)
