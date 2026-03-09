from __future__ import annotations

import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "maintenance" / "monitor_file_size.sh"


def write_lines(path: Path, count: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("x = 1\n" * count, encoding="utf-8")


def run_monitor(project_root: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    command = ["bash", str(SCRIPT_PATH), "--project-root", str(project_root), *extra_args]
    return subprocess.run(command, capture_output=True, text=True, check=False)


def test_monitor_file_size_outputs_json_violations(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    write_lines(project_root / "src" / "oversized.py", 801)
    write_lines(project_root / "src" / "small.py", 10)

    completed = run_monitor(project_root, "--format", "json")

    assert completed.returncode == 1
    payload = json.loads(completed.stdout)
    assert payload["oversized_count"] == 1
    assert payload["violations"][0]["path"] == "src/oversized.py"
    assert payload["violations"][0]["limit"] == 800


def test_monitor_file_size_reports_success_when_no_violation(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    write_lines(project_root / "src" / "healthy.py", 20)

    completed = run_monitor(project_root, "--format", "text")

    assert completed.returncode == 0
    assert "No oversized files detected." in completed.stdout
