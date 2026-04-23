import json
import os
import subprocess
from pathlib import Path


def test_tech_debt_weekly_report_script_has_stable_entrypoint_contract():
    script = Path("scripts/run_tech_debt_weekly_report.sh").read_text(encoding="utf-8")

    assert 'REPORT_DIR="${TECH_DEBT_WEEKLY_REPORT_DIR:-${PROJECT_ROOT}/reports/analysis/tech-debt-weekly-report-local}"' in script
    assert 'CURRENT_METRICS_PATH="${TECH_DEBT_CURRENT_JSON:-${REPORT_DIR}/tech-debt-current-${TIMESTAMP}.json}"' in script
    assert 'RUNTIME_BASELINE_PATH="${RUNTIME_OBSERVABILITY_BASELINE_JSON:-${PROJECT_ROOT}/reports/analysis/runtime-observability-baseline.json}"' in script
    assert 'API_PERFORMANCE_BASELINE_PATH="${API_PERFORMANCE_BASELINE_JSON:-${PROJECT_ROOT}/reports/analysis/api-performance-baseline.json}"' in script
    assert 'RUNTIME_GATE_DIR="${RUNTIME_DELIVERY_GATE_DIR:-}"' in script
    assert 'FRONTEND_GATE_DIR="${FRONTEND_RUNTIME_GATE_DIR:-}"' in script
    assert 'API_GATE_DIR="${API_PERFORMANCE_GATE_DIR:-}"' in script
    assert 'DOCKER_GATE_DIR="${DOCKER_RUNTIME_GATE_DIR:-${DOCKER_RUNTIME_DIR:-}}"' in script
    assert 'RUNTIME_GATE_CLOSEOUT_JSON="${RUNTIME_GATE_CLOSEOUT_JSON:-}"' in script
    assert 'FRONTEND_GATE_CLOSEOUT_JSON="${FRONTEND_GATE_CLOSEOUT_JSON:-}"' in script
    assert 'API_GATE_CLOSEOUT_JSON="${API_GATE_CLOSEOUT_JSON:-}"' in script
    assert 'DOCKER_GATE_CLOSEOUT_JSON="${DOCKER_GATE_CLOSEOUT_JSON:-}"' in script
    assert 'REQUIRE_VALID_CLOSEOUTS="${TECH_DEBT_WEEKLY_REQUIRE_VALID_CLOSEOUTS:-1}"' in script
    assert 'python "${PROJECT_ROOT}/scripts/dev/quality_gate/collect_tech_debt_baseline.py" --output "${CURRENT_METRICS_PATH}"' in script
    assert 'python "${PROJECT_ROOT}/scripts/dev/quality_gate/tech_debt_governance_gate.py"' in script
    assert '--api-performance-baseline "${API_PERFORMANCE_BASELINE_PATH}"' in script
    assert 'if [ -n "${RUNTIME_GATE_DIR}" ] && [ -z "${RUNTIME_SUMMARY_JSON}" ]; then' in script
    assert 'resolve_latest_dir()' in script
    assert 'if [ -n "${RUNTIME_GATE_CLOSEOUT_JSON}" ]; then' in script
    assert 'if [ -n "${FRONTEND_GATE_CLOSEOUT_JSON}" ]; then' in script
    assert 'if [ -n "${API_GATE_CLOSEOUT_JSON}" ]; then' in script
    assert 'if [ -n "${DOCKER_GATE_CLOSEOUT_JSON}" ]; then' in script
    assert 'if [ "${REQUIRE_VALID_CLOSEOUTS}" = "1" ] || [ "${REQUIRE_VALID_CLOSEOUTS}" = "true" ]; then' in script
    assert 'cmd+=(--fail-on-invalid-closeouts)' in script
    assert 'if [ -n "${RUNTIME_SUMMARY_JSON}" ]; then' in script
    assert 'if [ -n "${RUNTIME_CURRENT_JSON}" ]; then' in script


def test_tech_debt_weekly_report_script_generates_runtime_kpi_report(tmp_path: Path):
    report_dir = tmp_path / "weekly-report"
    current_path = tmp_path / "tech-debt-current.json"
    baseline_path = tmp_path / "tech-debt-baseline.json"
    runtime_baseline_path = tmp_path / "runtime-observability-baseline.json"
    api_performance_baseline_path = tmp_path / "api-performance-baseline.json"
    runtime_summary_path = tmp_path / "runtime-quality-summary.json"
    output_path = report_dir / "weekly-report.md"

    report_dir.mkdir()
    current_payload = {
        "frontend_type_errors": 0,
        "frontend_suppressions_count": 0,
        "skip_xfail_count": 0,
        "backend_api_documentation": {
            "json_success_missing_examples": 0,
            "non_json_success_responses": 0,
        },
    }
    baseline_path.write_text(json.dumps(current_payload) + "\n", encoding="utf-8")
    current_path.write_text(json.dumps(current_payload) + "\n", encoding="utf-8")
    runtime_baseline_path.write_text(
        json.dumps(
            {
                "generated_at": "2026-04-20T10:24:00+00:00",
                "overall_gate_status": "PASS",
                "frontend_runtime": {"type_errors_current": 0},
                "api_performance": {
                    "overall_p95_ms": 22.94,
                    "observability_status": "healthy",
                    "slow_http_requests_total_delta": 0.0,
                },
                "monitoring_auth_performance": {
                    "alert_rules_p95_ms": 271.53,
                    "observability_status": "healthy",
                    "slow_http_requests_total_delta": 0,
                },
                "docker_runtime": {
                    "backend_health": "PASS",
                    "backend_readiness": "PASS",
                    "frontend_index": "PASS",
                    "metrics_health": "healthy",
                    "http_requests_total_delta": 4.0,
                    "slow_http_requests_total_delta": 0,
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    runtime_summary_path.write_text(
        json.dumps(
            {
                "generated_at": "2026-04-21T02:18:35.227140+00:00",
                "service_urls": {"backend": "http://localhost:8020", "frontend": "http://localhost:3020"},
                "overall_gate_status": "PASS",
                "frontend_runtime": {
                    "structural_gate": "14 passed (4.2s)",
                    "regression_e2e": "E2E Summary: passed=44 failed=0 skipped=0",
                    "accessibility_smoke": "4 passed (12.1s)",
                    "regression_pytest": "Pytest Summary: passed=46 failed=0 skipped=18",
                    "current_frontend_type_errors": 0,
                    "repo_frontend_type_error_baseline": 0,
                },
                "api_performance": {
                    "slo_status": "COMPLIANT",
                    "overall_avg_ms": 19.05,
                    "overall_p95_ms": 22.94,
                    "observability_status": "healthy",
                    "slow_http_requests_total_delta": 0.0,
                    "trading_status": {"p95_ms": 13.7},
                    "trading_market_snapshot": {"p95_ms": 10.84},
                    "trading_risk_metrics": {"p95_ms": 12.9},
                },
                "monitoring_auth_performance": {
                    "slo_status": "COMPLIANT",
                    "observability_status": "healthy",
                    "slow_http_requests_total_delta": 0,
                    "alert_rules": {"p95_ms": 271.53},
                    "alerts": {"p95_ms": 144.19},
                },
                "docker_runtime": {
                    "backend_health": "PASS",
                    "backend_readiness": "PASS",
                    "frontend_index": "PASS",
                    "metrics_health": "healthy",
                    "http_requests_total_delta": 4.0,
                    "slow_http_requests_total_delta": 0,
                    "db_connections_active": {"postgresql": 8.0, "tdengine": 2.0, "redis": 1.0},
                },
                "api_performance_drift": {
                    "pass": True,
                    "violations": [],
                    "absolute_budget_ms": 10.0,
                    "relative_budget_ratio": 0.25,
                },
                "current_batch_issues": [],
                "existing_debt": [],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    api_performance_baseline_path.write_text(json.dumps({"overall_p95_ms": 22.94}) + "\n", encoding="utf-8")

    subprocess.run(
        ["bash", "scripts/run_tech_debt_weekly_report.sh"],
        cwd=Path(__file__).resolve().parents[2],
        env={
            **os.environ,
            "TECH_DEBT_WEEKLY_REPORT_DIR": str(report_dir),
            "TECH_DEBT_WEEKLY_REPORT_OUTPUT": str(output_path),
            "TECH_DEBT_CURRENT_JSON": str(current_path),
            "TECH_DEBT_BASELINE_JSON": str(baseline_path),
            "RUNTIME_OBSERVABILITY_BASELINE_JSON": str(runtime_baseline_path),
            "API_PERFORMANCE_BASELINE_JSON": str(api_performance_baseline_path),
            "RUNTIME_SUMMARY_JSON": str(runtime_summary_path),
            "TECH_DEBT_WEEKLY_THRESHOLD": "999999",
            "TECH_DEBT_WEEKLY_TOP_N": "1",
        },
        check=True,
    )

    report_text = output_path.read_text(encoding="utf-8")
    assert "## 4. Runtime Observability KPI" in report_text
    assert "## 4.1 Graphiti Gate Closeouts" in report_text
    assert "PM2 runtime overall gate status: measured=`PASS` baseline=`PASS` target=`PASS`" in report_text
    assert "API performance drift gate: measured=`PASS` baseline=`PASS` target=`PASS`" in report_text
    assert "Runtime drift gate: `PASS` violations=`0` not_measured=`0`" in report_text


def test_tech_debt_weekly_report_script_can_resolve_runtime_summary_from_gate_dir(tmp_path: Path):
    report_dir = tmp_path / "weekly-report"
    runtime_gate_dir = tmp_path / "runtime-delivery-gate"
    runtime_summary_dir = runtime_gate_dir / "runtime-quality-summary"
    current_path = tmp_path / "tech-debt-current.json"
    baseline_path = tmp_path / "tech-debt-baseline.json"
    runtime_baseline_path = tmp_path / "runtime-observability-baseline.json"
    api_performance_baseline_path = tmp_path / "api-performance-baseline.json"
    output_path = report_dir / "weekly-report.md"

    report_dir.mkdir()
    runtime_summary_dir.mkdir(parents=True)

    current_payload = {
        "frontend_type_errors": 0,
        "frontend_suppressions_count": 0,
        "skip_xfail_count": 0,
        "backend_api_documentation": {
            "json_success_missing_examples": 0,
            "non_json_success_responses": 0,
        },
    }
    baseline_path.write_text(json.dumps(current_payload) + "\n", encoding="utf-8")
    current_path.write_text(json.dumps(current_payload) + "\n", encoding="utf-8")
    runtime_baseline_path.write_text(
        json.dumps(
            {
                "generated_at": "2026-04-20T10:24:00+00:00",
                "overall_gate_status": "PASS",
                "frontend_runtime": {"type_errors_current": 0},
                "api_performance": {
                    "overall_p95_ms": 22.94,
                    "observability_status": "healthy",
                    "slow_http_requests_total_delta": 0.0,
                },
                "monitoring_auth_performance": {
                    "alert_rules_p95_ms": 271.53,
                    "observability_status": "healthy",
                    "slow_http_requests_total_delta": 0,
                },
                "docker_runtime": {
                    "backend_health": "PASS",
                    "backend_readiness": "PASS",
                    "frontend_index": "PASS",
                    "metrics_health": "healthy",
                    "http_requests_total_delta": 4.0,
                    "slow_http_requests_total_delta": 0,
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (runtime_summary_dir / "summary.json").write_text(
        json.dumps(
            {
                "generated_at": "2026-04-21T02:18:35.227140+00:00",
                "service_urls": {"backend": "http://localhost:8020", "frontend": "http://localhost:3020"},
                "overall_gate_status": "PASS",
                "frontend_runtime": {
                    "structural_gate": "14 passed (4.2s)",
                    "regression_e2e": "E2E Summary: passed=44 failed=0 skipped=0",
                    "accessibility_smoke": "4 passed (12.1s)",
                    "regression_pytest": "Pytest Summary: passed=46 failed=0 skipped=18",
                    "current_frontend_type_errors": 0,
                    "repo_frontend_type_error_baseline": 0,
                },
                "api_performance": {
                    "slo_status": "COMPLIANT",
                    "overall_avg_ms": 19.05,
                    "overall_p95_ms": 22.94,
                    "observability_status": "healthy",
                    "slow_http_requests_total_delta": 0.0,
                    "trading_status": {"p95_ms": 13.7},
                    "trading_market_snapshot": {"p95_ms": 10.84},
                    "trading_risk_metrics": {"p95_ms": 12.9},
                },
                "monitoring_auth_performance": {
                    "slo_status": "COMPLIANT",
                    "observability_status": "healthy",
                    "slow_http_requests_total_delta": 0,
                    "alert_rules": {"p95_ms": 271.53},
                    "alerts": {"p95_ms": 144.19},
                },
                "docker_runtime": {
                    "backend_health": "PASS",
                    "backend_readiness": "PASS",
                    "frontend_index": "PASS",
                    "metrics_health": "healthy",
                    "http_requests_total_delta": 4.0,
                    "slow_http_requests_total_delta": 0,
                    "db_connections_active": {"postgresql": 8.0, "tdengine": 2.0, "redis": 1.0},
                },
                "api_performance_drift": {
                    "pass": True,
                    "violations": [],
                    "absolute_budget_ms": 10.0,
                    "relative_budget_ratio": 0.25,
                },
                "current_batch_issues": [],
                "existing_debt": [],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    api_performance_baseline_path.write_text(json.dumps({"overall_p95_ms": 22.94}) + "\n", encoding="utf-8")

    subprocess.run(
        ["bash", "scripts/run_tech_debt_weekly_report.sh"],
        cwd=Path(__file__).resolve().parents[2],
        env={
            **os.environ,
            "TECH_DEBT_WEEKLY_REPORT_DIR": str(report_dir),
            "TECH_DEBT_WEEKLY_REPORT_OUTPUT": str(output_path),
            "TECH_DEBT_CURRENT_JSON": str(current_path),
            "TECH_DEBT_BASELINE_JSON": str(baseline_path),
            "RUNTIME_OBSERVABILITY_BASELINE_JSON": str(runtime_baseline_path),
            "API_PERFORMANCE_BASELINE_JSON": str(api_performance_baseline_path),
            "RUNTIME_DELIVERY_GATE_DIR": str(runtime_gate_dir),
            "TECH_DEBT_WEEKLY_THRESHOLD": "999999",
            "TECH_DEBT_WEEKLY_TOP_N": "1",
        },
        check=True,
    )

    report_text = output_path.read_text(encoding="utf-8")
    assert "Docker runtime smoke status: measured=`PASS/PASS/PASS` baseline=`PASS/PASS/PASS` target=`PASS/PASS/PASS`" in report_text
    assert "API performance drift gate: measured=`PASS` baseline=`PASS` target=`PASS`" in report_text
    assert "Runtime drift gate: `PASS` violations=`0` not_measured=`0`" in report_text
