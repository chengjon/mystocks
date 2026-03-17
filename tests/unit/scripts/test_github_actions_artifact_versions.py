from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
WORKFLOW_ROOT = PROJECT_ROOT / ".github" / "workflows"


def test_github_actions_workflows_do_not_use_deprecated_artifact_v3() -> None:
    deprecated_hits: list[str] = []

    for workflow in sorted(WORKFLOW_ROOT.glob("*.yml")):
        content = workflow.read_text(encoding="utf-8", errors="ignore")
        if "actions/upload-artifact@v3" in content or "actions/download-artifact@v3" in content:
            deprecated_hits.append(workflow.relative_to(PROJECT_ROOT).as_posix())

    assert deprecated_hits == []


def test_github_actions_download_artifact_v4_steps_define_a_path() -> None:
    missing_path_hits: list[str] = []

    for workflow in sorted(WORKFLOW_ROOT.glob("*.yml")):
        lines = workflow.read_text(encoding="utf-8", errors="ignore").splitlines()
        for index, line in enumerate(lines):
            if "uses: actions/download-artifact@v4" not in line:
                continue

            uses_indent = len(line) - len(line.lstrip())
            block_end = len(lines)
            for cursor in range(index + 1, len(lines)):
                candidate = lines[cursor]
                if not candidate.strip():
                    continue
                candidate_indent = len(candidate) - len(candidate.lstrip())
                if candidate_indent <= uses_indent and candidate.lstrip().startswith("- "):
                    block_end = cursor
                    break

            step_block = lines[index:block_end]
            has_path = any(candidate.lstrip().startswith("path:") for candidate in step_block)
            if not has_path:
                step_name = "<unnamed>"
                for candidate in reversed(lines[: index + 1]):
                    stripped = candidate.lstrip()
                    if stripped.startswith("name:"):
                        step_name = stripped.split(":", 1)[1].strip()
                        break
                missing_path_hits.append(
                    f"{workflow.relative_to(PROJECT_ROOT).as_posix()}::{step_name}"
                )

    assert missing_path_hits == []


def test_ai_test_optimization_uses_multiline_github_output_for_changed_files() -> None:
    workflow = WORKFLOW_ROOT / "ai-test-optimization.yml"
    content = workflow.read_text(encoding="utf-8", errors="ignore")

    assert 'echo "python-files=$CHANGED_FILES" >> $GITHUB_OUTPUT' not in content
    assert 'echo "files=$FILES" >> $GITHUB_OUTPUT' not in content
