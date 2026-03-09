from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from .config import HooksConfig, WorkspaceConfig
from .errors import HookExecutionError, WorkspaceSafetyError
from .models import Workspace


class WorkspaceManager:
    """Manage deterministic per-issue Symphony workspaces."""

    def __init__(
        self,
        workspace: WorkspaceConfig,
        hooks: HooksConfig,
        repo_root: Path | None = None,
        collab_registry: object | None = None,
    ) -> None:
        self.workspace = workspace
        self.hooks = hooks
        self.repo_root = (repo_root or Path.cwd()).resolve()
        self.collab_registry = collab_registry

    def ensure_workspace(
        self,
        issue_identifier: str,
        *,
        issue_id: str | None = None,
        owner_cli: str | None = None,
        branch_name: str | None = None,
    ) -> Workspace:
        workspace_key = self._sanitize_workspace_key(issue_identifier)
        workspace_path = self.workspace.root / workspace_key
        workspace_path = workspace_path.resolve()

        self.validate_workspace_path(workspace_path)
        self.workspace.root.mkdir(parents=True, exist_ok=True)

        created_now = False
        if workspace_path.exists():
            if not workspace_path.is_dir():
                raise WorkspaceSafetyError(f"Workspace path is not a directory: {workspace_path}")
        else:
            workspace_path.mkdir(parents=True, exist_ok=True)
            created_now = True

        workspace = Workspace(
            path=workspace_path,
            workspace_key=workspace_key,
            issue_identifier=issue_identifier,
            created_now=created_now,
        )
        if self.collab_registry is not None and hasattr(self.collab_registry, "register_workspace_for_issue"):
            self.collab_registry.register_workspace_for_issue(
                issue_identifier=issue_identifier,
                issue_id=issue_id,
                workspace=workspace,
                owner_cli=owner_cli,
                branch_name=branch_name,
            )
        if created_now and self.hooks.after_create:
            self._run_hook("after_create", self.hooks.after_create, workspace, fatal=True)

        return workspace

    def validate_workspace_path(self, workspace_path: Path) -> None:
        workspace_root = self.workspace.root.resolve()
        try:
            workspace_path.relative_to(workspace_root)
        except ValueError as exc:
            raise WorkspaceSafetyError(
                f"Workspace path {workspace_path} is outside configured root {workspace_root}."
            ) from exc

    def run_before_run(self, workspace: Workspace) -> None:
        if self.hooks.before_run:
            self._run_hook("before_run", self.hooks.before_run, workspace, fatal=True)

    def run_after_run(self, workspace: Workspace) -> None:
        if self.hooks.after_run:
            self._run_hook("after_run", self.hooks.after_run, workspace, fatal=False)

    def remove_workspace(self, issue_identifier: str) -> None:
        workspace_path = (self.workspace.root / self._sanitize_workspace_key(issue_identifier)).resolve()
        self.validate_workspace_path(workspace_path)
        if not workspace_path.exists():
            return

        workspace = Workspace(
            path=workspace_path,
            workspace_key=workspace_path.name,
            issue_identifier=issue_identifier,
            created_now=False,
        )
        if self.hooks.before_remove:
            self._run_hook("before_remove", self.hooks.before_remove, workspace, fatal=False)

        shutil.rmtree(workspace_path, ignore_errors=False)

    @staticmethod
    def _sanitize_workspace_key(issue_identifier: str) -> str:
        return "".join(
            character if character.isalnum() or character in "._-" else "_" for character in issue_identifier
        )

    def _run_hook(self, hook_name: str, script: str, workspace: Workspace, fatal: bool) -> None:
        env = os.environ.copy()
        env.update(
            {
                "SYMPHONY_REPO_ROOT": str(self.repo_root),
                "SYMPHONY_WORKSPACE_PATH": str(workspace.path),
                "SYMPHONY_WORKSPACE_KEY": workspace.workspace_key,
                "SYMPHONY_ISSUE_IDENTIFIER": workspace.issue_identifier,
            }
        )
        try:
            subprocess.run(
                ["bash", "-lc", script],
                cwd=workspace.path,
                env=env,
                capture_output=True,
                text=True,
                timeout=self.hooks.timeout_ms / 1000,
                check=True,
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            if fatal:
                raise HookExecutionError(f"{hook_name} hook failed for {workspace.workspace_key}") from exc
