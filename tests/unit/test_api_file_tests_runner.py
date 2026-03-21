from __future__ import annotations

from tests.api.file_tests import FileTestRunner, TestPriority
from tests.api.file_tests.run_file_tests import FileTestRunnerCLI


def test_cli_discovers_file_test_modules_instead_of_mock_api_paths() -> None:
    cli = FileTestRunnerCLI()

    assert "tests/api/file_tests/test_market_api.py" in cli.api_files
    assert all(path.startswith("tests/api/file_tests/test_") for path in cli.api_files)


def test_priority_filter_matches_test_file_names() -> None:
    cli = FileTestRunnerCLI()
    files = [
        "tests/api/file_tests/test_market_api.py",
        "tests/api/file_tests/test_trade_routes_api.py",
        "tests/api/file_tests/test_monitoring_api.py",
    ]

    assert cli.filter_files_by_priority(files, TestPriority.P0_CONTRACT) == [
        "tests/api/file_tests/test_market_api.py",
        "tests/api/file_tests/test_trade_routes_api.py",
    ]


def test_execute_file_tests_runs_real_pytest() -> None:
    runner = FileTestRunner(max_workers=1)

    result = __import__("asyncio").run(runner._execute_file_tests("tests/api/file_tests/test_market_api.py", {}))

    assert result["passed"] > 0
    assert result["failed"] == 0
    assert result["errors"] == []
