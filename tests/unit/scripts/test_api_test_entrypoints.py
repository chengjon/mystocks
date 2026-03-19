from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]


def test_root_api_test_wrapper_exists_and_delegates_to_scripts_tests_runner() -> None:
    wrapper = PROJECT_ROOT / "run-api-tests.sh"

    assert wrapper.exists()
    content = wrapper.read_text(encoding="utf-8")
    assert 'exec bash "${PROJECT_ROOT}/scripts/tests/run-api-tests.sh" "$@"' in content


def test_scripts_api_test_runner_uses_repo_relative_paths() -> None:
    runner = PROJECT_ROOT / "scripts" / "tests" / "run-api-tests.sh"
    content = runner.read_text(encoding="utf-8")

    assert 'PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"' in content
    assert 'BASE_URL="${BASE_URL:-http://localhost:8020}"' in content
    assert 'TEST_DIR="${PROJECT_ROOT}/web/frontend/tests"' in content
    assert 'TEST_PATH="tests/${TEST_FILE}"' in content
    assert 'REPORT_DIR="${PROJECT_ROOT}/docs/reports/test-results"' in content
    assert 'npx playwright test "${TEST_PATH}"' in content
    assert '--reporter=html' in content


def test_legacy_api_automation_suite_uses_repo_relative_report_dir() -> None:
    suite = PROJECT_ROOT / "web" / "frontend" / "tests" / "api-automation" / "legacy-suite.js"
    content = suite.read_text(encoding="utf-8")

    assert "const PROJECT_ROOT = path.resolve(__dirname, '../../../../');" in content
    assert "const REPORT_DIR = path.join(PROJECT_ROOT, 'docs', 'reports', 'test-results');" in content
