from pathlib import Path


def test_frontend_runtime_baseline_script_runs_full_quality_chain():
    script = Path("scripts/run_frontend_runtime_baseline.sh").read_text(encoding="utf-8")

    assert 'FRONTEND_GATE_JSON="${REPORT_DIR}/frontend-runtime-gate.json"' in script
    assert "python scripts/dev/quality_gate/collect_frontend_runtime_gate.py" in script
    assert "bash scripts/run_api_performance_baseline.sh" in script
    assert "bash scripts/run_monitoring_auth_performance_baseline.sh" in script
    assert "bash scripts/run_runtime_quality_summary.sh" in script
    assert 'FRONTEND_RUNTIME_DIR="${REPORT_DIR}"' in script
    assert 'API_PERFORMANCE_DIR="${API_BASELINE_DIR}"' in script
    assert 'MONITORING_AUTH_DIR="${MONITORING_BASELINE_DIR}"' in script
    assert 'PLAYWRIGHT_OUTPUT_DIR="${AXE_PLAYWRIGHT_OUTPUT_DIR}"' in script
    assert 'PLAYWRIGHT_HTML_REPORT_DIR="${AXE_PLAYWRIGHT_HTML_REPORT_DIR}"' in script
    assert 'PLAYWRIGHT_JSON_REPORT_FILE="${AXE_PLAYWRIGHT_JSON_REPORT_FILE}"' in script
    assert 'GRAPHITI_CLOSEOUT_REPORT="${REPORT_DIR}/frontend-runtime-gate-graphiti-closeout.json"' in script
    assert 'python "${PROJECT_ROOT}/scripts/runtime/record_quality_gate_closeout.py" \\' in script
    assert '--gate-kind frontend-runtime-gate \\' in script


def test_frontend_runtime_baseline_script_appends_runtime_summary_artifact_after_generation():
    script = Path("scripts/run_frontend_runtime_baseline.sh").read_text(encoding="utf-8")

    runtime_summary_call = script.index('bash scripts/run_runtime_quality_summary.sh 2>&1 | tee "${RUNTIME_SUMMARY_LOG}"')
    runtime_summary_artifact = script.index('printf -- \'- `%s`\\n\' "$(realpath --relative-to="${PROJECT_ROOT}" "${RUNTIME_QUALITY_DIR}/SUMMARY.md")" >> "${SUMMARY_PATH}"')
    graphiti_artifact = script.index('printf -- \'- `%s`\\n\' "$(realpath --relative-to="${PROJECT_ROOT}" "${GRAPHITI_CLOSEOUT_REPORT}")" >> "${SUMMARY_PATH}"')

    assert runtime_summary_call < runtime_summary_artifact
    assert runtime_summary_artifact < graphiti_artifact


def test_frontend_runtime_baseline_script_persists_frontend_runtime_gate_json_artifact():
    script = Path("scripts/run_frontend_runtime_baseline.sh").read_text(encoding="utf-8")

    assert 'python scripts/dev/quality_gate/collect_frontend_runtime_gate.py \\' in script
    assert '--output "${FRONTEND_GATE_JSON}"' in script
    assert '$(realpath --relative-to="${PROJECT_ROOT}" "${FRONTEND_GATE_JSON}")' in script
    assert 'if [ "${DISABLE_QUALITY_GATE_GRAPHITI_CLOSEOUT:-0}" = "1" ]; then' in script
    assert '$(realpath --relative-to="${PROJECT_ROOT}" "${GRAPHITI_CLOSEOUT_REPORT}")' in script


def test_runtime_quality_summary_script_supports_pm2_and_docker_modes():
    script = Path("scripts/run_runtime_quality_summary.sh").read_text(encoding="utf-8")

    assert 'resolve_latest_dir()' in script
    assert 'if [ "${has_pm2_runtime}" -eq 1 ]; then' in script
    assert 'cmd+=(--frontend-dir "${frontend_dir}")' in script
    assert 'cmd+=(--api-dir "${api_dir}")' in script
    assert 'cmd+=(--monitoring-dir "${monitoring_dir}")' in script
    assert 'if [ -n "${docker_dir}" ]; then' in script
    assert 'cmd+=(--docker-dir "${docker_dir}")' in script
    assert 'Runtime quality summary requires PM2 baseline dirs or DOCKER_RUNTIME_DIR' in script


def test_pm2_integration_regression_routes_runtime_artifacts_to_tmp():
    script = Path("scripts/run_pm2_integration_workflow.sh").read_text(encoding="utf-8")

    assert 'local playwright_output_dir="/tmp/mystocks-playwright-results-regression"' in script
    assert 'local playwright_html_report_dir="/tmp/mystocks-playwright-report-regression"' in script
    assert 'local playwright_json_report_file="/tmp/mystocks-playwright-results-regression/results.json"' in script
    assert 'PLAYWRIGHT_OUTPUT_DIR="${playwright_output_dir}" \\' in script
    assert 'PLAYWRIGHT_HTML_REPORT_DIR="${playwright_html_report_dir}" \\' in script
    assert 'PLAYWRIGHT_JSON_REPORT_FILE="${playwright_json_report_file}" \\' in script
    assert '-p no:tdd-guard \\' in script
    assert '-o "cache_dir=${pytest_cache_dir}" \\' in script
    assert '--timing-file="${pytest_timing_file}" \\' in script
