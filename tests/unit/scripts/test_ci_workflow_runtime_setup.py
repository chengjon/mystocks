from __future__ import annotations

from pathlib import Path
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[3]
WORKFLOW_ROOT = PROJECT_ROOT / ".github" / "workflows"


def _read_workflow(name: str) -> str:
    return (WORKFLOW_ROOT / name).read_text(encoding="utf-8")


    def test_key_workflows_are_valid_yaml_documents() -> None:
        for workflow_name in (
            "cicd-monthly-review.yml",
            "coverage-expansion.yml",
            "e2e-testing.yml",
            "e2e-tests-enhanced.yml",
            "performance-testing.yml",
            "python-type-check.yml",
            "security-testing.yml",
            "comprehensive-testing.yml",
            "test-coverage.yml",
            "typescript-type-check.yml",
        ):
            workflow_text = _read_workflow(workflow_name)
            assert yaml.safe_load(workflow_text) is not None


def test_api_automation_discovery_uses_python_module_pip_and_backend_runtime_dependencies() -> None:
    workflow = _read_workflow("api-automation-discovery.yml")

    assert "python -m pip install -r requirements.txt" in workflow
    assert "python -m pip install -r /tmp/backend-requirements-ci.txt" in workflow
    assert "uvicorn" in workflow
    assert "email-validator" in workflow
    assert "scripts/run-api-tests.sh" in workflow


def test_api_automation_discovery_sets_required_backend_runtime_env_vars() -> None:
    workflow = _read_workflow("api-automation-discovery.yml")

    assert "export POSTGRESQL_USER=postgres" in workflow
    assert "export BACKEND_PORT=8000" in workflow
    assert "export BACKEND_BACKUP_PORT=8001" in workflow


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


def test_data_sync_workflow_starts_backend_before_contract_tests_and_tolerates_missing_quality_artifacts() -> None:
    workflow = _read_workflow("data-sync-testing.yml")

    install_section = workflow.split("- name: Install Python dependencies", 1)[1].split("- name: Install frontend dependencies", 1)[0]
    assert "grep -Ev '^(TA-Lib|xlwings)==|^(TA-Lib|xlwings)>='" in install_section
    assert "python -m pip install -r /tmp/backend-requirements-ci.txt" in install_section

    assert "Start backend for API Contract Tests" in workflow
    contract_setup_section = workflow.split("- name: Start backend for API Contract Tests", 1)[1].split(
        "- name: Run API Contract Tests", 1
    )[0]
    assert "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000" in contract_setup_section
    assert "/tmp/contract_backend_pid" in contract_setup_section

    quality_gate_section = workflow.split("# Quality Gate Check", 1)[1]
    download_section = quality_gate_section.split("- name: Download Test Results", 1)[1].split("- name: Quality Gate Check", 1)[0]
    assert "continue-on-error: true" in download_section


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


def test_security_enhancement_scopes_bandit_to_relevant_python_changes() -> None:
    workflow = _read_workflow("security-enhancement.yml")

    assert "security-scope-detect" in workflow
    assert "bandit_required" in workflow
    assert "bandit_args" in workflow

    scope_section = workflow.split("security-scope-detect:", 1)[1].split("code-security-scan:", 1)[0]
    bandit_section = workflow.split("code-security-scan:", 1)[1].split("container-security:", 1)[0]

    assert "git diff --name-only" in scope_section
    assert "src/*.py|src/**/*.py|web/backend/app/*.py|web/backend/app/**/*.py" in scope_section
    assert "needs: security-scope-detect" in bandit_section
    assert "needs.security-scope-detect.outputs.bandit_required == 'true'" in bandit_section
    assert "${{ needs.security-scope-detect.outputs.bandit_args }}" in bandit_section
    assert "bandit -r src/ web/backend/app/" not in bandit_section


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


def test_frontend_testing_scopes_artdeco_and_security_gates_to_relevant_changes() -> None:
    workflow = _read_workflow("frontend-testing.yml")

    assert "frontend-gate-scope-detect" in workflow
    assert "artdeco_scope_changed" in workflow
    assert "dependency_audit_required" in workflow
    assert "frontend_source_changed" in workflow
    assert "optimization_audit_required" in workflow
    assert "Run frontend optimization scope detection" in workflow

    optimization_section = workflow.split("jobs:", 1)[1].split("route-layout-pm2-detect:", 1)[0]
    frontend_test_section = workflow.split("frontend-test:", 1)[1].split("frontend-security:", 1)[0]
    frontend_security_section = workflow.split("frontend-security:", 1)[1]

    assert "needs.frontend-gate-scope-detect.outputs.optimization_audit_required == 'true'" in optimization_section
    assert "needs.frontend-gate-scope-detect.outputs.artdeco_scope_changed == 'true'" in frontend_test_section
    assert "needs.frontend-gate-scope-detect.outputs.frontend_source_changed == 'true'" in frontend_test_section
    assert "needs.frontend-gate-scope-detect.outputs.dependency_audit_required == 'true'" in frontend_security_section


def test_visual_testing_scopes_pipeline_and_uses_full_frontend_dependencies() -> None:
    workflow = _read_workflow("visual-testing.yml")

    assert "visual-scope-detect" in workflow
    assert "visual_test_required" in workflow
    assert "Run visual scope detection" in workflow

    setup_section = workflow.split("visual-test-setup:", 1)[1].split("visual-tests:", 1)[0]
    visual_test_section = workflow.split("visual-tests:", 1)[1].split("visual-test-results:", 1)[0]

    assert "needs: visual-scope-detect" in setup_section
    assert "needs.visual-scope-detect.outputs.visual_test_required == 'true'" in setup_section
    assert "npm ci" in setup_section
    assert "--only=production" not in setup_section

    scope_section = workflow.split("visual-scope-detect:", 1)[1].split("visual-test-setup:", 1)[0]
    assert "web/frontend/src/*|web/frontend/src/**" in scope_section
    assert "tests/visual/*|tests/visual/**" in scope_section
    assert "web/frontend/**/*.ts" not in scope_section

    assert "needs: [visual-scope-detect, visual-test-setup]" in visual_test_section
    assert "needs.visual-scope-detect.outputs.visual_test_required == 'true'" in visual_test_section
    assert "npm ci" in visual_test_section
    assert "--only=production" not in visual_test_section
    assert "npm run dev -- --host 0.0.0.0 --port 5173" in visual_test_section


def test_ci_cd_basic_tests_install_backend_runtime_dependencies() -> None:
    workflow = _read_workflow("ci-cd.yml")
    basic_section = workflow.split("# 基础测试", 1)[1].split("# 前端测试", 1)[0]

    assert "pip install -r requirements.txt" in basic_section
    assert "grep -Ev '^(TA-Lib|xlwings)==|^(TA-Lib|xlwings)>='" in basic_section
    assert "pip install -r /tmp/backend-requirements-ci.txt" in basic_section


def test_comprehensive_testing_only_installs_requirements_dev_when_present() -> None:
    workflow = _read_workflow("comprehensive-testing.yml")

    assert 'if [ -f requirements-dev.txt ]; then' in workflow
    assert 'pip install -r requirements-dev.txt' in workflow


def test_comprehensive_testing_scopes_heavy_jobs_to_relevant_test_areas() -> None:
    workflow = _read_workflow("comprehensive-testing.yml")

    assert "comprehensive-scope-detect" in workflow
    assert "run_ai_tests" in workflow
    assert "run_contract_tests" in workflow
    assert "run_performance_tests" in workflow
    assert "run_security_tests" in workflow
    assert "run_chaos_tests" in workflow
    assert "run_data_tests" in workflow

    ai_section = workflow.split("ai-tests:", 1)[1].split("# Contract Tests", 1)[0]
    contract_section = workflow.split("contract-tests:", 1)[1].split("# Performance Tests", 1)[0]
    performance_section = workflow.split("performance-tests:", 1)[1].split("# Security Tests", 1)[0]

    assert "needs: comprehensive-scope-detect" in ai_section
    assert "needs.comprehensive-scope-detect.outputs.run_ai_tests == 'true'" in ai_section
    assert "needs.comprehensive-scope-detect.outputs.run_contract_tests == 'true'" in contract_section
    assert "needs.comprehensive-scope-detect.outputs.run_performance_tests == 'true'" in performance_section


def test_test_coverage_drops_unavailable_pytest_timing_dependency() -> None:
    workflow = _read_workflow("test-coverage.yml")

    assert "pip install pytest pytest-cov" in workflow
    assert "pytest-timing" not in workflow


def test_ci_cd_test_chain_validation_uses_current_script_locations() -> None:
    workflow = _read_workflow("ci-cd.yml")
    chain_section = workflow.split("# 测试链路验证", 1)[1].split("# 持续优化数据收集", 1)[0]

    assert "scripts/tests/test-runner/run-orchestration.sh" in chain_section
    assert "scripts/dev/tools/run-performance-suite.sh" in chain_section
    assert "scripts/dev/tools/ai_test_assistant.py" in chain_section
    assert "from scripts.dev.tools import ai_test_assistant" in chain_section

    assert "scripts/test-runner/run-orchestration.sh" not in chain_section
    assert "scripts/tools/run-performance-suite.sh" not in chain_section
    assert "from scripts.tools import ai_test_assistant" not in chain_section


def test_ci_cd_with_type_checking_avoids_types_all_meta_package() -> None:
    workflow = _read_workflow("ci-cd-with-type-checking.yml")
    install_section = workflow.split("- name: Install Python dependencies", 1)[1].split("- name: Install frontend dependencies", 1)[0]

    assert "pip install mypy" in install_section
    assert "pip install mypy types-all" not in install_section
    assert "requirements-mock.txt" in install_section


def test_ci_cd_with_type_checking_scopes_pipeline_to_type_relevant_changes() -> None:
    workflow = _read_workflow("ci-cd-with-type-checking.yml")

    assert "type-check-scope-detect" in workflow
    assert "type_check_required" in workflow
    assert "python_type_check_required" in workflow
    assert "frontend_type_check_required" in workflow
    assert "python_files" in workflow
    assert "Run type-check scope detection" in workflow

    scope_section = workflow.split("type-check-scope-detect:", 1)[1].split("# Type Checking Job", 1)[0]
    type_check_section = workflow.split("type-check:", 1)[1].split("# Code Quality Job", 1)[0]

    assert "src/*.py|src/**/*.py" in scope_section
    assert "web/frontend/src/*|web/frontend/src/**" in scope_section
    assert "config/mypy.ini" in scope_section
    assert "web/frontend/package.json" in scope_section
    assert "web/frontend/package-lock.json" in scope_section
    assert "needs: type-check-scope-detect" in type_check_section
    assert "needs.type-check-scope-detect.outputs.type_check_required == 'true'" in type_check_section
    assert "needs.type-check-scope-detect.outputs.python_type_check_required == 'true'" in type_check_section
    assert "needs.type-check-scope-detect.outputs.frontend_type_check_required == 'true'" in type_check_section
    assert "part[0-9]+\\.py|_tail\\.py" in scope_section
    assert '[[ "$changed_file" == src/gpu/* ]]' in scope_section
    assert 'if [ -z "$python_files" ]; then' in scope_section
    assert "python_type_check_required=false" in scope_section
    assert "mypy --config-file=config/mypy.ini ${{ needs.type-check-scope-detect.outputs.python_files }}" in type_check_section


def test_typescript_type_check_uses_explicit_path_filters_and_repo_repo_comments() -> None:
    workflow = _read_workflow("typescript-type-check.yml")

    assert "'web/frontend/src/**/*.ts'" in workflow
    assert "'web/frontend/src/**/*.tsx'" in workflow
    assert "'web/frontend/src/**/*.vue'" in workflow
    assert "'web/frontend/src/**/*.{ts,tsx,vue}'" not in workflow
    assert "repo: context.repo.repo" in workflow
    assert "repo: context.repo.name" not in workflow


def test_cicd_monthly_review_uses_job_output_for_report_month() -> None:
    workflow = _read_workflow("cicd-monthly-review.yml")

    assert "REPORT_MONTH:" not in workflow
    assert "outputs:" in workflow
    assert "report_month: ${{ steps.report_month.outputs.report_month }}" in workflow
    assert "id: report_month" in workflow
    assert "needs.monthly-review.outputs.report_month" in workflow
    assert "needs: [archive-historical-data, monthly-review]" in workflow
    assert "format(" not in workflow


def test_python_and_security_type_report_comments_use_repo_repo() -> None:
    python_workflow = _read_workflow("python-type-check.yml")
    security_workflow = _read_workflow("security-testing.yml")

    assert "repo: context.repo.repo" in python_workflow
    assert "repo: context.repo.name" not in python_workflow

    assert "repo: context.repo.repo" in security_workflow
    assert "repo: context.repo.name" not in security_workflow


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


def test_p0_quality_gate_scopes_pr_checks_to_changed_files() -> None:
    workflow = _read_workflow("p0-quality-gate.yml")

    assert "p0-scope-detect" in workflow
    assert "python_quality_required" in workflow
    assert "dependency_check_required" in workflow
    assert "python_files" in workflow

    scope_section = workflow.split("p0-scope-detect:", 1)[1].split("# P0-1", 1)[0]
    pylint_section = workflow.split("pylint-errors:", 1)[1].split("# P0-2", 1)[0]
    formatting_section = workflow.split("formatting-check:", 1)[1].split("# P0-3", 1)[0]
    security_section = workflow.split("security-scan:", 1)[1].split("# P0-4", 1)[0]
    dependency_section = workflow.split("dependency-check:", 1)[1].split("# P0-5", 1)[0]
    syntax_section = workflow.split("syntax-check:", 1)[1].split("# P0-6", 1)[0]

    assert "git diff --name-only" in scope_section
    assert "src/*.py|src/**/*.py" in scope_section
    assert "requirements.txt|requirements-mock.txt|config/requirements.txt|pyproject.toml" in scope_section

    assert "needs: p0-scope-detect" in pylint_section
    assert "needs.p0-scope-detect.outputs.python_quality_required == 'true'" in pylint_section
    assert "${{ needs.p0-scope-detect.outputs.python_files }}" in pylint_section

    assert "needs: p0-scope-detect" in formatting_section
    assert "needs.p0-scope-detect.outputs.python_quality_required == 'true'" in formatting_section
    assert "${{ needs.p0-scope-detect.outputs.python_files }}" in formatting_section

    assert "needs: p0-scope-detect" in security_section
    assert "needs.p0-scope-detect.outputs.python_quality_required == 'true'" in security_section
    assert "${{ needs.p0-scope-detect.outputs.python_files }}" in security_section

    assert "needs: p0-scope-detect" in dependency_section
    assert "needs.p0-scope-detect.outputs.dependency_check_required == 'true'" in dependency_section
    assert 'safety check "${SAFETY_ARGS[@]}" --json > safety-report.json' not in dependency_section
    assert 'safety check "${SAFETY_ARGS[@]}" || {' in dependency_section

    assert "needs: p0-scope-detect" in syntax_section
    assert "needs.p0-scope-detect.outputs.python_quality_required == 'true'" in syntax_section
    assert "${{ needs.p0-scope-detect.outputs.python_files }}" in syntax_section


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
