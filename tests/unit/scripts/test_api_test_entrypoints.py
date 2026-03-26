from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_root_api_test_wrapper_has_been_removed() -> None:
    wrapper = PROJECT_ROOT / "run-api-tests.sh"

    assert not wrapper.exists()


def test_scripts_api_test_runner_uses_repo_relative_paths() -> None:
    runner = PROJECT_ROOT / "scripts" / "tests" / "run-api-tests.sh"
    content = runner.read_text(encoding="utf-8")

    assert 'PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"' in content
    assert 'BASE_URL="${BASE_URL:-http://localhost:8020}"' in content
    assert 'FRONTEND_PORT="${FRONTEND_PORT:-3020}"' in content
    assert 'FRONTEND_BACKUP_PORT="${FRONTEND_BACKUP_PORT:-3021}"' in content
    assert 'TEST_DIR="${PROJECT_ROOT}/web/frontend/tests"' in content
    assert 'TEST_PATH="tests/${TEST_FILE}"' in content
    assert 'REPORT_DIR="${PROJECT_ROOT}/docs/reports/test-results"' in content
    assert 'curl -fsS "${BASE_URL}/api/announcement/health"' in content
    assert 'curl -fsS "${BASE_URL}/health/ready"' in content
    assert 'npx playwright test "${TEST_PATH}"' in content
    assert '--config=playwright.config.ts' in content
    assert '--reporter=html' in content


def test_legacy_scripts_api_test_runner_accepts_modern_health_probes() -> None:
    runner = PROJECT_ROOT / "scripts" / "run-api-tests.sh"
    content = runner.read_text(encoding="utf-8")

    assert 'curl -fsS "${BACKEND_BASE_URL}/api/announcement/health"' in content
    assert 'curl -fsS "${BACKEND_BASE_URL}/health/ready"' in content
    assert 'if [ ! -t 0 ] || [ -n "${CI:-}" ]; then' in content


def test_legacy_api_automation_suite_uses_repo_relative_report_dir() -> None:
    suite = PROJECT_ROOT / "web" / "frontend" / "tests" / "api-automation" / "legacy-suite.js"
    content = suite.read_text(encoding="utf-8")

    assert "const CI_MODE = process.env.CI === 'true' || process.env.API_AUTOMATION_MODE === 'ci';" in content
    assert "const CI_ENDPOINT_ALLOWLIST = [" in content
    assert "function selectEndpointsForRun(endpoints)" in content
    assert "开始测试 ${CI_MODE ? 'CI smoke 子集' : '所有'}端点" in content
    assert "const PROJECT_ROOT = path.resolve(__dirname, '../../../../');" in content
    assert "const REPORT_DIR = path.join(PROJECT_ROOT, 'docs', 'reports', 'test-results');" in content
    assert "test.afterAll(async () => {" in content
    assert "const summaryPath = path.join(REPORT_DIR, 'api-test-summary.json');" in content
    assert "CI mode skips duplicate tag replay after the primary discovery scan." in content


def test_frontend_playwright_config_can_skip_managed_webserver() -> None:
    config = PROJECT_ROOT / "web" / "frontend" / "playwright.config.js"
    content = config.read_text(encoding="utf-8")

    assert 'process.env.PLAYWRIGHT_EXTERNAL_FRONTEND === "1"' in content
    assert "webServer: useManagedServer" in content
    assert "? undefined" in content
