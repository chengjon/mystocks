from __future__ import annotations

import argparse
import json
from fnmatch import fnmatch
from pathlib import Path
from typing import Any


RULE_PATTERNS: dict[str, tuple[str, ...]] = {
    "app-root": ("web/frontend/src/App.vue",),
    "router": ("web/frontend/src/router/**",),
    "layout": ("web/frontend/src/layout/**", "web/frontend/src/layouts/**"),
}


def normalize_relative_paths(paths: list[str] | None) -> list[str]:
    if not paths:
        return []

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


def matched_rules(path_value: str) -> list[str]:
    matches: list[str] = []
    for rule_name, patterns in RULE_PATTERNS.items():
        if any(fnmatch(path_value, pattern) for pattern in patterns):
            matches.append(rule_name)
    return matches


def build_report(paths: list[str] | None = None) -> dict[str, Any]:
    normalized_paths = normalize_relative_paths(paths)
    matches: list[dict[str, Any]] = []

    for path_value in normalized_paths:
        rules = matched_rules(path_value)
        if not rules:
            continue
        matches.append({"path": path_value, "rules": rules})

    return {
        "paths": normalized_paths,
        "checked_paths": len(normalized_paths),
        "gate_required": bool(matches),
        "matched_paths": matches,
        "rules": {rule_name: list(patterns) for rule_name, patterns in RULE_PATTERNS.items()},
    }


def print_report(report: dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    print("Route/Layout PM2 Gate")
    print("=====================")
    print(f"checked_paths: {report['checked_paths']}")
    print(f"gate_required: {report['gate_required']}")

    if report["matched_paths"]:
        print("\nMatched paths:")
        for item in report["matched_paths"]:
            print(f"  - {item['path']}: {', '.join(item['rules'])}")
    else:
        print("\nNo route/layout/App.vue changes detected.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Detect whether route/layout changes require PM2 E2E gate")
    parser.add_argument("--path", action="append")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    report = build_report(args.path)
    print_report(report, args.format)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
