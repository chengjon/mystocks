#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

BASELINE_PATH="${RUNTIME_OBSERVABILITY_BASELINE_JSON:-${PROJECT_ROOT}/reports/analysis/runtime-observability-baseline.json}"
SUMMARY_JSON="${RUNTIME_QUALITY_SUMMARY_JSON:-}"
CURRENT_OBSERVABILITY_JSON="${RUNTIME_OBSERVABILITY_CURRENT_JSON:-}"
OUTPUT_PATH="${RUNTIME_OBSERVABILITY_DRIFT_REPORT_JSON:-}"

resolve_latest_summary_json() {
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

if [ -n "${SUMMARY_JSON}" ] && [ -n "${CURRENT_OBSERVABILITY_JSON}" ]; then
    printf 'Runtime observability drift gate accepts RUNTIME_QUALITY_SUMMARY_JSON or RUNTIME_OBSERVABILITY_CURRENT_JSON, not both\n' >&2
    exit 1
fi

if [ -z "${SUMMARY_JSON}" ] && [ -z "${CURRENT_OBSERVABILITY_JSON}" ]; then
    SUMMARY_JSON="$(resolve_latest_summary_json "${PROJECT_ROOT}/reports/analysis/runtime-quality-summary/*/summary.json")"
fi

if [ -z "${SUMMARY_JSON}" ] && [ -z "${CURRENT_OBSERVABILITY_JSON}" ]; then
    printf 'Runtime observability drift gate requires RUNTIME_QUALITY_SUMMARY_JSON, RUNTIME_OBSERVABILITY_CURRENT_JSON, or an existing reports/analysis/runtime-quality-summary/*/summary.json\n' >&2
    exit 1
fi

if [ -z "${OUTPUT_PATH}" ]; then
    if [ -n "${SUMMARY_JSON}" ]; then
        OUTPUT_PATH="$(dirname "${SUMMARY_JSON}")/runtime-observability-drift-report.json"
    else
        OUTPUT_PATH="${PROJECT_ROOT}/reports/analysis/runtime-observability-drift-report.json"
    fi
fi

cmd=(
    python "${PROJECT_ROOT}/scripts/dev/quality_gate/validate_runtime_observability_drift.py"
    --baseline "${BASELINE_PATH}"
    --output "${OUTPUT_PATH}"
)

if [ -n "${SUMMARY_JSON}" ]; then
    cmd+=(--current-summary-json "${SUMMARY_JSON}")
else
    cmd+=(--current-observability-json "${CURRENT_OBSERVABILITY_JSON}")
fi

"${cmd[@]}"

printf 'Runtime observability drift gate report written to %s\n' "${OUTPUT_PATH}"
