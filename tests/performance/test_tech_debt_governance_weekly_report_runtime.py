import json
import subprocess
from pathlib import Path


def test_weekly_report_includes_runtime_observability_kpis(tmp_path: Path):
    baseline_path = tmp_path / "tech-debt-baseline.json"
    current_path = tmp_path / "tech-debt-current.json"
    runtime_baseline_path = tmp_path / "runtime-observability-baseline.json"
    api_performance_baseline_path = tmp_path / "api-performance-baseline.json"
    runtime_summary_path = tmp_path / "runtime-quality-summary.json"
    runtime_gate_closeout_path = tmp_path / "runtime-delivery-gate-graphiti-closeout.json"
    frontend_gate_closeout_path = tmp_path / "frontend-runtime-gate-graphiti-closeout.json"
    api_gate_closeout_path = tmp_path / "api-performance-gate-graphiti-closeout.json"
    monitoring_gate_closeout_path = tmp_path / "monitoring-auth-performance-gate-graphiti-closeout.json"
    docker_gate_closeout_path = tmp_path / "docker-runtime-smoke-graphiti-closeout.json"
    output_path = tmp_path / "tech-debt-weekly-report.md"

    baseline_path.write_text(
        json.dumps(
            {
                "frontend_type_errors": 0,
                "frontend_suppressions_count": 0,
                "skip_xfail_count": 0,
                "backend_api_documentation": {
                    "json_success_missing_examples": 0,
                    "non_json_success_responses": 0,
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    current_path.write_text(
        json.dumps(
            {
                "frontend_type_errors": 0,
                "frontend_suppressions_count": 0,
                "skip_xfail_count": 0,
                "backend_api_documentation": {
                    "json_success_missing_examples": 0,
                    "non_json_success_responses": 0,
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
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
                    "technical_analysis_history_requests_total_delta": 3.0,
                    "technical_analysis_history_fallback_total_delta": 0.0,
                    "technical_analysis_history_fallback_ratio_delta": 0.0,
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
                "service_urls": {
                    "backend": "http://localhost:8020",
                    "frontend": "http://localhost:3020",
                },
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
                    "technical_analysis_history_requests_total_delta": 5.0,
                    "technical_analysis_history_fallback_total_delta": 1.0,
                    "technical_analysis_history_fallback_ratio_delta": 0.5,
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
    api_performance_baseline_path.write_text(
        json.dumps(
            {
                "generated_at": "2026-04-22T00:00:00+00:00",
                "overall_p95_ms": 22.94,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    runtime_gate_closeout_path.write_text(
        json.dumps({"status": "completed", "episode_uuid": "ep-runtime", "group_id": "mystocks_spec_runtime_delivery_gates", "ingest_status": "warming"}) + "\n",
        encoding="utf-8",
    )
    frontend_gate_closeout_path.write_text(
        json.dumps({"status": "completed", "episode_uuid": "ep-frontend", "group_id": "mystocks_spec_quality_gates", "ingest_status": "warming"}) + "\n",
        encoding="utf-8",
    )
    api_gate_closeout_path.write_text(
        json.dumps({"status": "completed", "episode_uuid": "ep-api", "group_id": "mystocks_spec_quality_gates", "ingest_status": "warming"}) + "\n",
        encoding="utf-8",
    )
    monitoring_gate_closeout_path.write_text(
        json.dumps({"status": "completed", "episode_uuid": "ep-monitoring", "group_id": "mystocks_spec_quality_gates", "ingest_status": "warming"}) + "\n",
        encoding="utf-8",
    )
    docker_gate_closeout_path.write_text(
        json.dumps({"status": "completed", "episode_uuid": "ep-docker", "group_id": "mystocks_spec_quality_gates", "ingest_status": "warming"}) + "\n",
        encoding="utf-8",
    )

    subprocess.run(
        [
            "python",
            "scripts/dev/quality_gate/tech_debt_governance_gate.py",
            "weekly-report",
            "--baseline",
            str(baseline_path),
            "--current",
            str(current_path),
            "--runtime-baseline",
            str(runtime_baseline_path),
            "--api-performance-baseline",
            str(api_performance_baseline_path),
            "--runtime-summary-json",
            str(runtime_summary_path),
            "--runtime-gate-closeout-json",
            str(runtime_gate_closeout_path),
            "--frontend-gate-closeout-json",
            str(frontend_gate_closeout_path),
            "--api-gate-closeout-json",
            str(api_gate_closeout_path),
            "--monitoring-gate-closeout-json",
            str(monitoring_gate_closeout_path),
            "--docker-gate-closeout-json",
            str(docker_gate_closeout_path),
            "--threshold",
            "999999",
            "--top-n",
            "1",
            "--output",
            str(output_path),
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=True,
    )

    report_text = output_path.read_text(encoding="utf-8")
    assert "## 4. Runtime Observability KPI" in report_text
    assert "## 4.1 Graphiti Gate Closeouts" in report_text
    assert "Runtime delivery gate: status=`completed` episode_uuid=`ep-runtime`" in report_text
    assert "Frontend runtime gate: status=`completed` episode_uuid=`ep-frontend`" in report_text
    assert "API performance gate: status=`completed` episode_uuid=`ep-api`" in report_text
    assert "Monitoring auth performance gate: status=`completed` episode_uuid=`ep-monitoring`" in report_text
    assert "Docker runtime smoke: status=`completed` episode_uuid=`ep-docker`" in report_text
    assert "PM2 runtime overall gate status: measured=`PASS` baseline=`PASS` target=`PASS`" in report_text
    assert "Anonymous API overall P95 (ms): measured=`22.94` baseline=`22.94` target=`<= 300`" in report_text
    assert "API performance drift gate: measured=`PASS` baseline=`PASS` target=`PASS`" in report_text
    assert "API performance drift violations: measured=`0` baseline=`0` target=`0`" in report_text
    assert "Technical analysis history requests delta: measured=`5.0` baseline=`3.0` target=`>= baseline`" in report_text
    assert "Technical analysis fallback total delta: measured=`1.0` baseline=`0.0` target=`<= baseline`" in report_text
    assert "Technical analysis fallback ratio delta: measured=`0.5` baseline=`0.0` target=`<= baseline + 1.0`" in report_text
    assert "Graphiti closeout coverage: `5/5` valid closeouts, missing=`0` invalid=`0`" in report_text
    assert "Graphiti closeout validity gate: `PASS`" in report_text
    assert "Monitoring auth alert-rules P95 (ms): measured=`271.53` baseline=`271.53` target=`<= 300`" in report_text
    assert "Docker runtime smoke status: measured=`PASS/PASS/PASS` baseline=`PASS/PASS/PASS` target=`PASS/PASS/PASS`" in report_text
    assert "Runtime drift gate: `FAIL` violations=`2` not_measured=`0`" in report_text


def test_weekly_report_degrades_invalid_closeout_payload_to_report_line(tmp_path: Path):
    baseline_path = tmp_path / "tech-debt-baseline.json"
    current_path = tmp_path / "tech-debt-current.json"
    runtime_baseline_path = tmp_path / "runtime-observability-baseline.json"
    api_performance_baseline_path = tmp_path / "api-performance-baseline.json"
    runtime_summary_path = tmp_path / "runtime-quality-summary.json"
    frontend_gate_closeout_path = tmp_path / "frontend-runtime-gate-graphiti-closeout.json"
    output_path = tmp_path / "tech-debt-weekly-report.md"

    baseline_payload = {
        "frontend_type_errors": 0,
        "frontend_suppressions_count": 0,
        "skip_xfail_count": 0,
        "backend_api_documentation": {
            "json_success_missing_examples": 0,
            "non_json_success_responses": 0,
        },
    }
    runtime_payload = {
        "generated_at": "2026-04-21T02:18:35.227140+00:00",
        "service_urls": {"backend": "http://localhost:8020", "frontend": "http://localhost:3020"},
        "overall_gate_status": "PASS",
        "frontend_runtime": {"current_frontend_type_errors": 0, "repo_frontend_type_error_baseline": 0},
        "api_performance": {"overall_p95_ms": 22.94, "observability_status": "healthy"},
        "monitoring_auth_performance": {"alert_rules": {"p95_ms": 271.53}, "observability_status": "healthy"},
        "docker_runtime": {
            "backend_health": "PASS",
            "backend_readiness": "PASS",
            "frontend_index": "PASS",
            "metrics_health": "healthy",
        },
        "api_performance_drift": {"pass": True, "violations": []},
    }

    baseline_path.write_text(json.dumps(baseline_payload) + "\n", encoding="utf-8")
    current_path.write_text(json.dumps(baseline_payload) + "\n", encoding="utf-8")
    runtime_baseline_path.write_text(json.dumps(runtime_payload) + "\n", encoding="utf-8")
    runtime_summary_path.write_text(json.dumps(runtime_payload) + "\n", encoding="utf-8")
    api_performance_baseline_path.write_text(json.dumps({"overall_p95_ms": 22.94}) + "\n", encoding="utf-8")
    frontend_gate_closeout_path.write_text("", encoding="utf-8")

    subprocess.run(
        [
            "python",
            "scripts/dev/quality_gate/tech_debt_governance_gate.py",
            "weekly-report",
            "--baseline",
            str(baseline_path),
            "--current",
            str(current_path),
            "--runtime-baseline",
            str(runtime_baseline_path),
            "--api-performance-baseline",
            str(api_performance_baseline_path),
            "--runtime-summary-json",
            str(runtime_summary_path),
            "--frontend-gate-closeout-json",
            str(frontend_gate_closeout_path),
            "--threshold",
            "999999",
            "--top-n",
            "1",
            "--output",
            str(output_path),
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=True,
    )

    report_text = output_path.read_text(encoding="utf-8")
    assert "Graphiti closeout validity gate: `FAIL`" in report_text
    assert "Frontend runtime gate: status=`invalid_payload`" in report_text
    assert "ingest_status=`not_loaded`" in report_text


def test_weekly_report_fails_when_closeout_gate_enabled_and_payload_invalid(tmp_path: Path):
    baseline_path = tmp_path / "tech-debt-baseline.json"
    current_path = tmp_path / "tech-debt-current.json"
    runtime_baseline_path = tmp_path / "runtime-observability-baseline.json"
    api_performance_baseline_path = tmp_path / "api-performance-baseline.json"
    runtime_summary_path = tmp_path / "runtime-quality-summary.json"
    frontend_gate_closeout_path = tmp_path / "frontend-runtime-gate-graphiti-closeout.json"
    output_path = tmp_path / "tech-debt-weekly-report.md"

    baseline_payload = {
        "frontend_type_errors": 0,
        "frontend_suppressions_count": 0,
        "skip_xfail_count": 0,
        "backend_api_documentation": {
            "json_success_missing_examples": 0,
            "non_json_success_responses": 0,
        },
    }
    runtime_payload = {
        "generated_at": "2026-04-21T02:18:35.227140+00:00",
        "service_urls": {"backend": "http://localhost:8020", "frontend": "http://localhost:3020"},
        "overall_gate_status": "PASS",
        "frontend_runtime": {"current_frontend_type_errors": 0, "repo_frontend_type_error_baseline": 0},
        "api_performance": {"overall_p95_ms": 22.94, "observability_status": "healthy"},
        "monitoring_auth_performance": {"alert_rules": {"p95_ms": 271.53}, "observability_status": "healthy"},
        "docker_runtime": {
            "backend_health": "PASS",
            "backend_readiness": "PASS",
            "frontend_index": "PASS",
            "metrics_health": "healthy",
        },
        "api_performance_drift": {"pass": True, "violations": []},
    }

    baseline_path.write_text(json.dumps(baseline_payload) + "\n", encoding="utf-8")
    current_path.write_text(json.dumps(baseline_payload) + "\n", encoding="utf-8")
    runtime_baseline_path.write_text(json.dumps(runtime_payload) + "\n", encoding="utf-8")
    runtime_summary_path.write_text(json.dumps(runtime_payload) + "\n", encoding="utf-8")
    api_performance_baseline_path.write_text(json.dumps({"overall_p95_ms": 22.94}) + "\n", encoding="utf-8")
    frontend_gate_closeout_path.write_text("", encoding="utf-8")

    completed = subprocess.run(
        [
            "python",
            "scripts/dev/quality_gate/tech_debt_governance_gate.py",
            "weekly-report",
            "--baseline",
            str(baseline_path),
            "--current",
            str(current_path),
            "--runtime-baseline",
            str(runtime_baseline_path),
            "--api-performance-baseline",
            str(api_performance_baseline_path),
            "--runtime-summary-json",
            str(runtime_summary_path),
            "--frontend-gate-closeout-json",
            str(frontend_gate_closeout_path),
            "--fail-on-invalid-closeouts",
            "--threshold",
            "999999",
            "--top-n",
            "1",
            "--output",
            str(output_path),
        ],
        cwd=Path(__file__).resolve().parents[2],
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 1
    assert "invalid Graphiti gate closeouts detected" in completed.stdout
    assert output_path.exists()
