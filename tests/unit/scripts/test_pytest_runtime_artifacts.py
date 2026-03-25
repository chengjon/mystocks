from __future__ import annotations

from pathlib import Path

from tests.pytest_runtime_artifacts import (
    CANONICAL_TIMING_FILE,
    cleanup_root_runtime_artifacts,
    ensure_canonical_timing_output,
)

CANONICAL_COVERAGE_JSON = "reports/coverage/coverage.json"
CANONICAL_COVERAGE_DATA_FILE = "var/reports/coverage/.coverage"
CANONICAL_COVERAGE_HTML_DIR = "var/reports/coverage/htmlcov"
CANONICAL_COVERAGE_XML = "var/reports/coverage/coverage.xml"
CANONICAL_PYTEST_CACHE_DIR = "var/cache/pytest"


def test_pytest_timing_csv_is_configured_under_var_reports() -> None:
    pytest_ini = Path("pytest.ini").read_text(encoding="utf-8")

    assert "--timing-file=var/reports/test_timing.csv" in pytest_ini


def test_pytest_coverage_json_is_configured_under_reports_coverage() -> None:
    pytest_ini = Path("pytest.ini").read_text(encoding="utf-8")

    assert "--cov-report=json:reports/coverage/coverage.json" in pytest_ini


def test_pytest_html_coverage_is_configured_under_var_reports() -> None:
    pytest_ini = Path("pytest.ini").read_text(encoding="utf-8")

    assert f"--cov-report=html:{CANONICAL_COVERAGE_HTML_DIR}" in pytest_ini
    assert "--cov-report=html:htmlcov" not in pytest_ini


def test_pytest_cache_dir_is_configured_under_var_cache() -> None:
    pytest_ini = Path("pytest.ini").read_text(encoding="utf-8")

    assert f"cache_dir = {CANONICAL_PYTEST_CACHE_DIR}" in pytest_ini


def test_pyproject_coverage_runtime_artifacts_are_configured_under_var_reports() -> None:
    pyproject = Path("pyproject.toml").read_text(encoding="utf-8")

    assert f'data_file = "{CANONICAL_COVERAGE_DATA_FILE}"' in pyproject
    assert "[tool.coverage.html]" in pyproject
    assert f'directory = "{CANONICAL_COVERAGE_HTML_DIR}"' in pyproject
    assert "[tool.coverage.xml]" in pyproject
    assert f'output = "{CANONICAL_COVERAGE_XML}"' in pyproject


def test_active_test_runners_use_canonical_coverage_artifact_paths() -> None:
    run_all_tests = Path("tests/run_all_tests.py").read_text(encoding="utf-8")
    e2e_runner = Path("scripts/tests/run_e2e_tests.sh").read_text(encoding="utf-8")

    assert CANONICAL_COVERAGE_HTML_DIR in run_all_tests
    assert CANONICAL_COVERAGE_XML in run_all_tests
    assert 'Path("htmlcov/index.html")' not in run_all_tests
    assert "HTML覆盖率报告: htmlcov/index.html" not in run_all_tests
    assert 'Path("coverage.xml")' not in run_all_tests

    assert CANONICAL_COVERAGE_HTML_DIR in e2e_runner
    assert 'file://$(pwd)/htmlcov/index.html' not in e2e_runner


class _FakePlugin:
    def __init__(self, timing_file_path: Path) -> None:
        self.timing_file_path = timing_file_path
        self.reconfigured_to: str | None = None

    def configure(self, timing_file_path: str) -> None:
        self.reconfigured_to = timing_file_path
        self.timing_file_path = Path(timing_file_path)


class _FakePluginManager:
    def __init__(self, plugin: _FakePlugin) -> None:
        self._plugin = plugin

    def get_plugin(self, name: str) -> _FakePlugin | None:
        if name == "timing_plugin":
            return self._plugin
        return None


class _FakeOption:
    def __init__(self, timing_file: str) -> None:
        self.timing_file = timing_file


class _FakeConfig:
    def __init__(self, plugin: _FakePlugin, timing_file: str) -> None:
        self.option = _FakeOption(timing_file)
        self.pluginmanager = _FakePluginManager(plugin)

    def getoption(self, name: str, default: str | None = None) -> str | None:
        if name == "timing_file":
            return self.option.timing_file
        return default


def test_conftest_reconfigures_default_timing_output_to_canonical_path(tmp_path: Path) -> None:
    root_timing_file = tmp_path / "test_timing.csv"
    root_timing_file.write_text("test_name,start_time,end_time,duration_seconds,result\n", encoding="utf-8")

    plugin = _FakePlugin(root_timing_file)
    config = _FakeConfig(plugin, "test_timing.csv")

    ensure_canonical_timing_output(config, project_root=tmp_path)

    expected_path = tmp_path / CANONICAL_TIMING_FILE

    assert config.option.timing_file == CANONICAL_TIMING_FILE
    assert plugin.reconfigured_to == str(expected_path)
    assert expected_path.exists()
    assert not root_timing_file.exists()


def test_cleanup_root_runtime_artifacts_moves_timing_csv_and_removes_root_pycache(tmp_path: Path) -> None:
    root_timing_file = tmp_path / "test_timing.csv"
    root_timing_file.write_text(
        "test_name,start_time,end_time,duration_seconds,result\n"
        "unit/test_example.py::test_ok,2026,2026,0.001,P\n",
        encoding="utf-8",
    )
    root_cache_dir = tmp_path / "__pycache__"
    root_cache_dir.mkdir()
    (root_cache_dir / "conftest.cpython-312.pyc").write_bytes(b"pyc")

    cleanup_root_runtime_artifacts(tmp_path)

    canonical_path = tmp_path / CANONICAL_TIMING_FILE

    assert canonical_path.exists()
    assert "unit/test_example.py::test_ok" in canonical_path.read_text(encoding="utf-8")
    assert not root_timing_file.exists()
    assert not root_cache_dir.exists()


def test_cleanup_root_runtime_artifacts_moves_root_coverage_json(tmp_path: Path) -> None:
    root_coverage_file = tmp_path / "coverage.json"
    root_coverage_file.write_text('{"totals": {"percent_covered": 91.5}}', encoding="utf-8")

    cleanup_root_runtime_artifacts(tmp_path)

    canonical_path = tmp_path / CANONICAL_COVERAGE_JSON

    assert canonical_path.exists()
    assert '"percent_covered": 91.5' in canonical_path.read_text(encoding="utf-8")
    assert not root_coverage_file.exists()


def test_cleanup_root_runtime_artifacts_removes_root_coverage_data_and_html_report(tmp_path: Path) -> None:
    root_coverage_data_file = tmp_path / ".coverage"
    root_coverage_data_file.write_text("coverage-data", encoding="utf-8")
    root_htmlcov_dir = tmp_path / "htmlcov"
    root_htmlcov_dir.mkdir()
    (root_htmlcov_dir / "index.html").write_text("<html>coverage</html>", encoding="utf-8")

    cleanup_root_runtime_artifacts(tmp_path)

    assert not root_coverage_data_file.exists()
    assert not root_htmlcov_dir.exists()
