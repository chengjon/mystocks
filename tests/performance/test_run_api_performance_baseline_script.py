import json
from pathlib import Path


def test_run_api_performance_baseline_script_emits_workload_class_summary_lines() -> None:
    script = Path("scripts/run_api_performance_baseline.sh").read_text(encoding="utf-8")

    assert "Business API average / P95 response time" in script
    assert "Infrastructure API average / P95 response time" in script
    assert '--warmup-requests 3 \\' in script
    assert 'for _ in $(seq 1 3); do' in script
    assert '"http://localhost:8020/health"' in script
    assert '"http://localhost:8020/api/health/ready"' in script
    assert 'GRAPHITI_CLOSEOUT_REPORT="${REPORT_DIR}/api-performance-gate-graphiti-closeout.json"' in script
    assert 'python "${PROJECT_ROOT}/scripts/runtime/record_quality_gate_closeout.py" \\' in script
    assert '--gate-kind api-performance-gate \\' in script
    assert 'if [ "${DISABLE_QUALITY_GATE_GRAPHITI_CLOSEOUT:-0}" = "1" ]; then' in script
    assert '$(realpath --relative-to="${PROJECT_ROOT}" "${GRAPHITI_CLOSEOUT_REPORT}")' in script


def test_api_smoke_endpoints_define_workload_classes() -> None:
    payload = json.loads(Path("tests/performance/api_smoke_endpoints.json").read_text(encoding="utf-8"))

    assert payload
    assert all("workload_class" in item for item in payload)
    assert {item["workload_class"] for item in payload} == {"business", "infrastructure"}
