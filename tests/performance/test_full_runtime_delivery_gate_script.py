from pathlib import Path


def test_full_runtime_delivery_gate_script_runs_docker_smoke_then_combined_summary():
    script = Path("scripts/run_full_runtime_delivery_gate.sh").read_text(encoding="utf-8")

    assert 'REPORT_DIR="${RUNTIME_DELIVERY_GATE_DIR:-${PROJECT_ROOT}/reports/analysis/runtime-delivery-gate/${TIMESTAMP}}"' in script
    assert 'MANIFEST_PATH="${REPORT_DIR}/runtime-delivery-gate-manifest.json"' in script
    assert 'POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-postgres}"' in script
    assert 'TDENGINE_PASSWORD="${TDENGINE_PASSWORD:-taosdata}"' in script
    assert 'bash "${PROJECT_ROOT}/scripts/run_containerized_runtime_smoke.sh"' in script
    assert 'docker_dir="$(resolve_latest_dir "${PROJECT_ROOT}/reports/analysis/docker-runtime-smoke/*")"' in script
    assert 'DOCKER_RUNTIME_DIR="${docker_dir}"' in script
    assert 'bash "${PROJECT_ROOT}/scripts/run_runtime_delivery_summary_local.sh"' in script
    assert 'runtime_observability_drift_pass' in script
    assert 'monitoring_rule_metric_reference_pass' in script


def test_full_runtime_delivery_gate_script_persists_summary_and_artifact_links():
    script = Path("scripts/run_full_runtime_delivery_gate.sh").read_text(encoding="utf-8")

    assert '# Full Runtime Delivery Gate' in script
    assert '- \\`mystocks-backend\\`: \\`http://localhost:8020\\`' in script
    assert '- \\`mystocks-frontend\\`: \\`http://localhost:3020\\`' in script
    assert '- \\`mystocks-backend\\`: \\`http://localhost:8021\\`' in script
    assert '- \\`mystocks-frontend\\`: \\`http://localhost:3021\\`' in script
    assert 'runtime-observability-drift-report.json' in script
    assert 'monitoring-rule-metric-reference-report.json' in script
    assert 'runtime-artifact-index.md' in script
    assert 'runtime-delivery-gate-manifest.json' in script
    assert 'docker-runtime-smoke.log' in script
    assert 'runtime-delivery-summary.log' in script
