#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TIMESTAMP="$(date '+%Y%m%d-%H%M%S')"
REPORT_DIR="${PROJECT_ROOT}/reports/analysis/runtime-quality-summary/${TIMESTAMP}"
SUMMARY_PATH="${REPORT_DIR}/SUMMARY.md"
JSON_PATH="${REPORT_DIR}/summary.json"

mkdir -p "${REPORT_DIR}"

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
        printf 'Runtime quality summary requires all PM2 baseline dirs together: FRONTEND_RUNTIME_DIR, API_PERFORMANCE_DIR, MONITORING_AUTH_DIR\n' >&2
        exit 1
    fi
    has_pm2_runtime=1
fi

if [ "${has_pm2_runtime}" -eq 0 ] && [ -z "${docker_dir}" ]; then
    printf 'Runtime quality summary requires PM2 baseline dirs or DOCKER_RUNTIME_DIR\n' >&2
    exit 1
fi

cmd=(
    python "${PROJECT_ROOT}/scripts/dev/quality_gate/build_runtime_quality_summary.py"
    --output-markdown "${SUMMARY_PATH}"
    --output-json "${JSON_PATH}"
)

if [ "${has_pm2_runtime}" -eq 1 ]; then
    cmd+=(--frontend-dir "${frontend_dir}")
    cmd+=(--api-dir "${api_dir}")
    cmd+=(--monitoring-dir "${monitoring_dir}")
fi

if [ -n "${docker_dir}" ]; then
    cmd+=(--docker-dir "${docker_dir}")
fi

"${cmd[@]}"

printf 'Runtime quality summary written to %s\n' "${SUMMARY_PATH}"
