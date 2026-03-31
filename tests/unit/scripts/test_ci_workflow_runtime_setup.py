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
    assert "FRONTEND_PORT=3020" in workflow
    assert "FRONTEND_BACKUP_PORT=3021" in workflow
    assert "BASE_URL=http://localhost:8000" in workflow
    assert "bash ./scripts/tests/run-api-tests.sh" in workflow


def test_api_automation_discovery_sets_required_backend_runtime_env_vars() -> None:
    workflow = _read_workflow("api-automation-discovery.yml")

    assert "export POSTGRESQL_USER=postgres" in workflow
    assert "export POSTGRESQL_DATABASE=mystocks" in workflow
    assert "export BACKEND_PORT=8000" in workflow
    assert "export BACKEND_BACKUP_PORT=8001" in workflow
    start_section = workflow.split("- name: Start Backend Service", 1)[1].split("- name: Run API Automation Tests", 1)[
        0
    ]
    assert "PYTHONPATH=$PWD:$PWD/web/backend" in start_section
    assert "python -m uvicorn app.main:app" in start_section
    assert "nohup" in start_section
    assert "/tmp/api_automation_backend_pid" in start_section
    assert "curl -fsS http://localhost:8000/api/announcement/health" in start_section
    assert "curl -fsS http://localhost:8000/health/ready" in start_section
    assert workflow.index("- name: Run API Automation Tests") < workflow.index("- name: Stop Backend Service")


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


def test_api_compliance_workflow_uses_supported_actions_and_safe_python_matrix_expansion() -> None:
    workflow = _read_workflow("api-compliance-testing.yml")

    assert "python-version: ['3.9', '3.10', '3.11']" in workflow
    assert "python-version: [3.9, 3.10, 3.11]" not in workflow
    assert "uses: actions/setup-python@v5" in workflow
    assert "uses: actions/cache@v4" in workflow
    assert "uses: actions/github-script@v7" in workflow
    assert 'MATRIX_PYTHON_VERSION: ${{ matrix.python-version }}' in workflow
    assert "print(f\"Python Version: {os.getenv('MATRIX_PYTHON_VERSION', 'unknown')}\")" in workflow
    assert "${{{{ matrix.python-version }}}}" not in workflow


def test_api_compliance_workflow_avoids_unavailable_talib_system_packages_and_filters_backend_requirements() -> None:
    workflow = _read_workflow("api-compliance-testing.yml")
    install_section = workflow.split("- name: Install system dependencies", 1)[1].split("- name: Set up environment variables", 1)[0]

    assert "libta libta-dev" not in install_section
    assert "libta-lib0" not in install_section
    assert "grep -Ev '^(TA-Lib|xlwings)==|^(TA-Lib|xlwings)>='" in install_section
    assert "python -m pip install -r /tmp/backend-requirements-ci.txt" in install_section


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
    assert (
        "python -m pytest -o addopts='' tests/real_data_synchronization_test.py::test_data_routing_real_correctness -v"
        in workflow
    )
    assert "ports:" in workflow
    assert "- 5432:5432" in workflow
    assert "psql -h localhost -U postgres -d postgres -tc" in workflow
    assert "uses: actions/download-artifact@v4" in workflow


def test_data_sync_workflow_starts_backend_before_contract_tests_and_tolerates_missing_quality_artifacts() -> None:
    workflow = _read_workflow("data-sync-testing.yml")

    install_section = workflow.split("- name: Install Python dependencies", 1)[1].split(
        "- name: Install frontend dependencies", 1
    )[0]
    assert "grep -Ev '^(TA-Lib|xlwings)==|^(TA-Lib|xlwings)>='" in install_section
    assert "python -m pip install -r /tmp/backend-requirements-ci.txt" in install_section

    assert "Start backend for API Contract Tests" in workflow
    contract_setup_section = workflow.split("- name: Start backend for API Contract Tests", 1)[1].split(
        "- name: Run API Contract Tests", 1
    )[0]
    assert "export POSTGRESQL_HOST=localhost" in contract_setup_section
    assert "export POSTGRESQL_USER=postgres" in contract_setup_section
    assert "export POSTGRESQL_PASSWORD=test_password" in contract_setup_section
    assert "export POSTGRESQL_DATABASE=mystocks_test" in contract_setup_section
    assert "export JWT_SECRET_KEY=$(openssl rand -hex 32)" in contract_setup_section
    assert "export BACKEND_PORT=8000" in contract_setup_section
    assert "export BACKEND_BACKUP_PORT=8001" in contract_setup_section
    assert "PYTHONPATH=$PWD:$PWD/web/backend" in contract_setup_section
    assert "python -m uvicorn app.main:app" in contract_setup_section
    assert "nohup" in contract_setup_section
    assert "/tmp/contract_backend_pid" in contract_setup_section

    quality_gate_section = workflow.split("# Quality Gate Check", 1)[1]
    download_section = quality_gate_section.split("- name: Download Test Results", 1)[1].split(
        "- name: Quality Gate Check", 1
    )[0]
    assert "continue-on-error: true" in download_section
    assert "bash ./scripts/ci_type_check.sh" in workflow


def test_data_sync_workflow_uses_ci_safe_frontend_build_without_repo_wide_type_gate() -> None:
    workflow = _read_workflow("data-sync-testing.yml")
    build_section = workflow.split("- name: Build Frontend", 1)[1].split("- name: Run UI Binding Tests", 1)[0]

    assert "npm run build:no-types" in build_section
    assert "npm run build\n" not in build_section
    assert "FRONTEND_PORT=${FRONTEND_PORT}" in build_section
    assert "FRONTEND_BACKUP_PORT=${FRONTEND_BACKUP_PORT}" in build_section
    assert "BACKEND_PORT=${BACKEND_PORT}" in build_section
    assert "BACKEND_BACKUP_PORT=${BACKEND_BACKUP_PORT}" in build_section


def test_data_sync_workflow_runs_existing_frontend_contract_smoke_instead_of_missing_ui_binding_script() -> None:
    workflow = _read_workflow("data-sync-testing.yml")
    ui_section = workflow.split("- name: Run UI Binding Tests", 1)[1].split("- name: Start Services for E2E Tests", 1)[
        0
    ]

    assert "npm run test:unit" not in ui_section
    assert "npx vitest run" in ui_section
    assert "tests/unit/port-config-consistency.spec.ts" in ui_section


def test_data_sync_workflow_uses_aligned_service_ports_and_frontend_stable_e2e_suite() -> None:
    workflow = _read_workflow("data-sync-testing.yml")
    start_section = workflow.split("- name: Start Services for E2E Tests", 1)[1].split(
        "- name: Run E2E Data Flow Tests", 1
    )[0]
    e2e_section = workflow.split("- name: Run E2E Data Flow Tests", 1)[1].split(
        "- name: Run Real Data Synchronization Tests", 1
    )[0]

    assert "export POSTGRESQL_HOST=localhost" in start_section
    assert "export POSTGRESQL_USER=postgres" in start_section
    assert "export POSTGRESQL_PASSWORD=test_password" in start_section
    assert "export POSTGRESQL_DATABASE=mystocks_test" in start_section
    assert "export JWT_SECRET_KEY=$(openssl rand -hex 32)" in start_section
    assert "export BACKEND_PORT=${BACKEND_PORT}" in start_section
    assert "export BACKEND_BACKUP_PORT=${BACKEND_BACKUP_PORT}" in start_section
    assert "PYTHONPATH=$PWD/../..:$PWD" in start_section
    assert "nohup python -m uvicorn app.main:app --host 0.0.0.0 --port ${BACKEND_PORT}" in start_section
    assert "npm run dev:no-types -- --host 0.0.0.0 --port ${FRONTEND_PORT} --strictPort" in start_section
    assert "curl -fsS http://localhost:${BACKEND_PORT}/api/announcement/health" in start_section
    assert "curl -fsS http://localhost:${BACKEND_PORT}/health/ready" in start_section
    assert "curl -fsS http://localhost:${FRONTEND_PORT}/" in start_section

    assert "cd web/frontend" in e2e_section
    assert "npx playwright install --with-deps chromium" in e2e_section
    assert "PLAYWRIGHT_EXTERNAL_FRONTEND=1 npm run test:e2e:stable" in e2e_section
    assert "tests/e2e_data_flow.spec.ts" not in e2e_section
    assert "--headed=false" not in e2e_section


def test_legacy_e2e_workflow_declares_stable_port_defaults() -> None:
    workflow = _read_workflow("e2e-test.yml")

    assert "FRONTEND_PORT: '3020'" in workflow
    assert "FRONTEND_BACKUP_PORT: '3021'" in workflow
    assert "BACKEND_PORT: '8020'" in workflow
    assert "BACKEND_BACKUP_PORT: '8021'" in workflow


def test_legacy_e2e_workflow_starts_services_before_stable_suite() -> None:
    workflow = _read_workflow("e2e-test.yml")

    assert "image: postgres:15" in workflow
    assert "POSTGRES_DB: mystocks_test" in workflow
    assert "python -m pip install -r requirements.txt" in workflow
    assert "python -m pip install -r /tmp/backend-requirements-ci.txt" in workflow
    assert "export POSTGRESQL_DATABASE=mystocks_test" in workflow
    assert "export TESTING=true" in workflow
    assert "Start backend service" in workflow
    assert "Start frontend service" in workflow
    assert "PYTHONPATH=$PWD:$PWD/web/backend" in workflow
    assert "PLAYWRIGHT_EXTERNAL_FRONTEND=1 npm run test:e2e:stable" in workflow
    assert "curl -fsS http://localhost:${BACKEND_PORT}/api/announcement/health" in workflow
    assert "curl -fsS http://localhost:${BACKEND_PORT}/health/ready" in workflow
    assert "curl -fsS http://localhost:${FRONTEND_PORT}/" in workflow
    assert "Stop services" in workflow


def test_kline_e2e_mocks_readiness_endpoint_before_navigation() -> None:
    spec = (PROJECT_ROOT / "web" / "frontend" / "tests" / "e2e" / "kline-chart.spec.ts").read_text(encoding="utf-8")

    assert "**/api/health/ready" in spec
    assert "e2e-kline-ready" in spec


def test_menu_navigation_e2e_mocks_readiness_endpoint_before_navigation() -> None:
    spec = (
        PROJECT_ROOT / "web" / "frontend" / "tests" / "e2e" / "critical" / "menu-navigation-fixed.spec.ts"
    ).read_text(encoding="utf-8")

    assert 'url.pathname === "/api/health/ready"' in spec
    assert 'status: "ready"' in spec or "status: 'ready'" in spec


def test_visual_chart_specs_use_existing_fixture_and_helper_paths() -> None:
    chart_specs = [
        PROJECT_ROOT / "web" / "frontend" / "tests" / "visual" / "components" / "charts" / "backtest.spec.ts",
        PROJECT_ROOT / "web" / "frontend" / "tests" / "visual" / "components" / "charts" / "technical-analysis.spec.ts",
    ]

    for spec_path in chart_specs:
        spec = spec_path.read_text(encoding="utf-8")
        assert "../../fixtures/visual.fixture" in spec
        assert "../../utils/helpers" in spec


def test_contract_testing_workflow_skips_when_framework_is_absent() -> None:
    workflow = _read_workflow("contract-testing.yml")

    assert "contract-framework-readiness" in workflow
    assert 'if [ -d "src/contract_testing" ]' in workflow
    assert "needs: contract-framework-readiness" in workflow
    assert "needs.contract-framework-readiness.outputs.ready == 'true'" in workflow


def test_playwright_workflow_runs_smoke_subset_only() -> None:
    workflow = _read_workflow("playwright.yml")

    assert "paths:" in workflow
    assert "'web/frontend/**'" in workflow or '"web/frontend/**"' in workflow
    assert "'/.github/workflows/playwright.yml'" not in workflow
    assert "'.github/workflows/playwright.yml'" in workflow or '".github/workflows/playwright.yml"' in workflow
    assert "FRONTEND_PORT: '3020'" in workflow
    assert "FRONTEND_BACKUP_PORT: '3021'" in workflow
    assert "BACKEND_PORT: '8020'" in workflow
    assert "BACKEND_BACKUP_PORT: '8021'" in workflow
    assert "npx playwright install --with-deps chromium" in workflow
    assert "Run Playwright smoke tests" in workflow
    assert "npm run test:e2e:stable" in workflow
    assert "playwright.config.js" not in workflow or "--config playwright.config.js" not in workflow


def test_e2e_tests_workflow_installs_backend_runtime_dependencies_and_downloads_gate_inputs() -> None:
    workflow = _read_workflow("e2e-tests.yml")
    install_section = workflow.split("- name: Install dependencies", 1)[1].split("- name: Start application", 1)[0]
    start_section = workflow.split("- name: Start application", 1)[1].split("- name: Run E2E tests", 1)[0]
    quality_gate_section = workflow.split("quality-gate:", 1)[1]

    assert "pip install -r requirements.txt" in install_section
    assert "grep -Ev '^(TA-Lib|xlwings)==|^(TA-Lib|xlwings)>='" in install_section
    assert "pip install -r /tmp/backend-requirements-ci.txt" in install_section
    assert "services:" in workflow
    assert "image: postgres:15" in workflow
    assert "export POSTGRESQL_HOST=${POSTGRESQL_HOST}" in start_section
    assert "export POSTGRESQL_USER=${POSTGRESQL_USER}" in start_section
    assert "export POSTGRESQL_PASSWORD=${POSTGRESQL_PASSWORD}" in start_section
    assert "export POSTGRESQL_DATABASE=${POSTGRESQL_DATABASE}" in start_section
    assert "export JWT_SECRET_KEY=$(openssl rand -hex 32)" in start_section
    assert "PYTHONPATH=$PWD:$PWD/web/backend" in start_section
    assert "python -m uvicorn app.main:app" in start_section
    assert "actions/download-artifact@v4" in quality_gate_section
    assert "continue-on-error: true" in quality_gate_section
    assert "name: e2e-test-results" in workflow
    assert "test-results/e2e-results.json" in quality_gate_section
    assert "locust -f tests/performance/locustfile.py --host=http://localhost:8000 --headless" in workflow
    assert 'if [ -f "test-results/e2e-results.json" ]' in quality_gate_section
    assert 'E2E_PASSED="pass"' in quality_gate_section


def test_e2e_testing_workflow_uses_ci_safe_backend_dependencies_and_non_blocking_pr_comment() -> None:
    workflow = _read_workflow("e2e-testing.yml")
    backend_install_section = workflow.split("- name: Install Backend Dependencies", 1)[1].split(
        "- name: Run Backend Tests", 1
    )[0]
    backend_test_section = workflow.split("- name: Run Backend Tests", 1)[1].split("- name: Start Backend Server", 1)[0]
    backend_start_section = workflow.split("- name: Start Backend Server", 1)[1].split("- name: Test Backend API", 1)[0]
    e2e_install_section = workflow.split("- name: Install Dependencies", 1)[1].split("- name: Start Services", 1)[0]
    e2e_start_section = workflow.split("- name: Start Services", 1)[1].split("- name: Run E2E Tests", 1)[0]

    assert "grep -Ev '^(TA-Lib|xlwings)==|^(TA-Lib|xlwings)>='" in workflow
    assert "pip install -r /tmp/backend-requirements-ci.txt" in workflow
    assert "python -m pip install -r requirements.txt" in backend_install_section
    assert "tests/test_post_rewrite_backend_import_stability.py" in workflow
    assert "tests/test_trading_runtime_routes.py" in workflow
    assert "curl -f http://localhost:8000/api/announcement/health" in workflow
    assert "curl -f http://localhost:8000/health/ready" in workflow
    assert "curl -f http://localhost:8000/api/csrf-token" in workflow
    assert "npm run build:no-types" in workflow
    assert "export PLAYWRIGHT_EXTERNAL_FRONTEND=1" in workflow
    assert "--no-cov" not in workflow
    assert "BACKEND_BACKUP_PORT: 8001" in workflow
    assert "export POSTGRESQL_HOST=localhost" in backend_test_section
    assert "export POSTGRESQL_USER=postgres" in backend_test_section
    assert "export POSTGRESQL_PASSWORD=postgres" in backend_test_section
    assert "export JWT_SECRET_KEY=$(openssl rand -hex 32)" in backend_test_section
    assert "export BACKEND_BACKUP_PORT=${BACKEND_BACKUP_PORT}" in backend_test_section
    assert "export POSTGRESQL_HOST=localhost" in backend_start_section
    assert "export POSTGRESQL_USER=postgres" in backend_start_section
    assert "export POSTGRESQL_PASSWORD=postgres" in backend_start_section
    assert "export POSTGRESQL_DATABASE=mystocks_test" in backend_start_section
    assert "export JWT_SECRET_KEY=$(openssl rand -hex 32)" in backend_start_section
    assert "export BACKEND_PORT=${BACKEND_PORT}" in backend_start_section
    assert "export BACKEND_BACKUP_PORT=${BACKEND_BACKUP_PORT}" in backend_start_section
    assert "PYTHONPATH=$PWD/../..:$PWD" in backend_start_section
    assert "cd web/frontend" in e2e_install_section
    assert "cd .." in e2e_install_section
    assert "grep -Ev '^(TA-Lib|xlwings)==|^(TA-Lib|xlwings)>='" in e2e_install_section
    assert "npx playwright install ${{ matrix.browser }} --with-deps" in e2e_install_section
    assert "image: postgres:15" in workflow
    assert "image: redis:7-alpine" in workflow
    assert "export POSTGRESQL_HOST=localhost" in e2e_start_section
    assert "export POSTGRESQL_USER=postgres" in e2e_start_section
    assert "export POSTGRESQL_PASSWORD=postgres" in e2e_start_section
    assert "export POSTGRESQL_DATABASE=mystocks_test" in e2e_start_section
    assert "export JWT_SECRET_KEY=$(openssl rand -hex 32)" in e2e_start_section
    assert "PYTHONPATH=$PWD/../..:$PWD" in e2e_start_section
    assert "PGPASSWORD=postgres psql -h localhost -U postgres -d mystocks_test -c 'SELECT 1'" in e2e_start_section
    assert "npm run dev:no-types -- --host 127.0.0.1 --port ${FRONTEND_PORT} --strictPort" in e2e_start_section
    assert "curl -f http://localhost:5173" in e2e_start_section

    comment_section = workflow.split("- name: Comment PR with Results", 1)[1].split("# 第六阶段", 1)[0]
    assert "continue-on-error: true" in comment_section


def test_e2e_testing_workflow_relies_on_playwright_config_outputs_and_skips_pr_check_publish() -> None:
    workflow = _read_workflow("e2e-testing.yml")
    run_section = workflow.split("- name: Run E2E Tests", 1)[1].split("- name: Upload E2E Test Results", 1)[0]
    upload_results_section = workflow.split("- name: Upload E2E Test Results", 1)[1].split(
        "- name: Upload Playwright Report", 1
    )[0]
    upload_report_section = workflow.split("- name: Upload Playwright Report", 1)[1].split("# 第五阶段", 1)[0]

    assert "--config=playwright.config.js" in run_section or "--config playwright.config.js" in run_section
    assert "tests/e2e/critical/menu-navigation-fixed.spec.ts" in run_section
    assert "tests/e2e/kline-chart.spec.ts" in run_section
    assert "--reporter=html,json,junit" not in run_section
    assert "--trace=on" not in run_section
    assert "--video=retain-on-failure" not in run_section
    assert "--screenshot=only-on-failure" not in run_section
    assert "Publish Test Results" not in workflow
    assert "${{ strategy.job-index }}" in upload_results_section
    assert "${{ strategy.job-index }}" in upload_report_section
    assert "continue-on-error: true" in upload_results_section
    assert "continue-on-error: true" in upload_report_section


def test_ci_cd_type_workflow_matches_recovery_mypy_baseline() -> None:
    workflow = _read_workflow("ci-cd-with-type-checking.yml")
    install_section = workflow.split("- name: Install Python dependencies", 1)[1].split(
        "- name: Install frontend dependencies", 1
    )[0]
    mypy_section = workflow.split("- name: Run Python type checking (mypy)", 1)[1].split(
        "- name: Generate type coverage report", 1
    )[0]

    assert "types-PyYAML" in install_section
    assert "pip install -e ." in install_section
    assert "--explicit-package-bases" in mypy_section
    assert "--non-interactive" not in mypy_section


def test_ci_cd_type_workflow_uses_baseline_safe_frontend_validation() -> None:
    workflow = _read_workflow("ci-cd-with-type-checking.yml")
    frontend_section = workflow.split("- name: Run frontend baseline validation", 1)[1].split(
        "- name: Upload type check results", 1
    )[0]

    assert "npx vue-tsc --noEmit" not in workflow
    assert "FRONTEND_PORT=3020" in frontend_section
    assert "FRONTEND_BACKUP_PORT=3021" in frontend_section
    assert "BACKEND_PORT=8020" in frontend_section
    assert "BACKEND_BACKUP_PORT=8021" in frontend_section
    assert "npm run build:no-types" in frontend_section
    assert "FRONTEND_PORT=3020 \\" in frontend_section
    assert "npx vitest run tests/unit/port-config-consistency.spec.ts --reporter=verbose" in frontend_section
    assert "BACKEND_PORT=8020 \\" in frontend_section
    assert "npx vitest run tests/unit/port-config-consistency.spec.ts --reporter=verbose" in frontend_section


def test_e2e_enhanced_workflow_uses_existing_pm2_configs_and_non_blocking_pr_comment() -> None:
    workflow = _read_workflow("e2e-tests-enhanced.yml")

    assert "pm2 start config/pm2/ecosystem.playwright.p1.fixed.config.js" not in workflow
    assert "pm2 start config/pm2/ecosystem.playwright.p2.config.js" not in workflow
    assert "FRONTEND_BACKUP_PORT: 3021" in workflow
    assert "BACKEND_BACKUP_PORT: 8001" in workflow
    assert "tests/e2e/critical/menu-navigation-fixed.spec.ts" in workflow
    assert "tests/e2e/kline-chart.spec.ts" in workflow
    assert "npx playwright install --with-deps chromium" in workflow
    assert "PLAYWRIGHT_EXTERNAL_FRONTEND=1 npx playwright test" in workflow
    assert "curl -s http://localhost:8000/api/announcement/health" in workflow
    assert "curl -s http://localhost:8000/health/ready" in workflow

    comment_section = workflow.split("- name: Comment PR with results", 1)[1].split("final-summary:", 1)[0]
    assert "continue-on-error: true" in comment_section


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


def test_frontend_testing_uses_pr_head_sha_for_pull_request_diff_scope() -> None:
    workflow = _read_workflow("frontend-testing.yml")

    assert 'HEAD_SHA="${{ github.event.pull_request.head.sha }}"' in workflow
    assert 'git diff --name-only "$BASE_SHA" "$HEAD_SHA"' in workflow or 'git diff --name-only "$BASE_SHA...$HEAD_SHA"' in workflow
    assert 'git diff --name-only "$BASE_SHA" "${{ github.sha }}"' not in workflow


def test_frontend_testing_skips_frontend_test_job_when_no_frontend_scope_changed() -> None:
    workflow = _read_workflow("frontend-testing.yml")
    frontend_test_section = workflow.split("frontend-test:", 1)[1].split("frontend-security:", 1)[0]

    assert "if: needs.frontend-gate-scope-detect.outputs.frontend_source_changed == 'true' || needs.frontend-gate-scope-detect.outputs.artdeco_scope_changed == 'true'" in frontend_test_section
    assert "needs.frontend-gate-scope-detect.outputs.frontend_source_changed == 'true'" in frontend_test_section
    assert "needs.frontend-gate-scope-detect.outputs.artdeco_scope_changed == 'true'" in frontend_test_section


def test_frontend_testing_uses_ci_safe_frontend_commands_instead_of_repo_wide_ts_gate_or_missing_scripts() -> None:
    workflow = _read_workflow("frontend-testing.yml")
    frontend_test_section = workflow.split("frontend-test:", 1)[1].split("frontend-security:", 1)[0]

    assert "FRONTEND_PORT: '3020'" in frontend_test_section
    assert "FRONTEND_BACKUP_PORT: '3021'" in frontend_test_section
    assert "BACKEND_PORT: '8020'" in frontend_test_section
    assert "BACKEND_BACKUP_PORT: '8021'" in frontend_test_section
    assert "npm run type-check" not in frontend_test_section
    assert "npm run test:unit:stable" in frontend_test_section
    assert "run: npm run test:unit\n" not in frontend_test_section
    assert "npx vitest run" in frontend_test_section
    assert "tests/unit/port-config-consistency.spec.ts" in frontend_test_section
    assert "npm run build:no-types" in frontend_test_section
    assert "npm run build\n" not in frontend_test_section
    assert "npx playwright install --with-deps chromium" in frontend_test_section
    assert "npm run test:e2e:stable" in frontend_test_section
    assert "PLAYWRIGHT_EXTERNAL_FRONTEND=1 npm run test:e2e:stable" not in frontend_test_section
    assert "npm run test:e2e\n" not in frontend_test_section


def test_visual_testing_scopes_pipeline_and_uses_full_frontend_dependencies() -> None:
    workflow = _read_workflow("visual-testing.yml")
    visual_config = (PROJECT_ROOT / "web" / "frontend" / "tests" / "visual" / "config" / "visual.config.ts").read_text(
        encoding="utf-8"
    )

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
    assert 'echo "FRONTEND_PORT=5173" >> $GITHUB_ENV' in visual_test_section
    assert 'echo "FRONTEND_BACKUP_PORT=5174" >> $GITHUB_ENV' in visual_test_section
    assert 'echo "BACKEND_PORT=8000" >> $GITHUB_ENV' in visual_test_section
    assert 'echo "BACKEND_BACKUP_PORT=8001" >> $GITHUB_ENV' in visual_test_section
    assert "Start Frontend Server" not in visual_test_section
    assert "npm run dev -- --host 0.0.0.0 --port 5173" not in visual_test_section
    assert "visual-test-results-${{ matrix.browser }}-${{ matrix.shard }}" not in workflow
    assert "visual-playwright-report-${{ matrix.browser }}-${{ matrix.shard }}" not in workflow
    assert "testDir: '..'" in visual_config
    assert "testDir: '../visual'" not in visual_config


def test_ci_cd_basic_tests_install_backend_runtime_dependencies() -> None:
    workflow = _read_workflow("ci-cd.yml")
    basic_section = workflow.split("# 基础测试", 1)[1].split("# 前端测试", 1)[0]

    assert "pip install -r requirements.txt" in basic_section
    assert "grep -Ev '^(TA-Lib|xlwings)==|^(TA-Lib|xlwings)>='" in basic_section
    assert "pip install -r /tmp/backend-requirements-ci.txt" in basic_section
    assert "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1" in basic_section
    assert "--no-cov" not in basic_section


def test_comprehensive_testing_only_installs_requirements_dev_when_present() -> None:
    workflow = _read_workflow("comprehensive-testing.yml")

    assert "if [ -f requirements-dev.txt ]; then" in workflow
    assert "pip install -r requirements-dev.txt" in workflow


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
    scope_section = workflow.split("coverage-scope-detect:", 1)[1].split("test-coverage:", 1)[0]

    assert "coverage-scope-detect" in workflow
    assert "coverage_required" in workflow
    assert "pip install pytest pytest-cov" in workflow
    assert "pytest-timing" not in workflow
    assert "python -m pytest -o addopts=''" in workflow
    assert "src/adapters/base_adapter.py" in workflow
    assert "src/adapters/data_validator.py" in workflow
    assert "src/core/exceptions/__init__.py" in workflow
    assert "src/core/config.py" in workflow
    assert "needs: coverage-scope-detect" in workflow
    assert "needs.coverage-scope-detect.outputs.coverage_required == 'true'" in workflow
    assert ".github/workflows/test-coverage.yml" not in scope_section


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
    install_section = workflow.split("- name: Install Python dependencies", 1)[1].split(
        "- name: Install frontend dependencies", 1
    )[0]

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
    code_quality_section = workflow.split("code-quality:", 1)[1].split("# Unit Tests Job", 1)[0]
    unit_test_section = workflow.split("unit-tests:", 1)[1].split("# Integration Tests Job", 1)[0]

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
    assert "needs.type-check-scope-detect.outputs.python_type_check_required == 'true'" in code_quality_section
    assert "black --check --diff ${{ needs.type-check-scope-detect.outputs.python_files }}" in code_quality_section
    assert "ruff check ${{ needs.type-check-scope-detect.outputs.python_files }}" in code_quality_section
    assert "bandit -f json -o bandit-report.json ${{ needs.type-check-scope-detect.outputs.python_files }}" in code_quality_section
    assert "black --check --diff src/ scripts/" not in code_quality_section
    assert "needs.type-check-scope-detect.outputs.python_type_check_required == 'true'" in unit_test_section
    assert "tests/unit/scripts/test_ci_workflow_runtime_setup.py -q" in unit_test_section
    assert "--cov-fail-under=0" in unit_test_section
    assert 'pytest tests/ -m "unit"' not in unit_test_section
    integration_section = workflow.split("integration-tests:", 1)[1].split("# E2E Tests Job", 1)[0]
    assert "pytest pytest-asyncio pytest-cov pytest-mock" in integration_section
    assert "grep -Ev '^(TA-Lib|xlwings)==|^(TA-Lib|xlwings)>='" in integration_section
    assert "pip install -r /tmp/backend-requirements-ci.txt" in integration_section
    assert "tests/test_post_rewrite_backend_import_stability.py" in integration_section
    assert "tests/test_trading_runtime_routes.py" in integration_section
    assert "tests/strategy_management/test_backtest_runtime_fallback.py" in integration_section
    assert "--cov-fail-under=0" in integration_section
    assert 'pytest tests/ -m "integration"' not in integration_section
    assert '[[ "$changed_file" == src/gpu/* ]]' in scope_section
    assert 'if [ -z "$python_files" ]; then' in scope_section
    assert "python_type_check_required=false" in scope_section
    assert (
        "mypy --config-file=config/mypy.ini ${{ needs.type-check-scope-detect.outputs.python_files }}"
        in type_check_section
    )


def test_ci_cd_with_type_checking_reinstalls_pytest_after_backend_requirements_for_integration_smoke() -> None:
    workflow = _read_workflow("ci-cd-with-type-checking.yml")
    integration_section = workflow.split("integration-tests:", 1)[1].split("# E2E Tests Job", 1)[0]
    integration_install_section = integration_section.split("- name: Install Python dependencies", 1)[1].split(
        "- name: Set up test database", 1
    )[0]

    assert "pip install -r /tmp/backend-requirements-ci.txt" in integration_install_section
    assert "pip install pytest==9.0.2 pytest-asyncio==1.3.0 pytest-cov pytest-mock" in integration_install_section
    assert "export BACKEND_PORT=8000" in integration_section
    assert "export BACKEND_BACKUP_PORT=8001" in integration_section


def test_ci_cd_with_type_checking_uses_baseline_safe_e2e_smoke() -> None:
    workflow = _read_workflow("ci-cd-with-type-checking.yml")
    e2e_section = workflow.split("e2e-tests:", 1)[1].split("# Performance Tests Job", 1)[0]

    assert "npm run build:no-types" in e2e_section
    assert "npm run build\n" not in e2e_section
    assert "grep -Ev '^(TA-Lib|xlwings)==|^(TA-Lib|xlwings)>='" in e2e_section
    assert "pip install -r /tmp/backend-requirements-ci.txt" in e2e_section
    assert "npx playwright install --with-deps chromium" in e2e_section
    assert "PLAYWRIGHT_EXTERNAL_FRONTEND=1" not in e2e_section
    assert "npm run test:e2e:stable" in e2e_section
    assert 'pytest tests/ -m "e2e"' not in e2e_section


def test_ci_cd_with_type_checking_skips_test_deploy_on_pull_requests() -> None:
    workflow = _read_workflow("ci-cd-with-type-checking.yml")
    deploy_section = workflow.split("deploy-test:", 1)[1].split("# Deploy to Production", 1)[0]

    assert "github.event_name == 'pull_request'" not in deploy_section
    assert "github.ref == 'refs/heads/develop' && github.event_name == 'push'" in deploy_section



def test_typescript_type_check_uses_explicit_path_filters_and_repo_repo_comments() -> None:
    workflow = _read_workflow("typescript-type-check.yml")
    count_section = workflow.split("- name: Count TypeScript errors", 1)[1].split("- name: Upload tsc results", 1)[0]
    quality_gate_section = workflow.split("type-check-gate:", 1)[1].split(
        "# ============================================================", 1
    )[0]

    assert "'web/frontend/src/**/*.ts'" in workflow
    assert "'web/frontend/src/**/*.tsx'" in workflow
    assert "'web/frontend/src/**/*.vue'" in workflow
    assert "'web/frontend/src/**/*.{ts,tsx,vue}'" not in workflow
    assert "repo: context.repo.repo" in workflow
    assert "repo: context.repo.name" not in workflow
    assert 'grep -c "error TS" tsc-output.txt 2>/dev/null || echo "0"' not in count_section
    assert 'if [ -z "$ERROR_COUNT" ]; then' in count_section
    assert "<<'PY'" not in quality_gate_section
    assert "python -c" in quality_gate_section


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

    python_section = python_workflow.split("Download all type check artifacts", 1)[1].split(
        "Generate consolidated report", 1
    )[0]
    typescript_section = typescript_workflow.split("Download all type check artifacts", 1)[1].split(
        "Generate consolidated report", 1
    )[0]

    assert "uses: actions/download-artifact@v4" in python_section
    assert "path: ." in python_section

    assert "uses: actions/download-artifact@v4" in typescript_section
    assert "path: ." in typescript_section


def test_python_type_check_scopes_pr_runs_to_relevant_src_files() -> None:
    workflow = _read_workflow("python-type-check.yml")

    assert "python-type-scope-detect" in workflow
    assert "python_type_required" in workflow
    assert "python_files" in workflow

    scope_section = workflow.split("python-type-scope-detect:", 1)[1].split("type-check-incremental:", 1)[0]
    incremental_section = workflow.split("type-check-incremental:", 1)[1].split("type-check-full:", 1)[0]
    full_section = workflow.split("type-check-full:", 1)[1].split("type-coverage:", 1)[0]

    assert "git diff --name-only" in scope_section
    assert "src/*.py|src/**/*.py|pyproject.toml|config/mypy.ini" in scope_section
    assert "part[0-9]+\\.py|_tail\\.py" in scope_section
    assert '[[ "$changed_file" == src/gpu/* ]]' in scope_section
    assert 'if [ -z "$python_files" ]; then' in scope_section

    assert "needs: python-type-scope-detect" in incremental_section
    assert "needs.python-type-scope-detect.outputs.python_type_required == 'true'" in incremental_section
    assert "mypy src/" not in incremental_section
    assert "--config-file=config/mypy.ini" in incremental_section
    assert "--explicit-package-bases" in incremental_section
    assert "${{ needs.python-type-scope-detect.outputs.python_files }}" in incremental_section

    assert "needs: python-type-scope-detect" in full_section
    assert "needs.python-type-scope-detect.outputs.python_type_required == 'true'" in full_section
    assert "mypy src/ tests/" not in full_section
    assert "--config-file=config/mypy.ini" in full_section
    assert "--explicit-package-bases" in full_section


def test_python_type_check_workflow_uses_non_blocking_pr_comments_and_no_invalid_coverage_package() -> None:
    workflow = _read_workflow("python-type-check.yml")

    comment_section = workflow.split("- name: Comment on PR", 1)[1].split("type-coverage:", 1)[0]
    coverage_section = workflow.split("type-coverage:", 1)[1].split("type-check-gate:", 1)[0]

    assert "continue-on-error: true" in comment_section
    assert "mypy-coverage-typing" not in coverage_section


def test_directory_compliance_uses_current_root_budget_without_api_wrapper_exception() -> None:
    workflow = _read_workflow("directory-compliance.yml")

    assert "MAX_ROOT_DIRS=15" in workflow
    assert "MAX_ROOT_FILES=32" in workflow
    assert "! -name 'run-api-tests.sh'" not in workflow


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
    assert "pip install black==25.11.0 isort" in formatting_section

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

    coverage_section = coverage_workflow.split("Download coverage report", 1)[1].split(
        "Generate test expansion plan", 1
    )[0]
    performance_section = performance_workflow.split("Download performance results", 1)[1].split(
        "Check for performance regressions", 1
    )[0]

    assert "uses: actions/download-artifact@v4" in coverage_section
    assert "path: ." in coverage_section

    assert "uses: actions/download-artifact@v4" in performance_section
    assert "path: ." in performance_section


def test_code_quality_workflow_keeps_coverage_generation_as_a_real_gate() -> None:
    workflow = _read_workflow("code-quality.yml")
    coverage_section = workflow.split("test-coverage:", 1)[1].split("# 性能基准测试阶段", 1)[0]

    assert "python -m pytest -o addopts='' tests/unit/core/test_simple_calculator.py --cov=src.core.simple_calculator --cov-report=xml:coverage.xml --cov-report=html:htmlcov --cov-fail-under=80 -q" in coverage_section
    assert "python -m pytest -o addopts='' scripts/tests/" not in coverage_section
    assert "python -m pytest -o addopts='' tests/unit/core/test_simple_calculator.py --cov=src.core.simple_calculator --cov-report=xml:coverage.xml --cov-report=html:htmlcov --cov-fail-under=80 -q || true" not in coverage_section
    assert 'echo "::warning::coverage.xml not generated; skipping coverage post-processing"' not in coverage_section
    assert 'echo "❌ coverage.xml not generated"' in coverage_section
    assert "exit 1" in coverage_section


def test_code_quality_quality_gate_fails_when_coverage_report_is_missing() -> None:
    workflow = _read_workflow("code-quality.yml")
    quality_gate_section = workflow.split("Quality Gate Evaluation", 1)[1].split("- name: Comment on PR", 1)[0]

    assert 'QUALITY_ISSUES="$QUALITY_ISSUES 覆盖率报告缺失"' in quality_gate_section


def test_code_quality_quality_gate_hard_fails_but_keeps_pr_comment_path() -> None:
    workflow = _read_workflow("code-quality.yml")
    quality_report_section = workflow.split("quality-report:", 1)[1].split("quality-gate:", 1)[0]
    quality_gate_section = workflow.split("Quality Gate Evaluation", 1)[1].split("- name: Comment on PR", 1)[0]
    comment_section = workflow.split("- name: Comment on PR", 1)[1].split("uses: actions/github-script@v7", 1)[0]

    failure_tail = quality_gate_section.split('echo "quality-pass=false" >> $GITHUB_OUTPUT', 1)[1]

    assert "if: always()" in quality_report_section
    assert "exit 1" in failure_tail
    assert "if: always() && github.event_name == 'pull_request' && steps.gate.outputs.quality-pass == 'false'" in comment_section


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


def test_security_testing_uses_parseable_report_generation_and_non_blocking_slack() -> None:
    workflow = _read_workflow("security-testing.yml")

    report_section = workflow.split("Generate consolidated security report", 1)[1].split("Upload security reports", 1)[
        0
    ]
    notification_section = workflow.split("security-notification:", 1)[1]

    assert "cat > security-reports/security-summary.md << 'EOF'" not in report_section
    assert "python - <<'PY'" in report_section
    assert "security-results.json" in report_section

    assert "if: always() && secrets.SLACK_WEBHOOK_URL != ''" in notification_section
    assert "webhook_url:" not in notification_section
    assert "continue-on-error: true" in notification_section


def test_security_testing_scopes_sast_gate_to_relevant_python_changes() -> None:
    workflow = _read_workflow("security-testing.yml")

    assert "security-test-scope-detect" in workflow
    assert "bandit_required" in workflow
    assert "bandit_args" in workflow

    scope_section = workflow.split("security-test-scope-detect:", 1)[1].split("security-scan:", 1)[0]
    scan_section = workflow.split("security-scan:", 1)[1].split("dependency-check:", 1)[0]

    assert "git diff --name-only" in scope_section
    assert "src/*.py|src/**/*.py|web/backend/app/*.py|web/backend/app/**/*.py" in scope_section
    assert "needs: security-test-scope-detect" in scan_section
    assert "needs.security-test-scope-detect.outputs.bandit_required == 'true'" in scan_section
    assert "${{ needs.security-test-scope-detect.outputs.bandit_args }}" in scan_section
    assert "bandit -r src/" not in scan_section


def test_quant_strategy_validation_uses_existing_script_path_and_safe_issue_body_heredoc() -> None:
    workflow = _read_workflow("quant-strategy-validation.yml")

    assert "chmod +x scripts/dev/ci/quant_strategy_validation.py" in workflow
    assert "python scripts/dev/ci/quant_strategy_validation.py" in workflow
    assert "ISSUE_BODY=$(cat <<EOF" in workflow
    assert '$(cat "$GITHUB_STEP_SUMMARY"' in workflow


def test_mainline_governance_summary_uses_single_line_python_command() -> None:
    workflow = _read_workflow("mainline-governance.yml")

    assert "Add workflow summary" in workflow
    assert "python -c 'import json, os; from pathlib import Path;" in workflow
    assert "python - <<'PY'" not in workflow
