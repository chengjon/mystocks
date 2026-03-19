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


def test_api_contract_and_api_file_workflows_install_backend_runtime_dependencies() -> None:
    contract_workflow = _read_workflow("api-contract-validation.yml")
    api_file_workflow = _read_workflow("api-file-tests.yml")

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
        assert package_name in contract_workflow
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


def test_ai_test_optimization_uses_repo_repo_for_new_pr_comments() -> None:
    workflow = _read_workflow("ai-test-optimization.yml")

    assert "await github.rest.issues.createComment" in workflow
    assert "repo: context.repo.repo" in workflow
    assert "repo: context.repo.name" not in workflow
