#!/usr/bin/env python3
"""Canonical cleanup planner for repository hygiene.

Default mode is dry-run. Destructive behavior requires ``--execute``.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path


TEMP_DIRECTORIES = ("temp", "tmp", "test_temp", "opencodetmp")
BACKUP_PATTERNS = ("*.bak", "*.backup", "*.orig", "*~")
ROOT_BACKUPS_DIR = "backups"
IGNORED_DIRECTORIES = {".git", ".venv", "node_modules", "var"}


def should_skip_path(path: Path, root_dir: Path) -> bool:
    try:
        relative_parts = path.relative_to(root_dir).parts
    except ValueError:
        return True

    if relative_parts and relative_parts[0] == ROOT_BACKUPS_DIR:
        return True

    return any(part in IGNORED_DIRECTORIES for part in relative_parts)


def iter_backup_files(root_dir: Path) -> list[Path]:
    backup_files: list[Path] = []
    for pattern in BACKUP_PATTERNS:
        for candidate in root_dir.rglob(pattern):
            if not candidate.is_file():
                continue
            if should_skip_path(candidate, root_dir):
                continue
            backup_files.append(candidate)
    unique_candidates = {candidate.resolve(): candidate for candidate in backup_files}
    return sorted(unique_candidates.values(), key=lambda item: item.as_posix())


def build_cleanup_plan(root_dir: str | Path, *, backup_stamp: str) -> dict[str, object]:
    project_root = Path(root_dir).resolve()
    actions: list[dict[str, object]] = []

    for directory_name in TEMP_DIRECTORIES:
        candidate = project_root / directory_name
        if candidate.exists():
            actions.append(
                {
                    "type": "remove_dir",
                    "path": candidate.relative_to(project_root).as_posix(),
                    "target": None,
                    "reason": "temporary_directory",
                },
            )

    for cache_dir in sorted(project_root.rglob("__pycache__")):
        if not cache_dir.is_dir():
            continue
        if should_skip_path(cache_dir, project_root):
            continue
        actions.append(
            {
                "type": "remove_dir",
                "path": cache_dir.relative_to(project_root).as_posix(),
                "target": None,
                "reason": "python_cache",
            },
        )

    coverage_dir = project_root / "htmlcov"
    if coverage_dir.exists():
        actions.append(
            {
                "type": "remove_dir",
                "path": coverage_dir.relative_to(project_root).as_posix(),
                "target": None,
                "reason": "coverage_html",
            },
        )

    root_backups_dir = project_root / ROOT_BACKUPS_DIR
    if root_backups_dir.exists():
        target = project_root / "var" / "backups" / backup_stamp / "legacy-root-backups"
        actions.append(
            {
                "type": "archive_dir",
                "path": root_backups_dir.relative_to(project_root).as_posix(),
                "target": target.relative_to(project_root).as_posix(),
                "reason": "legacy_root_backups",
            },
        )

    for backup_file in iter_backup_files(project_root):
        target = project_root / "var" / "backups" / backup_stamp / backup_file.name
        actions.append(
            {
                "type": "archive_file",
                "path": backup_file.relative_to(project_root).as_posix(),
                "target": target.relative_to(project_root).as_posix(),
                "reason": "backup_artifact",
            },
        )

    actions.sort(key=lambda item: (str(item["type"]), str(item["path"])))
    remove_dirs = sum(1 for item in actions if item["type"] == "remove_dir")
    archive_files = sum(1 for item in actions if item["type"] in {"archive_file", "archive_dir"})

    return {
        "project_root": str(project_root),
        "dry_run": True,
        "backup_stamp": backup_stamp,
        "summary": {
            "total_actions": len(actions),
            "remove_dirs": remove_dirs,
            "archive_files": archive_files,
        },
        "actions": actions,
    }


def execute_plan(plan: dict[str, object]) -> None:
    project_root = Path(str(plan["project_root"]))
    for action in plan["actions"]:
        source_path = project_root / str(action["path"])
        if action["type"] == "remove_dir":
            if source_path.exists():
                shutil.rmtree(source_path)
            continue

        if action["type"] == "archive_file":
            target_path = project_root / str(action["target"])
            target_path.parent.mkdir(parents=True, exist_ok=True)
            if source_path.exists():
                shutil.move(str(source_path), str(target_path))
            continue

        if action["type"] == "archive_dir":
            target_path = project_root / str(action["target"])
            target_path.parent.mkdir(parents=True, exist_ok=True)
            if source_path.exists():
                shutil.move(str(source_path), str(target_path))


def print_report(plan: dict[str, object], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return

    mode = "DRY-RUN" if plan["dry_run"] else "EXECUTE"
    print("Auto cleanup report")
    print("===================")
    print(f"mode: {mode}")
    print(f"project_root: {plan['project_root']}")
    print(f"backup_stamp: {plan['backup_stamp']}")
    print(f"total_actions: {plan['summary']['total_actions']}")
    print(f"remove_dirs: {plan['summary']['remove_dirs']}")
    print(f"archive_files: {plan['summary']['archive_files']}")

    if not plan["actions"]:
        print("\nNo cleanup actions detected.")
        return

    print("\nPlanned actions:")
    for action in plan["actions"]:
        target = f" -> {action['target']}" if action["target"] else ""
        print(f"  - {action['type']}: {action['path']}{target} ({action['reason']})")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Canonical repository auto cleanup planner")
    parser.add_argument("--root-dir", default=".")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--backup-stamp", default=datetime.utcnow().strftime("%Y%m%d"))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    plan = build_cleanup_plan(args.root_dir, backup_stamp=args.backup_stamp)
    plan["dry_run"] = not args.execute

    if args.execute:
        execute_plan(plan)

    print_report(plan, args.format)
    return 0


if __name__ == "__main__":
    sys.exit(main())
