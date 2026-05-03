import json
import subprocess
from pathlib import Path


def test_build_runtime_ci_bundle_writes_manifest_and_index(tmp_path: Path):
    frontend_dir = tmp_path / "frontend-runtime"
    api_dir = tmp_path / "api-performance"
    monitoring_dir = tmp_path / "monitoring-auth"
    runtime_quality_dir = tmp_path / "runtime-quality"
    docker_dir = tmp_path / "docker-runtime"
    drift_report_path = tmp_path / "runtime-observability-drift-report.json"
    performance_drift_report_path = tmp_path / "api-performance-drift-report.json"
    monitoring_rule_report_path = tmp_path / "monitoring-rule-metric-reference-report.json"
    container_deployment_contract_report_path = tmp_path / "container-deployment-contract-report.json"
    deployment_env_contract_report_path = tmp_path / "deployment-env-contract-report.json"
    akshare_availability_report_path = tmp_path / "akshare-market-function-availability.json"
    akshare_repo_truth_report_path = tmp_path / "akshare-market-repo-truth-gate.json"
    akshare_gate_summary_report_path = tmp_path / "akshare-market-gates-summary.json"

    frontend_dir.mkdir()
    api_dir.mkdir()
    monitoring_dir.mkdir()
    runtime_quality_dir.mkdir()
    docker_dir.mkdir()

    (frontend_dir / "SUMMARY.md").write_text("# Frontend Runtime\n", encoding="utf-8")
    (frontend_dir / "frontend-runtime-gate.json").write_text(
        json.dumps(
            {
                "metric_version": "v1",
                "structural_gate": "14 passed (4.9s)",
                "regression_e2e": "E2E Summary: passed=44 failed=0 skipped=0",
                "regression_pytest": "Pytest Summary: passed=46 failed=0 skipped=18",
                "accessibility_smoke": "4 passed (21.3s)",
                "pm2_services_online": ["mystocks-backend", "mystocks-frontend"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (api_dir / "SUMMARY.md").write_text(
        "\n".join(
            [
                "# API Summary",
                "- Overall average response time: `18.47ms`",
                "- Overall average P95 response time: `22.94ms`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (monitoring_dir / "SUMMARY.md").write_text(
        "- `GET /api/v1/monitoring/alert-rules`: avg=117.01ms p95=271.53ms error=0.0%\n",
        encoding="utf-8",
    )
    (runtime_quality_dir / "SUMMARY.md").write_text(
        "\n".join(
            [
                "# Runtime Quality Summary",
                "- Overall gate status: `PASS`",
                "- Structural syntax / PM2 navigation gate: `14 passed (4.9s)`",
                "- Frontend type errors vs baseline: `0` current vs `0` baseline",
                "- Regression E2E actual result: `E2E Summary: passed=44 failed=0 skipped=0`",
                "- Anonymous API baseline: `COMPLIANT`",
                "- Monitoring auth baseline: `COMPLIANT`",
                "- Prometheus `slow_http_requests_total` delta during run: `0`",
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
                "- Prometheus `http_requests_total` delta during run: `3.0`",
                "- Prometheus `slow_http_requests_total` delta during run: `0.0`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (docker_dir / "docker-runtime-smoke.json").write_text(
        json.dumps(
            {
                "metric_version": "v1",
                "service_urls": {"backend": "http://localhost:8021", "frontend": "http://localhost:3021"},
                "checks": {
                    "backend_health": "PASS",
                    "backend_readiness": "PASS",
                    "frontend_index": "PASS",
                },
                "metrics_health": "healthy",
                "prometheus_snapshot": {
                    "http_requests_total_delta": 3.0,
                    "slow_http_requests_total_delta": 0.0,
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    drift_report_path.write_text(
        json.dumps(
            {
                "generated_at": "2026-04-21T08:00:00+00:00",
                "metric_version": "v1",
                "baseline_generated_at": "2026-04-20T10:24:00+00:00",
                "current_generated_at": "2026-04-21T08:00:00+00:00",
                "pass": True,
                "violations": [],
                "not_measured": [],
                "checks": [],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    performance_drift_report_path.write_text(
        json.dumps(
            {
                "generated_at": "2026-04-21T08:00:30+00:00",
                "pass": True,
                "violations": [],
                "checks": [],
                "absolute_budget_ms": 10.0,
                "relative_budget_ratio": 0.25,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monitoring_rule_report_path.write_text(
        json.dumps(
            {
                "generated_at": "2026-04-21T08:01:00+00:00",
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
    container_deployment_contract_report_path.write_text(
        json.dumps(
            {
                "pass": True,
                "canonical_ports": {"backend": 8020, "frontend": 3020},
                "backup_smoke_ports": {"backend": 8021, "frontend": 3021},
                "violations": [],
                "checks": [],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    deployment_env_contract_report_path.write_text(
        json.dumps(
            {
                "pass": True,
                "backend_required_env_keys": ["BACKEND_BACKUP_PORT", "BACKEND_PORT"],
                "frontend_required_env_keys": [
                    "BACKEND_BACKUP_PORT",
                    "BACKEND_PORT",
                    "FRONTEND_BACKUP_PORT",
                    "FRONTEND_PORT",
                ],
                "violations": [],
                "checks": [],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    akshare_availability_report_path.write_text(
        json.dumps(
            {
                "module": "akshare",
                "import_ok": True,
                "module_version": "1.18.10",
                "summary": {
                    "tracked_count": 9,
                    "available_count": 4,
                    "missing_count": 5,
                    "available_functions": [
                        "stock_hot_follow_xq",
                        "stock_board_change_em",
                        "stock_zt_pool_em",
                        "stock_changes_em",
                    ],
                    "missing_functions": [
                        "stock_news_main_em",
                        "stock_dt_pool_em",
                        "stock_strong_pool_em",
                        "stock_weak_pool_em",
                        "stock_new_em",
                    ],
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    akshare_repo_truth_report_path.write_text(
        json.dumps(
            {
                "pass": True,
                "summary": {
                    "tracked_count": 9,
                    "passed_count": 9,
                    "failed_count": 0,
                    "violation_count": 0,
                },
                "violations": [],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    akshare_gate_summary_report_path.write_text(
        json.dumps(
            {
                "pass": True,
                "availability_exit_code": 0,
                "repo_truth_exit_code": 0,
                "summary": {
                    "tracked_count": 9,
                    "available_count": 4,
                    "missing_count": 5,
                    "repo_truth_passed_count": 9,
                    "repo_truth_failed_count": 0,
                    "repo_truth_violation_count": 0,
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    manifest_path = tmp_path / "bundle" / "runtime-artifact-manifest.json"
    index_path = tmp_path / "bundle" / "runtime-artifact-index.md"

    subprocess.run(
        [
            "python",
            "scripts/dev/quality_gate/build_runtime_ci_bundle.py",
            "--frontend-dir",
            str(frontend_dir),
            "--api-dir",
            str(api_dir),
            "--monitoring-dir",
            str(monitoring_dir),
            "--runtime-quality-dir",
            str(runtime_quality_dir),
            "--docker-dir",
            str(docker_dir),
            "--runtime-observability-drift-report",
            str(drift_report_path),
            "--api-performance-drift-report",
            str(performance_drift_report_path),
            "--monitoring-rule-report",
            str(monitoring_rule_report_path),
            "--container-deployment-contract-report",
            str(container_deployment_contract_report_path),
            "--deployment-env-contract-report",
            str(deployment_env_contract_report_path),
            "--akshare-market-function-availability-report",
            str(akshare_availability_report_path),
            "--akshare-market-repo-truth-report",
            str(akshare_repo_truth_report_path),
            "--akshare-market-gates-summary-report",
            str(akshare_gate_summary_report_path),
            "--output-manifest",
            str(manifest_path),
            "--output-index",
            str(index_path),
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=True,
    )

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    index_text = index_path.read_text(encoding="utf-8")

    assert manifest["frontend_runtime_dir"] == str(frontend_dir.resolve())
    assert manifest["api_performance_dir"] == str(api_dir.resolve())
    assert manifest["monitoring_auth_dir"] == str(monitoring_dir.resolve())
    assert manifest["runtime_quality_dir"] == str(runtime_quality_dir.resolve())
    assert manifest["docker_runtime_dir"] == str(docker_dir.resolve())
    assert manifest["runtime_observability_drift_report"] == str(drift_report_path.resolve())
    assert manifest["api_performance_drift_report"] == str(performance_drift_report_path.resolve())
    assert manifest["monitoring_rule_report"] == str(monitoring_rule_report_path.resolve())
    assert manifest["container_deployment_contract_report"] == str(container_deployment_contract_report_path.resolve())
    assert manifest["deployment_env_contract_report"] == str(deployment_env_contract_report_path.resolve())
    assert manifest["frontend_runtime_gate_report"] == str((frontend_dir / "frontend-runtime-gate.json").resolve())
    assert manifest["summary_files"]["runtime_quality"] == str((runtime_quality_dir / "SUMMARY.md").resolve())
    assert manifest["summary_files"]["frontend_runtime_gate"] == str((frontend_dir / "frontend-runtime-gate.json").resolve())
    assert manifest["summary_files"]["docker_runtime"] == str((docker_dir / "SUMMARY.md").resolve())
    assert manifest["docker_runtime_report"] == str((docker_dir / "docker-runtime-smoke.json").resolve())
    assert manifest["summary_files"]["docker_runtime_report"] == str((docker_dir / "docker-runtime-smoke.json").resolve())
    assert manifest["summary_files"]["runtime_observability_drift"] == str(drift_report_path.resolve())
    assert manifest["summary_files"]["api_performance_drift"] == str(performance_drift_report_path.resolve())
    assert manifest["summary_files"]["monitoring_rule_report"] == str(monitoring_rule_report_path.resolve())
    assert manifest["summary_files"]["container_deployment_contract_report"] == str(
        container_deployment_contract_report_path.resolve()
    )
    assert manifest["summary_files"]["deployment_env_contract_report"] == str(deployment_env_contract_report_path.resolve())
    assert manifest["akshare_market_function_availability_report"] == str(akshare_availability_report_path.resolve())
    assert manifest["akshare_market_repo_truth_report"] == str(akshare_repo_truth_report_path.resolve())
    assert manifest["akshare_market_gates_summary_report"] == str(akshare_gate_summary_report_path.resolve())
    assert manifest["summary_files"]["akshare_market_function_availability_report"] == str(
        akshare_availability_report_path.resolve()
    )
    assert manifest["summary_files"]["akshare_market_repo_truth_report"] == str(akshare_repo_truth_report_path.resolve())
    assert manifest["summary_files"]["akshare_market_gates_summary_report"] == str(akshare_gate_summary_report_path.resolve())

    assert "# Runtime Artifact Index" in index_text
    assert "## Key Gates" in index_text
    assert "## Report Entry Points" in index_text
    assert "## Performance Snapshot" in index_text
    assert "Overall gate status: `PASS`" in index_text
    assert "Structural syntax / PM2 navigation gate: `14 passed (4.9s)`" in index_text
    assert "Frontend type errors vs baseline: `0`" in index_text
    assert "Regression E2E: `E2E Summary: passed=44 failed=0 skipped=0`" in index_text
    assert "PM2 services online: `mystocks-backend, mystocks-frontend`" in index_text
    assert "Regression pytest: `Pytest Summary: passed=46 failed=0 skipped=18`" in index_text
    assert "Accessibility smoke: `4 passed (21.3s)`" in index_text
    assert "Anonymous API overall avg / P95: `18.47ms / 22.94ms`" in index_text
    assert "Monitoring auth key endpoint P95: `271.53ms`" in index_text
    assert "Runtime summary slow-request delta: `0`" in index_text
    assert "## Drift Gate" in index_text
    assert "Drift gate pass: `True`" in index_text
    assert "Drift gate violations: `0`" in index_text
    assert "Drift gate not_measured: `0`" in index_text
    assert "## API Performance Drift" in index_text
    assert "API performance drift pass: `True`" in index_text
    assert "API performance drift violations: `0`" in index_text
    assert "## Monitoring Rule Metrics" in index_text
    assert "Rule metric reference pass: `True`" in index_text
    assert "Rule metric reference violations: `0`" in index_text
    assert "## AkShare Market Gate" in index_text
    assert "AkShare module import: `True`" in index_text
    assert "AkShare module version: `1.18.10`" in index_text
    assert "AkShare tracked / available / missing: `9 / 4 / 5`" in index_text
    assert "AkShare gate bundle pass: `True`" in index_text
    assert "AkShare repo-truth gate pass: `True`" in index_text
    assert "AkShare repo-truth violations: `0`" in index_text
    assert "## Container Deployment Contract" in index_text
    assert "Container deployment contract pass: `True`" in index_text
    assert "Container deployment contract violations: `0`" in index_text
    assert "## Deployment Env Contract" in index_text
    assert "Deployment env contract pass: `True`" in index_text
    assert "Deployment env contract violations: `0`" in index_text
    assert "Dashboard files checked: `2`" in index_text
    assert "Docker runtime smoke: `PASS` / `PASS` / `PASS`" in index_text
    assert f"Frontend runtime gate report: `{frontend_dir / 'frontend-runtime-gate.json'}`" in index_text
    assert f"Docker runtime summary: `{docker_dir / 'SUMMARY.md'}`" in index_text
    assert f"Docker runtime report: `{docker_dir / 'docker-runtime-smoke.json'}`" in index_text
    assert "Docker metrics health: `healthy`" in index_text
    assert "Docker metrics http / slow delta: `3.0 / 0.0`" in index_text


def test_build_runtime_ci_bundle_supports_docker_only_runtime_summary(tmp_path: Path):
    runtime_quality_dir = tmp_path / "runtime-quality"
    docker_dir = tmp_path / "docker-runtime"
    drift_report_path = tmp_path / "runtime-observability-drift-report.json"
    monitoring_rule_report_path = tmp_path / "monitoring-rule-metric-reference-report.json"
    akshare_availability_report_path = tmp_path / "akshare-market-function-availability.json"
    akshare_repo_truth_report_path = tmp_path / "akshare-market-repo-truth-gate.json"
    akshare_gate_summary_report_path = tmp_path / "akshare-market-gates-summary.json"

    runtime_quality_dir.mkdir()
    docker_dir.mkdir()

    (runtime_quality_dir / "SUMMARY.md").write_text(
        "\n".join(
            [
                "# Runtime Quality Summary",
                "- Overall gate status: `PASS`",
                "- Anonymous API baseline: `n/a`",
                "- Monitoring auth baseline: `n/a`",
                "- Prometheus `slow_http_requests_total` delta during run: `n/a`",
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
                "- Prometheus `http_requests_total` delta during run: `5.0`",
                "- Prometheus `slow_http_requests_total` delta during run: `0.0`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (docker_dir / "docker-runtime-smoke.json").write_text(
        json.dumps(
            {
                "metric_version": "v1",
                "service_urls": {"backend": "http://localhost:8021", "frontend": "http://localhost:3021"},
                "checks": {
                    "backend_health": "PASS",
                    "backend_readiness": "PASS",
                    "frontend_index": "PASS",
                },
                "metrics_health": "healthy",
                "prometheus_snapshot": {
                    "http_requests_total_delta": 5.0,
                    "slow_http_requests_total_delta": 0.0,
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    drift_report_path.write_text(
        json.dumps(
            {
                "generated_at": "2026-04-21T08:00:00+00:00",
                "metric_version": "v1",
                "baseline_generated_at": "2026-04-20T10:24:00+00:00",
                "current_generated_at": "2026-04-21T08:00:00+00:00",
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
                "generated_at": "2026-04-21T08:01:00+00:00",
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
    akshare_availability_report_path.write_text(
        json.dumps(
            {
                "module": "akshare",
                "import_ok": True,
                "module_version": "1.18.10",
                "summary": {"tracked_count": 9, "available_count": 4, "missing_count": 5},
            }
        )
        + "\n",
        encoding="utf-8",
    )
    akshare_repo_truth_report_path.write_text(
        json.dumps(
            {
                "pass": True,
                "summary": {"tracked_count": 9, "passed_count": 9, "failed_count": 0, "violation_count": 0},
                "violations": [],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    akshare_gate_summary_report_path.write_text(
        json.dumps(
            {
                "pass": True,
                "availability_exit_code": 0,
                "repo_truth_exit_code": 0,
                "summary": {
                    "tracked_count": 9,
                    "available_count": 4,
                    "missing_count": 5,
                    "repo_truth_passed_count": 9,
                    "repo_truth_failed_count": 0,
                    "repo_truth_violation_count": 0,
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    manifest_path = tmp_path / "bundle" / "runtime-artifact-manifest.json"
    index_path = tmp_path / "bundle" / "runtime-artifact-index.md"

    subprocess.run(
        [
            "python",
            "scripts/dev/quality_gate/build_runtime_ci_bundle.py",
            "--runtime-quality-dir",
            str(runtime_quality_dir),
            "--docker-dir",
            str(docker_dir),
            "--runtime-observability-drift-report",
            str(drift_report_path),
            "--monitoring-rule-report",
            str(monitoring_rule_report_path),
            "--akshare-market-function-availability-report",
            str(akshare_availability_report_path),
            "--akshare-market-repo-truth-report",
            str(akshare_repo_truth_report_path),
            "--akshare-market-gates-summary-report",
            str(akshare_gate_summary_report_path),
            "--output-manifest",
            str(manifest_path),
            "--output-index",
            str(index_path),
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=True,
    )

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    index_text = index_path.read_text(encoding="utf-8")

    assert "frontend_runtime_dir" not in manifest
    assert "api_performance_dir" not in manifest
    assert "monitoring_auth_dir" not in manifest
    assert manifest["docker_runtime_dir"] == str(docker_dir.resolve())
    assert manifest["docker_runtime_report"] == str((docker_dir / "docker-runtime-smoke.json").resolve())
    assert manifest["runtime_observability_drift_report"] == str(drift_report_path.resolve())
    assert manifest["monitoring_rule_report"] == str(monitoring_rule_report_path.resolve())
    assert manifest["akshare_market_function_availability_report"] == str(akshare_availability_report_path.resolve())
    assert manifest["akshare_market_repo_truth_report"] == str(akshare_repo_truth_report_path.resolve())
    assert manifest["akshare_market_gates_summary_report"] == str(akshare_gate_summary_report_path.resolve())
    assert "Frontend runtime summary" not in index_text
    assert "API performance summary" not in index_text
    assert "Monitoring auth summary" not in index_text
    assert "Runtime observability drift report" in index_text
    assert "Monitoring rule metric reference report" in index_text
    assert "AkShare function availability report" in index_text
    assert "AkShare repo-truth gate report" in index_text
    assert "AkShare gate summary report" in index_text
    assert "Drift gate not_measured: `1`" in index_text
    assert "Docker runtime smoke: `PASS` / `PASS` / `PASS`" in index_text
    assert f"Docker runtime report: `{docker_dir / 'docker-runtime-smoke.json'}`" in index_text
    assert "Docker metrics http / slow delta: `5.0 / 0.0`" in index_text
