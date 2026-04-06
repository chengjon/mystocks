#!/usr/bin/env python3
"""Validate required structural debt fields in governance task markdown files."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_REPORTS_DIR = PROJECT_ROOT / "reports" / "governance"
TASK_FILE_GLOBS = ("*.TASK.md", "*.TASK-REPORT.md")

STRUCTURAL_DEBT_TOKENS = (
    "cleanup",
    "legacy",
    "backup",
    "shim",
    "truth",
    "prototype",
    "historical-reference",
    "active-reference-tail",
    "design-report",
    "re-export",
    "retire",
    "sunset",
    "deprecated",
    ".backup",
    ".broken",
    ".old",
    ".new",
)

METADATA_PREFIXES = (
    "- issue title:",
    "- objective:",
)

SECTION_PATTERNS: dict[str, re.Pattern[str]] = {
    "Structural Debt Disclosure": re.compile(r"^#{2,6}\s+Structural Debt Disclosure\s*$", re.MULTILINE),
    "Cleanup / Removal Decision": re.compile(r"^#{2,6}\s+Cleanup / Removal Decision\s*$", re.MULTILINE),
    "Temporary / Compatibility Asset Ledger": re.compile(
        r"^#{2,6}\s+Temporary / Compatibility Asset Ledger(?: Delta)?\s*$",
        re.MULTILINE,
    ),
    "Metrics Lens": re.compile(r"^#{2,6}\s+Metrics Lens\s*$", re.MULTILINE),
}

FIELD_PATTERNS: dict[str, re.Pattern[str]] = {
    "canonical_source": re.compile(r"^\s*-\s+canonical_source:\s*", re.MULTILINE),
    "compatibility_surface": re.compile(r"^\s*-\s+compatibility_surface:\s*", re.MULTILINE),
    "callers_or_consumers": re.compile(r"^\s*-\s+callers_or_consumers:\s*", re.MULTILINE),
    "verification_command": re.compile(r"^\s*-\s+verification_command:\s*", re.MULTILINE),
    "exit_condition": re.compile(r"^\s*-\s+exit_condition:\s*", re.MULTILINE),
    "code_path_verdict": re.compile(r"^\s*-\s+code_path_verdict:\s*", re.MULTILINE),
    "function_tree_verdict": re.compile(r"^\s*-\s+function_tree_verdict:\s*", re.MULTILINE),
    "removal_basis": re.compile(r"^\s*-\s+removal_basis:\s*", re.MULTILINE),
    "keep_reason": re.compile(r"^\s*-\s+keep_reason:\s*", re.MULTILINE),
}

ASSET_LEDGER_HEADER = (
    "| path | type | owner | introduced_by | reason | exit_condition | planned_removal_milestone | "
    "target_removal_date | current_status |"
)
METRICS_LENS_HEADER = "| metric | measured | baseline | inferred | target | source_or_command |"
INTRODUCED_BY_REQUIRED_TOKENS = ("issue_or_task=", "created_at=")


@dataclass(frozen=True)
class MarkdownViolation:
    path: str
    message: str


def iter_asset_ledger_rows(text: str) -> Iterable[list[str]]:
    lines = text.splitlines()

    for index, line in enumerate(lines):
        if line.strip() != ASSET_LEDGER_HEADER:
            continue

        cursor = index + 2
        while cursor < len(lines):
            row = lines[cursor].strip()
            if not row.startswith("|"):
                break

            cells = [cell.strip() for cell in row.strip("|").split("|")]
            if any(cell.strip("- ") for cell in cells):
                yield cells

            cursor += 1


def normalize_cell(value: str) -> str:
    return value.strip().strip("`")


def iter_target_files(paths: Sequence[Path] | None = None) -> list[Path]:
    if paths:
        return sorted(path.resolve() for path in paths)

    collected: list[Path] = []
    for pattern in TASK_FILE_GLOBS:
        collected.extend(DEFAULT_REPORTS_DIR.glob(pattern))
    return sorted(path.resolve() for path in collected)


def is_structural_debt_governance_file(path: Path, text: str) -> bool:
    normalized_name = path.name.lower()
    normalized_text = text.lower()

    if "structural debt disclosure" in normalized_text:
        return True

    metadata_only = "\n".join(
        line.strip()
        for line in normalized_text.splitlines()
        if line.strip().startswith(METADATA_PREFIXES)
    )

    return any(token in normalized_name or token in metadata_only for token in STRUCTURAL_DEBT_TOKENS)


def detect_structural_debt_markdown_violations(
    paths: Iterable[Path],
    *,
    project_root: Path = PROJECT_ROOT,
) -> list[MarkdownViolation]:
    violations: list[MarkdownViolation] = []

    for path in paths:
        text = path.read_text(encoding="utf-8")
        if not is_structural_debt_governance_file(path, text):
            continue

        rel_path = path.resolve().relative_to(project_root.resolve()).as_posix()

        for name, pattern in SECTION_PATTERNS.items():
            if not pattern.search(text):
                violations.append(MarkdownViolation(path=rel_path, message=f"missing section: {name}"))

        for field_name, pattern in FIELD_PATTERNS.items():
            if not pattern.search(text):
                violations.append(MarkdownViolation(path=rel_path, message=f"missing field: {field_name}"))

        if ASSET_LEDGER_HEADER not in text:
            violations.append(
                MarkdownViolation(
                    path=rel_path,
                    message=(
                        "missing asset ledger header: "
                        "path/type/owner/introduced_by/reason/exit_condition/"
                        "planned_removal_milestone/target_removal_date/current_status"
                    ),
                )
            )
        else:
            for row in iter_asset_ledger_rows(text):
                if len(row) != 9:
                    violations.append(
                        MarkdownViolation(
                            path=rel_path,
                            message="asset ledger row must contain 9 columns including planned_removal_milestone",
                        )
                    )
                    continue

                introduced_by = normalize_cell(row[3])
                planned_removal_milestone = normalize_cell(row[6])

                if introduced_by != "N/A" and not all(token in introduced_by for token in INTRODUCED_BY_REQUIRED_TOKENS):
                    violations.append(
                        MarkdownViolation(
                            path=rel_path,
                            message="asset ledger introduced_by must include issue_or_task=...; created_at=...",
                        )
                    )

                if not planned_removal_milestone:
                    violations.append(
                        MarkdownViolation(
                            path=rel_path,
                            message="asset ledger planned_removal_milestone must not be empty",
                        )
                    )

        if METRICS_LENS_HEADER not in text:
            violations.append(
                MarkdownViolation(
                    path=rel_path,
                    message="missing metrics lens header: metric/measured/baseline/inferred/target/source_or_command",
                )
            )

    return violations


def build_report(paths: Sequence[Path] | None = None) -> dict:
    target_files = iter_target_files(paths)
    structural_files = [
        path
        for path in target_files
        if is_structural_debt_governance_file(path, path.read_text(encoding="utf-8"))
    ]
    violations = detect_structural_debt_markdown_violations(target_files)

    return {
        "checked_files": len(target_files),
        "structural_files": len(structural_files),
        "errors": [asdict(item) for item in violations],
        "summary": {
            "checked_files": len(target_files),
            "structural_files": len(structural_files),
            "errors": len(violations),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate required structural debt fields in governance markdown files")
    parser.add_argument("--path", action="append", default=[], help="Limit validation to specific governance markdown path")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = [Path(item) for item in args.path] or None
    report = build_report(paths)

    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        summary = report["summary"]
        print(
            f"Governance markdown guard: checked_files={summary['checked_files']} "
            f"structural_files={summary['structural_files']} errors={summary['errors']}"
        )
        for item in report["errors"]:
            print(f"- {item['path']}: {item['message']}")

    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
