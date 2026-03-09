from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

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


def build_report(
    root_dir: str | Path = ".",
    *,
    limits: dict[str, int] | None = None,
    ignore_directories: set[str] | None = None,
    exclude_files: set[str] | None = None,
) -> dict[str, object]:
    effective_limits = dict(limits or DEFAULT_LIMITS)
    ignored = set(ignore_directories or DEFAULT_IGNORE_DIRECTORIES)
    excluded = set(exclude_files or set())
    root_path = Path(root_dir).resolve()

    violations: list[dict[str, object]] = []
    checked_files = 0

    for current_root, dirs, files in os.walk(root_path):
        dirs[:] = [directory for directory in dirs if directory not in ignored]

        for file_name in files:
            if file_name in excluded:
                continue

            limit_key = resolve_limit_key(file_name, effective_limits)
            if limit_key is None:
                continue

            file_path = Path(current_root) / file_name
            line_count = get_file_line_count(file_path)
            checked_files += 1

            if line_count > effective_limits[limit_key]:
                violations.append(
                    {
                        "path": file_path.relative_to(root_path).as_posix(),
                        "lines": line_count,
                        "limit": effective_limits[limit_key],
                        "type": limit_key,
                    }
                )

    violations.sort(key=lambda item: (int(item["limit"]), int(item["lines"])), reverse=True)

    return {
        "root_dir": str(root_path),
        "checked_files": checked_files,
        "oversized_count": len(violations),
        "violations": violations,
        "limits": effective_limits,
    }


def check_files(
    root_dir: str | Path = ".",
    *,
    limits: dict[str, int] | None = None,
    ignore_directories: set[str] | None = None,
    exclude_files: set[str] | None = None,
) -> list[str]:
    report = build_report(
        root_dir,
        limits=limits,
        ignore_directories=ignore_directories,
        exclude_files=exclude_files,
    )
    return [
        f"🚩 {item['path']}: {item['lines']} lines (Limit: {item['limit']})"
        for item in report["violations"]
    ]


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
                f"  - {item['path']}: {item['lines']} lines "
                f"(limit: {item['limit']}, type: {item['type']})"
            )
    else:
        print("\nNo oversized files detected.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Canonical file size guardrail monitor")
    parser.add_argument("--root-dir", default=".")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--ignore-dir", action="append", default=[])
    parser.add_argument("--exclude-file", action="append", default=[])
    args = parser.parse_args()

    report = build_report(
        args.root_dir,
        ignore_directories=DEFAULT_IGNORE_DIRECTORIES.union(args.ignore_dir),
        exclude_files=set(args.exclude_file),
    )
    print_report(report, args.format)
    return 1 if report["oversized_count"] else 0


if __name__ == "__main__":
    sys.exit(main())
