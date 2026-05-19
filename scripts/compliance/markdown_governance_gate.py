from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def load_markdown_governance_helpers():
    """Load helper constants without importing the heavy src package initializer."""
    module_path = PROJECT_ROOT / "src" / "utils" / "markdown_governance.py"
    spec = importlib.util.spec_from_file_location("markdown_governance_helpers", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load markdown governance helpers from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.BOUNDARY_NOTE_PATTERN, module.recommend_boundary_note_preset


BOUNDARY_NOTE_PATTERN, recommend_boundary_note_preset = load_markdown_governance_helpers()


RULE_ID = "markdown-governance-gate"
BANNED_PHRASES = ("以后者为准", "以前者为准", "一律以后者为准")
SKIP_EXACT_PATHS = {
    "architecture/STANDARDS.md",
    "openspec/AGENTS.md",
}
SKIP_PREFIXES = (
    ".worktrees/",
    "config/monitoring-stack/data/grafana/plugins/",
    "data/grafana/plugins/",
)
FALLBACK_IGNORE_DIRECTORIES = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "__pycache__",
    "node_modules",
}


def build_fix_hint(path_value: str, mode: str) -> str:
    recommended_preset = recommend_boundary_note_preset(path_value)
    apply_command = f"python scripts/dev/apply_markdown_boundary_note.py --preset {recommended_preset} {path_value}"

    if mode == "missing-boundary-note":
        return f"Add a controlled boundary note. Suggested command: `{apply_command}`"
    if mode == "missing-boundary-note-and-banned-phrases":
        return (
            f"Add a controlled boundary note and replace ambiguous source-of-truth wording with explicit file paths. "
            f"Suggested command: `{apply_command}`"
        )
    if mode == "banned-phrases":
        return "Replace ambiguous source-of-truth wording with explicit canonical file paths."
    if mode == "read-error":
        return "Ensure the tracked markdown file still exists and is readable in the current worktree."
    return ""


def normalize_relative_paths(paths: list[str] | None) -> list[str]:
    if not paths:
        return []

    normalized: set[str] = set()
    for raw_path in paths:
        path_value = raw_path.strip().replace("\\", "/")
        if not path_value:
            continue
        if len(path_value) >= 2 and path_value[0] == path_value[-1] == '"':
            path_value = path_value[1:-1]
        if path_value.startswith("./"):
            path_value = path_value[2:]
        normalized_path = Path(path_value).as_posix().strip("/")
        if normalized_path:
            normalized.add(normalized_path)
    return sorted(normalized)


def is_markdown_path(path_value: str) -> bool:
    return path_value.endswith(".md")


def is_excluded_path(path_value: str) -> bool:
    return path_value in SKIP_EXACT_PATHS or any(path_value.startswith(prefix) for prefix in SKIP_PREFIXES)


def discover_markdown_fallback(project_root: Path) -> list[str]:
    discovered: list[str] = []
    for current_root, dirs, files in os.walk(project_root):
        dirs[:] = [directory for directory in dirs if directory not in FALLBACK_IGNORE_DIRECTORIES]
        root_path = Path(current_root)
        for file_name in files:
            if not file_name.endswith(".md"):
                continue
            relative_path = (root_path / file_name).relative_to(project_root).as_posix()
            discovered.append(relative_path)
    return sorted(set(discovered))


def discover_git_tracked_markdown(project_root: Path) -> tuple[list[str], str]:
    command = ["git", "-C", str(project_root), "-c", "core.quotePath=false", "ls-files", "-z", "--", "*.md"]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        return discover_markdown_fallback(project_root), "filesystem-fallback"
    return normalize_relative_paths([item for item in completed.stdout.split("\0") if item]), "git-ls-files"


def discover_candidate_files(project_root: Path, paths: list[str] | None = None) -> tuple[list[str], str]:
    normalized_paths = normalize_relative_paths(paths)
    if normalized_paths:
        candidates = [
            path_value
            for path_value in normalized_paths
            if is_markdown_path(path_value) and (project_root / path_value).is_file()
        ]
        return sorted(set(candidates)), "path-args"

    tracked_markdown, discovery_mode = discover_git_tracked_markdown(project_root)
    existing_files = [path_value for path_value in tracked_markdown if (project_root / path_value).is_file()]
    return existing_files, discovery_mode


def evaluate_file(path_value: str, project_root: Path) -> dict[str, Any]:
    if is_excluded_path(path_value):
        return {
            "path": path_value,
            "passed": True,
            "mode": "excluded",
            "message": "Excluded from markdown governance boundary-note requirement",
        }

    file_path = project_root / path_value
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except OSError as exc:
        return {
            "path": path_value,
            "passed": False,
            "mode": "read-error",
            "message": f"Unable to read file: {exc}",
            "fix_hint": build_fix_hint(path_value, "read-error"),
        }

    banned_hits = [phrase for phrase in BANNED_PHRASES if phrase in content]
    has_boundary_note = bool(BOUNDARY_NOTE_PATTERN.search(content))

    if banned_hits and not has_boundary_note:
        return {
            "path": path_value,
            "passed": False,
            "mode": "missing-boundary-note-and-banned-phrases",
            "message": "Missing governance boundary note and contains banned ambiguous phrases",
            "banned_phrases": banned_hits,
            "fix_hint": build_fix_hint(path_value, "missing-boundary-note-and-banned-phrases"),
        }

    if banned_hits:
        return {
            "path": path_value,
            "passed": False,
            "mode": "banned-phrases",
            "message": "Contains banned ambiguous phrases; reference canonical sources explicitly",
            "banned_phrases": banned_hits,
            "fix_hint": build_fix_hint(path_value, "banned-phrases"),
        }

    if not has_boundary_note:
        return {
            "path": path_value,
            "passed": False,
            "mode": "missing-boundary-note",
            "message": "Missing governance boundary note",
            "fix_hint": build_fix_hint(path_value, "missing-boundary-note"),
        }

    return {
        "path": path_value,
        "passed": True,
        "mode": "pass",
        "message": "Boundary note present and no banned ambiguous phrases detected",
    }


def build_report(project_root: Path, paths: list[str] | None = None) -> dict[str, Any]:
    candidate_files, discovery_mode = discover_candidate_files(project_root, paths)
    results: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    for path_value in candidate_files:
        result = evaluate_file(path_value, project_root)
        results.append(result)
        if not result["passed"]:
            errors.append(
                {
                    "path": path_value,
                    "rule_id": RULE_ID,
                    "message": result["message"],
                    "mode": result["mode"],
                    "banned_phrases": result.get("banned_phrases", []),
                    "fix_hint": result.get("fix_hint", ""),
                }
            )

    return {
        "project_root": str(project_root),
        "paths": normalize_relative_paths(paths),
        "checked_files": len(candidate_files),
        "results": results,
        "errors": errors,
        "summary": {
            "errors": len(errors),
            "checked_files": len(candidate_files),
        },
        "discovery_mode": discovery_mode,
        "banned_phrases": list(BANNED_PHRASES),
        "skip_exact_paths": sorted(SKIP_EXACT_PATHS),
        "skip_prefixes": list(SKIP_PREFIXES),
    }


def print_report(report: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    print("Markdown Governance Gate")
    print("========================")
    print(f"checked_files: {report['checked_files']}")
    print(f"errors: {report['summary']['errors']}")
    print(f"discovery_mode: {report['discovery_mode']}")

    if not report["results"]:
        print("\nNo markdown files detected for governance validation.")
        return

    if not report["errors"]:
        print("\nNo markdown governance violations detected.")
        return

    print("\nViolations:")
    for item in report["errors"]:
        banned_suffix = f" | banned_phrases={item['banned_phrases']}" if item["banned_phrases"] else ""
        hint_suffix = f" | fix_hint={item['fix_hint']}" if item["fix_hint"] else ""
        print(f"  - {item['path']}: {item['mode']} — {item['message']}{banned_suffix}{hint_suffix}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate markdown governance boundary notes and ban ambiguous source-of-truth phrasing"
    )
    parser.add_argument("filenames", nargs="*")
    parser.add_argument("--root-dir", default=".")
    parser.add_argument("--path", action="append")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    merged_paths = [*(args.path or []), *args.filenames]
    report = build_report(Path(args.root_dir).resolve(), merged_paths or None)
    print_report(report, args.format)
    return 1 if report["summary"]["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
