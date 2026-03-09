from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "maintenance" / "rotate_logs.sh"


def write_log(path: Path, *, age_days: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("log-data\n", encoding="utf-8")
    timestamp = time.time() - age_days * 24 * 60 * 60
    os.utime(path, (timestamp, timestamp))


def run_rotate_logs(project_root: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    command = ["bash", str(SCRIPT_PATH), "--project-root", str(project_root), *extra_args]
    return subprocess.run(command, capture_output=True, text=True, check=False)


def test_rotate_logs_dry_run_reports_archive_target_without_mutation(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    old_log = project_root / "var" / "log" / "app" / "backend.log"
    write_log(old_log, age_days=10)

    completed = run_rotate_logs(project_root, "--dry-run", "--retention-days", "7")

    assert completed.returncode == 0
    assert old_log.exists()
    assert "DRY-RUN" in completed.stdout
    assert "archive/logs/app/backend.log" in completed.stdout
    assert not (project_root / "archive").exists()


def test_rotate_logs_moves_expired_logs_into_archive_on_execute(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    old_log = project_root / "var" / "log" / "app" / "worker.log"
    fresh_log = project_root / "var" / "log" / "app" / "current.log"
    write_log(old_log, age_days=10)
    write_log(fresh_log, age_days=1)

    completed = run_rotate_logs(project_root, "--retention-days", "7")

    archived_log = project_root / "archive" / "logs" / "app" / "worker.log"

    assert completed.returncode == 0
    assert not old_log.exists()
    assert archived_log.exists()
    assert fresh_log.exists()
    assert "rotated: 1" in completed.stdout
