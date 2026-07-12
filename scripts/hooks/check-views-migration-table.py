#!/usr/bin/env python3
"""Pre-commit hook: block new Vue pages under web/frontend/src/views
unless they are declared in the restructure migration table.

Migration table source:
  openspec/changes/restructure-frontend-directory/tasks.md
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TASKS_MD = PROJECT_ROOT / "openspec/changes/restructure-frontend-directory/tasks.md"
VIEWS_PREFIX = "web/frontend/src/views/"


def run_git_diff_cached_added() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=A"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    files = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return [f for f in files if f.startswith(VIEWS_PREFIX) and f.endswith(".vue")]


def normalize_to_src_views(path: str) -> str:
    trimmed = path.strip().lstrip("./")
    if trimmed.startswith("src/views/"):
        return trimmed
    if trimmed.startswith("views/"):
        return f"src/{trimmed}"
    return f"src/views/{trimmed.lstrip('/')}"


def load_allowed_paths() -> set[str]:
    if not TASKS_MD.exists():
        raise FileNotFoundError(f"Missing migration table: {TASKS_MD}")

    content = TASKS_MD.read_text(encoding="utf-8")
    allowed: set[str] = set()

    # Parse movement items: Move `source` → `target`
    move_pattern = re.compile(r"Move\s+`([^`]+)`\s+→\s+`([^`]+)`")
    for source, target in move_pattern.findall(content):
        if source.endswith(".vue"):
            allowed.add(normalize_to_src_views(source))
        if target.endswith(".vue"):
            allowed.add(normalize_to_src_views(target))

    # Parse explicit .vue references (retentions/checks) under src/views
    code_path_pattern = re.compile(r"`([^`]+\.vue)`")
    for path in code_path_pattern.findall(content):
        candidate = normalize_to_src_views(path)
        if candidate.startswith("src/views/"):
            allowed.add(candidate)

    return allowed


def main() -> int:
    try:
        staged_new_views = run_git_diff_cached_added()
        if not staged_new_views:
            print("[views-migration-gate] No new src/views/*.vue files staged. Pass.")
            return 0

        allowed = load_allowed_paths()
        violations: list[str] = []

        for staged_path in staged_new_views:
            relative_to_frontend = staged_path.replace("web/frontend/", "", 1)
            if relative_to_frontend not in allowed:
                violations.append(staged_path)

        if not violations:
            print("[views-migration-gate] All newly added view files are declared in migration table. Pass.")
            return 0

        print("[views-migration-gate] BLOCKED: Found new view files not in migration table:")
        for path in violations:
            print(f"  - {path}")

        print("\nFix:")
        print("1) Add the file path into migration move items in:")
        print(f"   {TASKS_MD}")
        print("2) Re-stage and commit.")
        return 1
    except subprocess.CalledProcessError as error:
        print(f"[views-migration-gate] Failed to inspect staged files: {error}")
        return 2
    except FileNotFoundError as error:
        print(f"[views-migration-gate] {error}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
