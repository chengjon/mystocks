from __future__ import annotations

from tests.api.file_tests.run_file_tests import FileTestRunnerCLI


def test_api_file_runner_discovers_real_backend_api_tree() -> None:
    runner = FileTestRunnerCLI()

    assert len(runner.api_files) > 7
    assert any(path.startswith("web/backend/app/api/") for path in runner.api_files)
