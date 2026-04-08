#!/usr/bin/env python3
"""Technical debt governance gate utilities (Stage B/C)."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_BASELINE = PROJECT_ROOT / "reports/analysis/tech-debt-baseline.json"

TARGET_EXTENSIONS = {".py", ".ts", ".tsx", ".vue"}
TTL_PATTERNS = [
    re.compile(r"ttl=(\d{4}-\d{2}-\d{2})"),
    re.compile(r"ttl:\s*(\d{4}-\d{2}-\d{2})", re.IGNORECASE),
    re.compile(r"due_date:\s*(\d{4}-\d{2}-\d{2})", re.IGNORECASE),
]

DEBT_MARKER_PATTERN = re.compile(
    r"(@ts-ignore|@ts-expect-error|@ts-nocheck|\sas any\b|#\s*type:\s*ignore|@pytest\.mark\.skip|@pytest\.mark\.xfail|pytest\.skip\(|pytest\.xfail\(|TODO|FIXME|HACK)",
    re.IGNORECASE,
)

REQUIRED_MARKER_FIELDS = ("owner", "issue", "ttl")


@dataclass(frozen=True)
class MetricRule:
    path: str
    direction: str
    required: bool = True


GATE_METRIC_RULES = (
    MetricRule("frontend_type_errors", "max"),
    MetricRule("frontend_suppressions_count", "max"),
    MetricRule("skip_xfail_count", "max"),
    MetricRule("backend_api_documentation.documented_endpoints", "min", required=False),
    MetricRule("backend_api_documentation.documented_percentage", "min", required=False),
    MetricRule("backend_api_documentation.endpoints_with_examples", "min", required=False),
    MetricRule("backend_api_documentation.example_percentage", "min", required=False),
    MetricRule("backend_api_documentation.endpoints_with_errors", "min", required=False),
    MetricRule("backend_api_documentation.error_response_percentage", "min", required=False),
    MetricRule("backend_api_documentation.total_issues", "max", required=False),
    MetricRule("backend_api_documentation.schema_issue_count", "max", required=False),
    MetricRule("backend_api_documentation.authentication_issue_count", "max", required=False),
    MetricRule("backend_api_documentation.json_success_missing_examples", "max", required=False),
)


@dataclass
class MarkerViolation:
    path: str
    line: int
    message: str


def parse_ttl(text: str) -> date | None:
    for pattern in TTL_PATTERNS:
        match = pattern.search(text)
        if match:
            try:
                return datetime.strptime(match.group(1), "%Y-%m-%d").date()
            except ValueError:
                return None
    return None


def load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_baseline_review_exceptions(path: Path | None) -> dict[str, dict]:
    if path is None:
        return {}

    payload = load_json(path)
    items = payload.get("exceptions", [])
    if not isinstance(items, list):
        raise ValueError("baseline review exceptions must contain an 'exceptions' list")

    exceptions: dict[str, dict] = {}
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("baseline review exception entries must be objects")

        metric_path = item.get("path")
        approved_value = item.get("approved_value")
        if not isinstance(metric_path, str) or not isinstance(approved_value, (int, float)):
            raise ValueError("baseline review exception entries require string 'path' and numeric 'approved_value'")

        for field in ("owner", "issue", "ttl", "reason"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise ValueError(f"baseline review exception '{metric_path}' missing field: {field}")

        exceptions[metric_path] = item
    return exceptions


def get_metric_value(payload: dict, path: str) -> int | float | None:
    current: object = payload
    for segment in path.split("."):
        if not isinstance(current, dict) or segment not in current:
            return None
        current = current[segment]
    return current if isinstance(current, (int, float)) else None


def is_approved_baseline_review_exception(
    path: str,
    proposed_value: int | float,
    review_exceptions: dict[str, dict] | None,
    as_of: date,
) -> bool:
    if not review_exceptions:
        return False

    item = review_exceptions.get(path)
    if not isinstance(item, dict):
        return False

    ttl = parse_ttl(f"ttl={item.get('ttl', '')}")
    approved_value = item.get("approved_value")
    if ttl is None or ttl < as_of or not isinstance(approved_value, (int, float)):
        return False

    return approved_value == proposed_value


def evaluate_no_new_debt(current: dict, baseline: dict) -> list[str]:
    violations: list[str] = []
    for rule in GATE_METRIC_RULES:
        base_value = get_metric_value(baseline, rule.path)
        current_value = get_metric_value(current, rule.path)
        if base_value is None or current_value is None:
            if rule.required:
                violations.append(f"missing numeric metric: {rule.path}")
            continue
        if rule.direction == "max" and current_value > base_value:
            violations.append(f"metric {rule.path} regressed: current={current_value} > baseline={base_value}")
        if rule.direction == "min" and current_value < base_value:
            violations.append(f"metric {rule.path} regressed: current={current_value} < baseline={base_value}")
    return violations


def evaluate_baseline_review(
    previous_baseline: dict,
    proposed_baseline: dict,
    review_exceptions: dict[str, dict] | None = None,
    as_of: date | None = None,
) -> list[str]:
    violations: list[str] = []
    review_date = as_of or date.today()
    for rule in GATE_METRIC_RULES:
        old_value = get_metric_value(previous_baseline, rule.path)
        new_value = get_metric_value(proposed_baseline, rule.path)
        if old_value is None or new_value is None:
            if rule.required:
                violations.append(f"missing numeric metric in baseline review: {rule.path}")
            continue
        if rule.direction == "max" and new_value > old_value:
            if not is_approved_baseline_review_exception(rule.path, new_value, review_exceptions, review_date):
                violations.append(f"baseline metric {rule.path} increased: proposed={new_value} > previous={old_value}")
        if rule.direction == "min" and new_value < old_value:
            if not is_approved_baseline_review_exception(rule.path, new_value, review_exceptions, review_date):
                violations.append(f"baseline metric {rule.path} decreased: proposed={new_value} < previous={old_value}")
    return violations


def git_changed_files(base_sha: str | None) -> set[Path]:
    if not base_sha:
        return set()
    cmd = ["git", "diff", "--name-only", f"{base_sha}...HEAD"]
    proc = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "failed to resolve changed files")

    changed: set[Path] = set()
    for line in proc.stdout.splitlines():
        candidate = PROJECT_ROOT / line.strip()
        if candidate.suffix.lower() in TARGET_EXTENSIONS and candidate.exists() and candidate.is_file():
            changed.add(candidate)
    return changed


def iter_target_files(base_sha: str | None) -> Iterable[Path]:
    if base_sha:
        return sorted(git_changed_files(base_sha))

    all_files: list[Path] = []
    for root in (
        PROJECT_ROOT / "src",
        PROJECT_ROOT / "web/frontend/src",
        PROJECT_ROOT / "web/backend/app",
        PROJECT_ROOT / "tests",
    ):
        if root.exists():
            all_files.extend(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in TARGET_EXTENSIONS)
    return sorted(all_files)


def extract_marker_violations(base_sha: str | None, as_of: date) -> list[MarkerViolation]:
    violations: list[MarkerViolation] = []
    for path in iter_target_files(base_sha):
        rel_path = path.relative_to(PROJECT_ROOT).as_posix()
        text = path.read_text(encoding="utf-8", errors="ignore")
        for index, line in enumerate(text.splitlines(), start=1):
            if not DEBT_MARKER_PATTERN.search(line):
                continue

            lowered = line.lower()
            missing_fields = [field for field in REQUIRED_MARKER_FIELDS if field not in lowered]
            if missing_fields:
                violations.append(
                    MarkerViolation(
                        path=rel_path,
                        line=index,
                        message=f"missing metadata fields: {', '.join(missing_fields)}",
                    )
                )
                continue

            ttl = parse_ttl(line)
            if ttl is None:
                violations.append(MarkerViolation(path=rel_path, line=index, message="invalid or missing ttl date"))
                continue

            if ttl < as_of:
                violations.append(
                    MarkerViolation(
                        path=rel_path,
                        line=index,
                        message=f"expired ttl: {ttl.isoformat()} < {as_of.isoformat()}",
                    )
                )
    return violations


def count_debt_markers(base_sha: str | None) -> int:
    total = 0
    for path in iter_target_files(base_sha):
        text = path.read_text(encoding="utf-8", errors="ignore")
        total += len(DEBT_MARKER_PATTERN.findall(text))
    return total


def count_recent_touches(path: str, since_days: int) -> int:
    cmd = ["git", "log", f"--since={since_days}.days", "--pretty=format:%H", "--", path]
    proc = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return 0
    return len([line for line in proc.stdout.splitlines() if line.strip()])


def collect_large_files(threshold: int) -> list[dict]:
    results: list[dict] = []
    for base in (
        PROJECT_ROOT / "src",
        PROJECT_ROOT / "web/frontend/src",
        PROJECT_ROOT / "web/backend/app",
        PROJECT_ROOT / "tests",
    ):
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in TARGET_EXTENSIONS:
                continue
            lines = len(path.read_text(encoding="utf-8", errors="ignore").splitlines())
            if lines >= threshold:
                results.append(
                    {
                        "path": path.relative_to(PROJECT_ROOT).as_posix(),
                        "lines": lines,
                    }
                )
    return results


def compute_hotspot_scores(large_files: list[dict], touch_counts: dict[str, int], top_n: int) -> list[dict]:
    scored: list[dict] = []
    for item in large_files:
        path = item["path"]
        lines = int(item.get("lines", 0))
        touches = int(touch_counts.get(path, 0))
        score = lines * max(touches, 1)
        scored.append({"path": path, "lines": lines, "touches": touches, "score": score})
    return sorted(scored, key=lambda x: x["score"], reverse=True)[:top_n]


def render_weekly_report(metrics: dict, kpi: dict, hotspots: list[dict], ttl_violations: list[MarkerViolation]) -> str:
    now = datetime.now(timezone.utc).isoformat()
    baseline_doc = metrics.get("baseline", {}).get("backend_api_documentation", {})
    current_doc = metrics.get("current", {}).get("backend_api_documentation", {})
    lines = [
        "# Technical Debt Weekly Governance Report",
        "",
        f"- generated_at: `{now}`",
        "",
        "## 1. Overview",
        f"- new_debt_violations: `{len(kpi.get('no_new_debt_violations', []))}`",
        f"- baseline_type_errors: `{metrics.get('baseline', {}).get('frontend_type_errors', 'N/A')}`",
        f"- current_type_errors: `{metrics.get('current', {}).get('frontend_type_errors', 'N/A')}`",
        f"- ttl_expired_items: `{len(ttl_violations)}`",
        "",
        "## 2. KPI",
        f"- no-new-debt: `{'PASS' if not kpi.get('no_new_debt_violations') else 'FAIL'}`",
        f"- baseline-non-increase: `{'PASS' if not kpi.get('baseline_review_violations') else 'FAIL'}`",
        f"- exception-compliance-rate: `{kpi.get('exception_compliance_rate', 0.0):.2f}`",
        f"- ttl-cleanup-rate: `{kpi.get('ttl_cleanup_rate', 0.0):.2f}`",
        "",
        "## 3. OpenAPI Documentation Debt",
        f"- baseline_json_success_missing_examples: `{baseline_doc.get('json_success_missing_examples', 'N/A')}`",
        f"- current_json_success_missing_examples: `{current_doc.get('json_success_missing_examples', 'N/A')}`",
        f"- baseline_non_json_success_responses: `{baseline_doc.get('non_json_success_responses', 'N/A')}`",
        f"- current_non_json_success_responses: `{current_doc.get('non_json_success_responses', 'N/A')}`",
        "",
        "## 4. Risk Hotspots (Top N)",
    ]

    if hotspots:
        for item in hotspots:
            lines.append(f"- `{item['path']}` | lines={item['lines']} touches={item['touches']} score={item['score']}")
    else:
        lines.append("- no hotspot files detected")

    lines.extend(["", "## 5. Expired Items", ""])
    if ttl_violations:
        for violation in ttl_violations[:30]:
            lines.append(f"- {violation.path}:{violation.line} -> {violation.message}")
    else:
        lines.append("- no expired debt markers")

    lines.extend(
        [
            "",
            "## 6. Actions",
            "- owners should remediate expired markers before merge",
            "- baseline updates are allowed only if metrics are non-increasing",
            "",
        ]
    )
    return "\n".join(lines)


def run_hotspot(args: argparse.Namespace) -> int:
    large_files = collect_large_files(args.threshold)
    touch_counts = {item["path"]: count_recent_touches(item["path"], args.since_days) for item in large_files}
    hotspots = compute_hotspot_scores(large_files=large_files, touch_counts=touch_counts, top_n=args.top_n)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "threshold": args.threshold,
        "since_days": args.since_days,
        "top_n": args.top_n,
        "hotspots": hotspots,
    }
    output = (PROJECT_ROOT / args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[hotspot] report written: {output}")
    return 0


def run_ttl_gate(args: argparse.Namespace) -> int:
    violations = extract_marker_violations(base_sha=args.base_sha, as_of=date.today())
    output = (PROJECT_ROOT / args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "base_sha": args.base_sha,
                "violations": [{"path": item.path, "line": item.line, "message": item.message} for item in violations],
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    if violations:
        print("[ttl-gate] failed, violations detected")
        for item in violations[:50]:
            print(f"- {item.path}:{item.line} {item.message}")
        return 1

    print("[ttl-gate] passed")
    return 0


def run_kpi_gate(args: argparse.Namespace) -> int:
    baseline = load_json((PROJECT_ROOT / args.baseline).resolve())
    current = load_json((PROJECT_ROOT / args.current).resolve())

    no_new_debt_violations = evaluate_no_new_debt(current=current, baseline=baseline)
    baseline_review_violations = evaluate_baseline_review(previous_baseline=baseline, proposed_baseline=current)

    ttl_violations = extract_marker_violations(base_sha=args.base_sha, as_of=date.today())
    total_markers = count_debt_markers(base_sha=args.base_sha)
    expired_markers = len([v for v in ttl_violations if "expired ttl" in v.message])

    exception_compliance_rate = (
        1.0 if total_markers == 0 else max((total_markers - len(ttl_violations)) / total_markers, 0.0)
    )
    ttl_cleanup_rate = 1.0 if expired_markers == 0 else 0.0

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "baseline": baseline,
        "current": current,
        "no_new_debt_violations": no_new_debt_violations,
        "baseline_review_violations": baseline_review_violations,
        "exception_compliance_rate": exception_compliance_rate,
        "ttl_cleanup_rate": ttl_cleanup_rate,
    }

    output = (PROJECT_ROOT / args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    failed = bool(no_new_debt_violations or baseline_review_violations)
    if failed:
        print("[kpi-gate] failed")
        for item in no_new_debt_violations + baseline_review_violations:
            print(f"- {item}")
        return 1

    print("[kpi-gate] passed")
    return 0


def run_weekly_report(args: argparse.Namespace) -> int:
    baseline = load_json((PROJECT_ROOT / args.baseline).resolve())
    current = load_json((PROJECT_ROOT / args.current).resolve())

    large_files = collect_large_files(args.threshold)
    touch_counts = {item["path"]: count_recent_touches(item["path"], args.since_days) for item in large_files}
    hotspots = compute_hotspot_scores(large_files=large_files, touch_counts=touch_counts, top_n=args.top_n)

    no_new_debt_violations = evaluate_no_new_debt(current=current, baseline=baseline)
    baseline_review_violations = evaluate_baseline_review(previous_baseline=baseline, proposed_baseline=current)
    ttl_violations = extract_marker_violations(base_sha=args.base_sha, as_of=date.today())

    kpi = {
        "no_new_debt_violations": no_new_debt_violations,
        "baseline_review_violations": baseline_review_violations,
        "exception_compliance_rate": 1.0 if not ttl_violations else 0.0,
        "ttl_cleanup_rate": 1.0 if not ttl_violations else 0.0,
    }

    content = render_weekly_report(
        metrics={"baseline": baseline, "current": current},
        kpi=kpi,
        hotspots=hotspots,
        ttl_violations=ttl_violations,
    )

    output = (PROJECT_ROOT / args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    print(f"[weekly-report] written: {output}")
    return 0


def run_baseline_review(args: argparse.Namespace) -> int:
    previous = load_json((PROJECT_ROOT / args.previous).resolve())
    proposed = load_json((PROJECT_ROOT / args.proposed).resolve())
    review_exceptions = load_baseline_review_exceptions(
        (PROJECT_ROOT / args.exceptions).resolve() if args.exceptions else None
    )

    violations = evaluate_baseline_review(
        previous_baseline=previous,
        proposed_baseline=proposed,
        review_exceptions=review_exceptions,
    )
    if violations:
        print("[baseline-review] failed")
        for item in violations:
            print(f"- {item}")
        return 1

    print("[baseline-review] passed")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Technical debt governance gate")
    sub = parser.add_subparsers(dest="command", required=True)

    hotspot = sub.add_parser("hotspot", help="Generate large-file hotspot report")
    hotspot.add_argument("--threshold", type=int, default=800)
    hotspot.add_argument("--since-days", type=int, default=90)
    hotspot.add_argument("--top-n", type=int, default=20)
    hotspot.add_argument("--output", default="reports/analysis/large-file-hotspots.json")
    hotspot.set_defaults(func=run_hotspot)

    ttl_gate = sub.add_parser("ttl-gate", help="Validate TTL metadata and expiration")
    ttl_gate.add_argument("--base-sha", default=None)
    ttl_gate.add_argument("--output", default="reports/analysis/ttl-gate-report.json")
    ttl_gate.set_defaults(func=run_ttl_gate)

    kpi_gate = sub.add_parser("kpi-gate", help="Evaluate governance KPI gates")
    kpi_gate.add_argument("--baseline", default=str(DEFAULT_BASELINE.relative_to(PROJECT_ROOT)))
    kpi_gate.add_argument("--current", default="reports/analysis/tech-debt-current.json")
    kpi_gate.add_argument("--base-sha", default=None)
    kpi_gate.add_argument("--output", default="reports/analysis/tech-debt-kpi-report.json")
    kpi_gate.set_defaults(func=run_kpi_gate)

    weekly = sub.add_parser("weekly-report", help="Generate weekly governance report")
    weekly.add_argument("--baseline", default=str(DEFAULT_BASELINE.relative_to(PROJECT_ROOT)))
    weekly.add_argument("--current", default="reports/analysis/tech-debt-current.json")
    weekly.add_argument("--base-sha", default=None)
    weekly.add_argument("--threshold", type=int, default=800)
    weekly.add_argument("--since-days", type=int, default=90)
    weekly.add_argument("--top-n", type=int, default=10)
    weekly.add_argument("--output", default="reports/analysis/tech-debt-weekly-report.md")
    weekly.set_defaults(func=run_weekly_report)

    review = sub.add_parser("baseline-review", help="Ensure baseline update is non-increasing")
    review.add_argument("--previous", required=True)
    review.add_argument("--proposed", required=True)
    review.add_argument("--exceptions", help="Optional JSON manifest for approved rebaseline exceptions")
    review.set_defaults(func=run_baseline_review)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
