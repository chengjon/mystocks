from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Any


SCOPE_ROOTS = ("src", "web/backend/app")
RULE_ID = "backend-singleton-none-init"


def normalize_relative_paths(paths: list[str] | None) -> list[str]:
    if not paths:
        return []

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


def is_in_scope(path_value: str) -> bool:
    return any(path_value == root or path_value.startswith(f"{root}/") for root in SCOPE_ROOTS)


def discover_candidate_files(project_root: Path, scoped_paths: list[str] | None) -> list[Path]:
    if scoped_paths:
        candidates: list[Path] = []
        for relative_path in scoped_paths:
            if not relative_path.endswith(".py") or not is_in_scope(relative_path):
                continue
            file_path = project_root / relative_path
            if file_path.is_file():
                candidates.append(file_path)
        return sorted(set(candidates))

    discovered: list[Path] = []
    for scope_root in SCOPE_ROOTS:
        base = project_root / scope_root
        if not base.exists():
            continue
        discovered.extend(sorted(base.rglob("*.py")))
    return discovered


def extract_module_level_none_assignments(tree: ast.Module) -> set[str]:
    initialized: set[str] = set()

    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) and node.value.value is None:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    initialized.add(target.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if isinstance(node.value, ast.Constant) and node.value.value is None:
                initialized.add(node.target.id)

    return initialized


def extract_global_names(tree: ast.AST) -> set[str]:
    global_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Global):
            global_names.update(node.names)
    return global_names


def build_report(project_root: Path, paths: list[str] | None = None) -> dict[str, Any]:
    normalized_paths = normalize_relative_paths(paths)
    candidate_files = discover_candidate_files(project_root, normalized_paths)
    errors: list[dict[str, Any]] = []
    parse_errors: list[dict[str, Any]] = []

    for file_path in candidate_files:
        relative_path = file_path.relative_to(project_root).as_posix()

        try:
            tree = ast.parse(file_path.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            parse_errors.append(
                {
                    "path": relative_path,
                    "rule_id": "python-parse-error",
                    "message": f"Failed to parse Python file: {exc.msg}",
                }
            )
            continue

        module_level_none_names = extract_module_level_none_assignments(tree)
        global_names = extract_global_names(tree)
        missing_names = sorted(name for name in global_names if name not in module_level_none_names)

        if missing_names:
            errors.append(
                {
                    "path": relative_path,
                    "rule_id": RULE_ID,
                    "message": "Global singleton variables must be initialized to None at module top level",
                    "names": missing_names,
                }
            )

    summary = {
        "errors": len(errors) + len(parse_errors),
        "checked_files": len(candidate_files),
    }

    return {
        "project_root": str(project_root),
        "scope_roots": list(SCOPE_ROOTS),
        "paths": normalized_paths,
        "checked_files": len(candidate_files),
        "errors": errors + parse_errors,
        "summary": summary,
    }


def print_report(report: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    print("Backend Singleton None Guard")
    print("============================")
    print(f"checked_files: {report['checked_files']}")
    print(f"errors: {report['summary']['errors']}")

    if report["errors"]:
        print("\nBlocking findings:")
        for item in report["errors"]:
            names = item.get("names")
            suffix = f" ({', '.join(names)})" if names else ""
            print(f"  - {item['path']}: {item['message']}{suffix}")
    else:
        print("\nNo backend singleton None guard violations detected.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate backend global singletons are initialized to None")
    parser.add_argument("--root-dir", default=".")
    parser.add_argument("--path", action="append")
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    project_root = Path(args.root_dir).resolve()
    combined_paths = list(args.path or [])
    combined_paths.extend(args.paths)
    report = build_report(project_root, combined_paths)
    print_report(report, args.format)
    return 1 if report["summary"]["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
