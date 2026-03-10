from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "compliance" / "file_size_guardrail.py"


def write_lines(path: Path, count: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("line\n" * count, encoding="utf-8")


def run_guard(project_root: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    assert SCRIPT_PATH.exists(), f"missing script: {SCRIPT_PATH}"
    command = [sys.executable, str(SCRIPT_PATH), "--root-dir", str(project_root), "--format", "json", *extra_args]
    return subprocess.run(command, capture_output=True, text=True, check=False, cwd=PROJECT_ROOT)


def test_path_mode_checks_only_selected_scoped_files(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    oversized = project_root / "web" / "frontend" / "src" / "views" / "BigView.vue"
    healthy = project_root / "tests" / "e2e" / "healthy.spec.ts"
    outside_scope = project_root / "docs" / "oversized.ts"

    write_lines(oversized, 501)
    write_lines(healthy, 200)
    write_lines(outside_scope, 800)

    completed = run_guard(
        project_root,
        "--scope-root",
        "web/frontend",
        "--scope-root",
        "tests",
        "--path",
        "web/frontend/src/views/BigView.vue",
        "--path",
        "tests/e2e/healthy.spec.ts",
        "--path",
        "docs/oversized.ts",
    )

    assert completed.returncode == 1
    payload = json.loads(completed.stdout)
    assert payload["checked_files"] == 2
    assert payload["oversized_count"] == 1
    assert payload["violations"][0]["path"] == "web/frontend/src/views/BigView.vue"
    assert payload["violations"][0]["limit"] == 500


def test_path_mode_ignores_unrelated_existing_baseline_debt(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    legacy = project_root / "tests" / "e2e" / "legacy_big.spec.ts"
    changed = project_root / "web" / "frontend" / "src" / "components" / "SmallPanel.vue"

    write_lines(legacy, 1200)
    write_lines(changed, 120)

    completed = run_guard(
        project_root,
        "--scope-root",
        "web/frontend",
        "--scope-root",
        "tests",
        "--path",
        "web/frontend/src/components/SmallPanel.vue",
    )

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["checked_files"] == 1
    assert payload["oversized_count"] == 0


def test_supports_positional_filenames_for_pre_commit(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    oversized = project_root / "tests" / "helpers" / "oversized.ts"
    write_lines(oversized, 501)

    completed = run_guard(
        project_root,
        "--scope-root",
        "web/frontend",
        "--scope-root",
        "tests",
        "tests/helpers/oversized.ts",
    )

    assert completed.returncode == 1
    payload = json.loads(completed.stdout)
    assert payload["checked_files"] == 1
    assert payload["oversized_count"] == 1
    assert payload["violations"][0]["path"] == "tests/helpers/oversized.ts"


def test_full_scan_with_scope_roots_keeps_existing_monitor_behavior(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    healthy = project_root / "web" / "frontend" / "src" / "composables" / "usePanel.ts"
    oversized = project_root / "tests" / "e2e" / "big.spec.ts"

    write_lines(healthy, 500)
    write_lines(oversized, 1001)

    completed = run_guard(project_root, "--scope-root", "web/frontend", "--scope-root", "tests")

    assert completed.returncode == 1
    payload = json.loads(completed.stdout)
    assert payload["checked_files"] == 2
    assert payload["oversized_count"] == 1
    assert payload["violations"][0]["path"] == "tests/e2e/big.spec.ts"
