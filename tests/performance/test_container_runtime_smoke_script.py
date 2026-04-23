from pathlib import Path


def test_container_runtime_smoke_script_runs_build_up_and_health_checks():
    script = Path("scripts/run_containerized_runtime_smoke.sh").read_text(encoding="utf-8")

    assert 'docker compose -p "${COMPOSE_PROJECT_NAME}" -f "${COMPOSE_FILE}" "$@"' in script
    assert 'compose_cmd config > "${COMPOSE_RENDERED_PATH}"' in script
    assert 'BUILD_TIMEOUT_SECONDS="${BUILD_TIMEOUT_SECONDS:-900}"' in script
    assert 'timeout --preserve-status "${BUILD_TIMEOUT_SECONDS}"' in script
    assert 'docker compose -p "${COMPOSE_PROJECT_NAME}" -f "${COMPOSE_FILE}" build backend frontend 2>&1 | tee "${BUILD_LOG_PATH}"' in script
    assert 'compose_cmd up -d postgresql redis backend frontend >/dev/null' in script
    assert 'wait_for_url "http://localhost:${BACKEND_PORT}/health" "Backend /health"' in script
    assert 'wait_for_url "http://localhost:${BACKEND_PORT}/api/health/ready" "Backend /api/health/ready"' in script
    assert 'wait_for_url "http://localhost:${FRONTEND_PORT}/" "Frontend /"' in script
    assert 'curl --noproxy \'*\' --silent --fail "http://localhost:${BACKEND_PORT}/api/metrics/health" > "${METRICS_HEALTH_PATH}"' in script
    assert 'python "${PROJECT_ROOT}/scripts/dev/quality_gate/summarize_metrics_snapshot.py"' in script


def test_container_runtime_smoke_script_persists_summary_and_logs():
    script = Path("scripts/run_containerized_runtime_smoke.sh").read_text(encoding="utf-8")

    assert 'REPORT_DIR="${PROJECT_ROOT}/reports/analysis/docker-runtime-smoke/${TIMESTAMP}"' in script
    assert 'DOCKER_RUNTIME_JSON_PATH="${REPORT_DIR}/docker-runtime-smoke.json"' in script
    assert 'compose_cmd logs backend > "${BACKEND_LOG_PATH}" 2>&1 || true' in script
    assert 'compose_cmd logs frontend > "${FRONTEND_LOG_PATH}" 2>&1 || true' in script
    assert 'compose_cmd ps > "${PS_LOG_PATH}" 2>&1 || true' in script
    assert '# Docker Runtime Smoke' in script
    assert '- Build timeout: \\`${BUILD_TIMEOUT_SECONDS}s\\`' in script
    assert '- Backup smoke service URLs:' in script
    assert '- Backend health: \\`PASS\\`' in script
    assert '- Backend readiness: \\`PASS\\`' in script
    assert '- Frontend index: \\`PASS\\`' in script
    assert '## Observability Snapshot' in script
    assert '- \\`/api/metrics/health\\`: \\`${METRICS_HEALTH_STATUS}\\`' in script
    assert '- Prometheus \\`http_requests_total\\` delta during run: \\`${PROM_HTTP_DELTA}\\`' in script
    assert '- Prometheus \\`slow_http_requests_total\\` delta during run: \\`${PROM_SLOW_DELTA}\\`' in script
    assert 'METRICS_SUMMARY_PATH="${REPORT_DIR}/metrics-summary.json"' in script
    assert 'GRAPHITI_CLOSEOUT_REPORT="${REPORT_DIR}/docker-runtime-smoke-graphiti-closeout.json"' in script
    assert '"metric_version": "v1"' in script
    assert '"service_urls"' in script
    assert '"service_url_roles"' in script
    assert '"service_role": "backup_smoke"' in script
    assert '"checks"' in script
    assert '"artifacts"' in script
    assert 'python "${PROJECT_ROOT}/scripts/runtime/record_quality_gate_closeout.py" \\' in script
    assert '--gate-kind docker-runtime-smoke \\' in script
    assert 'if [ "${DISABLE_QUALITY_GATE_GRAPHITI_CLOSEOUT:-0}" = "1" ]; then' in script
    assert '$(realpath --relative-to="${PROJECT_ROOT}" "${GRAPHITI_CLOSEOUT_REPORT}")' in script
    assert 'Docker build timed out after %ss. See %s\\n' in script
