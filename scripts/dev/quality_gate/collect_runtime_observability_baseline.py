#!/usr/bin/env python3
"""Collect a machine-readable runtime/observability baseline from runtime summary artifacts."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT = PROJECT_ROOT / "reports" / "analysis" / "runtime-observability-baseline.json"


def resolve_latest_runtime_summary_json() -> Path:
    candidates = sorted((PROJECT_ROOT / "reports" / "analysis" / "runtime-quality-summary").glob("*/summary.json"))
    if not candidates:
        raise FileNotFoundError("No runtime quality summary json found under reports/analysis/runtime-quality-summary/*/summary.json")
    return candidates[-1]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_counts(summary_text: str) -> dict[str, int]:
    counts: dict[str, int] = {"passed": 0, "failed": 0, "skipped": 0}
    matched = False
    for token in summary_text.replace(",", " ").split():
        if "=" not in token:
            continue
        key, raw_value = token.split("=", 1)
        if key in counts:
            try:
                counts[key] = int(float(raw_value))
            except ValueError:
                counts[key] = 0
            matched = True
    if matched:
        return counts

    for key in counts:
        pattern = re.compile(rf"(?<!\d)(\d+)\s+{key}\b", re.IGNORECASE)
        match = pattern.search(summary_text)
        if match:
            counts[key] = int(match.group(1))
    return counts


def _build_frontend_runtime(frontend: dict[str, Any] | None) -> dict[str, Any] | None:
    if frontend is None:
        return None
    return {
        "structural_gate": frontend.get("structural_gate"),
        "type_errors_current": frontend.get("current_frontend_type_errors"),
        "type_errors_baseline": frontend.get("repo_frontend_type_error_baseline"),
        "regression_e2e": _parse_counts(frontend.get("regression_e2e", "")),
        "accessibility_smoke": _parse_counts(frontend.get("accessibility_smoke", "")),
        "regression_pytest": _parse_counts(frontend.get("regression_pytest", "")),
    }


def _build_api_performance(api: dict[str, Any] | None) -> dict[str, Any] | None:
    if api is None:
        return None
    return {
        "slo_status": api.get("slo_status"),
        "overall_avg_ms": api.get("overall_avg_ms"),
        "overall_p95_ms": api.get("overall_p95_ms"),
        "observability_status": api.get("observability_status"),
        "slow_http_requests_total_delta": api.get("slow_http_requests_total_delta"),
        "trading_status_p95_ms": (api.get("trading_status") or {}).get("p95_ms"),
        "trading_market_snapshot_p95_ms": (api.get("trading_market_snapshot") or {}).get("p95_ms"),
        "trading_risk_metrics_p95_ms": (api.get("trading_risk_metrics") or {}).get("p95_ms"),
    }


def _build_monitoring_auth_performance(monitoring: dict[str, Any] | None) -> dict[str, Any] | None:
    if monitoring is None:
        return None
    return {
        "slo_status": monitoring.get("slo_status"),
        "observability_status": monitoring.get("observability_status"),
        "slow_http_requests_total_delta": monitoring.get("slow_http_requests_total_delta"),
        "alert_rules_p95_ms": (monitoring.get("alert_rules") or {}).get("p95_ms"),
        "alerts_p95_ms": (monitoring.get("alerts") or {}).get("p95_ms"),
    }


def _build_docker_runtime(docker: dict[str, Any] | None) -> dict[str, Any] | None:
    if docker is None:
        return None
    return {
        "backend_health": docker.get("backend_health"),
        "backend_readiness": docker.get("backend_readiness"),
        "frontend_index": docker.get("frontend_index"),
        "metrics_health": docker.get("metrics_health"),
        "http_requests_total_delta": docker.get("http_requests_total_delta"),
        "slow_http_requests_total_delta": docker.get("slow_http_requests_total_delta"),
        "db_connections_active": docker.get("db_connections_active"),
    }


def build_runtime_observability_baseline(summary_payload: dict[str, Any], summary_path: Path) -> dict[str, Any]:
    frontend = summary_payload.get("frontend_runtime")
    api = summary_payload.get("api_performance")
    monitoring = summary_payload.get("monitoring_auth_performance")
    docker = summary_payload.get("docker_runtime")

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "metric_version": "v1",
        "source_summary_json": str(summary_path.resolve()),
        "source_generated_at": summary_payload.get("generated_at"),
        "service_urls": summary_payload.get("service_urls", {}),
        "overall_gate_status": summary_payload.get("overall_gate_status"),
        "frontend_runtime": _build_frontend_runtime(frontend),
        "api_performance": _build_api_performance(api),
        "monitoring_auth_performance": _build_monitoring_auth_performance(monitoring),
        "docker_runtime": _build_docker_runtime(docker),
        "current_batch_issues": summary_payload.get("current_batch_issues", []),
        "existing_debt": summary_payload.get("existing_debt", []),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect runtime/observability baseline from runtime quality summary")
    parser.add_argument(
        "--summary-json",
        type=Path,
        help="Path to runtime quality summary JSON. Defaults to latest reports/analysis/runtime-quality-summary/*/summary.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output JSON path",
    )
    args = parser.parse_args()

    summary_path = args.summary_json.resolve() if args.summary_json else resolve_latest_runtime_summary_json()
    summary_payload = _read_json(summary_path)
    baseline = build_runtime_observability_baseline(summary_payload, summary_path)

    output_path = args.output.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(baseline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[runtime-observability-baseline] written: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
