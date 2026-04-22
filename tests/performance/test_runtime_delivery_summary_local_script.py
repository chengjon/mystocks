import json
import os
import subprocess
from pathlib import Path


def test_runtime_delivery_summary_local_script_supports_pm2_and_docker_modes():
    script = Path("scripts/run_runtime_delivery_summary_local.sh").read_text(encoding="utf-8")

    assert 'SUMMARY_DIR="${RUNTIME_DELIVERY_SUMMARY_DIR:-${PROJECT_ROOT}/reports/analysis/runtime-quality-summary-ci-local}"' in script
    assert 'BUNDLE_DIR="${RUNTIME_DELIVERY_BUNDLE_DIR:-${PROJECT_ROOT}/reports/analysis/runtime-ci-bundle-combined-local}"' in script
    assert 'DRIFT_REPORT_PATH="${SUMMARY_DIR}/runtime-observability-drift-report.json"' in script
    assert 'MONITORING_RULE_REPORT_PATH="${SUMMARY_DIR}/monitoring-rule-metric-reference-report.json"' in script
    assert 'resolve_latest_dir()' in script
    assert 'python "${PROJECT_ROOT}/scripts/dev/quality_gate/build_runtime_quality_summary.py"' in script
    assert 'python "${PROJECT_ROOT}/scripts/dev/quality_gate/validate_runtime_observability_drift.py"' in script
    assert 'python "${PROJECT_ROOT}/scripts/dev/quality_gate/validate_monitoring_prometheus_references.py"' in script
    assert 'python "${PROJECT_ROOT}/scripts/dev/quality_gate/build_runtime_ci_bundle.py"' in script
    assert '--runtime-observability-drift-report "${DRIFT_REPORT_PATH}"' in script
    assert '--monitoring-rule-report "${MONITORING_RULE_REPORT_PATH}"' in script
    assert '--dashboard-file "${PROJECT_ROOT}/config/monitoring/dashboards/api-overview.json"' in script
    assert '--dashboard-file "${PROJECT_ROOT}/config/monitoring/dashboards/user-experience-dashboard.json"' in script
    assert '--declared-metrics-python-file "${PROJECT_ROOT}/web/backend/app/api/metrics.py"' in script
    assert '--declared-metrics-python-file "${PROJECT_ROOT}/src/monitoring/metrics_collector.py"' in script
    assert '--declared-metrics-python-file "${PROJECT_ROOT}/web/backend/app/core/middleware/performance.py"' in script
    assert '--declared-metrics-python-file "${PROJECT_ROOT}/web/backend/app/core/user_experience_monitor.py"' in script
    assert 'if [ "${has_pm2_runtime}" -eq 1 ]; then' in script
    assert 'if [ -n "${docker_dir}" ]; then' in script
    assert 'Runtime delivery summary requires PM2 baseline dirs or DOCKER_RUNTIME_DIR' in script
    assert 'Runtime delivery summary requires at least one metrics.raw.txt snapshot for monitoring rule validation' in script


def test_runtime_delivery_summary_local_script_rebuilds_pm2_and_docker_outputs(tmp_path: Path):
    frontend_dir = tmp_path / "frontend"
    api_dir = tmp_path / "api"
    monitoring_dir = tmp_path / "monitoring"
    docker_dir = tmp_path / "docker"
    summary_dir = tmp_path / "runtime-quality-summary-ci-local"
    bundle_dir = tmp_path / "runtime-ci-bundle-combined-local"

    frontend_dir.mkdir()
    api_dir.mkdir()
    monitoring_dir.mkdir()
    docker_dir.mkdir()

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
        "- SLO status (`P95 <= 300ms`, `error_rate <= 0.1%`): `COMPLIANT`\n- Overall average response time: `18.47ms`\n- Overall average P95 response time: `22.94ms`\n",
        encoding="utf-8",
    )
    (api_dir / "benchmark.json").write_text(
        json.dumps(
            {
                "slo_status": {"compliant": True},
                "summary": {"overall_avg_ms": 18.47, "overall_p95_ms": 22.94},
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
                    "slow_http_requests_total": 0,
                    "slow_http_requests_total_delta": 0,
                    "slow_request_endpoints": [],
                    "slow_request_endpoints_delta": [],
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (api_dir / "metrics.raw.txt").write_text(
        "\n".join(
            [
                'http_requests_total{endpoint="/health",method="GET",status_code="200"} 26',
                'http_requests_active{endpoint="/health",method="GET"} 0',
                'http_request_duration_seconds_bucket{le="0.5"} 3',
                'slow_http_requests_total{endpoint="/api/trading/status",method="GET"} 0',
                "mystocks_cache_hits_total 10",
                "mystocks_cache_misses_total 2",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (monitoring_dir / "SUMMARY.md").write_text(
        "- SLO status (`P95 <= 300ms`, `error_rate <= 0.1%`): `COMPLIANT`\n- `GET /api/v1/monitoring/alert-rules`: avg=117.01ms p95=271.53ms error=0.0%\n",
        encoding="utf-8",
    )
    (monitoring_dir / "benchmark.json").write_text(
        json.dumps(
            {
                "slo_status": {"compliant": True},
                "endpoints": [
                    {"endpoint": "/api/v1/monitoring/alert-rules", "p95_ms": 271.53, "error_rate_percent": 0.0},
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
                    "slow_http_requests_total": 0,
                    "slow_http_requests_total_delta": 0,
                    "slow_request_endpoints": [],
                    "slow_request_endpoints_delta": [],
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (monitoring_dir / "metrics.raw.txt").write_text(
        "\n".join(
            [
                'http_requests_total{endpoint="/api/v1/monitoring/alert-rules",method="GET",status_code="200"} 20',
                'http_requests_active{endpoint="/api/v1/monitoring/alert-rules",method="GET"} 0',
                'http_request_duration_seconds_bucket{le="0.5"} 4',
                'slow_http_requests_total{endpoint="/api/v1/monitoring/alert-rules",method="GET"} 0',
                "mystocks_cache_hits_total 10",
                "mystocks_cache_misses_total 2",
            ]
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
                "- Prometheus `http_requests_total` delta during run: `4.0`",
                "- Prometheus `slow_http_requests_total` delta during run: `0.0`",
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
    (docker_dir / "metrics.raw.txt").write_text(
        "\n".join(
            [
                'http_requests_total{endpoint="/health",method="GET",status_code="200"} 4',
                'http_requests_active{endpoint="/health",method="GET"} 0',
                'http_request_duration_seconds_bucket{le="0.5"} 1',
                'slow_http_requests_total{endpoint="/health",method="GET"} 0',
                "mystocks_cache_hits_total 10",
                "mystocks_cache_misses_total 2",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    subprocess.run(
        [
            "bash",
            "scripts/run_runtime_delivery_summary_local.sh",
        ],
        cwd=Path(__file__).resolve().parents[2],
        env={
            **os.environ,
            "FRONTEND_RUNTIME_DIR": str(frontend_dir),
            "API_PERFORMANCE_DIR": str(api_dir),
            "MONITORING_AUTH_DIR": str(monitoring_dir),
            "DOCKER_RUNTIME_DIR": str(docker_dir),
            "RUNTIME_DELIVERY_SUMMARY_DIR": str(summary_dir),
            "RUNTIME_DELIVERY_BUNDLE_DIR": str(bundle_dir),
        },
        check=True,
    )

    summary_text = (summary_dir / "SUMMARY.md").read_text(encoding="utf-8")
    summary_payload = json.loads((summary_dir / "summary.json").read_text(encoding="utf-8"))
    drift_report = json.loads((summary_dir / "runtime-observability-drift-report.json").read_text(encoding="utf-8"))
    rule_report = json.loads((summary_dir / "monitoring-rule-metric-reference-report.json").read_text(encoding="utf-8"))
    manifest = json.loads((bundle_dir / "runtime-artifact-manifest.json").read_text(encoding="utf-8"))
    index_text = (bundle_dir / "runtime-artifact-index.md").read_text(encoding="utf-8")

    assert "## Frontend Runtime Gate" in summary_text
    assert "## Container Runtime Smoke" in summary_text
    assert "## Runtime Observability Drift Gate" in summary_text
    assert "## Monitoring Rule And Dashboard Metric References" in summary_text
    assert "Overall gate status: `PASS`" in summary_text
    assert summary_payload["overall_gate_status"] == "PASS"
    assert summary_payload["runtime_observability_drift"]["pass"] is True
    assert summary_payload["monitoring_rule_metrics"]["pass"] is True
    assert drift_report["pass"] is True
    assert rule_report["pass"] is True
    assert manifest["runtime_quality_dir"] == str(summary_dir.resolve())
    assert manifest["docker_runtime_dir"] == str(docker_dir.resolve())
    assert manifest["runtime_observability_drift_report"] == str((summary_dir / "runtime-observability-drift-report.json").resolve())
    assert manifest["monitoring_rule_report"] == str((summary_dir / "monitoring-rule-metric-reference-report.json").resolve())
    assert "Docker runtime smoke: `PASS` / `PASS` / `PASS`" in index_text
    assert "Anonymous API overall avg / P95: `18.47ms / 22.94ms`" in index_text
    assert "Drift gate pass: `True`" in index_text
    assert "Rule metric reference pass: `True`" in index_text
    assert "Dashboard files checked: `2`" in index_text
