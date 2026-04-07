from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "compliance" / "markdown_governance_gate.py"


def init_repo(project_root: Path) -> None:
    project_root.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init"], cwd=project_root, check=True, capture_output=True, text=True)


def add_tracked_file(project_root: Path, relative_path: str, content: str) -> None:
    target = project_root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    subprocess.run(["git", "add", relative_path], cwd=project_root, check=True, capture_output=True, text=True)


def run_guard(project_root: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    assert SCRIPT_PATH.exists(), f"missing script: {SCRIPT_PATH}"
    command = [sys.executable, str(SCRIPT_PATH), "--root-dir", str(project_root), "--format", "json", *extra_args]
    return subprocess.run(command, capture_output=True, text=True, check=False, cwd=PROJECT_ROOT)


def test_fails_when_boundary_note_is_missing(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    init_repo(project_root)
    add_tracked_file(project_root, "docs/guide.md", "# Guide\n\nNo boundary note here.\n")

    completed = run_guard(project_root)

    assert completed.returncode == 1
    payload = json.loads(completed.stdout)
    assert payload["summary"]["errors"] == 1
    assert payload["errors"][0]["path"] == "docs/guide.md"
    assert payload["errors"][0]["mode"] == "missing-boundary-note"
    assert "apply_markdown_boundary_note.py --preset authority docs/guide.md" in payload["errors"][0]["fix_hint"]


def test_fails_when_banned_phrase_is_present(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    init_repo(project_root)
    add_tracked_file(
        project_root,
        "docs/status.md",
        "> **历史状态说明**: 当前共享规则以 `architecture/STANDARDS.md` 为准。\n\n若冲突，以后者为准。\n",
    )

    completed = run_guard(project_root)

    assert completed.returncode == 1
    payload = json.loads(completed.stdout)
    assert payload["summary"]["errors"] == 1
    assert payload["errors"][0]["mode"] == "banned-phrases"
    assert "以后者为准" in payload["errors"][0]["banned_phrases"]
    assert "explicit canonical file paths" in payload["errors"][0]["fix_hint"]


def test_path_mode_checks_only_selected_markdown_files(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    init_repo(project_root)
    add_tracked_file(
        project_root,
        "docs/good.md",
        "> **导航说明**: 当前共享规则以 `architecture/STANDARDS.md` 为准。\n\n正文。\n",
    )
    add_tracked_file(project_root, "docs/bad.md", "# Missing note\n")
    notes = project_root / "docs" / "notes.txt"
    notes.parent.mkdir(parents=True, exist_ok=True)
    notes.write_text("not markdown", encoding="utf-8")

    completed = run_guard(project_root, "--path", "docs/good.md", "--path", "docs/notes.txt")

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["checked_files"] == 1
    assert payload["summary"]["errors"] == 0
    assert payload["results"][0]["path"] == "docs/good.md"


def test_excluded_paths_are_not_blocked(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    init_repo(project_root)
    add_tracked_file(project_root, "openspec/AGENTS.md", "# OpenSpec\n\nNo boundary note on purpose.\n")

    completed = run_guard(project_root)

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["checked_files"] == 1
    assert payload["summary"]["errors"] == 0
    assert payload["results"][0]["mode"] == "excluded"


def test_full_scan_handles_non_ascii_markdown_paths(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    init_repo(project_root)
    add_tracked_file(
        project_root,
        "docs/中文说明.md",
        "> **导航说明**: 当前共享规则以 `architecture/STANDARDS.md` 为准。\n\n正文。\n",
    )

    completed = run_guard(project_root)

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["summary"]["errors"] == 0
    assert any(result["path"] == "docs/中文说明.md" for result in payload["results"])


def test_full_scan_ignores_tracked_markdown_files_missing_in_dirty_worktree(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    init_repo(project_root)
    add_tracked_file(
        project_root,
        "docs/to-be-removed.md",
        "> **导航说明**: 当前共享规则以 `architecture/STANDARDS.md` 为准。\n\n正文。\n",
    )
    (project_root / "docs" / "to-be-removed.md").unlink()

    completed = run_guard(project_root)

    assert completed.returncode == 0, completed.stdout + completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["summary"]["errors"] == 0
    assert all(result["path"] != "docs/to-be-removed.md" for result in payload["results"])


def test_report_recommends_historical_preset_for_reports_paths(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    init_repo(project_root)
    add_tracked_file(project_root, "docs/reports/status.md", "# Status\n\nNo boundary note here.\n")

    completed = run_guard(project_root)

    assert completed.returncode == 1
    payload = json.loads(completed.stdout)
    assert (
        "apply_markdown_boundary_note.py --preset historical docs/reports/status.md" in payload["errors"][0]["fix_hint"]
    )


def test_report_recommends_usage_preset_for_task_files(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    init_repo(project_root)
    add_tracked_file(project_root, "foo/TASK.md", "# TASK\n\nMissing note\n")

    completed = run_guard(project_root)

    assert completed.returncode == 1
    payload = json.loads(completed.stdout)
    assert "apply_markdown_boundary_note.py --preset usage foo/TASK.md" in payload["errors"][0]["fix_hint"]


def test_report_recommends_usage_preset_for_task_files(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    init_repo(project_root)
    add_tracked_file(project_root, "foo/TASK.md", "# TASK\n\nMissing note\n")

    completed = run_guard(project_root)

    assert completed.returncode == 1
    payload = json.loads(completed.stdout)
    assert "apply_markdown_boundary_note.py --preset usage foo/TASK.md" in payload["errors"][0]["fix_hint"]


def test_report_recommends_usage_preset_for_task_files(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    init_repo(project_root)
    add_tracked_file(project_root, "foo/TASK.md", "# TASK\n\nMissing note\n")

    completed = run_guard(project_root)

    assert completed.returncode == 1
    payload = json.loads(completed.stdout)
    assert "apply_markdown_boundary_note.py --preset usage foo/TASK.md" in payload["errors"][0]["fix_hint"]
