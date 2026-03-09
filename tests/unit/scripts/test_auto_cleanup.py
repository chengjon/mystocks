from __future__ import annotations

import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "cleanup" / "auto_cleanup.sh"


def write_text(path: Path, content: str = "data\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_auto_cleanup(project_root: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    command = ["bash", str(SCRIPT_PATH), "--project-root", str(project_root), *extra_args]
    return subprocess.run(command, capture_output=True, text=True, check=False)


def test_auto_cleanup_dry_run_reports_actions_without_mutation(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    write_text(project_root / "temp" / "cache.txt")
    write_text(project_root / "src" / "__pycache__" / "module.pyc")
    write_text(project_root / "htmlcov" / "index.html")
    write_text(project_root / "notes.bak")

    completed = run_auto_cleanup(project_root, "--format", "json")

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    action_paths = {item["path"] for item in payload["actions"]}

    assert payload["dry_run"] is True
    assert action_paths == {"temp", "src/__pycache__", "htmlcov", "notes.bak"}
    assert (project_root / "temp").exists()
    assert (project_root / "src" / "__pycache__").exists()
    assert (project_root / "htmlcov").exists()
    assert (project_root / "notes.bak").exists()


def test_auto_cleanup_execute_removes_runtime_dirs_and_archives_backup_files(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    write_text(project_root / "tmp" / "scratch.txt")
    write_text(project_root / "pkg" / "__pycache__" / "cache.pyc")
    write_text(project_root / "htmlcov" / "coverage.html")
    write_text(project_root / "snapshot.backup")

    completed = run_auto_cleanup(
        project_root,
        "--execute",
        "--format",
        "json",
        "--backup-stamp",
        "test-run",
    )

    payload = json.loads(completed.stdout)
    archived_backup = project_root / "var" / "backups" / "test-run" / "snapshot.backup"

    assert completed.returncode == 0
    assert payload["dry_run"] is False
    assert not (project_root / "tmp").exists()
    assert not (project_root / "pkg" / "__pycache__").exists()
    assert not (project_root / "htmlcov").exists()
    assert not (project_root / "snapshot.backup").exists()
    assert archived_backup.exists()


def test_auto_cleanup_execute_rehomes_root_backups_directory_into_var_backups(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    write_text(project_root / "backups" / "data_source_registry" / "registry_backup.json", "{\"ok\": true}\n")

    completed = run_auto_cleanup(
        project_root,
        "--execute",
        "--format",
        "json",
        "--backup-stamp",
        "test-run",
    )

    payload = json.loads(completed.stdout)
    migrated_backup_dir = project_root / "var" / "backups" / "test-run" / "legacy-root-backups"

    assert completed.returncode == 0
    assert payload["dry_run"] is False
    assert not (project_root / "backups").exists()
    assert migrated_backup_dir.exists()
    assert (migrated_backup_dir / "data_source_registry" / "registry_backup.json").exists()
