from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _first_match(pattern: str, text: str, fallback: str = "n/a") -> str:
    match = re.search(pattern, text, re.MULTILINE)
    return match.group(1).strip() if match else fallback


def build_bundle_manifest(
    frontend_dir: Path | None,
    api_dir: Path | None,
    monitoring_dir: Path | None,
    runtime_quality_dir: Path,
    docker_dir: Path | None = None,
    runtime_observability_drift_report_path: Path | None = None,
    monitoring_rule_report_path: Path | None = None,
) -> dict[str, object]:
    manifest: dict[str, object] = {
        "runtime_quality_dir": str(runtime_quality_dir),
        "summary_files": {"runtime_quality": str(runtime_quality_dir / "SUMMARY.md")},
    }
    if frontend_dir is not None:
        manifest["frontend_runtime_dir"] = str(frontend_dir)
        summary_files = manifest["summary_files"]
        assert isinstance(summary_files, dict)
        summary_files["frontend_runtime"] = str(frontend_dir / "SUMMARY.md")
    if api_dir is not None:
        manifest["api_performance_dir"] = str(api_dir)
        summary_files = manifest["summary_files"]
        assert isinstance(summary_files, dict)
        summary_files["api_performance"] = str(api_dir / "SUMMARY.md")
    if monitoring_dir is not None:
        manifest["monitoring_auth_dir"] = str(monitoring_dir)
        summary_files = manifest["summary_files"]
        assert isinstance(summary_files, dict)
        summary_files["monitoring_auth"] = str(monitoring_dir / "SUMMARY.md")
    if docker_dir is not None:
        manifest["docker_runtime_dir"] = str(docker_dir)
        summary_files = manifest["summary_files"]
        assert isinstance(summary_files, dict)
        summary_files["docker_runtime"] = str(docker_dir / "SUMMARY.md")
    if runtime_observability_drift_report_path is not None:
        manifest["runtime_observability_drift_report"] = str(runtime_observability_drift_report_path)
        summary_files = manifest["summary_files"]
        assert isinstance(summary_files, dict)
        summary_files["runtime_observability_drift"] = str(runtime_observability_drift_report_path)
    if monitoring_rule_report_path is not None:
        manifest["monitoring_rule_report"] = str(monitoring_rule_report_path)
        summary_files = manifest["summary_files"]
        assert isinstance(summary_files, dict)
        summary_files["monitoring_rule_report"] = str(monitoring_rule_report_path)
    return manifest


def build_bundle_index(
    frontend_dir: Path | None,
    api_dir: Path | None,
    monitoring_dir: Path | None,
    runtime_quality_dir: Path,
    docker_dir: Path | None = None,
    runtime_observability_drift_report_path: Path | None = None,
    monitoring_rule_report_path: Path | None = None,
) -> str:
    api_summary = _read_text(api_dir / "SUMMARY.md") if api_dir is not None else ""
    monitoring_summary = _read_text(monitoring_dir / "SUMMARY.md") if monitoring_dir is not None else ""
    runtime_quality_summary = _read_text(runtime_quality_dir / "SUMMARY.md")
    docker_summary = _read_text(docker_dir / "SUMMARY.md") if docker_dir is not None else ""
    drift_report_text = _read_text(runtime_observability_drift_report_path) if runtime_observability_drift_report_path is not None else ""
    drift_report = json.loads(drift_report_text) if drift_report_text else None
    monitoring_rule_report_text = _read_text(monitoring_rule_report_path) if monitoring_rule_report_path is not None else ""
    monitoring_rule_report = json.loads(monitoring_rule_report_text) if monitoring_rule_report_text else None

    lines = [
        "# Runtime Artifact Index",
        "",
        "## Key Gates",
        "",
        f"- Overall gate status: `{_first_match(r'- Overall gate status: `([^`]+)`', runtime_quality_summary)}`",
        f"- Structural syntax / PM2 navigation gate: `{_first_match(r'- Structural syntax / PM2 navigation gate: `([^`]+)`', runtime_quality_summary)}`",
        f"- Frontend type errors vs baseline: `{_first_match(r'- Frontend type errors vs baseline: `([^`]+)`', runtime_quality_summary)}`",
        f"- Regression E2E: `{_first_match(r'- Regression E2E actual result: `([^`]+)`', runtime_quality_summary)}`",
        f"- Anonymous API baseline: `{_first_match(r'- Anonymous API baseline: `([^`]+)`', runtime_quality_summary)}`",
        f"- Monitoring auth baseline: `{_first_match(r'- Monitoring auth baseline: `([^`]+)`', runtime_quality_summary)}`",
    ]
    if docker_dir is not None:
        lines.append(
            f"- Docker runtime smoke: `{_first_match(r'- Backend health: `([^`]+)`', docker_summary)}` / `{_first_match(r'- Backend readiness: `([^`]+)`', docker_summary)}` / `{_first_match(r'- Frontend index: `([^`]+)`', docker_summary)}`"
        )

    lines.extend(
        [
            "",
            "## Report Entry Points",
            "",
            f"- Unified runtime summary: `{runtime_quality_dir / 'SUMMARY.md'}`",
        ]
    )
    if runtime_observability_drift_report_path is not None:
        lines.append(f"- Runtime observability drift report: `{runtime_observability_drift_report_path}`")
    if monitoring_rule_report_path is not None:
        lines.append(f"- Monitoring rule metric reference report: `{monitoring_rule_report_path}`")
    if frontend_dir is not None:
        lines.append(f"- Frontend runtime summary: `{frontend_dir / 'SUMMARY.md'}`")
    if api_dir is not None:
        lines.append(f"- API performance summary: `{api_dir / 'SUMMARY.md'}`")
    if monitoring_dir is not None:
        lines.append(f"- Monitoring auth summary: `{monitoring_dir / 'SUMMARY.md'}`")
    if docker_dir is not None:
        lines.append(f"- Docker runtime summary: `{docker_dir / 'SUMMARY.md'}`")
    lines.extend(["", "## Performance Snapshot", ""])
    if api_dir is not None:
        lines.append(
            f"- Anonymous API overall avg / P95: `{_first_match(r'- Overall average response time: `([^`]+)`', api_summary)} / {_first_match(r'- Overall average P95 response time: `([^`]+)`', api_summary)}`"
        )
    if monitoring_dir is not None:
        lines.append(
            f"- Monitoring auth key endpoint P95: `{_first_match(r'- `GET /api/v1/monitoring/alert-rules`: avg=[^\\n]+ p95=([^ ]+) error=', monitoring_summary)}`"
        )
    lines.append(
        f"- Runtime summary slow-request delta: `{_first_match(r'- Prometheus `slow_http_requests_total` delta during run: `([^`]+)`', runtime_quality_summary)}`"
    )
    if drift_report is not None:
        lines.extend(
            [
                "",
                "## Drift Gate",
                "",
                f"- Drift gate pass: `{drift_report.get('pass', 'n/a')}`",
                f"- Drift gate violations: `{len(drift_report.get('violations', []))}`",
                f"- Drift gate not_measured: `{len(drift_report.get('not_measured', []))}`",
            ]
        )
    if monitoring_rule_report is not None:
        lines.extend(
            [
                "",
                "## Monitoring Rule Metrics",
                "",
                f"- Rule metric reference pass: `{monitoring_rule_report.get('pass', 'n/a')}`",
                f"- Rule metric reference violations: `{len(monitoring_rule_report.get('violations', []))}`",
                f"- Rule metric snapshots used: `{len(monitoring_rule_report.get('metrics_files', []))}`",
                f"- Dashboard files checked: `{len(monitoring_rule_report.get('dashboard_files', []))}`",
            ]
        )
    if docker_dir is not None:
        lines.extend(
            [
                f"- Docker metrics health: `{_first_match(r'- `/api/metrics/health`: `([^`]+)`', docker_summary)}`",
                f"- Docker metrics http / slow delta: `{_first_match(r'- Prometheus `http_requests_total` delta during run: `([^`]+)`', docker_summary)} / {_first_match(r'- Prometheus `slow_http_requests_total` delta during run: `([^`]+)`', docker_summary)}`",
            ]
        )
    lines.extend(
        [
            "",
            "See `runtime-artifact-manifest.json` for machine-readable paths.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the runtime CI artifact manifest and index.")
    parser.add_argument("--frontend-dir", type=Path)
    parser.add_argument("--api-dir", type=Path)
    parser.add_argument("--monitoring-dir", type=Path)
    parser.add_argument("--runtime-quality-dir", required=True, type=Path)
    parser.add_argument("--docker-dir", type=Path)
    parser.add_argument("--runtime-observability-drift-report", type=Path)
    parser.add_argument("--monitoring-rule-report", type=Path)
    parser.add_argument("--output-manifest", required=True, type=Path)
    parser.add_argument("--output-index", required=True, type=Path)
    args = parser.parse_args()

    manifest = build_bundle_manifest(
        frontend_dir=args.frontend_dir.resolve() if args.frontend_dir else None,
        api_dir=args.api_dir.resolve() if args.api_dir else None,
        monitoring_dir=args.monitoring_dir.resolve() if args.monitoring_dir else None,
        runtime_quality_dir=args.runtime_quality_dir.resolve(),
        docker_dir=args.docker_dir.resolve() if args.docker_dir else None,
        runtime_observability_drift_report_path=args.runtime_observability_drift_report.resolve() if args.runtime_observability_drift_report else None,
        monitoring_rule_report_path=args.monitoring_rule_report.resolve() if args.monitoring_rule_report else None,
    )
    index_text = build_bundle_index(
        frontend_dir=args.frontend_dir.resolve() if args.frontend_dir else None,
        api_dir=args.api_dir.resolve() if args.api_dir else None,
        monitoring_dir=args.monitoring_dir.resolve() if args.monitoring_dir else None,
        runtime_quality_dir=args.runtime_quality_dir.resolve(),
        docker_dir=args.docker_dir.resolve() if args.docker_dir else None,
        runtime_observability_drift_report_path=args.runtime_observability_drift_report.resolve() if args.runtime_observability_drift_report else None,
        monitoring_rule_report_path=args.monitoring_rule_report.resolve() if args.monitoring_rule_report else None,
    )

    args.output_manifest.parent.mkdir(parents=True, exist_ok=True)
    args.output_index.parent.mkdir(parents=True, exist_ok=True)
    args.output_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.output_index.write_text(index_text, encoding="utf-8")


if __name__ == "__main__":
    main()
