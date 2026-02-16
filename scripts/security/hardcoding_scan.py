#!/usr/bin/env python3
"""Tiered hardcoding scanner for MyStocks runtime code paths."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, Iterable

import yaml

SEVERITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
DEFAULT_RULES_PATH = "config/security/hardcoding-rules.yml"
DEFAULT_EXCEPTIONS_PATH = "config/security/hardcoding_exceptions.yml"


@dataclass(frozen=True)
class Rule:
    rule_id: str
    severity: str
    description: str
    pattern: re.Pattern[str]
    include_extensions: tuple[str, ...]
    excludes: tuple[re.Pattern[str], ...]


@dataclass(frozen=True)
class Hit:
    severity: str
    rule_id: str
    description: str
    file: str
    line: int
    column: int
    snippet: str


@dataclass(frozen=True)
class ExceptionItem:
    exception_id: str
    rule_id: str
    severity: str
    file: str
    line: int
    due_date: date

    @property
    def key(self) -> tuple[str, str, int]:
        return (self.rule_id, self.file, self.line)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan hardcoding risks by severity tier.")
    parser.add_argument("--scope", default="runtime", help="Scope name defined in rules file.")
    parser.add_argument(
        "--format",
        choices=("json", "md"),
        default="json",
        help="Output format.",
    )
    parser.add_argument("--out", help="Output path. If omitted, print to stdout.")
    parser.add_argument(
        "--severity",
        help="Comma-separated severities, e.g. P0,P1.",
    )
    parser.add_argument(
        "--path",
        action="append",
        default=[],
        help="Optional path override; can be used multiple times.",
    )
    parser.add_argument("--rules", default=DEFAULT_RULES_PATH, help="Rules YAML path.")
    parser.add_argument("--exceptions", default=DEFAULT_EXCEPTIONS_PATH, help="Exceptions YAML path.")
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root path for relative file output.",
    )
    parser.add_argument(
        "--max-file-size-kb",
        type=int,
        default=1024,
        help="Skip files larger than this size in KB.",
    )
    return parser.parse_args()


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"YAML file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return data


def compile_rules(raw_rules: list[dict[str, Any]]) -> list[Rule]:
    compiled: list[Rule] = []
    for raw in raw_rules:
        rule_id = str(raw.get("id", "")).strip()
        severity = str(raw.get("severity", "")).strip().upper()
        regex = str(raw.get("regex", "")).strip()
        description = str(raw.get("description", "")).strip() or rule_id
        if not rule_id or not regex or severity not in SEVERITY_ORDER:
            raise ValueError(f"Invalid rule: {raw}")
        try:
            pattern = re.compile(regex)
        except re.error as exc:
            raise ValueError(f"Invalid regex for rule {rule_id}: {exc}") from exc

        excludes = tuple(re.compile(str(item)) for item in raw.get("excludes", []))
        include_extensions = tuple(str(ext) for ext in raw.get("include_extensions", []))
        compiled.append(
            Rule(
                rule_id=rule_id,
                severity=severity,
                description=description,
                pattern=pattern,
                include_extensions=include_extensions,
                excludes=excludes,
            )
        )
    return compiled


def normalize_relpath(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def match_any(patterns: Iterable[str], rel_path: str) -> bool:
    normalized = rel_path.lstrip("./")
    for pattern in patterns:
        candidate = pattern.lstrip("./")
        if fnmatch(normalized, candidate):
            return True
        if normalized == candidate:
            return True
        if normalized.startswith(candidate.rstrip("/") + "/"):
            return True
    return False


def collect_target_files(
    repo_root: Path,
    includes: list[str],
    excludes: list[str],
    max_file_size_kb: int,
) -> list[Path]:
    files: list[Path] = []
    seen: set[str] = set()
    for raw_target in includes:
        target = (repo_root / raw_target).resolve()
        if not target.exists():
            continue
        candidates = [target] if target.is_file() else [p for p in target.rglob("*") if p.is_file()]
        for file_path in candidates:
            try:
                rel = normalize_relpath(file_path, repo_root)
            except ValueError:
                continue
            if match_any(excludes, rel):
                continue
            if file_path.stat().st_size > max_file_size_kb * 1024:
                continue
            if rel in seen:
                continue
            seen.add(rel)
            files.append(file_path)
    return sorted(files)


def load_exceptions(path: Path, repo_root: Path) -> tuple[dict[tuple[str, str, int], ExceptionItem], list[ExceptionItem]]:
    if not path.exists():
        return {}, []
    data = load_yaml(path)
    entries = data.get("exceptions", [])
    if not isinstance(entries, list):
        raise ValueError(f"'exceptions' must be a list in {path}")

    active: dict[tuple[str, str, int], ExceptionItem] = {}
    expired: list[ExceptionItem] = []
    today = date.today()
    for raw in entries:
        try:
            item = ExceptionItem(
                exception_id=str(raw["id"]),
                rule_id=str(raw["rule_id"]),
                severity=str(raw["severity"]).upper(),
                file=str(Path(str(raw["file"])).as_posix()),
                line=int(raw["line"]),
                due_date=datetime.strptime(str(raw["due_date"]), "%Y-%m-%d").date(),
            )
        except (KeyError, ValueError, TypeError) as exc:
            raise ValueError(f"Invalid exception item: {raw}") from exc
        if item.due_date < today:
            expired.append(item)
            continue
        active[item.key] = item
    return active, expired


def scan_file(file_path: Path, rel_path: str, rules: list[Rule], severity_filter: set[str]) -> list[Hit]:
    try:
        content = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []

    hits: list[Hit] = []
    lines = content.splitlines()
    ext = file_path.suffix.lower()
    for idx, line in enumerate(lines, start=1):
        for rule in rules:
            if rule.severity not in severity_filter:
                continue
            if rule.include_extensions and ext not in rule.include_extensions:
                continue
            if any(ex.search(line) for ex in rule.excludes):
                continue
            match = rule.pattern.search(line)
            if not match:
                continue
            snippet = line.strip()
            if len(snippet) > 220:
                snippet = snippet[:217] + "..."
            hits.append(
                Hit(
                    severity=rule.severity,
                    rule_id=rule.rule_id,
                    description=rule.description,
                    file=rel_path,
                    line=idx,
                    column=match.start() + 1,
                    snippet=snippet,
                )
            )
    return hits


def build_report(
    repo_root: Path,
    scope: str,
    files_scanned: int,
    included_targets: list[str],
    hits: list[Hit],
    active_exceptions: int,
    expired_exceptions: list[ExceptionItem],
) -> dict[str, Any]:
    by_severity = Counter(hit.severity for hit in hits)
    by_rule = Counter(hit.rule_id for hit in hits)
    by_file = Counter(hit.file for hit in hits)

    ordered_hits = sorted(
        hits,
        key=lambda h: (SEVERITY_ORDER.get(h.severity, 99), h.file, h.line, h.column),
    )
    hit_items = [
        {
            "severity": h.severity,
            "rule_id": h.rule_id,
            "description": h.description,
            "file": h.file,
            "line": h.line,
            "column": h.column,
            "snippet": h.snippet,
        }
        for h in ordered_hits
    ]

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "scope": scope,
        "targets": included_targets,
        "files_scanned": files_scanned,
        "stats": {
            "total_hits": len(hits),
            "by_severity": dict(sorted(by_severity.items(), key=lambda x: SEVERITY_ORDER.get(x[0], 99))),
            "by_rule": dict(by_rule.most_common()),
            "top_files": [{"file": file, "count": count} for file, count in by_file.most_common(20)],
            "active_exceptions": active_exceptions,
            "expired_exceptions": len(expired_exceptions),
        },
        "expired_exceptions": [
            {
                "id": item.exception_id,
                "rule_id": item.rule_id,
                "file": item.file,
                "line": item.line,
                "due_date": item.due_date.isoformat(),
            }
            for item in sorted(expired_exceptions, key=lambda x: (x.file, x.line))
        ],
        "hits": hit_items,
    }


def render_markdown(report: dict[str, Any]) -> str:
    stats = report["stats"]
    lines: list[str] = []
    lines.append("# Hardcoding Baseline Report")
    lines.append("")
    lines.append(f"- Generated: `{report['generated_at']}`")
    lines.append(f"- Scope: `{report['scope']}`")
    lines.append(f"- Files scanned: `{report['files_scanned']}`")
    lines.append(f"- Total hits: `{stats['total_hits']}`")
    lines.append(f"- Active exceptions: `{stats['active_exceptions']}`")
    lines.append(f"- Expired exceptions: `{stats['expired_exceptions']}`")
    lines.append("")
    lines.append("## Severity Summary")
    lines.append("")
    lines.append("| Severity | Count |")
    lines.append("|---|---:|")
    for severity in ("P0", "P1", "P2", "P3"):
        lines.append(f"| {severity} | {stats['by_severity'].get(severity, 0)} |")
    lines.append("")
    lines.append("## Top Files")
    lines.append("")
    lines.append("| File | Hits |")
    lines.append("|---|---:|")
    for item in stats["top_files"][:20]:
        lines.append(f"| `{item['file']}` | {item['count']} |")
    lines.append("")
    lines.append("## Top Findings")
    lines.append("")
    lines.append("| Severity | Rule | File:Line | Snippet |")
    lines.append("|---|---|---|---|")
    for finding in report["hits"][:200]:
        snippet = finding["snippet"].replace("|", "\\|").replace("`", "\\`")
        lines.append(
            f"| {finding['severity']} | `{finding['rule_id']}` | "
            f"`{finding['file']}:{finding['line']}` | `{snippet}` |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    rules_data = load_yaml((repo_root / args.rules).resolve())
    rules = compile_rules(rules_data.get("rules", []))
    if not rules:
        raise ValueError("No rules configured.")

    scopes = rules_data.get("scopes", {})
    if args.scope not in scopes and not args.path:
        raise ValueError(f"Scope '{args.scope}' not found in rules file.")

    if args.path:
        includes = args.path
        excludes = scopes.get(args.scope, {}).get("exclude", [])
    else:
        include_raw = scopes.get(args.scope, {}).get("include", [])
        excludes = scopes.get(args.scope, {}).get("exclude", [])
        includes = list(include_raw)

    if args.severity:
        requested = {part.strip().upper() for part in args.severity.split(",") if part.strip()}
    else:
        requested = set(SEVERITY_ORDER.keys())
    unknown = requested - set(SEVERITY_ORDER.keys())
    if unknown:
        raise ValueError(f"Unknown severities: {sorted(unknown)}")

    files = collect_target_files(
        repo_root=repo_root,
        includes=includes,
        excludes=excludes,
        max_file_size_kb=args.max_file_size_kb,
    )

    active_exceptions, expired_exceptions = load_exceptions((repo_root / args.exceptions).resolve(), repo_root)
    findings: list[Hit] = []
    for path in files:
        rel = normalize_relpath(path, repo_root)
        hits = scan_file(path, rel, rules, requested)
        for hit in hits:
            if (hit.rule_id, hit.file, hit.line) in active_exceptions:
                continue
            findings.append(hit)

    report = build_report(
        repo_root=repo_root,
        scope=args.scope,
        files_scanned=len(files),
        included_targets=includes,
        hits=findings,
        active_exceptions=len(active_exceptions),
        expired_exceptions=expired_exceptions,
    )

    output = json.dumps(report, ensure_ascii=False, indent=2) if args.format == "json" else render_markdown(report)
    if args.out:
        out_path = (repo_root / args.out).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output + ("\n" if not output.endswith("\n") else ""), encoding="utf-8")
    else:
        print(output)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[hardcoding-scan] ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
