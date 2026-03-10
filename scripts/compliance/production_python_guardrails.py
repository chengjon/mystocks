from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Any


DEFAULT_SCOPE_ROOTS = ("src", "web/backend/app")
DEFAULT_IGNORE_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "node_modules",
}
DEFAULT_WARNING_LINES = 650
DEFAULT_FAILURE_LINES = 700


def normalize_relative_paths(paths: list[str] | None) -> list[str] | None:
    if paths is None:
        return None

    normalized: set[str] = set()
    for raw_path in paths:
        path_value = raw_path.strip()
        if not path_value:
            continue
        if path_value.startswith("./"):
            path_value = path_value[2:]
        normalized_path = Path(path_value).as_posix().strip("/")
        if normalized_path:
            normalized.add(normalized_path)
    return sorted(normalized)


def is_within_scope(relative_path: str, scope_roots: tuple[str, ...]) -> bool:
    return any(relative_path == scope_root or relative_path.startswith(f"{scope_root}/") for scope_root in scope_roots)


def iter_python_files(
    root_dir: Path,
    *,
    scope_roots: tuple[str, ...],
    paths: list[str] | None = None,
    ignore_dirs: set[str] | None = None,
) -> list[Path]:
    ignored = ignore_dirs or DEFAULT_IGNORE_DIRS
    normalized_paths = normalize_relative_paths(paths)

    if normalized_paths is not None:
        selected_files: list[Path] = []
        for relative_path in normalized_paths:
            if not is_within_scope(relative_path, scope_roots):
                continue
            candidate = root_dir / relative_path
            if candidate.is_file() and candidate.suffix == ".py":
                selected_files.append(candidate)
        return sorted(set(selected_files))

    discovered: list[Path] = []
    for scope_root in scope_roots:
        scope_path = root_dir / scope_root
        if not scope_path.exists():
            continue
        for path in scope_path.rglob("*.py"):
            if any(part in ignored for part in path.parts):
                continue
            discovered.append(path)
    return sorted(set(discovered))


def count_lines(file_path: Path) -> int:
    with file_path.open("r", encoding="utf-8", errors="ignore") as handle:
        return sum(1 for _ in handle)


def read_source(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8", errors="ignore")


def find_bare_print_calls(tree: ast.AST) -> list[tuple[int, int]]:
    findings: list[tuple[int, int]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            findings.append((getattr(node, "lineno", 0), getattr(node, "col_offset", 0) + 1))
    return sorted(findings)


def make_finding(
    *,
    severity: str,
    path: str,
    rule_id: str,
    message: str,
    line: int | None = None,
    column: int | None = None,
    lines: int | None = None,
) -> dict[str, Any]:
    finding: dict[str, Any] = {
        "severity": severity,
        "path": path,
        "rule_id": rule_id,
        "message": message,
    }
    if line is not None:
        finding["line"] = line
    if column is not None:
        finding["column"] = column
    if lines is not None:
        finding["lines"] = lines
    return finding


def build_report(
    root_dir: str | Path = ".",
    *,
    scope_roots: tuple[str, ...] = DEFAULT_SCOPE_ROOTS,
    paths: list[str] | None = None,
    warning_lines: int = DEFAULT_WARNING_LINES,
    failure_lines: int = DEFAULT_FAILURE_LINES,
) -> dict[str, Any]:
    if warning_lines >= failure_lines:
        raise ValueError("warning_lines must be lower than failure_lines")

    root_path = Path(root_dir).resolve()
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    files = iter_python_files(root_path, scope_roots=scope_roots, paths=paths)
    for file_path in files:
        relative_path = file_path.relative_to(root_path).as_posix()
        line_count = count_lines(file_path)

        if line_count > failure_lines:
            errors.append(
                make_finding(
                    severity="error",
                    path=relative_path,
                    rule_id="python-lines-error",
                    message=f"Python file exceeds failure threshold ({line_count} > {failure_lines})",
                    lines=line_count,
                )
            )
        elif line_count > warning_lines:
            warnings.append(
                make_finding(
                    severity="warning",
                    path=relative_path,
                    rule_id="python-lines-warning",
                    message=f"Python file exceeds warning threshold ({line_count} > {warning_lines})",
                    lines=line_count,
                )
            )

        source = read_source(file_path)
        try:
            tree = ast.parse(source, filename=str(file_path))
        except SyntaxError as error:
            errors.append(
                make_finding(
                    severity="error",
                    path=relative_path,
                    rule_id="python-parse-error",
                    message=f"Python file is not parseable: {error.msg}",
                    line=error.lineno or 0,
                    column=error.offset or 0,
                )
            )
            continue

        for line, column in find_bare_print_calls(tree):
            errors.append(
                make_finding(
                    severity="error",
                    path=relative_path,
                    rule_id="no-bare-print",
                    message="Bare print() is forbidden in production Python code; use the project logger instead",
                    line=line,
                    column=column,
                )
            )

    errors.sort(key=lambda item: (item["path"], item["rule_id"], item.get("line", 0)))
    warnings.sort(key=lambda item: (item["path"], item["rule_id"], item.get("line", 0)))

    return {
        "project_root": str(root_path),
        "scope_roots": list(scope_roots),
        "paths": normalize_relative_paths(paths) or [],
        "checked_files": len(files),
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "errors": len(errors),
            "warnings": len(warnings),
            "checked_files": len(files),
        },
        "policy": {
            "warning_lines": warning_lines,
            "failure_lines": failure_lines,
        },
    }


def print_report(report: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    print("Production Python Guardrails")
    print("============================")
    print(f"project_root: {report['project_root']}")
    print(f"checked_files: {report['checked_files']}")
    print(f"errors: {report['summary']['errors']}")
    print(f"warnings: {report['summary']['warnings']}")

    if report["errors"]:
        print("\nBlocking findings:")
        for item in report["errors"]:
            suffix = f" @ {item['line']}:{item['column']}" if "line" in item and "column" in item else ""
            print(f"  - {item['path']}{suffix}: {item['message']}")

    if report["warnings"]:
        print("\nWarnings:")
        for item in report["warnings"]:
            print(f"  - {item['path']}: {item['message']}")

    if not report["errors"] and not report["warnings"]:
        print("\nNo production Python guardrail findings.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Production Python guardrails for line counts and bare print usage")
    parser.add_argument("--root-dir", default=".")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--scope", action="append", default=list(DEFAULT_SCOPE_ROOTS))
    parser.add_argument("--path", action="append")
    parser.add_argument("--warning-lines", type=int, default=DEFAULT_WARNING_LINES)
    parser.add_argument("--failure-lines", type=int, default=DEFAULT_FAILURE_LINES)
    args = parser.parse_args(argv)

    report = build_report(
        args.root_dir,
        scope_roots=tuple(args.scope),
        paths=args.path,
        warning_lines=args.warning_lines,
        failure_lines=args.failure_lines,
    )
    print_report(report, args.format)
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
