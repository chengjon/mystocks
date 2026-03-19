from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
WORKFLOW_ROOT = PROJECT_ROOT / ".github" / "workflows"


def _read_workflow(name: str) -> str:
    return (WORKFLOW_ROOT / name).read_text(encoding="utf-8")


def test_api_automation_discovery_uses_python_module_pip_and_backend_runtime_dependencies() -> None:
    workflow = _read_workflow("api-automation-discovery.yml")

    assert "python -m pip install -r requirements.txt" in workflow
    assert "python -m pip install -r /tmp/backend-requirements-ci.txt" in workflow
    assert "uvicorn" in workflow
    assert "email-validator" in workflow
    assert "scripts/run-api-tests.sh" in workflow


def test_api_contract_validation_uses_backend_import_environment_and_scope_gate() -> None:
    workflow = _read_workflow("api-contract-validation.yml")

    assert "contract_scope_changed" in workflow
    assert "Detect contract scope changes" in workflow
    assert "PYTHONPATH=$PWD/web/backend" in workflow
    assert "from app.api.contract.models import ContractVersion, ContractDiff, ContractValidation" in workflow
    assert "from app.main import app" in workflow
    assert "continue-on-error: true" in workflow


def test_api_contract_validation_report_job_tolerates_missing_generated_spec() -> None:
    workflow = _read_workflow("api-contract-validation.yml")
    report_section = workflow.split("name: Generate Contract Validation Report", 1)[1]
    download_section = report_section.split("- name: Generate comprehensive report", 1)[0]

    assert "continue-on-error: true" in download_section
    assert "if: needs.validate-contracts.outputs.contract_scope_changed == 'true'" in download_section


def test_api_contract_validation_pr_comment_is_non_blocking() -> None:
    workflow = _read_workflow("api-contract-validation.yml")
    report_section = workflow.split("name: Generate Contract Validation Report", 1)[1]
    comment_section = report_section.split("- name: Comment on PR", 1)[1].split("uses: actions/github-script@v7", 1)[0]

    assert "continue-on-error: true" in comment_section


def test_api_contract_and_api_file_workflows_install_backend_runtime_dependencies() -> None:
    contract_workflow = _read_workflow("api-contract-validation.yml")
    api_file_workflow = _read_workflow("api-file-tests.yml")

    assert "pip install -r web/backend/requirements.txt" in contract_workflow

    for package_name in (
        "structlog",
        "email-validator",
        "sqlalchemy",
        "PyJWT",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
        "openpyxl",
        "prometheus-client",
        "pydantic-settings",
        "psutil",
    ):
        assert package_name in api_file_workflow

    assert "ports:" in api_file_workflow
    assert "- 5432:5432" in api_file_workflow
    assert "- 6379:6379" in api_file_workflow


def test_api_file_workflow_uses_readiness_gate_and_real_pytest_modules() -> None:
    workflow = _read_workflow("api-file-tests.yml")

    assert "api-file-tests-readiness" in workflow
    assert "needs: api-file-tests-readiness" in workflow
    assert "needs.api-file-tests-readiness.outputs.ready == 'true'" in workflow
    assert "python-version: [3.11, 3.12]" in workflow
    assert "python -m pytest tests/api/file_tests -q -o addopts=''" in workflow
    assert "Enforce file test coverage threshold" in workflow


def test_data_sync_workflow_uses_python_module_pip_and_ci_safe_pytest_invocations() -> None:
    workflow = _read_workflow("data-sync-testing.yml")

    assert "python -m pip install -r requirements.txt" in workflow
    assert "python -m pip install pytest pytest-asyncio pytest-cov pytest-mock schemathesis locust" in workflow
    assert "BASE_URL=http://localhost:8000 python -m pytest -o addopts=''" in workflow
    assert "python -m pytest -o addopts='' tests/data_mapping_tests.py -v" in workflow
    assert "BASE_URL=http://localhost:8000 python tests/real_data_synchronization_test.py" in workflow
    assert "ports:" in workflow
    assert "- 5432:5432" in workflow
    assert "psql -h localhost -U postgres -d postgres -tc" in workflow
    assert "uses: actions/download-artifact@v4" in workflow


def test_legacy_e2e_workflow_declares_stable_port_defaults() -> None:
    workflow = _read_workflow("e2e-test.yml")

    assert "FRONTEND_PORT: '3020'" in workflow
    assert "FRONTEND_BACKUP_PORT: '3021'" in workflow
    assert "BACKEND_PORT: '8020'" in workflow
    assert "BACKEND_BACKUP_PORT: '8021'" in workflow


def test_kline_e2e_mocks_readiness_endpoint_before_navigation() -> None:
    spec = (PROJECT_ROOT / "web" / "frontend" / "tests" / "e2e" / "kline-chart.spec.ts").read_text(encoding="utf-8")

    assert "**/api/health/ready" in spec
    assert "e2e-kline-ready" in spec


def test_contract_testing_workflow_skips_when_framework_is_absent() -> None:
    workflow = _read_workflow("contract-testing.yml")

    assert "contract-framework-readiness" in workflow
    assert "if [ -d \"src/contract_testing\" ]" in workflow
    assert "needs: contract-framework-readiness" in workflow
    assert "needs.contract-framework-readiness.outputs.ready == 'true'" in workflow


def test_playwright_workflow_runs_smoke_subset_only() -> None:
    workflow = _read_workflow("playwright.yml")

    assert "npx playwright install --with-deps chromium" in workflow
    assert "Run Playwright smoke tests" in workflow
    assert "tests/env-test.spec.ts" in workflow
    assert "--config=playwright.config.ts" in workflow


def test_security_enhancement_pr_comment_is_non_blocking() -> None:
    workflow = _read_workflow("security-enhancement.yml")

    assert "Comment security summary on PR" in workflow
    assert "continue-on-error: true" in workflow


def test_security_enhancement_fetches_full_history_for_secret_scanning() -> None:
    workflow = _read_workflow("security-enhancement.yml")

    assert "Scan for secrets" in workflow
    assert "fetch-depth: 0" in workflow


def test_security_enhancement_skips_missing_license_header_script_and_uploads_bandit_artifact() -> None:
    workflow = _read_workflow("security-enhancement.yml")

    assert 'if [ -f "scripts/check_license_headers.py" ]; then' in workflow
    assert "License header check script not present; skipping file header scan" in workflow
    assert "Generate Bandit JSON report" in workflow
    assert "continue-on-error: true" in workflow
    assert "name: bandit-security-report" in workflow


def test_security_enhancement_uses_inline_security_summary_and_threshold_checks() -> None:
    workflow = _read_workflow("security-enhancement.yml")

    assert "Download Bandit security report" in workflow
    assert "bandit-report.json" in workflow
    assert "scripts/generate_security_report.py" not in workflow
    assert "scripts/check_security_thresholds.py" not in workflow


def test_ai_test_optimization_uses_repo_repo_for_new_pr_comments() -> None:
    workflow = _read_workflow("ai-test-optimization.yml")

    assert "await github.rest.issues.createComment" in workflow
    assert "repo: context.repo.repo" in workflow
    assert "repo: context.repo.name" not in workflow


def test_ai_test_optimization_normalizes_changed_file_outputs_and_tolerates_missing_reports() -> None:
    workflow = _read_workflow("ai-test-optimization.yml")

    assert "NORMALIZED_CHANGED_FILES=" in workflow
    assert 'tr "\\n" " "' in workflow or "tr '\\n' ' '" in workflow
    assert 'echo "python-files=$NORMALIZED_CHANGED_FILES" >> $GITHUB_OUTPUT' in workflow

    quality_gate_section = workflow.split("name: Quality Gate", 1)[1].split("- name: Quality Gate Evaluation", 1)[0]
    summary_section = workflow.split("name: AI Optimization Summary", 1)[1].split("- name: Generate Summary", 1)[0]

    assert "continue-on-error: true" in quality_gate_section
    assert "continue-on-error: true" in summary_section


def test_ai_test_optimization_pr_comment_is_non_blocking() -> None:
    workflow = _read_workflow("ai-test-optimization.yml")
    comment_section = workflow.split("- name: Comment on PR", 1)[1].split("uses: actions/github-script@v6", 1)[0]

    assert "continue-on-error: true" in comment_section


def test_frontend_testing_uses_repo_root_relative_compliance_script_paths() -> None:
    workflow = _read_workflow("frontend-testing.yml")

    assert "python ../../scripts/compliance/app_route_purity_gate.py" in workflow
    assert "python ../../scripts/compliance/request_id_visibility_gate.py" in workflow


def test_python_and_typescript_type_check_workflows_download_artifacts_into_workspace() -> None:
    python_workflow = _read_workflow("python-type-check.yml")
    typescript_workflow = _read_workflow("typescript-type-check.yml")

    python_section = python_workflow.split("Download all type check artifacts", 1)[1].split("Generate consolidated report", 1)[0]
    typescript_section = typescript_workflow.split("Download all type check artifacts", 1)[1].split(
        "Generate consolidated report", 1
    )[0]

    assert "uses: actions/download-artifact@v4" in python_section
    assert "path: ." in python_section

    assert "uses: actions/download-artifact@v4" in typescript_section
    assert "path: ." in typescript_section


def test_directory_compliance_uses_current_root_budget_and_excludes_api_wrapper() -> None:
    workflow = _read_workflow("directory-compliance.yml")

    assert "MAX_ROOT_DIRS=15" in workflow
    assert "MAX_ROOT_FILES=32" in workflow
    assert "! -name 'run-api-tests.sh'" in workflow


def test_coverage_and_performance_workflows_download_artifacts_into_workspace() -> None:
    coverage_workflow = _read_workflow("coverage-expansion.yml")
    performance_workflow = _read_workflow("performance-testing.yml")

    coverage_section = coverage_workflow.split("Download coverage report", 1)[1].split("Generate test expansion plan", 1)[0]
    performance_section = performance_workflow.split("Download performance results", 1)[1].split(
        "Check for performance regressions", 1
    )[0]

    assert "uses: actions/download-artifact@v4" in coverage_section
    assert "path: ." in coverage_section

    assert "uses: actions/download-artifact@v4" in performance_section
    assert "path: ." in performance_section


def test_security_testing_merges_downloaded_artifacts_into_workspace() -> None:
    workflow = _read_workflow("security-testing.yml")

    all_security_section = workflow.split("Download all security artifacts", 1)[1].split(
        "Generate consolidated security report", 1
    )[0]
    quality_gate_section = workflow.split("Download security reports", 1)[1].split("Security Quality Gate Check", 1)[0]
    final_section = workflow.split("Download final security reports", 1)[1].split("Final security verification", 1)[0]

    assert "uses: actions/download-artifact@v4" in all_security_section
    assert "path: ." in all_security_section
    assert "merge-multiple: true" in all_security_section

    assert "uses: actions/download-artifact@v4" in quality_gate_section
    assert "path: ." in quality_gate_section
    assert "merge-multiple: true" in quality_gate_section

    assert "uses: actions/download-artifact@v4" in final_section
    assert "path: ." in final_section


def test_quant_strategy_validation_uses_existing_script_path_and_safe_issue_body_heredoc() -> None:
    workflow = _read_workflow("quant-strategy-validation.yml")

    assert "chmod +x scripts/dev/ci/quant_strategy_validation.py" in workflow
    assert "python scripts/dev/ci/quant_strategy_validation.py" in workflow
    assert 'ISSUE_BODY=$(cat <<EOF' in workflow
    assert '$(cat "$GITHUB_STEP_SUMMARY"' in workflow


def test_mainline_governance_summary_uses_single_line_python_command() -> None:
    workflow = _read_workflow("mainline-governance.yml")

    assert "Add workflow summary" in workflow
    assert "python -c 'import json, os; from pathlib import Path;" in workflow
    assert "python - <<'PY'" not in workflow
