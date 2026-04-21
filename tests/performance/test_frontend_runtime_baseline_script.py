from pathlib import Path


def test_frontend_runtime_baseline_script_runs_full_quality_chain():
    script = Path("scripts/run_frontend_runtime_baseline.sh").read_text(encoding="utf-8")

    assert "bash scripts/run_api_performance_baseline.sh" in script
    assert "bash scripts/run_monitoring_auth_performance_baseline.sh" in script
    assert "bash scripts/run_runtime_quality_summary.sh" in script
    assert 'FRONTEND_RUNTIME_DIR="${REPORT_DIR}"' in script
    assert 'API_PERFORMANCE_DIR="${API_BASELINE_DIR}"' in script
    assert 'MONITORING_AUTH_DIR="${MONITORING_BASELINE_DIR}"' in script


def test_frontend_runtime_baseline_script_appends_runtime_summary_artifact_after_generation():
    script = Path("scripts/run_frontend_runtime_baseline.sh").read_text(encoding="utf-8")

    runtime_summary_call = script.index('bash scripts/run_runtime_quality_summary.sh 2>&1 | tee "${RUNTIME_SUMMARY_LOG}"')
    runtime_summary_artifact = script.index('printf -- \'- `%s`\\n\' "$(realpath --relative-to="${PROJECT_ROOT}" "${RUNTIME_QUALITY_DIR}/SUMMARY.md")" >> "${SUMMARY_PATH}"')

    assert runtime_summary_call < runtime_summary_artifact


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
