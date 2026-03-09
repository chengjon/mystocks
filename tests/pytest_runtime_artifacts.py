from __future__ import annotations

import shutil
from pathlib import Path

CANONICAL_COVERAGE_JSON = "reports/coverage/coverage.json"
CANONICAL_TIMING_FILE = "var/reports/test_timing.csv"


def ensure_canonical_timing_output(config, *, project_root: Path | None = None) -> None:
    root = project_root or Path.cwd()
    timing_file = config.getoption("timing_file", default=None)
    if timing_file != "test_timing.csv":
        return

    canonical_path = root / CANONICAL_TIMING_FILE
    canonical_path.parent.mkdir(parents=True, exist_ok=True)

    generated_root_file = root / timing_file
    plugin = config.pluginmanager.get_plugin("timing_plugin")
    config.option.timing_file = CANONICAL_TIMING_FILE

    if plugin is not None:
        plugin.configure(str(canonical_path))
    elif not canonical_path.exists():
        canonical_path.touch()

    if not canonical_path.exists():
        canonical_path.touch()

    if generated_root_file.exists():
        generated_root_file.unlink()


def cleanup_root_runtime_artifacts(project_root: Path | None = None) -> None:
    root = project_root or Path.cwd()
    canonical_coverage_path = root / CANONICAL_COVERAGE_JSON
    canonical_path = root / CANONICAL_TIMING_FILE
    root_coverage_file = root / "coverage.json"
    root_timing_file = root / "test_timing.csv"

    if root_coverage_file.exists():
        canonical_coverage_path.parent.mkdir(parents=True, exist_ok=True)
        canonical_coverage_path.write_text(root_coverage_file.read_text(encoding="utf-8"), encoding="utf-8")
        root_coverage_file.unlink()

    if root_timing_file.exists():
        canonical_path.parent.mkdir(parents=True, exist_ok=True)
        root_content = root_timing_file.read_text(encoding="utf-8")

        if canonical_path.exists():
            canonical_content = canonical_path.read_text(encoding="utf-8")
            if root_content.startswith("test_name,"):
                root_lines = root_content.splitlines()
                append_text = "\n".join(root_lines[1:])
                if append_text:
                    with canonical_path.open("a", encoding="utf-8") as handle:
                        if canonical_content and not canonical_content.endswith("\n"):
                            handle.write("\n")
                        handle.write(append_text)
                        if not append_text.endswith("\n"):
                            handle.write("\n")
            else:
                with canonical_path.open("a", encoding="utf-8") as handle:
                    handle.write(root_content)
        else:
            canonical_path.write_text(root_content, encoding="utf-8")

        root_timing_file.unlink()

    root_cache_dir = root / "__pycache__"
    if root_cache_dir.exists():
        shutil.rmtree(root_cache_dir)
