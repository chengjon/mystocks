import json
import subprocess
from pathlib import Path


def test_build_runtime_quality_summary_aggregates_three_baselines(tmp_path: Path):
    frontend_dir = tmp_path / "frontend"
    api_dir = tmp_path / "api"
    monitoring_dir = tmp_path / "monitoring"
    docker_dir = tmp_path / "docker"
    frontend_dir.mkdir()
    api_dir.mkdir()
    monitoring_dir.mkdir()
    docker_dir.mkdir()
    drift_report_path = tmp_path / "runtime-observability-drift-report.json"
    monitoring_rule_report_path = tmp_path / "monitoring-rule-metric-reference-report.json"

    (frontend_dir / "SUMMARY.md").write_text(
        "\n".join(
            [
                "# Frontend Runtime Baseline",
                "- Structural syntax / PM2 navigation gate: 14 passed (4.9s)",
                "- Type ceiling: [type-ceiling] TypeScript errors 0 are within configured ceiling 0.",
                "- Regression E2E: E2E Summary: passed=44 failed=0 skipped=0",
                "- Accessibility smoke: 4 passed (21.3s)",
                "- Regression pytest: Pytest Summary: passed=46 failed=0 skipped=18",
                "mystocks-backend online",
                "mystocks-frontend online",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (frontend_dir / "tech-debt-baseline.current.json").write_text(
        json.dumps({"frontend_type_errors": 0}) + "\n",
        encoding="utf-8",
    )

    (api_dir / "SUMMARY.md").write_text(
        "- SLO status (`P95 <= 300ms`, `error_rate <= 0.1%`): `COMPLIANT`\n",
        encoding="utf-8",
    )
    (api_dir / "benchmark.json").write_text(
        json.dumps(
            {
                "slo_status": {"compliant": True},
                "summary": {"overall_avg_ms": 20.0, "overall_p95_ms": 30.0},
                "endpoints": [
                    {"endpoint": "/api/trading/status", "p95_ms": 12.2, "error_rate_percent": 0.0},
                    {"endpoint": "/api/trading/market/snapshot", "p95_ms": 11.6, "error_rate_percent": 0.0},
                    {"endpoint": "/api/trading/risk/metrics", "p95_ms": 10.5, "error_rate_percent": 0.0},
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (api_dir / "metrics-summary.json").write_text(
        json.dumps(
            {
                "metrics_health": {"status": "healthy"},
                "prometheus_snapshot": {
                    "slow_http_requests_total": 2,
                    "slow_http_requests_total_delta": 1,
                    "slow_request_endpoints": [
                        {"endpoint": "/api/v1/market/kline", "method": "GET", "count": 2.0}
                    ],
                    "slow_request_endpoints_delta": [
                        {"endpoint": "/api/v1/market/kline", "method": "GET", "count": 1.0}
                    ],
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    (monitoring_dir / "SUMMARY.md").write_text(
        "- SLO status (`P95 <= 300ms`, `error_rate <= 0.1%`): `COMPLIANT`\n",
        encoding="utf-8",
    )
    (monitoring_dir / "benchmark.json").write_text(
        json.dumps(
            {
                "slo_status": {"compliant": True},
                "endpoints": [
                    {"endpoint": "/api/v1/monitoring/alert-rules", "p95_ms": 240.98, "error_rate_percent": 0.0},
                    {"endpoint": "/api/v1/monitoring/alerts", "p95_ms": 106.94, "error_rate_percent": 0.0},
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (monitoring_dir / "metrics-summary.json").write_text(
        json.dumps(
            {
                "metrics_health": {"status": "healthy"},
                "prometheus_snapshot": {
                    "slow_http_requests_total": 1,
                    "slow_http_requests_total_delta": 0,
                    "slow_request_endpoints": [
                        {"endpoint": "/api/v1/monitoring/alert-rules", "method": "GET", "count": 1.0}
                    ],
                    "slow_request_endpoints_delta": [],
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (docker_dir / "SUMMARY.md").write_text(
        "\n".join(
            [
                "# Docker Runtime Smoke",
                "- Backend health: `PASS`",
                "- Backend readiness: `PASS`",
                "- Frontend index: `PASS`",
                "- `/api/metrics/health`: `healthy`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (docker_dir / "metrics-summary.json").write_text(
        json.dumps(
            {
                "prometheus_snapshot": {
                    "http_requests_total_delta": 4.0,
                    "slow_http_requests_total_delta": 0.0,
                    "db_connections_active": {"postgresql": 8.0, "redis": 1.0},
                }
            }
        )
        + "\n",
        encoding="utf-8",
    )
    drift_report_path.write_text(
        json.dumps(
            {
                "generated_at": "2026-04-21T09:07:31.843158+00:00",
                "pass": True,
                "violations": [],
                "not_measured": [],
                "checks": [],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monitoring_rule_report_path.write_text(
        json.dumps(
            {
                "generated_at": "2026-04-21T09:08:00+00:00",
                "pass": True,
                "violations": [],
                "metrics_files": [str((api_dir / "metrics.raw.txt").resolve())],
                "rule_files": ["/opt/claude/mystocks_spec/config/monitoring/rules/mystocks-alerts.yml"],
                "dashboard_files": [
                    "/opt/claude/mystocks_spec/config/monitoring/dashboards/api-overview.json",
                    "/opt/claude/mystocks_spec/config/monitoring/dashboards/user-experience-dashboard.json",
                ],
                "checks": [],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    markdown_path = tmp_path / "runtime-summary" / "SUMMARY.md"
    json_path = tmp_path / "runtime-summary" / "summary.json"

    subprocess.run(
        [
            "python",
            "scripts/dev/quality_gate/build_runtime_quality_summary.py",
            "--frontend-dir",
            str(frontend_dir),
            "--api-dir",
            str(api_dir),
            "--monitoring-dir",
            str(monitoring_dir),
            "--docker-dir",
            str(docker_dir),
            "--runtime-observability-drift-report",
            str(drift_report_path),
            "--monitoring-rule-report",
            str(monitoring_rule_report_path),
            "--output-markdown",
            str(markdown_path),
            "--output-json",
            str(json_path),
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=True,
    )

    summary_text = markdown_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))

    assert "Overall gate status: `PASS`" in summary_text
    assert "`GET /api/trading/status`: `p95=12.2ms error=0.0%`" in summary_text
    assert "`GET /api/v1/monitoring/alert-rules`: `p95=240.98ms error=0.0%`" in summary_text
    assert "Prometheus `slow_http_requests_total` delta during run: `1`" in summary_text
    assert "Slow endpoint sample: `GET /api/v1/market/kline count=1.0`" in summary_text
    assert "Monitoring Prometheus `slow_http_requests_total`: `1`" in summary_text
    assert "Monitoring Prometheus `slow_http_requests_total` delta during run: `0`" in summary_text
    assert "Slow endpoint sample: `GET /api/v1/monitoring/alert-rules count=1.0`" not in summary_text
    assert "## Container Runtime Smoke" in summary_text
    assert "Backend health: `PASS`" in summary_text
    assert "Docker metrics health: `healthy`" in summary_text
    assert "Docker Prometheus `http_requests_total` delta during run: `4.0`" in summary_text
    assert "## Runtime Observability Drift Gate" in summary_text
    assert "Drift gate pass: `True`" in summary_text
    assert "Drift gate violations: `0`" in summary_text
    assert "## Monitoring Rule And Dashboard Metric References" in summary_text
    assert "Rule metric reference pass: `True`" in summary_text
    assert "Rule metric reference violations: `0`" in summary_text
    assert "Dashboard files checked: `2`" in summary_text
    assert payload["overall_gate_status"] == "PASS"
    assert payload["current_batch_issues"] == []
    assert payload["docker_runtime"]["metrics_health"] == "healthy"
    assert payload["runtime_observability_drift"]["pass"] is True
    assert payload["monitoring_rule_metrics"]["pass"] is True


def test_build_runtime_quality_summary_supports_docker_only_input(tmp_path: Path):
    docker_dir = tmp_path / "docker"
    docker_dir.mkdir()
    drift_report_path = tmp_path / "runtime-observability-drift-report.json"
    monitoring_rule_report_path = tmp_path / "monitoring-rule-metric-reference-report.json"

    (docker_dir / "SUMMARY.md").write_text(
        "\n".join(
            [
                "# Docker Runtime Smoke",
                "- Backend health: `PASS`",
                "- Backend readiness: `PASS`",
                "- Frontend index: `PASS`",
                "- `/api/metrics/health`: `healthy`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (docker_dir / "metrics-summary.json").write_text(
        json.dumps(
            {
                "prometheus_snapshot": {
                    "http_requests_total_delta": 2.0,
                    "slow_http_requests_total_delta": 0.0,
                    "db_connections_active": {"postgresql": 3.0},
                }
            }
        )
        + "\n",
        encoding="utf-8",
    )
    drift_report_path.write_text(
        json.dumps(
            {
                "generated_at": "2026-04-21T09:07:31.843158+00:00",
                "pass": True,
                "violations": [],
                "not_measured": [{"path": "api_performance.overall_p95_ms"}],
                "checks": [],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monitoring_rule_report_path.write_text(
        json.dumps(
            {
                "generated_at": "2026-04-21T09:08:00+00:00",
                "pass": True,
                "violations": [],
                "metrics_files": [str((docker_dir / "metrics.raw.txt").resolve())],
                "rule_files": ["/opt/claude/mystocks_spec/config/monitoring/rules/mystocks-alerts.yml"],
                "dashboard_files": [
                    "/opt/claude/mystocks_spec/config/monitoring/dashboards/api-overview.json",
                    "/opt/claude/mystocks_spec/config/monitoring/dashboards/user-experience-dashboard.json",
                ],
                "checks": [],
            }
        )
        + "\n",
        encoding="utf-8",
    )

    markdown_path = tmp_path / "runtime-summary" / "SUMMARY.md"
    json_path = tmp_path / "runtime-summary" / "summary.json"

    subprocess.run(
        [
            "python",
            "scripts/dev/quality_gate/build_runtime_quality_summary.py",
            "--docker-dir",
            str(docker_dir),
            "--runtime-observability-drift-report",
            str(drift_report_path),
            "--monitoring-rule-report",
            str(monitoring_rule_report_path),
            "--output-markdown",
            str(markdown_path),
            "--output-json",
            str(json_path),
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=True,
    )

    summary_text = markdown_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))

    assert "## Frontend Runtime Gate" not in summary_text
    assert "## API Performance Gate" not in summary_text
    assert "## Monitoring Auth Performance Gate" not in summary_text
    assert "## Container Runtime Smoke" in summary_text
    assert "## Runtime Observability Drift Gate" in summary_text
    assert "## Monitoring Rule And Dashboard Metric References" in summary_text
    assert "Drift gate not_measured: `1`" in summary_text
    assert "Backend health: `PASS`" in summary_text
    assert payload["overall_gate_status"] == "PASS"
    assert payload["frontend_runtime"] is None
    assert payload["api_performance"] is None
    assert payload["monitoring_auth_performance"] is None
    assert payload["docker_runtime"]["http_requests_total_delta"] == 2.0
    assert payload["runtime_observability_drift"]["pass"] is True
    assert payload["monitoring_rule_metrics"]["pass"] is True
