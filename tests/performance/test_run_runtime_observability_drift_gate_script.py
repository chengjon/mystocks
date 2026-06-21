import json
import os
import subprocess
from pathlib import Path


def _baseline_payload() -> dict:
    return {
        "generated_at": "2026-04-20T10:24:00+00:00",
        "metric_version": "v1",
        "overall_gate_status": "PASS",
        "frontend_runtime": {"type_errors_current": 0},
        "api_performance": {
            "overall_p95_ms": 22.94,
            "observability_status": "healthy",
            "slow_http_requests_total_delta": 0.0,
            "technical_analysis_history_fallback_total_delta": 1.0,
            "technical_analysis_history_fallback_ratio_delta": 0.25,
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


def _summary_payload() -> dict:
    return {
        "generated_at": "2026-04-21T02:18:35.227140+00:00",
        "overall_gate_status": "PASS",
        "frontend_runtime": {
            "current_frontend_type_errors": 0,
            "repo_frontend_type_error_baseline": 0,
        },
        "api_performance": {
            "overall_p95_ms": 22.94,
            "observability_status": "healthy",
            "slow_http_requests_total_delta": 0.0,
            "technical_analysis_history_fallback_total_delta": 1.0,
            "technical_analysis_history_fallback_ratio_delta": 0.25,
        },
        "monitoring_auth_performance": {
            "alert_rules": {"p95_ms": 271.53},
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


def test_run_runtime_observability_drift_gate_script_has_stable_entrypoint_contract():
    script = Path("scripts/run_runtime_observability_drift_gate.sh").read_text(encoding="utf-8")

    assert 'BASELINE_PATH="${RUNTIME_OBSERVABILITY_BASELINE_JSON:-${PROJECT_ROOT}/reports/analysis/runtime-observability-baseline.json}"' in script
    assert 'SUMMARY_JSON="${RUNTIME_QUALITY_SUMMARY_JSON:-}"' in script
    assert 'CURRENT_OBSERVABILITY_JSON="${RUNTIME_OBSERVABILITY_CURRENT_JSON:-}"' in script
    assert 'OUTPUT_PATH="${RUNTIME_OBSERVABILITY_DRIFT_REPORT_JSON:-}"' in script
    assert 'resolve_latest_summary_json()' in script
    assert 'reports/analysis/runtime-quality-summary/*/summary.json' in script
    assert 'python "${PROJECT_ROOT}/scripts/dev/quality_gate/validate_runtime_observability_drift.py"' in script
    assert '--baseline "${BASELINE_PATH}"' in script
    assert '--output "${OUTPUT_PATH}"' in script
    assert '--current-summary-json "${SUMMARY_JSON}"' in script
    assert '--current-observability-json "${CURRENT_OBSERVABILITY_JSON}"' in script


def test_run_runtime_observability_drift_gate_script_writes_report_next_to_summary(tmp_path: Path):
    baseline_path = tmp_path / "runtime-observability-baseline.json"
    summary_dir = tmp_path / "runtime-quality-summary" / "20260424-030000"
    summary_dir.mkdir(parents=True)
    summary_path = summary_dir / "summary.json"

    baseline_path.write_text(json.dumps(_baseline_payload()) + "\n", encoding="utf-8")
    summary_path.write_text(json.dumps(_summary_payload()) + "\n", encoding="utf-8")

    subprocess.run(
        ["bash", "scripts/run_runtime_observability_drift_gate.sh"],
        cwd=Path(__file__).resolve().parents[2],
        env={
            **os.environ,
            "RUNTIME_OBSERVABILITY_BASELINE_JSON": str(baseline_path),
            "RUNTIME_QUALITY_SUMMARY_JSON": str(summary_path),
        },
        check=True,
    )

    report_path = summary_dir / "runtime-observability-drift-report.json"
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["pass"] is True
    assert payload["current_source"] == str(summary_path.resolve())


def test_run_runtime_observability_drift_gate_script_fails_on_regression(tmp_path: Path):
    baseline_path = tmp_path / "runtime-observability-baseline.json"
    summary_dir = tmp_path / "runtime-quality-summary" / "20260424-030100"
    summary_dir.mkdir(parents=True)
    summary_path = summary_dir / "summary.json"

    summary_payload = _summary_payload()
    summary_payload["monitoring_auth_performance"]["alert_rules"]["p95_ms"] = 299.99
    summary_payload["api_performance"]["overall_p95_ms"] = 40.0

    baseline_path.write_text(json.dumps(_baseline_payload()) + "\n", encoding="utf-8")
    summary_path.write_text(json.dumps(summary_payload) + "\n", encoding="utf-8")

    proc = subprocess.run(
        ["bash", "scripts/run_runtime_observability_drift_gate.sh"],
        cwd=Path(__file__).resolve().parents[2],
        env={
            **os.environ,
            "RUNTIME_OBSERVABILITY_BASELINE_JSON": str(baseline_path),
            "RUNTIME_QUALITY_SUMMARY_JSON": str(summary_path),
        },
        check=False,
        capture_output=True,
        text=True,
    )

    report_path = summary_dir / "runtime-observability-drift-report.json"
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert proc.returncode == 1
    assert payload["pass"] is False
    assert any(item["path"] == "api_performance.overall_p95_ms" for item in payload["violations"])
