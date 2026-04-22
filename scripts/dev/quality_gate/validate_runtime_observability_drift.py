#!/usr/bin/env python3
"""Validate runtime observability measurements do not regress against the frozen baseline."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from scripts.dev.quality_gate.collect_runtime_observability_baseline import (
        build_runtime_observability_baseline,
        resolve_latest_runtime_summary_json,
    )
except ModuleNotFoundError:
    from collect_runtime_observability_baseline import (
        build_runtime_observability_baseline,
        resolve_latest_runtime_summary_json,
    )


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_BASELINE = PROJECT_ROOT / "reports" / "analysis" / "runtime-observability-baseline.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "reports" / "analysis" / "runtime-observability-drift-report.json"


@dataclass(frozen=True)
class DriftRule:
    path: str
    comparator: str
    gated: bool = True
    threshold: int | float | str | None = None
    description: str = ""


GATED_RULES: tuple[DriftRule, ...] = (
    DriftRule("overall_gate_status", "exact", threshold="PASS", description="PM2 runtime overall gate must stay PASS"),
    DriftRule(
        "frontend_runtime.type_errors_current",
        "max",
        threshold=0,
        description="frontend type errors must not exceed baseline or zero ceiling",
    ),
    DriftRule(
        "api_performance.overall_p95_ms",
        "max",
        threshold=300.0,
        description="anonymous API overall P95 must stay within baseline and <= 300ms",
    ),
    DriftRule(
        "api_performance.observability_status",
        "exact",
        threshold="healthy",
        description="anonymous API metrics health must stay healthy",
    ),
    DriftRule(
        "api_performance.slow_http_requests_total_delta",
        "max",
        description="anonymous API slow request delta must not increase",
    ),
    DriftRule(
        "monitoring_auth_performance.alert_rules_p95_ms",
        "max",
        threshold=300.0,
        description="monitoring auth alert-rules P95 must stay within baseline and <= 300ms",
    ),
    DriftRule(
        "monitoring_auth_performance.observability_status",
        "exact",
        threshold="healthy",
        description="monitoring auth metrics health must stay healthy",
    ),
    DriftRule(
        "monitoring_auth_performance.slow_http_requests_total_delta",
        "max",
        description="monitoring auth slow request delta must not increase",
    ),
    DriftRule("docker_runtime.backend_health", "exact", threshold="PASS", description="docker backend health must stay PASS"),
    DriftRule(
        "docker_runtime.backend_readiness",
        "exact",
        threshold="PASS",
        description="docker backend readiness must stay PASS",
    ),
    DriftRule("docker_runtime.frontend_index", "exact", threshold="PASS", description="docker frontend index must stay PASS"),
    DriftRule(
        "docker_runtime.metrics_health",
        "exact",
        threshold="healthy",
        description="docker metrics endpoint must stay healthy",
    ),
    DriftRule(
        "docker_runtime.http_requests_total_delta",
        "min",
        threshold=0.0,
        description="docker smoke request volume must not drop below baseline or zero",
    ),
    DriftRule(
        "docker_runtime.slow_http_requests_total_delta",
        "max",
        description="docker slow request delta must not increase",
    ),
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _get_path(payload: dict[str, Any], path: str) -> Any:
    current: Any = payload
    for segment in path.split("."):
        if not isinstance(current, dict) or segment not in current:
            return None
        current = current[segment]
    return current


def _effective_threshold(rule: DriftRule, baseline_value: Any) -> Any:
    if rule.comparator == "max":
        if isinstance(rule.threshold, (int, float)) and isinstance(baseline_value, (int, float)):
            return min(float(baseline_value), float(rule.threshold))
        if rule.threshold is not None:
            return rule.threshold
        return baseline_value
    if rule.comparator == "min":
        if isinstance(rule.threshold, (int, float)) and isinstance(baseline_value, (int, float)):
            return max(float(baseline_value), float(rule.threshold))
        if rule.threshold is not None:
            return rule.threshold
        return baseline_value
    return rule.threshold if rule.threshold is not None else baseline_value


def _is_top_level_scope_measured(current: dict[str, Any], path: str) -> bool:
    top_level = path.split(".", 1)[0]
    if top_level == "overall_gate_status":
        return True
    return current.get(top_level) is not None


def _evaluate_rule(rule: DriftRule, baseline: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    baseline_value = _get_path(baseline, rule.path)
    current_value = _get_path(current, rule.path)
    effective_threshold = _effective_threshold(rule, baseline_value)

    if baseline_value is None:
        return {
            "path": rule.path,
            "description": rule.description,
            "comparator": rule.comparator,
            "baseline": baseline_value,
            "current": current_value,
            "effective_threshold": effective_threshold,
            "status": "missing_baseline",
            "message": f"baseline missing required metric: {rule.path}",
            "gated": rule.gated,
        }

    if not _is_top_level_scope_measured(current, rule.path):
        return {
            "path": rule.path,
            "description": rule.description,
            "comparator": rule.comparator,
            "baseline": baseline_value,
            "current": current_value,
            "effective_threshold": effective_threshold,
            "status": "not_measured",
            "message": f"current scope not measured for metric: {rule.path}",
            "gated": rule.gated,
        }

    if current_value is None:
        return {
            "path": rule.path,
            "description": rule.description,
            "comparator": rule.comparator,
            "baseline": baseline_value,
            "current": current_value,
            "effective_threshold": effective_threshold,
            "status": "missing_current",
            "message": f"current measurement missing required metric: {rule.path}",
            "gated": rule.gated,
        }

    passed = False
    if rule.comparator == "exact":
        passed = current_value == effective_threshold
    elif rule.comparator == "max":
        passed = isinstance(current_value, (int, float)) and isinstance(effective_threshold, (int, float)) and float(current_value) <= float(effective_threshold)
    elif rule.comparator == "min":
        passed = isinstance(current_value, (int, float)) and isinstance(effective_threshold, (int, float)) and float(current_value) >= float(effective_threshold)
    else:
        raise ValueError(f"Unsupported comparator: {rule.comparator}")

    if passed:
        message = f"{rule.path} ok"
        status = "pass"
    elif rule.comparator == "max":
        message = f"{rule.path} regressed: current={current_value} > allowed={effective_threshold} (baseline={baseline_value})"
        status = "regressed"
    elif rule.comparator == "min":
        message = f"{rule.path} regressed: current={current_value} < allowed={effective_threshold} (baseline={baseline_value})"
        status = "regressed"
    else:
        message = (
            f"{rule.path} regressed: current={current_value!r} != required={effective_threshold!r} "
            f"(baseline={baseline_value!r})"
        )
        status = "regressed"

    return {
        "path": rule.path,
        "description": rule.description,
        "comparator": rule.comparator,
        "baseline": baseline_value,
        "current": current_value,
        "effective_threshold": effective_threshold,
        "status": status,
        "message": message,
        "gated": rule.gated,
    }


def build_runtime_observability_drift_report(
    baseline_payload: dict[str, Any],
    current_payload: dict[str, Any],
) -> dict[str, Any]:
    checks = [_evaluate_rule(rule, baseline_payload, current_payload) for rule in GATED_RULES]
    violations = [
        item
        for item in checks
        if item["gated"] and item["status"] not in {"pass", "not_measured"}
    ]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "metric_version": "v1",
        "baseline_generated_at": baseline_payload.get("generated_at"),
        "current_generated_at": current_payload.get("generated_at"),
        "pass": not violations,
        "violations": violations,
        "checks": checks,
        "not_measured": [item for item in checks if item["status"] == "not_measured"],
    }


def _load_current_payload(args: argparse.Namespace) -> tuple[dict[str, Any], str]:
    if args.current_observability_json:
        path = args.current_observability_json.resolve()
        return _read_json(path), str(path)

    summary_path = args.current_summary_json.resolve() if args.current_summary_json else resolve_latest_runtime_summary_json()
    summary_payload = _read_json(summary_path)
    return build_runtime_observability_baseline(summary_payload, summary_path), str(summary_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate runtime observability metrics do not drift below the frozen baseline")
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE, help="Frozen runtime observability baseline JSON")
    parser.add_argument(
        "--current-summary-json",
        type=Path,
        help="Current runtime quality summary JSON. Defaults to latest reports/analysis/runtime-quality-summary/*/summary.json",
    )
    parser.add_argument(
        "--current-observability-json",
        type=Path,
        help="Current machine-readable observability snapshot JSON. If provided, bypass summary-to-snapshot conversion.",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output drift report JSON path")
    args = parser.parse_args()

    if args.current_summary_json and args.current_observability_json:
        parser.error("--current-summary-json and --current-observability-json are mutually exclusive")

    baseline_path = args.baseline.resolve()
    baseline_payload = _read_json(baseline_path)
    current_payload, current_source = _load_current_payload(args)
    report = build_runtime_observability_drift_report(baseline_payload=baseline_payload, current_payload=current_payload)
    report["baseline_path"] = str(baseline_path)
    report["current_source"] = current_source

    output_path = args.output.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if report["pass"]:
        print("[runtime-observability-drift] passed")
        print(f"[runtime-observability-drift] report: {output_path}")
        return 0

    print("[runtime-observability-drift] failed")
    for item in report["violations"]:
        print(f"- {item['message']}")
    print(f"[runtime-observability-drift] report: {output_path}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
