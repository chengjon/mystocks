from pathlib import Path


def test_run_monitoring_auth_performance_baseline_script_emits_graphiti_closeout() -> None:
    script = Path("scripts/run_monitoring_auth_performance_baseline.sh").read_text(encoding="utf-8")

    assert 'GRAPHITI_CLOSEOUT_REPORT="${REPORT_DIR}/monitoring-auth-performance-gate-graphiti-closeout.json"' in script
    assert 'python "${PROJECT_ROOT}/scripts/runtime/record_quality_gate_closeout.py" \\' in script
    assert '--gate-kind monitoring-auth-performance-gate \\' in script
    assert 'if [ "${DISABLE_QUALITY_GATE_GRAPHITI_CLOSEOUT:-0}" = "1" ]; then' in script
    assert '$(realpath --relative-to="${PROJECT_ROOT}" "${GRAPHITI_CLOSEOUT_REPORT}")' in script
