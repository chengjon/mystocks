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


def test_target_workflows_are_valid_yaml() -> None:
    for filename in ("mainline-governance.yml", "directory-compliance.yml"):
        workflow = WORKFLOW_ROOT / filename
        yaml.safe_load(workflow.read_text(encoding="utf-8", errors="ignore"))


def test_mainline_governance_summary_avoids_heredoc_python_block() -> None:
    workflow = WORKFLOW_ROOT / "mainline-governance.yml"
    content = workflow.read_text(encoding="utf-8", errors="ignore")

    assert "python - <<'PY'" not in content
    assert "python -c '" in content


def test_directory_compliance_uses_budgeted_root_file_threshold_variable() -> None:
    workflow = WORKFLOW_ROOT / "directory-compliance.yml"
    content = workflow.read_text(encoding="utf-8", errors="ignore")

    assert "MAX_ROOT_FILES=40" in content
    assert 'echo "Root files: $ROOT_FILES (max: $MAX_ROOT_FILES)"' in content
    assert 'if [ "$ROOT_FILES" -gt "$MAX_ROOT_FILES" ]' in content
    assert 'if [ "$ROOT_FILES" -gt 20 ]' not in content


def test_ai_test_optimization_uses_multiline_github_output_for_changed_python_files() -> None:
    workflow = WORKFLOW_ROOT / "ai-test-optimization.yml"
    content = workflow.read_text(encoding="utf-8", errors="ignore")

    assert 'echo "python-files=$CHANGED_FILES" >> $GITHUB_OUTPUT' not in content
    assert 'echo "files=$FILES" >> $GITHUB_OUTPUT' not in content
    assert 'echo "python-files<<EOF"' in content
    assert 'echo "files<<EOF"' in content


def test_ci_cd_with_type_checking_uses_explicit_installable_type_stubs() -> None:
    workflow = WORKFLOW_ROOT / "ci-cd-with-type-checking.yml"
    content = workflow.read_text(encoding="utf-8", errors="ignore")

    assert "pip install mypy types-all" not in content
    assert "pip install mypy types-requests types-PyYAML" in content


def test_ci_cd_workflow_references_existing_test_chain_scripts() -> None:
    workflow = WORKFLOW_ROOT / "ci-cd.yml"
    content = workflow.read_text(encoding="utf-8", errors="ignore")

    assert "ls -la scripts/test-runner/run-orchestration.sh" not in content
    assert "ls -la scripts/tools/run-performance-suite.sh" not in content
    assert 'python -c "import sys; sys.path.append(\'.\'); from scripts.tools import ai_test_assistant"' not in content

    assert "scripts/tests/test-runner/run-orchestration.sh" in content
    assert "scripts/dev/tools/run-performance-suite.sh" in content
    assert "python -m py_compile scripts/dev/tools/ai_test_assistant.py" in content


def test_ci_cd_workflow_uses_existing_performance_suite_script() -> None:
    workflow = WORKFLOW_ROOT / "ci-cd.yml"
    content = workflow.read_text(encoding="utf-8", errors="ignore")

    assert "scripts/tools/performance_test_suite.py" not in content
    assert "scripts/dev/tools/performance_test_suite.py" in content


def test_data_sync_testing_workflow_uses_pm2_and_downloads_artifacts() -> None:
    workflow = WORKFLOW_ROOT / "data-sync-testing.yml"
    content = workflow.read_text(encoding="utf-8", errors="ignore")

    assert "npm install -g pm2" in content
    assert "pm2 start ecosystem.test.config.js" in content
    assert "pm2 status" in content
    assert "uses: actions/download-artifact@v4" in content
    assert "uses: actions/upload-artifact@v4" in content


def test_e2e_testing_workflow_uses_explicit_pm2_orchestration() -> None:
    workflow = WORKFLOW_ROOT / "e2e-testing.yml"
    content = workflow.read_text(encoding="utf-8", errors="ignore")

    assert "npm install -g pm2" in content
    assert "pm2 start ecosystem.test.config.js" in content
    assert "pm2 status" in content
    assert "pm2 delete all || true" in content


def test_visual_baseline_update_workflow_uses_pm2_and_job_outputs() -> None:
    workflow = WORKFLOW_ROOT / "visual-baseline-update.yml"
    content = workflow.read_text(encoding="utf-8", errors="ignore")

    assert "npm install -g pm2" in content
    assert "pm2 start ecosystem.test.config.js" in content
    assert "outputs:\n      has_changes: ${{ steps.changed.outputs.has_changes }}" in content
    assert "needs.update-baselines.outputs.has_changes" in content
    assert "pm2 delete all || true" in content


def test_visual_testing_workflow_uses_explicit_pm2_orchestration() -> None:
    workflow = WORKFLOW_ROOT / "visual-testing.yml"
    content = workflow.read_text(encoding="utf-8", errors="ignore")

    assert "npm install -g pm2" in content
    assert "pm2 start ecosystem.test.config.js" in content
    assert "pm2 status" in content
    assert "pm2 delete all || true" in content
