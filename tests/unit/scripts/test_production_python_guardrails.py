from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "compliance" / "production_python_guardrails.py"


def write_lines(path: Path, count: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("value = 1\n" * count, encoding="utf-8")


def run_guardrail(project_root: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    assert SCRIPT_PATH.exists(), f"missing script: {SCRIPT_PATH}"
    command = [sys.executable, str(SCRIPT_PATH), "--root-dir", str(project_root), "--format", "json", *extra_args]
    return subprocess.run(command, capture_output=True, text=True, check=False)


def test_warns_but_does_not_fail_for_python_file_between_651_and_700_lines(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    write_lines(project_root / "src" / "warning_case.py", 680)

    completed = run_guardrail(project_root)

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["summary"]["warnings"] == 1
    assert payload["summary"]["errors"] == 0
    assert payload["warnings"][0]["path"] == "src/warning_case.py"
    assert payload["warnings"][0]["rule_id"] == "python-lines-warning"


def test_fails_for_python_file_above_700_lines(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    write_lines(project_root / "src" / "error_case.py", 701)

    completed = run_guardrail(project_root)

    assert completed.returncode == 1
    payload = json.loads(completed.stdout)
    assert payload["summary"]["errors"] == 1
    assert payload["errors"][0]["path"] == "src/error_case.py"
    assert payload["errors"][0]["rule_id"] == "python-lines-error"


def test_fails_for_bare_print_in_production_code(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    file_path = project_root / "src" / "print_case.py"
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text("def run() -> None:\n    print('debug')\n", encoding="utf-8")

    completed = run_guardrail(project_root)

    assert completed.returncode == 1
    payload = json.loads(completed.stdout)
    assert payload["summary"]["errors"] == 1
    assert payload["errors"][0]["path"] == "src/print_case.py"
    assert payload["errors"][0]["rule_id"] == "no-bare-print"


def test_scope_paths_ignore_unrelated_existing_baseline_debt(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    write_lines(project_root / "src" / "legacy_big.py", 710)
    write_lines(project_root / "src" / "changed_ok.py", 10)

    completed = run_guardrail(project_root, "--path", "src/changed_ok.py")

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["summary"]["errors"] == 0
    assert payload["summary"]["warnings"] == 0
    assert payload["checked_files"] == 1
