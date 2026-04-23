#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

SUMMARY_DIR="${RUNTIME_DELIVERY_SUMMARY_DIR:-${PROJECT_ROOT}/reports/analysis/runtime-quality-summary-ci-local}"
BUNDLE_DIR="${RUNTIME_DELIVERY_BUNDLE_DIR:-${PROJECT_ROOT}/reports/analysis/runtime-ci-bundle-combined-local}"
SUMMARY_PATH="${SUMMARY_DIR}/SUMMARY.md"
JSON_PATH="${SUMMARY_DIR}/summary.json"
DRIFT_REPORT_PATH="${SUMMARY_DIR}/runtime-observability-drift-report.json"
API_PERFORMANCE_DRIFT_REPORT_PATH="${SUMMARY_DIR}/api-performance-drift-report.json"
MONITORING_RULE_REPORT_PATH="${SUMMARY_DIR}/monitoring-rule-metric-reference-report.json"
BACKEND_RUNTIME_DEP_REPORT_PATH="${SUMMARY_DIR}/backend-runtime-dependency-report.json"
CONTAINER_DEPLOYMENT_CONTRACT_REPORT_PATH="${SUMMARY_DIR}/container-deployment-contract-report.json"
DEPLOYMENT_ENV_CONTRACT_REPORT_PATH="${SUMMARY_DIR}/deployment-env-contract-report.json"
MANIFEST_PATH="${BUNDLE_DIR}/runtime-artifact-manifest.json"
INDEX_PATH="${BUNDLE_DIR}/runtime-artifact-index.md"
docker_dir="${DOCKER_RUNTIME_DIR:-}"

resolve_latest_dir() {
    local glob_pattern="$1"
    local latest=""
    shopt -s nullglob
    local matches=(${glob_pattern})
    shopt -u nullglob
    if [ ${#matches[@]} -gt 0 ]; then
        latest="$(printf '%s\n' "${matches[@]}" | sort -r | head -n 1)"
    fi
    printf '%s' "${latest}"
}

frontend_dir="${FRONTEND_RUNTIME_DIR:-$(resolve_latest_dir "${PROJECT_ROOT}/reports/analysis/frontend-runtime-gate/*")}"
api_dir="${API_PERFORMANCE_DIR:-$(resolve_latest_dir "${PROJECT_ROOT}/reports/analysis/api-performance-gate/*")}"
monitoring_dir="${MONITORING_AUTH_DIR:-$(resolve_latest_dir "${PROJECT_ROOT}/reports/analysis/api-monitoring-auth-gate/*")}"

has_pm2_runtime=0
if [ -n "${frontend_dir}" ] || [ -n "${api_dir}" ] || [ -n "${monitoring_dir}" ]; then
    if [ -z "${frontend_dir}" ] || [ -z "${api_dir}" ] || [ -z "${monitoring_dir}" ]; then
        printf 'Runtime delivery summary requires all PM2 baseline dirs together: FRONTEND_RUNTIME_DIR, API_PERFORMANCE_DIR, MONITORING_AUTH_DIR\n' >&2
        exit 1
    fi
    has_pm2_runtime=1
fi

if [ "${has_pm2_runtime}" -eq 0 ] && [ -z "${docker_dir}" ]; then
    printf 'Runtime delivery summary requires PM2 baseline dirs or DOCKER_RUNTIME_DIR\n' >&2
    exit 1
fi

rm -rf "${SUMMARY_DIR}" "${BUNDLE_DIR}"
mkdir -p "${SUMMARY_DIR}" "${BUNDLE_DIR}"

summary_cmd=(
    python "${PROJECT_ROOT}/scripts/dev/quality_gate/build_runtime_quality_summary.py"
    --output-markdown "${SUMMARY_PATH}"
    --output-json "${JSON_PATH}"
)

summary_with_drift_cmd=(
    python "${PROJECT_ROOT}/scripts/dev/quality_gate/build_runtime_quality_summary.py"
    --runtime-observability-drift-report "${DRIFT_REPORT_PATH}"
    --api-performance-drift-report "${API_PERFORMANCE_DRIFT_REPORT_PATH}"
    --monitoring-rule-report "${MONITORING_RULE_REPORT_PATH}"
    --backend-runtime-dependency-report "${BACKEND_RUNTIME_DEP_REPORT_PATH}"
    --container-deployment-contract-report "${CONTAINER_DEPLOYMENT_CONTRACT_REPORT_PATH}"
    --deployment-env-contract-report "${DEPLOYMENT_ENV_CONTRACT_REPORT_PATH}"
    --output-markdown "${SUMMARY_PATH}"
    --output-json "${JSON_PATH}"
)

bundle_cmd=(
    python "${PROJECT_ROOT}/scripts/dev/quality_gate/build_runtime_ci_bundle.py"
    --runtime-quality-dir "${SUMMARY_DIR}"
    --runtime-observability-drift-report "${DRIFT_REPORT_PATH}"
    --api-performance-drift-report "${API_PERFORMANCE_DRIFT_REPORT_PATH}"
    --monitoring-rule-report "${MONITORING_RULE_REPORT_PATH}"
    --backend-runtime-dependency-report "${BACKEND_RUNTIME_DEP_REPORT_PATH}"
    --container-deployment-contract-report "${CONTAINER_DEPLOYMENT_CONTRACT_REPORT_PATH}"
    --deployment-env-contract-report "${DEPLOYMENT_ENV_CONTRACT_REPORT_PATH}"
    --output-manifest "${MANIFEST_PATH}"
    --output-index "${INDEX_PATH}"
)

if [ "${has_pm2_runtime}" -eq 1 ]; then
    summary_cmd+=(--frontend-dir "${frontend_dir}")
    summary_cmd+=(--api-dir "${api_dir}")
    summary_cmd+=(--monitoring-dir "${monitoring_dir}")
    summary_with_drift_cmd+=(--frontend-dir "${frontend_dir}")
    summary_with_drift_cmd+=(--api-dir "${api_dir}")
    summary_with_drift_cmd+=(--monitoring-dir "${monitoring_dir}")

    bundle_cmd+=(--frontend-dir "${frontend_dir}")
    bundle_cmd+=(--api-dir "${api_dir}")
    bundle_cmd+=(--monitoring-dir "${monitoring_dir}")
fi

if [ -n "${docker_dir}" ]; then
    summary_cmd+=(--docker-dir "${docker_dir}")
    summary_with_drift_cmd+=(--docker-dir "${docker_dir}")
    bundle_cmd+=(--docker-dir "${docker_dir}")
fi

reference_cmd=(
    python "${PROJECT_ROOT}/scripts/dev/quality_gate/validate_monitoring_prometheus_references.py"
    --rule-file "${PROJECT_ROOT}/config/monitoring/rules/mystocks-alerts.yml"
    --dashboard-file "${PROJECT_ROOT}/config/monitoring/dashboards/api-overview.json"
    --dashboard-file "${PROJECT_ROOT}/config/monitoring/dashboards/user-experience-dashboard.json"
    --declared-metrics-python-file "${PROJECT_ROOT}/web/backend/app/api/metrics.py"
    --declared-metrics-python-file "${PROJECT_ROOT}/src/monitoring/metrics_collector.py"
    --declared-metrics-python-file "${PROJECT_ROOT}/web/backend/app/core/middleware/performance.py"
    --declared-metrics-python-file "${PROJECT_ROOT}/web/backend/app/core/user_experience_monitor.py"
    --output "${MONITORING_RULE_REPORT_PATH}"
)

metrics_file_count=0
for dir in "${api_dir}" "${monitoring_dir}" "${docker_dir}"; do
    if [ -n "${dir}" ] && [ -f "${dir}/metrics.raw.txt" ]; then
        reference_cmd+=(--metrics-file "${dir}/metrics.raw.txt")
        metrics_file_count=$((metrics_file_count + 1))
    fi
done

if [ "${metrics_file_count}" -eq 0 ]; then
    printf 'Runtime delivery summary requires at least one metrics.raw.txt snapshot for monitoring rule validation\n' >&2
    exit 1
fi

"${summary_cmd[@]}"
python "${PROJECT_ROOT}/scripts/dev/quality_gate/validate_backend_runtime_dependencies.py" \
    --dockerfile "${PROJECT_ROOT}/web/backend/Dockerfile" \
    --requirements "${PROJECT_ROOT}/web/backend/requirements.txt" \
    --output "${BACKEND_RUNTIME_DEP_REPORT_PATH}"
python "${PROJECT_ROOT}/scripts/dev/quality_gate/validate_container_deployment_contract.py" \
    --compose-file "${PROJECT_ROOT}/web/docker-compose.yml" \
    --smoke-script "${PROJECT_ROOT}/scripts/run_containerized_runtime_smoke.sh" \
    --output "${CONTAINER_DEPLOYMENT_CONTRACT_REPORT_PATH}"
python "${PROJECT_ROOT}/scripts/dev/quality_gate/validate_deployment_env_contract.py" \
    --env-example "${PROJECT_ROOT}/.env.example" \
    --backend-ecosystem "${PROJECT_ROOT}/web/backend/ecosystem.config.js" \
    --frontend-ecosystem "${PROJECT_ROOT}/web/frontend/ecosystem.config.js" \
    --output "${DEPLOYMENT_ENV_CONTRACT_REPORT_PATH}"
if [ "${has_pm2_runtime}" -eq 1 ]; then
    python "${PROJECT_ROOT}/scripts/dev/quality_gate/validate_api_performance_drift.py" \
        --baseline "${PROJECT_ROOT}/reports/analysis/api-performance-baseline.json" \
        --current-benchmark-json "${api_dir}/benchmark.json" \
        --output "${API_PERFORMANCE_DRIFT_REPORT_PATH}"
fi
RUNTIME_OBSERVABILITY_BASELINE_JSON="${PROJECT_ROOT}/reports/analysis/runtime-observability-baseline.json" \
RUNTIME_QUALITY_SUMMARY_JSON="${JSON_PATH}" \
RUNTIME_OBSERVABILITY_DRIFT_REPORT_JSON="${DRIFT_REPORT_PATH}" \
    bash "${PROJECT_ROOT}/scripts/run_runtime_observability_drift_gate.sh"
"${reference_cmd[@]}"
"${summary_with_drift_cmd[@]}"
"${bundle_cmd[@]}"

printf 'Runtime delivery summary written to %s\n' "${SUMMARY_PATH}"
printf 'Runtime observability drift report written to %s\n' "${DRIFT_REPORT_PATH}"
if [ -f "${API_PERFORMANCE_DRIFT_REPORT_PATH}" ]; then
    printf 'API performance drift report written to %s\n' "${API_PERFORMANCE_DRIFT_REPORT_PATH}"
fi
printf 'Monitoring rule metric reference report written to %s\n' "${MONITORING_RULE_REPORT_PATH}"
printf 'Backend runtime dependency report written to %s\n' "${BACKEND_RUNTIME_DEP_REPORT_PATH}"
printf 'Container deployment contract report written to %s\n' "${CONTAINER_DEPLOYMENT_CONTRACT_REPORT_PATH}"
printf 'Deployment env contract report written to %s\n' "${DEPLOYMENT_ENV_CONTRACT_REPORT_PATH}"
printf 'Runtime delivery bundle index written to %s\n' "${INDEX_PATH}"
