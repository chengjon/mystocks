import json
import subprocess
from pathlib import Path


def test_collect_runtime_observability_baseline_writes_machine_readable_snapshot(tmp_path: Path):
    summary_payload = {
        "generated_at": "2026-04-20T08:18:35.227140+00:00",
        "service_urls": {
            "backend": "http://localhost:8020",
            "frontend": "http://localhost:3020",
        },
        "overall_gate_status": "PASS",
        "frontend_runtime": {
            "structural_gate": "14 passed (4.4s)",
            "regression_e2e": "E2E Summary: passed=44 failed=0 skipped=0",
            "accessibility_smoke": "4 passed (12.1s)",
            "regression_pytest": "Pytest Summary: passed=46 failed=0 skipped=18",
            "current_frontend_type_errors": 0,
            "repo_frontend_type_error_baseline": 0,
        },
        "api_performance": {
            "slo_status": "COMPLIANT",
            "overall_avg_ms": 18.47,
            "overall_p95_ms": 22.94,
            "observability_status": "healthy",
            "slow_http_requests_total_delta": 0.0,
            "technical_analysis_history_requests_total_delta": 4.0,
            "technical_analysis_history_fallback_total_delta": 1.0,
            "technical_analysis_history_fallback_ratio_delta": 0.25,
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
        "current_batch_issues": [],
        "existing_debt": ["Frontend type debt remains at repository baseline (0) with no new regression"],
    }

    summary_path = tmp_path / "summary.json"
    output_path = tmp_path / "runtime-observability-baseline.json"
    summary_path.write_text(json.dumps(summary_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    subprocess.run(
        [
            "python",
            "scripts/dev/quality_gate/collect_runtime_observability_baseline.py",
            "--summary-json",
            str(summary_path),
            "--output",
            str(output_path),
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=True,
    )

    baseline = json.loads(output_path.read_text(encoding="utf-8"))
    assert baseline["metric_version"] == "v1"
    assert baseline["overall_gate_status"] == "PASS"
    assert baseline["service_urls"]["backend"] == "http://localhost:8020"
    assert baseline["frontend_runtime"]["regression_e2e"]["passed"] == 44
    assert baseline["frontend_runtime"]["accessibility_smoke"]["passed"] == 4
    assert baseline["frontend_runtime"]["regression_pytest"]["skipped"] == 18
    assert baseline["api_performance"]["overall_p95_ms"] == 22.94
    assert baseline["api_performance"]["technical_analysis_history_requests_total_delta"] == 4.0
    assert baseline["api_performance"]["technical_analysis_history_fallback_total_delta"] == 1.0
    assert baseline["api_performance"]["technical_analysis_history_fallback_ratio_delta"] == 0.25
    assert baseline["monitoring_auth_performance"]["alert_rules_p95_ms"] == 271.53
    assert baseline["docker_runtime"]["http_requests_total_delta"] == 4.0
    assert baseline["docker_runtime"]["db_connections_active"]["tdengine"] == 2.0


def test_collect_runtime_observability_baseline_preserves_absent_scopes_as_null(tmp_path: Path):
    summary_payload = {
        "generated_at": "2026-04-21T08:18:35.227140+00:00",
        "service_urls": {
            "backend": "http://localhost:8021",
            "frontend": "http://localhost:3021",
        },
        "overall_gate_status": "PASS",
        "frontend_runtime": None,
        "api_performance": None,
        "monitoring_auth_performance": None,
        "docker_runtime": {
            "backend_health": "PASS",
            "backend_readiness": "PASS",
            "frontend_index": "PASS",
            "metrics_health": "healthy",
            "http_requests_total_delta": 4.0,
            "slow_http_requests_total_delta": 0,
            "db_connections_active": {"postgresql": 8.0},
        },
        "current_batch_issues": [],
        "existing_debt": [],
    }

    summary_path = tmp_path / "summary.json"
    output_path = tmp_path / "runtime-observability-baseline.json"
    summary_path.write_text(json.dumps(summary_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    subprocess.run(
        [
            "python",
            "scripts/dev/quality_gate/collect_runtime_observability_baseline.py",
            "--summary-json",
            str(summary_path),
            "--output",
            str(output_path),
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=True,
    )

    baseline = json.loads(output_path.read_text(encoding="utf-8"))
    assert baseline["frontend_runtime"] is None
    assert baseline["api_performance"] is None
    assert baseline["monitoring_auth_performance"] is None
    assert baseline["docker_runtime"]["backend_health"] == "PASS"
