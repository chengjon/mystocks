from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
REPO_BASELINE_PATH = PROJECT_ROOT / "reports" / "analysis" / "tech-debt-baseline.json"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(_read_text(path))


def _require_match(pattern: str, text: str, label: str) -> str:
    match = re.search(pattern, text, re.MULTILINE)
    if not match:
        raise ValueError(f"Could not parse {label}")
    return match.group(1).strip()


def _relative(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(resolved)


def _append_section(lines: list[str], title: str, body_lines: list[str]) -> None:
    lines.extend([title, "", *body_lines, ""])


def parse_frontend_report(report_dir: Path) -> dict[str, Any]:
    summary_text = _read_text(report_dir / "SUMMARY.md")
    current_baseline = _read_json(report_dir / "tech-debt-baseline.current.json")
    repo_baseline = _read_json(REPO_BASELINE_PATH)

    pm2_matches = re.findall(r"mystocks-(?:backend|frontend).*online.*", summary_text)

    return {
        "report_dir": str(report_dir),
        "summary_path": str(report_dir / "SUMMARY.md"),
        "tech_debt_baseline_path": str(report_dir / "tech-debt-baseline.current.json"),
        "structural_gate": _require_match(
            r"- Structural syntax / PM2 navigation gate:\s*(.+)",
            summary_text,
            "frontend structural gate",
        ),
        "type_ceiling": _require_match(
            r"- Type ceiling:\s*(.+)",
            summary_text,
            "frontend type ceiling",
        ),
        "regression_e2e": _require_match(
            r"- Regression E2E:\s*(.+)",
            summary_text,
            "frontend regression e2e",
        ),
        "accessibility_smoke": _require_match(
            r"- Accessibility smoke:\s*(.+)",
            summary_text,
            "frontend accessibility smoke",
        ),
        "regression_pytest": _require_match(
            r"- Regression pytest:\s*(.+)",
            summary_text,
            "frontend regression pytest",
        ),
        "pm2_status_lines": pm2_matches,
        "current_frontend_type_errors": current_baseline.get("frontend_type_errors"),
        "repo_frontend_type_error_baseline": repo_baseline.get("frontend_type_errors"),
    }


def parse_api_report(report_dir: Path) -> dict[str, Any]:
    summary_text = _read_text(report_dir / "SUMMARY.md")
    benchmark = _read_json(report_dir / "benchmark.json")
    metrics_summary = _read_json(report_dir / "metrics-summary.json")

    endpoint_map = {item["endpoint"]: item for item in benchmark["endpoints"]}
    return {
        "report_dir": str(report_dir),
        "summary_path": str(report_dir / "SUMMARY.md"),
        "benchmark_path": str(report_dir / "benchmark.json"),
        "metrics_summary_path": str(report_dir / "metrics-summary.json"),
        "slo_status": "COMPLIANT" if benchmark["slo_status"]["compliant"] else "NON-COMPLIANT",
        "overall_avg_ms": benchmark["summary"]["overall_avg_ms"],
        "overall_p95_ms": benchmark["summary"]["overall_p95_ms"],
        "observability_status": metrics_summary["metrics_health"].get("status", "unknown"),
        "slow_http_requests_total": metrics_summary["prometheus_snapshot"]["slow_http_requests_total"],
        "slow_http_requests_total_delta": metrics_summary["prometheus_snapshot"].get("slow_http_requests_total_delta", 0),
        "slow_request_endpoints": metrics_summary["prometheus_snapshot"].get("slow_request_endpoints", []),
        "slow_request_endpoints_delta": metrics_summary["prometheus_snapshot"].get("slow_request_endpoints_delta", []),
        "trading_status": endpoint_map.get("/api/trading/status"),
        "trading_market_snapshot": endpoint_map.get("/api/trading/market/snapshot"),
        "trading_risk_metrics": endpoint_map.get("/api/trading/risk/metrics"),
        "summary_excerpt": _require_match(
            r"- SLO status \(`P95 <= 300ms`, `error_rate <= 0\.1%`\): `([^`]+)`",
            summary_text,
            "api slo status",
        ),
    }


def parse_monitoring_report(report_dir: Path) -> dict[str, Any]:
    summary_text = _read_text(report_dir / "SUMMARY.md")
    benchmark = _read_json(report_dir / "benchmark.json")
    metrics_summary = _read_json(report_dir / "metrics-summary.json")

    endpoint_map = {item["endpoint"]: item for item in benchmark["endpoints"]}
    return {
        "report_dir": str(report_dir),
        "summary_path": str(report_dir / "SUMMARY.md"),
        "benchmark_path": str(report_dir / "benchmark.json"),
        "metrics_summary_path": str(report_dir / "metrics-summary.json"),
        "slo_status": "COMPLIANT" if benchmark["slo_status"]["compliant"] else "NON-COMPLIANT",
        "observability_status": metrics_summary["metrics_health"].get("status", "unknown"),
        "slow_http_requests_total": metrics_summary["prometheus_snapshot"].get("slow_http_requests_total", 0),
        "slow_http_requests_total_delta": metrics_summary["prometheus_snapshot"].get("slow_http_requests_total_delta", 0),
        "slow_request_endpoints": metrics_summary["prometheus_snapshot"].get("slow_request_endpoints", []),
        "slow_request_endpoints_delta": metrics_summary["prometheus_snapshot"].get("slow_request_endpoints_delta", []),
        "alert_rules": endpoint_map.get("/api/v1/monitoring/alert-rules"),
        "alerts": endpoint_map.get("/api/v1/monitoring/alerts"),
        "summary_excerpt": _require_match(
            r"- SLO status \(`P95 <= 300ms`, `error_rate <= 0\.1%`\): `([^`]+)`",
            summary_text,
            "monitoring slo status",
        ),
    }


def parse_docker_report(report_dir: Path) -> dict[str, Any]:
    summary_text = _read_text(report_dir / "SUMMARY.md")
    metrics_summary = _read_json(report_dir / "metrics-summary.json")

    return {
        "report_dir": str(report_dir),
        "summary_path": str(report_dir / "SUMMARY.md"),
        "metrics_summary_path": str(report_dir / "metrics-summary.json"),
        "backend_health": _require_match(r"- Backend health: `([^`]+)`", summary_text, "docker backend health"),
        "backend_readiness": _require_match(
            r"- Backend readiness: `([^`]+)`",
            summary_text,
            "docker backend readiness",
        ),
        "frontend_index": _require_match(r"- Frontend index: `([^`]+)`", summary_text, "docker frontend index"),
        "metrics_health": _require_match(r"- `/api/metrics/health`: `([^`]+)`", summary_text, "docker metrics health"),
        "http_requests_total_delta": metrics_summary["prometheus_snapshot"].get("http_requests_total_delta", 0),
        "slow_http_requests_total_delta": metrics_summary["prometheus_snapshot"].get("slow_http_requests_total_delta", 0),
        "db_connections_active": metrics_summary["prometheus_snapshot"].get("db_connections_active", {}),
    }


def build_summary_payload(
    frontend_dir: Path | None = None,
    api_dir: Path | None = None,
    monitoring_dir: Path | None = None,
    docker_dir: Path | None = None,
    runtime_observability_drift_report: Path | None = None,
    monitoring_rule_report: Path | None = None,
) -> dict[str, Any]:
    frontend = parse_frontend_report(frontend_dir) if frontend_dir is not None else None
    api = parse_api_report(api_dir) if api_dir is not None else None
    monitoring = parse_monitoring_report(monitoring_dir) if monitoring_dir is not None else None
    docker = parse_docker_report(docker_dir) if docker_dir is not None else None

    has_pm2_runtime = frontend is not None and api is not None and monitoring is not None
    if not has_pm2_runtime and docker is None:
        raise ValueError("At least one runtime input is required: PM2 baseline trio or docker runtime smoke")
    if any(item is not None for item in (frontend, api, monitoring)) and not has_pm2_runtime:
        raise ValueError("Frontend/API/monitoring runtime inputs must be provided together")

    frontend_current = frontend["current_frontend_type_errors"] if frontend is not None else None
    frontend_baseline = frontend["repo_frontend_type_error_baseline"] if frontend is not None else None
    type_regression = (
        frontend_current is not None
        and frontend_baseline is not None
        and frontend_current > frontend_baseline
    )

    current_batch_issues: list[str] = []
    if type_regression:
        current_batch_issues.append(
            f"Frontend type errors regressed above baseline ({frontend_current} > {frontend_baseline})"
        )
    if api is not None and api["slo_status"] != "COMPLIANT":
        current_batch_issues.append("Anonymous API performance baseline is non-compliant")
    if monitoring is not None and monitoring["slo_status"] != "COMPLIANT":
        current_batch_issues.append("Monitoring auth performance baseline is non-compliant")
    if docker is not None and (
        docker["backend_health"] != "PASS"
        or docker["backend_readiness"] != "PASS"
        or docker["frontend_index"] != "PASS"
    ):
        current_batch_issues.append("Containerized runtime smoke is non-compliant")

    existing_debt: list[str] = []
    if frontend_current == frontend_baseline and frontend_baseline is not None:
        existing_debt.append(
            f"Frontend type debt remains at repository baseline ({frontend_baseline}) with no new regression"
        )

    drift_report = _read_json(runtime_observability_drift_report) if runtime_observability_drift_report is not None else None
    rule_report = _read_json(monitoring_rule_report) if monitoring_rule_report is not None else None

    if rule_report is not None and not rule_report.get("pass", False):
        current_batch_issues.append("Monitoring rule metric references do not match runtime /metrics snapshots")

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "service_urls": {
            "backend": "http://localhost:8020",
            "frontend": "http://localhost:3020",
        },
        "frontend_runtime": frontend,
        "api_performance": api,
        "monitoring_auth_performance": monitoring,
        "docker_runtime": docker,
        "runtime_observability_drift": drift_report,
        "monitoring_rule_metrics": rule_report,
        "current_batch_issues": current_batch_issues,
        "existing_debt": existing_debt,
        "overall_gate_status": "PASS" if not current_batch_issues else "CHECK",
    }


def write_summary(payload: dict[str, Any], output_markdown: Path, output_json: Path) -> None:
    frontend = payload["frontend_runtime"]
    api = payload["api_performance"]
    monitoring = payload["monitoring_auth_performance"]
    docker = payload.get("docker_runtime")
    drift = payload.get("runtime_observability_drift")
    rule_report = payload.get("monitoring_rule_metrics")
    lines = [
        "# Runtime Quality Summary",
        "",
        f"- Generated at: `{payload['generated_at']}`",
        f"- Overall gate status: `{payload['overall_gate_status']}`",
        "- Service URLs:",
        "  - `mystocks-backend`: `http://localhost:8020`",
        "  - `mystocks-frontend`: `http://localhost:3020`",
        "",
    ]
    if frontend is not None:
        _append_section(
            lines,
            "## Frontend Runtime Gate",
            [
                f"- Structural syntax / PM2 navigation gate: `{frontend['structural_gate']}`",
                f"- Frontend type errors vs baseline: `{frontend['current_frontend_type_errors']}` current vs `{frontend['repo_frontend_type_error_baseline']}` baseline",
                f"- Type ceiling: `{frontend['type_ceiling']}`",
                f"- Regression E2E actual result: `{frontend['regression_e2e']}`",
                f"- Accessibility smoke actual result: `{frontend['accessibility_smoke']}`",
                f"- Regression pytest actual result: `{frontend['regression_pytest']}`",
            ],
        )
        _append_section(
            lines,
            "## PM2 Health",
            [*[f"- `{line}`" for line in frontend["pm2_status_lines"]]],
        )
    if api is not None:
        trading_status = api["trading_status"] or {}
        trading_market_snapshot = api["trading_market_snapshot"] or {}
        trading_risk_metrics = api["trading_risk_metrics"] or {}
        api_slow_lines = [
            f"- Slow endpoint sample: `{item['method']} {item['endpoint']} count={item['count']}`"
            for item in api["slow_request_endpoints_delta"][:5]
        ] or ["- Slow endpoint sample: `none`"]
        _append_section(
            lines,
            "## API Performance Gate",
            [
                f"- Anonymous API baseline: `{api['slo_status']}`",
                f"- Anonymous API overall avg / P95: `{api['overall_avg_ms']}ms / {api['overall_p95_ms']}ms`",
                f"- Anonymous API observability health: `{api['observability_status']}`",
                f"- Prometheus `slow_http_requests_total`: `{api['slow_http_requests_total']}`",
                f"- Prometheus `slow_http_requests_total` delta during run: `{api['slow_http_requests_total_delta']}`",
                f"- `GET /api/trading/status`: `p95={trading_status.get('p95_ms', 'n/a')}ms error={trading_status.get('error_rate_percent', 'n/a')}%`",
                f"- `GET /api/trading/market/snapshot`: `p95={trading_market_snapshot.get('p95_ms', 'n/a')}ms error={trading_market_snapshot.get('error_rate_percent', 'n/a')}%`",
                f"- `GET /api/trading/risk/metrics`: `p95={trading_risk_metrics.get('p95_ms', 'n/a')}ms error={trading_risk_metrics.get('error_rate_percent', 'n/a')}%`",
                *api_slow_lines,
            ],
        )
    if monitoring is not None:
        alert_rules = monitoring["alert_rules"] or {}
        alerts = monitoring["alerts"] or {}
        monitoring_slow_lines = [
            f"- Slow endpoint sample: `{item['method']} {item['endpoint']} count={item['count']}`"
            for item in monitoring["slow_request_endpoints_delta"][:5]
        ] or ["- Slow endpoint sample: `none`"]
        _append_section(
            lines,
            "## Monitoring Auth Performance Gate",
            [
                f"- Monitoring auth baseline: `{monitoring['slo_status']}`",
                f"- Monitoring observability health: `{monitoring['observability_status']}`",
                f"- Monitoring Prometheus `slow_http_requests_total`: `{monitoring['slow_http_requests_total']}`",
                f"- Monitoring Prometheus `slow_http_requests_total` delta during run: `{monitoring['slow_http_requests_total_delta']}`",
                f"- `GET /api/v1/monitoring/alert-rules`: `p95={alert_rules.get('p95_ms', 'n/a')}ms error={alert_rules.get('error_rate_percent', 'n/a')}%`",
                f"- `GET /api/v1/monitoring/alerts`: `p95={alerts.get('p95_ms', 'n/a')}ms error={alerts.get('error_rate_percent', 'n/a')}%`",
                *monitoring_slow_lines,
            ],
        )
    if docker is not None:
        _append_section(
            lines,
            "## Container Runtime Smoke",
            [
                f"- Backend health: `{docker['backend_health']}`",
                f"- Backend readiness: `{docker['backend_readiness']}`",
                f"- Frontend index: `{docker['frontend_index']}`",
                f"- Docker metrics health: `{docker['metrics_health']}`",
                f"- Docker Prometheus `http_requests_total` delta during run: `{docker['http_requests_total_delta']}`",
                f"- Docker Prometheus `slow_http_requests_total` delta during run: `{docker['slow_http_requests_total_delta']}`",
                f"- Docker active DB connections: `{docker['db_connections_active']}`",
            ],
        )
    if drift is not None:
        _append_section(
            lines,
            "## Runtime Observability Drift Gate",
            [
                f"- Drift gate pass: `{drift.get('pass', 'n/a')}`",
                f"- Drift gate violations: `{len(drift.get('violations', []))}`",
                f"- Drift gate not_measured: `{len(drift.get('not_measured', []))}`",
            ],
        )
    if rule_report is not None:
        _append_section(
            lines,
            "## Monitoring Rule And Dashboard Metric References",
            [
                f"- Rule metric reference pass: `{rule_report.get('pass', 'n/a')}`",
                f"- Rule metric reference violations: `{len(rule_report.get('violations', []))}`",
                f"- Metrics snapshots used: `{len(rule_report.get('metrics_files', []))}`",
                f"- Rule files checked: `{len(rule_report.get('rule_files', []))}`",
                f"- Dashboard files checked: `{len(rule_report.get('dashboard_files', []))}`",
            ],
        )
    lines.extend(
        [
            "## Current Batch vs Existing Debt",
            "",
        ]
    )

    if payload["current_batch_issues"]:
        lines.extend([f"- Current batch issue: `{item}`" for item in payload["current_batch_issues"]])
    else:
        lines.append("- Current batch introduced issues: `none`")

    if payload["existing_debt"]:
        lines.extend([f"- Existing debt: `{item}`" for item in payload["existing_debt"]])
    else:
        lines.append("- Existing debt: `none captured by this summary`")

    lines.extend(
        [
            "",
            "## Source Artifacts",
            "",
        ]
    )
    if frontend is not None:
        lines.extend(
            [
                f"- `{_relative(Path(frontend['summary_path']))}`",
                f"- `{_relative(Path(frontend['tech_debt_baseline_path']))}`",
            ]
        )
    if api is not None:
        lines.extend(
            [
                f"- `{_relative(Path(api['summary_path']))}`",
                f"- `{_relative(Path(api['benchmark_path']))}`",
                f"- `{_relative(Path(api['metrics_summary_path']))}`",
            ]
        )
    if monitoring is not None:
        lines.extend(
            [
                f"- `{_relative(Path(monitoring['summary_path']))}`",
                f"- `{_relative(Path(monitoring['benchmark_path']))}`",
                f"- `{_relative(Path(monitoring['metrics_summary_path']))}`",
            ]
        )
    if docker is not None:
        lines.extend(
            [
                f"- `{_relative(Path(docker['summary_path']))}`",
                f"- `{_relative(Path(docker['metrics_summary_path']))}`",
            ]
        )
    if rule_report is not None:
        lines.append(f"- `{_relative(output_json.parent / 'monitoring-rule-metric-reference-report.json')}`")

    output_markdown.write_text("\n".join(lines) + "\n", encoding="utf-8")
    output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a unified runtime quality summary from baseline artifacts.")
    parser.add_argument("--frontend-dir", type=Path)
    parser.add_argument("--api-dir", type=Path)
    parser.add_argument("--monitoring-dir", type=Path)
    parser.add_argument("--docker-dir", type=Path)
    parser.add_argument("--runtime-observability-drift-report", type=Path)
    parser.add_argument("--monitoring-rule-report", type=Path)
    parser.add_argument("--output-markdown", required=True, type=Path)
    parser.add_argument("--output-json", required=True, type=Path)
    args = parser.parse_args()

    payload = build_summary_payload(
        frontend_dir=args.frontend_dir.resolve() if args.frontend_dir else None,
        api_dir=args.api_dir.resolve() if args.api_dir else None,
        monitoring_dir=args.monitoring_dir.resolve() if args.monitoring_dir else None,
        docker_dir=args.docker_dir.resolve() if args.docker_dir else None,
        runtime_observability_drift_report=(
            args.runtime_observability_drift_report.resolve() if args.runtime_observability_drift_report else None
        ),
        monitoring_rule_report=args.monitoring_rule_report.resolve() if args.monitoring_rule_report else None,
    )
    args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    write_summary(payload, args.output_markdown.resolve(), args.output_json.resolve())


if __name__ == "__main__":
    main()
