#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TIMESTAMP="$(date '+%Y%m%d-%H%M%S')"
REPORT_DIR="${PROJECT_ROOT}/reports/analysis/frontend-runtime-gate/${TIMESTAMP}"
SUMMARY_PATH="${REPORT_DIR}/SUMMARY.md"
TYPECHECK_LOG="${REPORT_DIR}/type-check.log"
TYPECEILING_LOG="${REPORT_DIR}/type-ceiling.log"
PM2_GATE_LOG="${REPORT_DIR}/pm2-gate.log"
REGRESSION_LOG="${REPORT_DIR}/regression.log"
AXE_LOG="${REPORT_DIR}/axe.log"
BASELINE_JSON="${REPORT_DIR}/tech-debt-baseline.current.json"
API_REPORT_PATH="${REPORT_DIR}/api-performance-report.txt"
MONITORING_REPORT_PATH="${REPORT_DIR}/monitoring-auth-performance-report.txt"
RUNTIME_SUMMARY_LOG="${REPORT_DIR}/runtime-quality-summary.txt"

mkdir -p "${REPORT_DIR}"

saved_pm2=0
if command -v pm2 >/dev/null 2>&1; then
    pm2 save >/dev/null 2>&1 && saved_pm2=1 || true
fi

restore_pm2() {
    if [ "${saved_pm2}" -eq 1 ]; then
        pm2 resurrect >/dev/null 2>&1 || true
    fi
}

trap restore_pm2 EXIT

cd "${PROJECT_ROOT}"

npm --prefix web/frontend run type-check 2>&1 | tee "${TYPECHECK_LOG}"
npm --prefix web/frontend run test:type-ceiling 2>&1 | tee "${TYPECEILING_LOG}"
bash scripts/run_e2e_pm2.sh 2>&1 | tee "${PM2_GATE_LOG}"
bash scripts/run_pm2_integration_workflow.sh regression 2>&1 | tee "${REGRESSION_LOG}"
PLAYWRIGHT_EXTERNAL_FRONTEND=1 FRONTEND_BASE_URL=http://127.0.0.1:3020 E2E_FRONTEND_URL=http://127.0.0.1:3020 \
    npm --prefix web/frontend run test:e2e:axe 2>&1 | tee "${AXE_LOG}"
python scripts/dev/quality_gate/collect_tech_debt_baseline.py --output "${BASELINE_JSON#${PROJECT_ROOT}/}" >/dev/null
bash scripts/run_api_performance_baseline.sh 2>&1 | tee "${API_REPORT_PATH}"
bash scripts/run_monitoring_auth_performance_baseline.sh 2>&1 | tee "${MONITORING_REPORT_PATH}"
API_BASELINE_DIR="$(ls -1dt "${PROJECT_ROOT}"/reports/analysis/api-performance-gate/* | head -n 1)"
MONITORING_BASELINE_DIR="$(ls -1dt "${PROJECT_ROOT}"/reports/analysis/api-monitoring-auth-gate/* | head -n 1)"

pm2_gate_summary="$(grep -E '^[[:space:]]+[0-9]+ passed' "${PM2_GATE_LOG}" | tail -n 1 || true)"
regression_e2e_summary="$(grep -E '^E2E Summary:' "${REGRESSION_LOG}" | tail -n 1 || true)"
regression_pytest_summary="$(grep -E '^Pytest Summary:' "${REGRESSION_LOG}" | tail -n 1 || true)"
axe_summary="$(
    grep -E '([0-9]+ passed)' "${AXE_LOG}" | tail -n 1 \
        | sed -E 's/^\x1b\[[0-9;]*[[:alpha:]]//g' \
        | sed -E 's/^::notice title=.*::[[:space:]]*//' \
        || true
)"
pm2_status_lines="$(grep -E 'mystocks-(backend|frontend)' "${REGRESSION_LOG}" | tail -n 2 || true)"

cat > "${SUMMARY_PATH}" <<EOF
# Frontend Runtime Baseline

- Generated at: $(date '+%Y-%m-%d %H:%M:%S %z')
- Report directory: \`${REPORT_DIR}\`
- Service URLs:
  - \`mystocks-backend\`: \`http://localhost:8020\`
  - \`mystocks-frontend\`: \`http://localhost:3020\`

## Commands

\`\`\`bash
npm --prefix web/frontend run type-check
npm --prefix web/frontend run test:type-ceiling
bash scripts/run_e2e_pm2.sh
bash scripts/run_pm2_integration_workflow.sh regression
PLAYWRIGHT_EXTERNAL_FRONTEND=1 FRONTEND_BASE_URL=http://127.0.0.1:3020 E2E_FRONTEND_URL=http://127.0.0.1:3020 npm --prefix web/frontend run test:e2e:axe
python scripts/dev/quality_gate/collect_tech_debt_baseline.py --output ${BASELINE_JSON#${PROJECT_ROOT}/}
bash scripts/run_api_performance_baseline.sh
bash scripts/run_monitoring_auth_performance_baseline.sh
FRONTEND_RUNTIME_DIR=${REPORT_DIR} API_PERFORMANCE_DIR=${API_BASELINE_DIR} MONITORING_AUTH_DIR=${MONITORING_BASELINE_DIR} bash scripts/run_runtime_quality_summary.sh
\`\`\`

## Results

- Structural syntax / PM2 navigation gate: ${pm2_gate_summary:-"see ${PM2_GATE_LOG}"}
- Type ceiling: $(tail -n 1 "${TYPECEILING_LOG}" || true)
- Regression E2E: ${regression_e2e_summary:-"see ${REGRESSION_LOG}"}
- Accessibility smoke: ${axe_summary:-"see ${AXE_LOG}"}
- Regression pytest: ${regression_pytest_summary:-"see ${REGRESSION_LOG}"}

## PM2 Status

\`\`\`
${pm2_status_lines:-"(see ${REGRESSION_LOG})"}
\`\`\`

## Artifacts

- \`$(realpath --relative-to="${PROJECT_ROOT}" "${TYPECHECK_LOG}")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${TYPECEILING_LOG}")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${PM2_GATE_LOG}")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${REGRESSION_LOG}")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${AXE_LOG}")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${BASELINE_JSON}")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${API_REPORT_PATH}")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${MONITORING_REPORT_PATH}")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${RUNTIME_SUMMARY_LOG}")\`
EOF

FRONTEND_RUNTIME_DIR="${REPORT_DIR}" \
API_PERFORMANCE_DIR="${API_BASELINE_DIR}" \
MONITORING_AUTH_DIR="${MONITORING_BASELINE_DIR}" \
    bash scripts/run_runtime_quality_summary.sh 2>&1 | tee "${RUNTIME_SUMMARY_LOG}"
RUNTIME_QUALITY_DIR="$(ls -1dt "${PROJECT_ROOT}"/reports/analysis/runtime-quality-summary/* | head -n 1)"
printf -- '- `%s`\n' "$(realpath --relative-to="${PROJECT_ROOT}" "${RUNTIME_QUALITY_DIR}/SUMMARY.md")" >> "${SUMMARY_PATH}"

printf 'Frontend runtime baseline written to %s\n' "${SUMMARY_PATH}"
