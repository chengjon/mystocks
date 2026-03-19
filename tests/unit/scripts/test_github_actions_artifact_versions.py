from __future__ import annotations

from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[3]
WORKFLOW_ROOT = PROJECT_ROOT / ".github" / "workflows"
EXTERNALLY_OWNED_WORKFLOWS = {"data-sync-testing.yml"}


def test_github_actions_workflows_do_not_use_deprecated_artifact_v3() -> None:
    deprecated_hits: list[str] = []

    for workflow in sorted(WORKFLOW_ROOT.glob("*.yml")):
        if workflow.name in EXTERNALLY_OWNED_WORKFLOWS:
            continue
        content = workflow.read_text(encoding="utf-8", errors="ignore")
        if "actions/upload-artifact@v3" in content or "actions/download-artifact@v3" in content:
            deprecated_hits.append(workflow.relative_to(PROJECT_ROOT).as_posix())

    assert deprecated_hits == []


def test_github_actions_download_artifact_v4_steps_define_a_path() -> None:
    missing_path_hits: list[str] = []

    for workflow in sorted(WORKFLOW_ROOT.glob("*.yml")):
        if workflow.name in EXTERNALLY_OWNED_WORKFLOWS:
            continue
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
                missing_path_hits.append(f"{workflow.relative_to(PROJECT_ROOT).as_posix()}::{step_name}")

    assert missing_path_hits == []


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
    assert "repo: context.repo.name" not in content
    assert "repo: context.repo.repo" in content
    assert "continue-on-error: true" in content


def test_ci_cd_with_type_checking_uses_explicit_installable_type_stubs() -> None:
    workflow = WORKFLOW_ROOT / "ci-cd-with-type-checking.yml"
    content = workflow.read_text(encoding="utf-8", errors="ignore")

    assert "pip install mypy types-all" not in content
    assert "pip install mypy types-requests types-PyYAML" in content


def test_api_automation_discovery_workflow_uses_existing_runner_and_backend_runtime_packages() -> None:
    workflow = WORKFLOW_ROOT / "api-automation-discovery.yml"
    content = workflow.read_text(encoding="utf-8", errors="ignore")

    assert "chmod +x run-api-tests.sh" not in content
    assert "./run-api-tests.sh -u http://localhost:8000" not in content
    assert "chmod +x scripts/run-api-tests.sh" in content
    assert "BACKEND_PORT=8000 API_BASE_URL=http://localhost:8000 ./scripts/run-api-tests.sh all" in content
    assert "structlog" in content
    assert "PyJWT" in content
    assert "PYTHONPATH=.:web/backend python -m uvicorn web.backend.app.main:app" in content


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


def test_e2e_testing_workflow_uses_explicit_pm2_orchestration() -> None:
    workflow = WORKFLOW_ROOT / "e2e-testing.yml"
    content = workflow.read_text(encoding="utf-8", errors="ignore")

    assert "npm install -g pm2" in content
    assert "pm2 start ecosystem.test.config.js" in content
    assert "pm2 status" in content
    assert "pm2 delete all || true" in content


def test_code_quality_workflow_downloads_v4_artifacts_to_explicit_paths() -> None:
    workflow = WORKFLOW_ROOT / "code-quality.yml"
    content = workflow.read_text(encoding="utf-8", errors="ignore")

    assert "uses: actions/download-artifact@v4" in content
    assert "path: quality-artifacts/" in content
    assert "path: quality-reports/" in content
    assert "path: ci-artifacts/" in content


def test_code_quality_final_report_needs_existing_jobs_only() -> None:
    workflow = WORKFLOW_ROOT / "code-quality.yml"
    content = workflow.read_text(encoding="utf-8", errors="ignore")

    assert "needs: [security-gate, quality-gate]" not in content
    assert "needs: [hardcoding-governance, quality-gate]" in content
    assert "needs.hardcoding-governance.result" in content
    assert "fetch-depth: 0" in content


def test_security_enhancement_workflow_does_not_reference_missing_helper_scripts() -> None:
    workflow = WORKFLOW_ROOT / "security-enhancement.yml"
    content = workflow.read_text(encoding="utf-8", errors="ignore")

    assert "scripts/check_license_headers.py" not in content
    assert "scripts/generate_security_report.py" not in content
    assert "scripts/check_security_thresholds.py" not in content
    assert "../bandit-report.json" not in content
    assert "name: code-security-results" in content
    assert "continue-on-error: true" in content


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
