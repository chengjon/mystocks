from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "compliance" / "backend_singleton_none_guard.py"


def run_guard(project_root: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    assert SCRIPT_PATH.exists(), f"missing script: {SCRIPT_PATH}"
    command = [sys.executable, str(SCRIPT_PATH), "--root-dir", str(project_root), "--format", "json", *extra_args]
    return subprocess.run(command, capture_output=True, text=True, check=False, cwd=PROJECT_ROOT)


def test_passes_when_global_singleton_has_module_level_none_init(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    target = project_root / "web" / "backend" / "app" / "core" / "singleton_ok.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        """
from __future__ import annotations

_manager = None

def get_manager():
    global _manager
    if _manager is None:
        _manager = object()
    return _manager
""".strip(),
        encoding="utf-8",
    )

    completed = run_guard(project_root)

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["summary"]["errors"] == 0
    assert payload["checked_files"] == 1


def test_passes_for_annotated_none_init(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    target = project_root / "web" / "backend" / "app" / "core" / "annotated_ok.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        """
from __future__ import annotations

from typing import Optional

_manager: Optional[object] = None

def get_manager():
    global _manager
    if _manager is None:
        _manager = object()
    return _manager
""".strip(),
        encoding="utf-8",
    )

    completed = run_guard(project_root)

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["summary"]["errors"] == 0


def test_fails_when_global_singleton_missing_none_init(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    target = project_root / "web" / "backend" / "app" / "core" / "singleton_bad.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        """
from __future__ import annotations

def get_manager():
    global _manager
    if _manager is None:
        _manager = object()
    return _manager
""".strip(),
        encoding="utf-8",
    )

    completed = run_guard(project_root)

    assert completed.returncode == 1
    payload = json.loads(completed.stdout)
    assert payload["summary"]["errors"] == 1
    assert payload["errors"][0]["path"] == "web/backend/app/core/singleton_bad.py"
    assert payload["errors"][0]["rule_id"] == "backend-singleton-none-init"
    assert payload["errors"][0]["names"] == ["_manager"]


def test_scope_paths_ignore_unrelated_existing_baseline_debt(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    bad = project_root / "web" / "backend" / "app" / "core" / "legacy_bad.py"
    ok = project_root / "web" / "backend" / "app" / "core" / "changed_ok.py"
    bad.parent.mkdir(parents=True, exist_ok=True)
    bad.write_text(
        """
def get_manager():
    global _legacy_manager
    if _legacy_manager is None:
        _legacy_manager = object()
    return _legacy_manager
""".strip(),
        encoding="utf-8",
    )
    ok.write_text(
        """
_changed_manager = None

def get_manager():
    global _changed_manager
    if _changed_manager is None:
        _changed_manager = object()
    return _changed_manager
""".strip(),
        encoding="utf-8",
    )

    completed = run_guard(project_root, "--path", "web/backend/app/core/changed_ok.py")

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert payload["summary"]["errors"] == 0
    assert payload["checked_files"] == 1


def test_passes_for_current_repo_state() -> None:
    completed = run_guard(PROJECT_ROOT)

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["summary"]["errors"] == 0

