import json
import subprocess
from pathlib import Path


def _build_baseline_payload() -> dict:
    return {
        "generated_at": "2026-04-20T10:24:00+00:00",
        "metric_version": "v1",
        "source_summary_json": "/opt/claude/mystocks_spec/reports/analysis/runtime-quality-summary/20260420-161835/summary.json",
        "source_generated_at": "2026-04-20T08:18:35.227140+00:00",
        "service_urls": {
            "backend": "http://localhost:8020",
            "frontend": "http://localhost:3020",
        },
        "overall_gate_status": "PASS",
        "frontend_runtime": {
            "structural_gate": "14 passed (4.4s)",
            "type_errors_current": 0,
            "type_errors_baseline": 0,
            "regression_e2e": {"passed": 44, "failed": 0, "skipped": 0},
            "accessibility_smoke": {"passed": 4, "failed": 0, "skipped": 0},
            "regression_pytest": {"passed": 46, "failed": 0, "skipped": 18},
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
            "trading_status_p95_ms": 13.7,
            "trading_market_snapshot_p95_ms": 10.84,
            "trading_risk_metrics_p95_ms": 12.9,
        },
        "monitoring_auth_performance": {
            "slo_status": "COMPLIANT",
            "observability_status": "healthy",
            "slow_http_requests_total_delta": 0,
            "alert_rules_p95_ms": 271.53,
            "alerts_p95_ms": 144.19,
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


def _build_summary_payload() -> dict:
    return {
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
        "existing_debt": [],
    }


def test_validate_runtime_observability_drift_passes_for_non_regressed_summary(tmp_path: Path):
    baseline_path = tmp_path / "runtime-observability-baseline.json"
    summary_path = tmp_path / "summary.json"
    output_path = tmp_path / "runtime-observability-drift-report.json"

    baseline_path.write_text(json.dumps(_build_baseline_payload(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary_path.write_text(json.dumps(_build_summary_payload(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    subprocess.run(
        [
            "python",
            "scripts/dev/quality_gate/validate_runtime_observability_drift.py",
            "--baseline",
            str(baseline_path),
            "--current-summary-json",
            str(summary_path),
            "--output",
            str(output_path),
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=True,
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["pass"] is True
    assert payload["violations"] == []
    assert payload["checks"][0]["path"] == "overall_gate_status"


def test_validate_runtime_observability_drift_fails_on_p95_regression(tmp_path: Path):
    baseline_path = tmp_path / "runtime-observability-baseline.json"
    summary_path = tmp_path / "summary.json"
    output_path = tmp_path / "runtime-observability-drift-report.json"

    summary_payload = _build_summary_payload()
    summary_payload["api_performance"]["overall_p95_ms"] = 45.0

    baseline_path.write_text(json.dumps(_build_baseline_payload(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary_path.write_text(json.dumps(summary_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    proc = subprocess.run(
        [
            "python",
            "scripts/dev/quality_gate/validate_runtime_observability_drift.py",
            "--baseline",
            str(baseline_path),
            "--current-summary-json",
            str(summary_path),
            "--output",
            str(output_path),
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=False,
        capture_output=True,
        text=True,
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert proc.returncode == 1
    assert payload["pass"] is False
    assert any(item["path"] == "api_performance.overall_p95_ms" for item in payload["violations"])


def test_validate_runtime_observability_drift_fails_on_technical_analysis_fallback_regression(tmp_path: Path):
    baseline_path = tmp_path / "runtime-observability-baseline.json"
    summary_path = tmp_path / "summary.json"
    output_path = tmp_path / "runtime-observability-drift-report.json"

    summary_payload = _build_summary_payload()
    summary_payload["api_performance"]["technical_analysis_history_fallback_total_delta"] = 3.0
    summary_payload["api_performance"]["technical_analysis_history_fallback_ratio_delta"] = 0.75

    baseline_path.write_text(json.dumps(_build_baseline_payload(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary_path.write_text(json.dumps(summary_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    proc = subprocess.run(
        [
            "python",
            "scripts/dev/quality_gate/validate_runtime_observability_drift.py",
            "--baseline",
            str(baseline_path),
            "--current-summary-json",
            str(summary_path),
            "--output",
            str(output_path),
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=False,
        capture_output=True,
        text=True,
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert proc.returncode == 1
    assert payload["pass"] is False
    assert any(
        item["path"] == "api_performance.technical_analysis_history_fallback_total_delta"
        for item in payload["violations"]
    )


def test_validate_runtime_observability_drift_fails_when_docker_request_delta_drops(tmp_path: Path):
    baseline_path = tmp_path / "runtime-observability-baseline.json"
    current_path = tmp_path / "runtime-observability-current.json"
    output_path = tmp_path / "runtime-observability-drift-report.json"

    current_payload = _build_baseline_payload()
    current_payload["generated_at"] = "2026-04-21T03:00:00+00:00"
    current_payload["docker_runtime"]["http_requests_total_delta"] = 3.0

    baseline_path.write_text(json.dumps(_build_baseline_payload(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    current_path.write_text(json.dumps(current_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    proc = subprocess.run(
        [
            "python",
            "scripts/dev/quality_gate/validate_runtime_observability_drift.py",
            "--baseline",
            str(baseline_path),
            "--current-observability-json",
            str(current_path),
            "--output",
            str(output_path),
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=False,
        capture_output=True,
        text=True,
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert proc.returncode == 1
    assert payload["pass"] is False
    assert any(item["path"] == "docker_runtime.http_requests_total_delta" for item in payload["violations"])


def test_validate_runtime_observability_drift_skips_unmeasured_scopes_for_docker_only_summary(tmp_path: Path):
    baseline_path = tmp_path / "runtime-observability-baseline.json"
    summary_path = tmp_path / "summary.json"
    output_path = tmp_path / "runtime-observability-drift-report.json"

    docker_only_summary = {
        "generated_at": "2026-04-21T04:18:35.227140+00:00",
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
            "db_connections_active": {"postgresql": 8.0, "tdengine": 2.0, "redis": 1.0},
        },
        "current_batch_issues": [],
        "existing_debt": [],
    }

    baseline_path.write_text(json.dumps(_build_baseline_payload(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary_path.write_text(json.dumps(docker_only_summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    subprocess.run(
        [
            "python",
            "scripts/dev/quality_gate/validate_runtime_observability_drift.py",
            "--baseline",
            str(baseline_path),
            "--current-summary-json",
            str(summary_path),
            "--output",
            str(output_path),
        ],
        cwd=Path(__file__).resolve().parents[2],
        check=True,
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["pass"] is True
    assert any(item["path"] == "api_performance.overall_p95_ms" for item in payload["not_measured"])
