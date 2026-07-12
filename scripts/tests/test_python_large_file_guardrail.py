from __future__ import annotations

from pathlib import Path


SCAN_ROOTS = [Path("src"), Path("web/backend/app")]
IGNORE_MARKERS = (".bak", ".old", ".new", ".backup")
LINE_LIMIT = 1000


def _iter_python_files() -> list[Path]:
    python_files: list[Path] = []

    for root in SCAN_ROOTS:
        for path in root.rglob("*.py"):
            path_str = str(path)
            if any(marker in path_str for marker in IGNORE_MARKERS):
                continue
            python_files.append(path)

    return sorted(python_files)


def _collect_oversized_files() -> list[str]:
    oversized: list[str] = []

    for path in _iter_python_files():
        with open(path, encoding="utf-8", errors="ignore") as file:
            line_count = sum(1 for _ in file)

        if line_count > LINE_LIMIT:
            oversized.append(f"{path}: {line_count} lines")

    return oversized


def test_no_python_file_exceeds_1000_lines_in_runtime_roots() -> None:
    oversized = _collect_oversized_files()

    assert not oversized, "Oversized Python files detected:\n" + "\n".join(oversized)
