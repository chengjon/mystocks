#!/usr/bin/env python3
"""Validate hardcoding exceptions schema and expiration."""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

REQUIRED_FIELDS = (
    "id",
    "rule_id",
    "severity",
    "file",
    "line",
    "reason",
    "owner",
    "created_at",
    "due_date",
    "mitigation",
)
VALID_SEVERITY = {"P0", "P1", "P2", "P3"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate hardcoding exception registry.")
    parser.add_argument(
        "--file",
        default="config/security/hardcoding_exceptions.yml",
        help="Path to hardcoding exceptions yaml file.",
    )
    return parser.parse_args()


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError("YAML root must be a mapping.")
    return data


def validate_item(item: dict[str, Any], idx: int, today: date) -> tuple[list[str], bool]:
    errors: list[str] = []
    expired = False

    for field in REQUIRED_FIELDS:
        if field not in item:
            errors.append(f"[{idx}] missing field: {field}")

    if errors:
        return errors, expired

    severity = str(item["severity"]).upper()
    if severity not in VALID_SEVERITY:
        errors.append(f"[{idx}] invalid severity: {severity}")

    try:
        int(item["line"])
    except (TypeError, ValueError):
        errors.append(f"[{idx}] invalid line: {item['line']}")

    for field_name in ("created_at", "due_date"):
        try:
            datetime.strptime(str(item[field_name]), "%Y-%m-%d")
        except ValueError:
            errors.append(f"[{idx}] invalid {field_name} format (expected YYYY-MM-DD): {item[field_name]}")

    if not errors:
        due = datetime.strptime(str(item["due_date"]), "%Y-%m-%d").date()
        if due < today:
            expired = True
    return errors, expired


def main() -> int:
    args = parse_args()
    file_path = Path(args.file)
    data = load_yaml(file_path)
    exceptions = data.get("exceptions", [])
    if not isinstance(exceptions, list):
        print("ERROR: 'exceptions' must be a list.", file=sys.stderr)
        return 2

    today = date.today()
    errors: list[str] = []
    expired_count = 0
    for idx, raw in enumerate(exceptions, start=1):
        if not isinstance(raw, dict):
            errors.append(f"[{idx}] exception item must be a mapping")
            continue
        item_errors, expired = validate_item(raw, idx, today)
        errors.extend(item_errors)
        expired_count += 1 if expired else 0

    if errors:
        print("Hardcoding exceptions validation failed:")
        for err in errors:
            print(f"- {err}")
        return 2

    if expired_count > 0:
        print(f"Hardcoding exceptions validation failed: {expired_count} expired exception(s).")
        return 1

    print(f"Hardcoding exceptions validation passed ({len(exceptions)} active entries).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
