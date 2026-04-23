from pathlib import Path


def test_full_runtime_delivery_gate_script_runs_docker_smoke_then_combined_summary():
    script = Path("scripts/run_full_runtime_delivery_gate.sh").read_text(encoding="utf-8")

    assert 'REPORT_DIR="${RUNTIME_DELIVERY_GATE_DIR:-${PROJECT_ROOT}/reports/analysis/runtime-delivery-gate/${TIMESTAMP}}"' in script
    assert 'MANIFEST_PATH="${REPORT_DIR}/runtime-delivery-gate-manifest.json"' in script
    assert 'BUILD_TIMEOUT_SECONDS="${BUILD_TIMEOUT_SECONDS:-900}"' in script
    assert 'POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-postgres}"' in script
    assert 'TDENGINE_PASSWORD="${TDENGINE_PASSWORD:-taosdata}"' in script
    assert 'bash "${PROJECT_ROOT}/scripts/run_containerized_runtime_smoke.sh"' in script
    assert 'docker_dir="$(resolve_latest_dir "${PROJECT_ROOT}/reports/analysis/docker-runtime-smoke/*")"' in script
    assert 'DOCKER_RUNTIME_DIR="${docker_dir}"' in script
    assert 'bash "${PROJECT_ROOT}/scripts/run_runtime_delivery_summary_local.sh"' in script
    assert 'runtime_observability_drift_pass' in script
    assert 'api_performance_drift_pass' in script
    assert 'monitoring_rule_metric_reference_pass' in script
    assert 'backend_runtime_dependency_pass' in script
    assert 'container_deployment_contract_pass' in script
    assert 'deployment_env_contract_pass' in script
    assert 'docker_runtime_smoke_checks' in script
    assert 'docker_runtime_service_role' in script
    assert 'docker_runtime_service_url_roles' in script
    assert 'GRAPHITI_CLOSEOUT_REPORT="${REPORT_DIR}/runtime-delivery-gate-graphiti-closeout.json"' in script
    assert 'CHILD_GATE_CLOSEOUT_VALIDATION_REPORT="${REPORT_DIR}/runtime-child-gate-closeout-validation.json"' in script
    assert '"${SUMMARY_DIR}/backend-runtime-dependency-report.json"' in script
    assert '"${SUMMARY_DIR}/container-deployment-contract-report.json"' in script
    assert '"${SUMMARY_DIR}/deployment-env-contract-report.json"' in script
    assert '"${docker_dir}/docker-runtime-smoke.json"' in script
    assert 'frontend_dir="${FRONTEND_RUNTIME_DIR:-$(resolve_latest_dir "${PROJECT_ROOT}/reports/analysis/frontend-runtime-gate/*")}"' in script
    assert 'api_dir="${API_PERFORMANCE_DIR:-$(resolve_latest_dir "${PROJECT_ROOT}/reports/analysis/api-performance-gate/*")}"' in script
    assert 'if [ "${DISABLE_RUNTIME_CHILD_GATE_CLOSEOUT_VALIDATION:-0}" = "1" ]; then' in script
    assert 'python "${PROJECT_ROOT}/scripts/runtime/validate_runtime_child_gate_closeouts.py" \\' in script
    assert '--frontend-closeout-json "${frontend_dir}/frontend-runtime-gate-graphiti-closeout.json" \\' in script
    assert '--api-closeout-json "${api_dir}/api-performance-gate-graphiti-closeout.json" \\' in script
    assert '--docker-closeout-json "${docker_dir}/docker-runtime-smoke-graphiti-closeout.json" \\' in script
    assert '--output "${CHILD_GATE_CLOSEOUT_VALIDATION_REPORT}" \\' in script
    assert '--fail-on-invalid' in script
    assert 'if [ "${DISABLE_RUNTIME_GATE_GRAPHITI_CLOSEOUT:-0}" = "1" ]; then' in script
    assert 'python "${PROJECT_ROOT}/scripts/runtime/record_runtime_delivery_gate_closeout.py"' in script
    assert '--manifest-path "${MANIFEST_PATH}"' in script
    assert '--summary-json "${SUMMARY_DIR}/summary.json"' in script
    assert '--gate-summary-path "${SUMMARY_PATH}"' in script
    assert '"${GRAPHITI_CLOSEOUT_REPORT}"' in script


def test_full_runtime_delivery_gate_script_persists_summary_and_artifact_links():
    script = Path("scripts/run_full_runtime_delivery_gate.sh").read_text(encoding="utf-8")

    assert '# Full Runtime Delivery Gate' in script
    assert '- \\`mystocks-backend\\`: \\`http://localhost:8020\\`' in script
    assert '- \\`mystocks-frontend\\`: \\`http://localhost:3020\\`' in script
    assert '- Backup smoke URLs (container-only, not canonical PM2 runtime):' in script
    assert '- \\`mystocks-backend\\`: \\`http://localhost:8021\\`' in script
    assert '- \\`mystocks-frontend\\`: \\`http://localhost:3021\\`' in script
    assert 'BUILD_TIMEOUT_SECONDS=${BUILD_TIMEOUT_SECONDS:-900}' in script
    assert 'runtime-observability-drift-report.json' in script
    assert 'api-performance-drift-report.json' in script
    assert 'monitoring-rule-metric-reference-report.json' in script
    assert 'backend-runtime-dependency-report.json' in script
    assert 'container-deployment-contract-report.json' in script
    assert 'deployment-env-contract-report.json' in script
    assert 'runtime-child-gate-closeout-validation.json' in script
    assert 'runtime-artifact-index.md' in script
    assert 'runtime-delivery-gate-manifest.json' in script
    assert 'runtime-delivery-gate-graphiti-closeout.json' in script
    assert 'docker-runtime-smoke.json' in script
    assert 'docker-runtime-smoke.log' in script
    assert 'runtime-delivery-summary.log' in script
