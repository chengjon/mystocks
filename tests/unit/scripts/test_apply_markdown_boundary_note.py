from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "dev" / "apply_markdown_boundary_note.py"
GATE_SCRIPT_PATH = PROJECT_ROOT / "scripts" / "compliance" / "markdown_governance_gate.py"


def run_script(workdir: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(SCRIPT_PATH), *extra_args]
    return subprocess.run(command, capture_output=True, text=True, check=False, cwd=workdir)


def run_gate(workdir: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(GATE_SCRIPT_PATH), "--root-dir", str(workdir), "--format", "text", *extra_args]
    return subprocess.run(command, capture_output=True, text=True, check=False, cwd=PROJECT_ROOT)


def init_repo(project_root: Path) -> None:
    project_root.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init"], cwd=project_root, check=True, capture_output=True, text=True)


def test_inserts_navigation_note_after_first_heading(tmp_path: Path) -> None:
    target = tmp_path / "guide.md"
    target.write_text("# Guide\n\nBody\n", encoding="utf-8")

    completed = run_script(tmp_path, "--preset", "navigation", str(target))

    assert completed.returncode == 0, completed.stdout + completed.stderr
    content = target.read_text(encoding="utf-8")
    assert content.startswith("# Guide\n\n> **导航说明**:")
    assert "architecture/STANDARDS.md" in content
    assert "AGENTS.md" in content
    assert "CLAUDE.md" in content


def test_inserts_note_at_top_when_heading_is_missing(tmp_path: Path) -> None:
    target = tmp_path / "notes.md"
    target.write_text("plain body\n", encoding="utf-8")

    completed = run_script(tmp_path, "--preset", "historical", str(target))

    assert completed.returncode == 0, completed.stdout + completed.stderr
    content = target.read_text(encoding="utf-8")
    assert content.startswith("> **历史文档说明**:")
    assert content.rstrip().endswith("plain body")


def test_skips_when_boundary_note_exists_without_replace_flag(tmp_path: Path) -> None:
    target = tmp_path / "existing.md"
    target.write_text("# Existing\n\n> **导航说明**:\n> old text\n\nBody\n", encoding="utf-8")

    completed = run_script(tmp_path, "--preset", "navigation", str(target))

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "SKIPPED" in completed.stdout
    assert "> old text" in target.read_text(encoding="utf-8")


def test_replaces_existing_boundary_note_with_replace_flag(tmp_path: Path) -> None:
    target = tmp_path / "existing.md"
    target.write_text("# Existing\n\n> **导航说明**:\n> old text\n\nBody\n", encoding="utf-8")

    completed = run_script(tmp_path, "--preset", "usage", "--replace-existing", str(target))

    assert completed.returncode == 0, completed.stdout + completed.stderr
    content = target.read_text(encoding="utf-8")
    assert "REPLACED" in completed.stdout
    assert "> old text" not in content
    assert "> **使用说明**:" in content


def test_returns_error_for_non_markdown_file(tmp_path: Path) -> None:
    target = tmp_path / "notes.txt"
    target.write_text("plain body\n", encoding="utf-8")

    completed = run_script(tmp_path, "--preset", "navigation", str(target))

    assert completed.returncode == 1
    assert "expected a .md file" in completed.stdout


def test_rejects_custom_title_outside_allowed_boundary_titles(tmp_path: Path) -> None:
    target = tmp_path / "guide.md"
    target.write_text("# Guide\n\nBody\n", encoding="utf-8")

    completed = run_script(tmp_path, "--preset", "navigation", "--title", "文档用途", str(target))

    assert completed.returncode == 1
    assert "unsupported boundary note title" in completed.stdout


def test_generated_boundary_note_passes_markdown_governance_gate(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    init_repo(project_root)
    target = project_root / "docs" / "report.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("# Report\n\nBody\n", encoding="utf-8")

    completed = run_script(project_root, "--preset", "historical", str(target))

    assert completed.returncode == 0, completed.stdout + completed.stderr
    subprocess.run(["git", "add", "docs/report.md"], cwd=project_root, check=True, capture_output=True, text=True)
    gate_completed = run_gate(project_root, "--path", "docs/report.md")

    assert gate_completed.returncode == 0, gate_completed.stdout + gate_completed.stderr
    assert "No markdown governance violations detected." in gate_completed.stdout


def test_auto_preset_selects_historical_for_reports_paths(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    init_repo(project_root)
    target = project_root / "docs" / "reports" / "status.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("# Status\n\nBody\n", encoding="utf-8")

    completed = run_script(project_root, "--preset", "auto", str(target))

    assert completed.returncode == 0, completed.stdout + completed.stderr
    content = target.read_text(encoding="utf-8")
    assert "> **历史文档说明**:" in content


def test_auto_preset_selects_usage_for_task_paths(tmp_path: Path) -> None:
    project_root = tmp_path / "repo"
    init_repo(project_root)
    target = project_root / "foo" / "TASK.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("# TASK\n\nBody\n", encoding="utf-8")

    completed = run_script(project_root, "--preset", "auto", str(target))

    assert completed.returncode == 0, completed.stdout + completed.stderr
    content = target.read_text(encoding="utf-8")
    assert "> **使用说明**:" in content


def test_inserts_boundary_note_after_front_matter_when_heading_is_missing(tmp_path: Path) -> None:
    target = tmp_path / "workflow.md"
    target.write_text("---\nkey: value\n---\n\nBody\n", encoding="utf-8")

    completed = run_script(tmp_path, "--preset", "usage", str(target))

    assert completed.returncode == 0, completed.stdout + completed.stderr
    content = target.read_text(encoding="utf-8")
    assert content.startswith("---\nkey: value\n---\n\n> **使用说明**:")
    assert content.rstrip().endswith("Body")


def test_inserts_boundary_note_after_heading_when_front_matter_and_heading_both_exist(tmp_path: Path) -> None:
    target = tmp_path / "workflow.md"
    target.write_text("---\nkey: value\n---\n\n# Workflow\n\nBody\n", encoding="utf-8")

    completed = run_script(tmp_path, "--preset", "usage", str(target))

    assert completed.returncode == 0, completed.stdout + completed.stderr
    content = target.read_text(encoding="utf-8")
    assert content.startswith("---\nkey: value\n---\n\n# Workflow\n\n> **使用说明**:")
    assert content.rstrip().endswith("Body")
