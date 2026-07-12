from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any


DEFAULT_LIMITS = {
    ".py": 800,
    ".ts": 500,
    ".vue": 500,
    ".spec.ts": 1000,
    ".spec.js": 1000,
}

DEFAULT_IGNORE_DIRECTORIES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "archived",
    "node_modules",
}


def normalize_relative_paths(paths: list[str] | None) -> list[str] | None:
    if paths is None:
        return None

    normalized: set[str] = set()
    for raw_path in paths:
        path_value = raw_path.strip()
        if not path_value:
            continue
        path_value = path_value.removeprefix("./")
        normalized_path = Path(path_value).as_posix().strip("/")
        if normalized_path:
            normalized.add(normalized_path)
    return sorted(normalized)


def resolve_limit_key(file_name: str, limits: dict[str, int]) -> str | None:
    if file_name.endswith(".spec.ts") and ".spec.ts" in limits:
        return ".spec.ts"
    if file_name.endswith(".spec.js") and ".spec.js" in limits:
        return ".spec.js"

    suffix = Path(file_name).suffix
    if suffix in limits:
        return suffix
    return None


def get_file_line_count(file_path: Path) -> int:
    try:
        with file_path.open("r", encoding="utf-8", errors="ignore") as handle:
            return sum(1 for _ in handle)
    except OSError:
        return 0


def is_within_scope(relative_path: str, scope_roots: tuple[str, ...]) -> bool:
    return any(relative_path == scope_root or relative_path.startswith(f"{scope_root}/") for scope_root in scope_roots)


def should_exclude(file_path: Path, root_path: Path, excluded: set[str]) -> bool:
    relative_path = file_path.relative_to(root_path).as_posix()
    return relative_path in excluded or file_path.name in excluded


def iter_candidate_files(
    root_path: Path,
    *,
    limits: dict[str, int],
    ignore_directories: set[str],
    exclude_files: set[str],
    scope_roots: tuple[str, ...] | None,
    paths: list[str] | None,
) -> list[Path]:
    normalized_paths = normalize_relative_paths(paths)

    if normalized_paths is not None:
        selected_files: list[Path] = []
        for relative_path in normalized_paths:
            if scope_roots and not is_within_scope(relative_path, scope_roots):
                continue
            candidate = root_path / relative_path
            if not candidate.is_file():
                continue
            if should_exclude(candidate, root_path, exclude_files):
                continue
            if resolve_limit_key(candidate.name, limits) is None:
                continue
            selected_files.append(candidate)
        return sorted(set(selected_files))

    discovered: list[Path] = []
    search_roots = [root_path / scope_root for scope_root in scope_roots] if scope_roots else [root_path]

    for search_root in search_roots:
        if not search_root.exists():
            continue

        for current_root, dirs, files in os.walk(search_root):
            dirs[:] = [directory for directory in dirs if directory not in ignore_directories]

            for file_name in files:
                file_path = Path(current_root) / file_name
                if should_exclude(file_path, root_path, exclude_files):
                    continue

                limit_key = resolve_limit_key(file_name, limits)
                if limit_key is None:
                    continue

                discovered.append(file_path)

    return sorted(set(discovered))


def build_report(
    root_dir: str | Path = ".",
    *,
    limits: dict[str, int] | None = None,
    ignore_directories: set[str] | None = None,
    exclude_files: set[str] | None = None,
    scope_roots: tuple[str, ...] | None = None,
    paths: list[str] | None = None,
) -> dict[str, Any]:
    effective_limits = dict(limits or DEFAULT_LIMITS)
    ignored = set(ignore_directories or DEFAULT_IGNORE_DIRECTORIES)
    excluded = set(exclude_files or set())
    root_path = Path(root_dir).resolve()
    effective_scope_roots = tuple(scope_roots) if scope_roots else None

    violations: list[dict[str, object]] = []
    candidate_files = iter_candidate_files(
        root_path,
        limits=effective_limits,
        ignore_directories=ignored,
        exclude_files=excluded,
        scope_roots=effective_scope_roots,
        paths=paths,
    )

    for file_path in candidate_files:
        limit_key = resolve_limit_key(file_path.name, effective_limits)
        if limit_key is None:
            continue

        line_count = get_file_line_count(file_path)

        if line_count > effective_limits[limit_key]:
            violations.append(
                {
                    "path": file_path.relative_to(root_path).as_posix(),
                    "lines": line_count,
                    "limit": effective_limits[limit_key],
                    "type": limit_key,
                },
            )

    violations.sort(key=lambda item: (int(item["limit"]), int(item["lines"])), reverse=True)

    return {
        "root_dir": str(root_path),
        "scope_roots": list(effective_scope_roots or []),
        "paths": normalize_relative_paths(paths) or [],
        "checked_files": len(candidate_files),
        "oversized_count": len(violations),
        "violations": violations,
        "limits": effective_limits,
        "summary": {
            "checked_files": len(candidate_files),
            "oversized_count": len(violations),
        },
    }


def check_files(
    root_dir: str | Path = ".",
    *,
    limits: dict[str, int] | None = None,
    ignore_directories: set[str] | None = None,
    exclude_files: set[str] | None = None,
    scope_roots: tuple[str, ...] | None = None,
    paths: list[str] | None = None,
) -> list[str]:
    report = build_report(
        root_dir,
        limits=limits,
        ignore_directories=ignore_directories,
        exclude_files=exclude_files,
        scope_roots=scope_roots,
        paths=paths,
    )
    return [f"🚩 {item['path']}: {item['lines']} lines (Limit: {item['limit']})" for item in report["violations"]]


def print_report(report: dict[str, object], output_format: str = "text") -> None:
    if output_format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    print("File size monitor report")
    print("========================")
    print(f"root_dir: {report['root_dir']}")
    print(f"checked_files: {report['checked_files']}")
    print(f"oversized_count: {report['oversized_count']}")

    violations = report["violations"]
    if violations:
        print("\nOversized files:")
        for item in violations:
            print(
                f"  - {item['path']}: {item['lines']} lines (limit: {item['limit']}, type: {item['type']})",
            )
    else:
        print("\nNo oversized files detected.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Canonical file size guardrail monitor")
    parser.add_argument("filenames", nargs="*")
    parser.add_argument("--root-dir", default=".")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--path", action="append")
    parser.add_argument("--scope-root", action="append")
    parser.add_argument("--ignore-dir", action="append", default=[])
    parser.add_argument("--exclude-file", action="append", default=[])
    args = parser.parse_args()

    combined_paths = [*(args.path or []), *args.filenames]
    report = build_report(
        args.root_dir,
        ignore_directories=DEFAULT_IGNORE_DIRECTORIES.union(args.ignore_dir),
        exclude_files=set(args.exclude_file),
        scope_roots=tuple(args.scope_root) if args.scope_root else None,
        paths=combined_paths or None,
    )
    print_report(report, args.format)
    return 1 if report["oversized_count"] else 0


if __name__ == "__main__":
    sys.exit(main())
