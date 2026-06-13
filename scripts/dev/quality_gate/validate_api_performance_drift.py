#!/usr/bin/env python3
"""Validate API benchmark measurements do not regress beyond the frozen baseline budget."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from scripts.dev.quality_gate.collect_api_performance_baseline import build_api_performance_baseline
except ModuleNotFoundError:
    from collect_api_performance_baseline import build_api_performance_baseline


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_BASELINE = PROJECT_ROOT / "reports" / "analysis" / "api-performance-baseline.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "reports" / "analysis" / "api-performance-drift-report.json"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _allowed_max(
    baseline_value: Any,
    *,
    absolute_budget_ms: float,
    relative_budget_ratio: float,
    hard_ceiling_ms: float | None = None,
) -> float | None:
    if not isinstance(baseline_value, (int, float)):
        return None
    allowed = max(float(baseline_value) + absolute_budget_ms, float(baseline_value) * (1.0 + relative_budget_ratio))
    if hard_ceiling_ms is not None:
        allowed = min(allowed, hard_ceiling_ms)
    return round(allowed, 2)


def _make_check(
    path: str,
    baseline: Any,
    current: Any,
    allowed: Any,
    *,
    comparator: str,
    description: str,
) -> dict[str, Any]:
    if baseline is None:
        return {
            "path": path,
            "description": description,
            "baseline": baseline,
            "current": current,
            "allowed": allowed,
            "comparator": comparator,
            "status": "missing_baseline",
            "message": f"baseline missing required metric: {path}",
        }
    if current is None:
        return {
            "path": path,
            "description": description,
            "baseline": baseline,
            "current": current,
            "allowed": allowed,
            "comparator": comparator,
            "status": "missing_current",
            "message": f"current benchmark missing required metric: {path}",
        }

    passed = False
    if comparator == "exact":
        passed = current == allowed
    elif comparator == "max":
        passed = isinstance(current, (int, float)) and isinstance(allowed, (int, float)) and float(current) <= float(allowed)
    elif comparator == "min":
        passed = isinstance(current, (int, float)) and isinstance(allowed, (int, float)) and float(current) >= float(allowed)
    else:
        raise ValueError(f"Unsupported comparator: {comparator}")

    if passed:
        status = "pass"
        message = f"{path} ok"
    elif comparator == "max":
        status = "regressed"
        message = f"{path} regressed: current={current} > allowed={allowed} (baseline={baseline})"
    elif comparator == "min":
        status = "regressed"
        message = f"{path} regressed: current={current} < allowed={allowed} (baseline={baseline})"
    else:
        status = "regressed"
        message = f"{path} regressed: current={current!r} != required={allowed!r} (baseline={baseline!r})"

    return {
        "path": path,
        "description": description,
        "baseline": baseline,
        "current": current,
        "allowed": allowed,
        "comparator": comparator,
        "status": status,
        "message": message,
    }


def _make_presence_violation(
    path: str,
    *,
    description: str,
    baseline: Any,
    current: Any,
    status: str,
    message: str,
) -> dict[str, Any]:
    return {
        "path": path,
        "description": description,
        "baseline": baseline,
        "current": current,
        "allowed": "endpoint-set-match",
        "comparator": "exact",
        "status": status,
        "message": message,
    }


def build_api_performance_drift_report(
    baseline_payload: dict[str, Any],
    current_payload: dict[str, Any],
    *,
    absolute_budget_ms: float,
    relative_budget_ratio: float,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    checks.append(
        _make_check(
            "slo_status",
            baseline_payload.get("slo_status"),
            current_payload.get("slo_status"),
            "COMPLIANT",
            comparator="exact",
            description="API benchmark SLO status must remain compliant",
        )
    )

    overall_p95_baseline = baseline_payload.get("overall_p95_ms")
    checks.append(
        _make_check(
            "overall_p95_ms",
            overall_p95_baseline,
            current_payload.get("overall_p95_ms"),
            _allowed_max(
                overall_p95_baseline,
                absolute_budget_ms=absolute_budget_ms,
                relative_budget_ratio=relative_budget_ratio,
                hard_ceiling_ms=300.0,
            ),
            comparator="max",
            description="Overall API P95 must stay within drift budget and <= 300ms",
        )
    )

    business_baseline = ((baseline_payload.get("workload_classes") or {}).get("business") or {}).get("overall_p95_ms")
    business_current = ((current_payload.get("workload_classes") or {}).get("business") or {}).get("overall_p95_ms")
    if business_baseline is not None:
        checks.append(
            _make_check(
                "workload_classes.business.overall_p95_ms",
                business_baseline,
                business_current,
                _allowed_max(
                    business_baseline,
                    absolute_budget_ms=absolute_budget_ms,
                    relative_budget_ratio=relative_budget_ratio,
                    hard_ceiling_ms=300.0,
                ),
                comparator="max",
                description="Business API P95 must stay within drift budget and <= 300ms",
            )
        )

    endpoint_checks: list[dict[str, Any]] = []
    current_endpoint_map = current_payload.get("endpoints") or {}
    baseline_endpoint_map = baseline_payload.get("endpoints") or {}
    baseline_endpoint_keys = set(baseline_endpoint_map)
    current_endpoint_keys = set(current_endpoint_map)

    for missing_key in sorted(baseline_endpoint_keys - current_endpoint_keys):
        endpoint_checks.append(
            _make_presence_violation(
                f"endpoints.{missing_key}",
                description="Current benchmark must continue measuring every frozen baseline endpoint",
                baseline=baseline_endpoint_map.get(missing_key),
                current=None,
                status="missing_current",
                message=f"current benchmark is missing baseline endpoint: {missing_key}",
            )
        )

    for unexpected_key in sorted(current_endpoint_keys - baseline_endpoint_keys):
        endpoint_checks.append(
            _make_presence_violation(
                f"endpoints.{unexpected_key}",
                description="Current benchmark endpoint set must match the frozen baseline endpoint set",
                baseline=None,
                current=current_endpoint_map.get(unexpected_key),
                status="unexpected_current",
                message=f"current benchmark contains endpoint not present in baseline: {unexpected_key}",
            )
        )

    for key, current_endpoint in sorted(current_endpoint_map.items()):
        baseline_endpoint = baseline_endpoint_map.get(key)
        if baseline_endpoint is None:
            continue
        endpoint_checks.append(
            _make_check(
                f"endpoints.{key}.p95_ms",
                baseline_endpoint.get("p95_ms"),
                current_endpoint.get("p95_ms"),
                _allowed_max(
                    baseline_endpoint.get("p95_ms"),
                    absolute_budget_ms=absolute_budget_ms,
                    relative_budget_ratio=relative_budget_ratio,
                    hard_ceiling_ms=300.0,
                ),
                comparator="max",
                description=f"{key} P95 must stay within drift budget and <= 300ms",
            )
        )
        endpoint_checks.append(
            _make_check(
                f"endpoints.{key}.error_rate_percent",
                baseline_endpoint.get("error_rate_percent"),
                current_endpoint.get("error_rate_percent"),
                _allowed_max(
                    baseline_endpoint.get("error_rate_percent"),
                    absolute_budget_ms=0.1,
                    relative_budget_ratio=0.0,
                    hard_ceiling_ms=0.1,
                ),
                comparator="max",
                description=f"{key} error rate must stay <= 0.1%",
            )
        )

    checks.extend(endpoint_checks)
    violations = [item for item in checks if item["status"] != "pass"]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "metric_version": "v1",
        "baseline_generated_at": baseline_payload.get("generated_at"),
        "current_generated_at": current_payload.get("generated_at"),
        "absolute_budget_ms": absolute_budget_ms,
        "relative_budget_ratio": relative_budget_ratio,
        "pass": not violations,
        "violations": violations,
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate API performance benchmark drift against frozen baseline")
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE, help="Frozen baseline JSON path")
    parser.add_argument("--current-benchmark-json", type=Path, required=True, help="Current benchmark.json path")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output report path")
    parser.add_argument(
        "--absolute-budget-ms",
        type=float,
        default=10.0,
        help="Absolute latency budget above baseline for max comparisons",
    )
    parser.add_argument(
        "--relative-budget-ratio",
        type=float,
        default=0.25,
        help="Relative latency budget above baseline for max comparisons",
    )
    args = parser.parse_args()

    baseline_payload = _read_json(args.baseline.resolve())
    current_benchmark_path = args.current_benchmark_json.resolve()
    current_payload = build_api_performance_baseline(_read_json(current_benchmark_path), current_benchmark_path)
    report = build_api_performance_drift_report(
        baseline_payload,
        current_payload,
        absolute_budget_ms=args.absolute_budget_ms,
        relative_budget_ratio=args.relative_budget_ratio,
    )

    output_path = args.output.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[api-performance-drift] written: {output_path}")
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
