from __future__ import annotations

from pathlib import Path

from tests.pytest_runtime_artifacts import (
    CANONICAL_TIMING_FILE,
    cleanup_root_runtime_artifacts,
    ensure_canonical_timing_output,
)

CANONICAL_COVERAGE_JSON = "reports/coverage/coverage.json"


def test_pytest_timing_csv_is_configured_under_var_reports() -> None:
    pytest_ini = Path("pytest.ini").read_text(encoding="utf-8")

    assert "--timing-file=var/reports/test_timing.csv" in pytest_ini


def test_pytest_coverage_json_is_configured_under_reports_coverage() -> None:
    pytest_ini = Path("pytest.ini").read_text(encoding="utf-8")

    assert "--cov-report=json:reports/coverage/coverage.json" in pytest_ini


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
