import json
import os
import subprocess
from pathlib import Path


def test_runtime_delivery_summary_local_script_supports_pm2_and_docker_modes():
    script = Path("scripts/run_runtime_delivery_summary_local.sh").read_text(encoding="utf-8")

    assert 'SUMMARY_DIR="${RUNTIME_DELIVERY_SUMMARY_DIR:-${PROJECT_ROOT}/reports/analysis/runtime-quality-summary-ci-local}"' in script
    assert 'BUNDLE_DIR="${RUNTIME_DELIVERY_BUNDLE_DIR:-${PROJECT_ROOT}/reports/analysis/runtime-ci-bundle-combined-local}"' in script
    assert 'resolve_latest_dir()' in script
    assert 'python "${PROJECT_ROOT}/scripts/dev/quality_gate/build_runtime_quality_summary.py"' in script
    assert 'python "${PROJECT_ROOT}/scripts/dev/quality_gate/build_runtime_ci_bundle.py"' in script
    assert 'if [ "${has_pm2_runtime}" -eq 1 ]; then' in script
    assert 'if [ -n "${docker_dir}" ]; then' in script
    assert 'Runtime delivery summary requires PM2 baseline dirs or DOCKER_RUNTIME_DIR' in script


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
    manifest = json.loads((bundle_dir / "runtime-artifact-manifest.json").read_text(encoding="utf-8"))
    index_text = (bundle_dir / "runtime-artifact-index.md").read_text(encoding="utf-8")

    assert "## Frontend Runtime Gate" in summary_text
    assert "## Container Runtime Smoke" in summary_text
    assert "Overall gate status: `PASS`" in summary_text
    assert summary_payload["overall_gate_status"] == "PASS"
    assert manifest["runtime_quality_dir"] == str(summary_dir.resolve())
    assert manifest["docker_runtime_dir"] == str(docker_dir.resolve())
    assert "Docker runtime smoke: `PASS` / `PASS` / `PASS`" in index_text
    assert "Anonymous API overall avg / P95: `18.47ms / 22.94ms`" in index_text
