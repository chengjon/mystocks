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
RUNTIME_SUMMARY_JSON="${RUNTIME_SUMMARY_JSON:-}"
RUNTIME_CURRENT_JSON="${RUNTIME_CURRENT_JSON:-}"
THRESHOLD="${TECH_DEBT_WEEKLY_THRESHOLD:-800}"
SINCE_DAYS="${TECH_DEBT_WEEKLY_SINCE_DAYS:-90}"
TOP_N="${TECH_DEBT_WEEKLY_TOP_N:-10}"
BASE_SHA="${TECH_DEBT_WEEKLY_BASE_SHA:-}"

mkdir -p "${REPORT_DIR}"

if [ ! -f "${CURRENT_METRICS_PATH}" ]; then
    python "${PROJECT_ROOT}/scripts/dev/quality_gate/collect_tech_debt_baseline.py" --output "${CURRENT_METRICS_PATH}"
fi

cmd=(
    python "${PROJECT_ROOT}/scripts/dev/quality_gate/tech_debt_governance_gate.py"
    weekly-report
    --baseline "${BASELINE_PATH}"
    --current "${CURRENT_METRICS_PATH}"
    --runtime-baseline "${RUNTIME_BASELINE_PATH}"
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

"${cmd[@]}"

printf 'Technical debt weekly report written to %s\n' "${OUTPUT_PATH}"
