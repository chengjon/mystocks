from __future__ import annotations

from pathlib import Path

import yaml


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


def test_ci_cd_workflow_references_existing_test_chain_scripts() -> None:
    workflow = WORKFLOW_ROOT / "ci-cd.yml"
    content = workflow.read_text(encoding="utf-8", errors="ignore")

    assert "scripts/test-runner/run-orchestration.sh" not in content
    assert "scripts/tools/run-performance-suite.sh" not in content
    assert "from scripts.tools import ai_test_assistant" not in content
    assert "cicd_summary.md" not in content

    assert "scripts/tests/test-runner/run-orchestration.sh" in content
    assert "scripts/dev/tools/run-performance-suite.sh" in content
    assert "python -m py_compile scripts/dev/tools/ai_test_assistant.py" in content


def test_security_enhancement_workflow_does_not_reference_missing_helper_scripts() -> None:
    workflow = WORKFLOW_ROOT / "security-enhancement.yml"
    content = workflow.read_text(encoding="utf-8", errors="ignore")

    assert "scripts/check_license_headers.py" not in content
    assert "scripts/generate_security_report.py" not in content
    assert "scripts/check_security_thresholds.py" not in content
    assert "../bandit-report.json" not in content


def test_ci_cd_workflow_uses_existing_performance_suite_script() -> None:
    workflow = WORKFLOW_ROOT / "ci-cd.yml"
    content = workflow.read_text(encoding="utf-8", errors="ignore")

    assert "scripts/tools/performance_test_suite.py" not in content
    assert "scripts/dev/tools/performance_test_suite.py" in content


def test_quant_strategy_validation_workflow_uses_existing_strategy_validation_script() -> None:
    workflow = WORKFLOW_ROOT / "quant-strategy-validation.yml"
    content = workflow.read_text(encoding="utf-8", errors="ignore")

    assert "scripts/ci/quant_strategy_validation.py" not in content
    assert "scripts/dev/ci/quant_strategy_validation.py" in content


def test_quant_strategy_validation_workflow_is_valid_yaml() -> None:
    workflow = WORKFLOW_ROOT / "quant-strategy-validation.yml"
    yaml.safe_load(workflow.read_text(encoding="utf-8", errors="ignore"))
