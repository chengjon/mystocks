#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TIMESTAMP="$(date '+%Y%m%d-%H%M%S')"
REPORT_DIR="${TECH_DEBT_WEEKLY_REPORT_DIR:-${PROJECT_ROOT}/reports/analysis/tech-debt-weekly-report-local}"
OUTPUT_PATH="${TECH_DEBT_WEEKLY_REPORT_OUTPUT:-${REPORT_DIR}/tech-debt-weekly-report-${TIMESTAMP}.md}"
CURRENT_METRICS_PATH="${TECH_DEBT_CURRENT_JSON:-${REPORT_DIR}/tech-debt-current-${TIMESTAMP}.json}"
BASELINE_PATH="${TECH_DEBT_BASELINE_JSON:-${PROJECT_ROOT}/reports/analysis/tech-debt-baseline.json}"
RUNTIME_BASELINE_PATH="${RUNTIME_OBSERVABILITY_BASELINE_JSON:-${PROJECT_ROOT}/reports/analysis/runtime-observability-baseline.json}"
API_PERFORMANCE_BASELINE_PATH="${API_PERFORMANCE_BASELINE_JSON:-${PROJECT_ROOT}/reports/analysis/api-performance-baseline.json}"
RUNTIME_GATE_DIR="${RUNTIME_DELIVERY_GATE_DIR:-}"
RUNTIME_SUMMARY_JSON="${RUNTIME_SUMMARY_JSON:-}"
RUNTIME_CURRENT_JSON="${RUNTIME_CURRENT_JSON:-}"
FRONTEND_GATE_DIR="${FRONTEND_RUNTIME_GATE_DIR:-}"
API_GATE_DIR="${API_PERFORMANCE_GATE_DIR:-}"
DOCKER_GATE_DIR="${DOCKER_RUNTIME_GATE_DIR:-${DOCKER_RUNTIME_DIR:-}}"
RUNTIME_GATE_CLOSEOUT_JSON="${RUNTIME_GATE_CLOSEOUT_JSON:-}"
FRONTEND_GATE_CLOSEOUT_JSON="${FRONTEND_GATE_CLOSEOUT_JSON:-}"
API_GATE_CLOSEOUT_JSON="${API_GATE_CLOSEOUT_JSON:-}"
DOCKER_GATE_CLOSEOUT_JSON="${DOCKER_GATE_CLOSEOUT_JSON:-}"
THRESHOLD="${TECH_DEBT_WEEKLY_THRESHOLD:-800}"
SINCE_DAYS="${TECH_DEBT_WEEKLY_SINCE_DAYS:-90}"
TOP_N="${TECH_DEBT_WEEKLY_TOP_N:-10}"
BASE_SHA="${TECH_DEBT_WEEKLY_BASE_SHA:-}"

mkdir -p "${REPORT_DIR}"

if [ -n "${RUNTIME_GATE_DIR}" ] && [ -z "${RUNTIME_SUMMARY_JSON}" ]; then
    candidate_runtime_summary="${RUNTIME_GATE_DIR}/runtime-quality-summary/summary.json"
    if [ ! -f "${candidate_runtime_summary}" ]; then
        printf 'RUNTIME_DELIVERY_GATE_DIR provided but summary is missing: %s\n' "${candidate_runtime_summary}" >&2
        exit 1
    fi
    RUNTIME_SUMMARY_JSON="${candidate_runtime_summary}"
fi

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

if [ -z "${FRONTEND_GATE_DIR}" ]; then
    FRONTEND_GATE_DIR="$(resolve_latest_dir "${PROJECT_ROOT}/reports/analysis/frontend-runtime-gate/*")"
fi

if [ -z "${API_GATE_DIR}" ]; then
    API_GATE_DIR="$(resolve_latest_dir "${PROJECT_ROOT}/reports/analysis/api-performance-gate/*")"
fi

if [ -z "${DOCKER_GATE_DIR}" ]; then
    DOCKER_GATE_DIR="$(resolve_latest_dir "${PROJECT_ROOT}/reports/analysis/docker-runtime-smoke/*")"
fi

if [ -n "${RUNTIME_GATE_DIR}" ] && [ -z "${RUNTIME_GATE_CLOSEOUT_JSON}" ] && [ -f "${RUNTIME_GATE_DIR}/runtime-delivery-gate-graphiti-closeout.json" ]; then
    RUNTIME_GATE_CLOSEOUT_JSON="${RUNTIME_GATE_DIR}/runtime-delivery-gate-graphiti-closeout.json"
fi

if [ -n "${FRONTEND_GATE_DIR}" ] && [ -z "${FRONTEND_GATE_CLOSEOUT_JSON}" ] && [ -f "${FRONTEND_GATE_DIR}/frontend-runtime-gate-graphiti-closeout.json" ]; then
    FRONTEND_GATE_CLOSEOUT_JSON="${FRONTEND_GATE_DIR}/frontend-runtime-gate-graphiti-closeout.json"
fi

if [ -n "${API_GATE_DIR}" ] && [ -z "${API_GATE_CLOSEOUT_JSON}" ] && [ -f "${API_GATE_DIR}/api-performance-gate-graphiti-closeout.json" ]; then
    API_GATE_CLOSEOUT_JSON="${API_GATE_DIR}/api-performance-gate-graphiti-closeout.json"
fi

if [ -n "${DOCKER_GATE_DIR}" ] && [ -z "${DOCKER_GATE_CLOSEOUT_JSON}" ] && [ -f "${DOCKER_GATE_DIR}/docker-runtime-smoke-graphiti-closeout.json" ]; then
    DOCKER_GATE_CLOSEOUT_JSON="${DOCKER_GATE_DIR}/docker-runtime-smoke-graphiti-closeout.json"
fi

if [ ! -f "${CURRENT_METRICS_PATH}" ]; then
    python "${PROJECT_ROOT}/scripts/dev/quality_gate/collect_tech_debt_baseline.py" --output "${CURRENT_METRICS_PATH}"
fi

cmd=(
    python "${PROJECT_ROOT}/scripts/dev/quality_gate/tech_debt_governance_gate.py"
    weekly-report
    --baseline "${BASELINE_PATH}"
    --current "${CURRENT_METRICS_PATH}"
    --runtime-baseline "${RUNTIME_BASELINE_PATH}"
    --api-performance-baseline "${API_PERFORMANCE_BASELINE_PATH}"
    --threshold "${THRESHOLD}"
    --since-days "${SINCE_DAYS}"
    --top-n "${TOP_N}"
    --output "${OUTPUT_PATH}"
)

if [ -n "${BASE_SHA}" ]; then
    cmd+=(--base-sha "${BASE_SHA}")
fi

if [ -n "${RUNTIME_SUMMARY_JSON}" ]; then
    cmd+=(--runtime-summary-json "${RUNTIME_SUMMARY_JSON}")
fi

if [ -n "${RUNTIME_CURRENT_JSON}" ]; then
    cmd+=(--runtime-current "${RUNTIME_CURRENT_JSON}")
fi

if [ -n "${RUNTIME_GATE_CLOSEOUT_JSON}" ]; then
    cmd+=(--runtime-gate-closeout-json "${RUNTIME_GATE_CLOSEOUT_JSON}")
fi

if [ -n "${FRONTEND_GATE_CLOSEOUT_JSON}" ]; then
    cmd+=(--frontend-gate-closeout-json "${FRONTEND_GATE_CLOSEOUT_JSON}")
fi

if [ -n "${API_GATE_CLOSEOUT_JSON}" ]; then
    cmd+=(--api-gate-closeout-json "${API_GATE_CLOSEOUT_JSON}")
fi

if [ -n "${DOCKER_GATE_CLOSEOUT_JSON}" ]; then
    cmd+=(--docker-gate-closeout-json "${DOCKER_GATE_CLOSEOUT_JSON}")
fi

"${cmd[@]}"

printf 'Technical debt weekly report written to %s\n' "${OUTPUT_PATH}"
