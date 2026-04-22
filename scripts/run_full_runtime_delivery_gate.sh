#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TIMESTAMP="$(date '+%Y%m%d-%H%M%S')"
REPORT_DIR="${RUNTIME_DELIVERY_GATE_DIR:-${PROJECT_ROOT}/reports/analysis/runtime-delivery-gate/${TIMESTAMP}}"
SUMMARY_DIR="${REPORT_DIR}/runtime-quality-summary"
BUNDLE_DIR="${REPORT_DIR}/runtime-ci-bundle"
DOCKER_SMOKE_LOG="${REPORT_DIR}/docker-runtime-smoke.log"
COMBINED_SUMMARY_LOG="${REPORT_DIR}/runtime-delivery-summary.log"
SUMMARY_PATH="${REPORT_DIR}/SUMMARY.md"

mkdir -p "${REPORT_DIR}"

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

docker_dir="${DOCKER_RUNTIME_DIR:-}"

if [ -z "${docker_dir}" ]; then
    env \
        POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-postgres}" \
        TDENGINE_PASSWORD="${TDENGINE_PASSWORD:-taosdata}" \
        bash "${PROJECT_ROOT}/scripts/run_containerized_runtime_smoke.sh" 2>&1 | tee "${DOCKER_SMOKE_LOG}"
    docker_dir="$(resolve_latest_dir "${PROJECT_ROOT}/reports/analysis/docker-runtime-smoke/*")"
else
    printf 'Using existing docker runtime smoke dir: %s\n' "${docker_dir}" | tee "${DOCKER_SMOKE_LOG}"
fi

if [ -z "${docker_dir}" ]; then
    printf 'Full runtime delivery gate requires DOCKER_RUNTIME_DIR or a successful docker runtime smoke run\n' >&2
    exit 1
fi

DOCKER_RUNTIME_DIR="${docker_dir}" \
RUNTIME_DELIVERY_SUMMARY_DIR="${SUMMARY_DIR}" \
RUNTIME_DELIVERY_BUNDLE_DIR="${BUNDLE_DIR}" \
    bash "${PROJECT_ROOT}/scripts/run_runtime_delivery_summary_local.sh" 2>&1 | tee "${COMBINED_SUMMARY_LOG}"

cat > "${SUMMARY_PATH}" <<EOF
# Full Runtime Delivery Gate

- Generated at: \`$(date '+%Y-%m-%d %H:%M:%S %z')\`
- Service URLs:
  - \`mystocks-backend\`: \`http://localhost:8020\`
  - \`mystocks-frontend\`: \`http://localhost:3020\`
- Docker smoke URLs:
  - \`mystocks-backend\`: \`http://localhost:8021\`
  - \`mystocks-frontend\`: \`http://localhost:3021\`

## Commands

\`\`\`bash
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-postgres} TDENGINE_PASSWORD=${TDENGINE_PASSWORD:-taosdata} bash scripts/run_containerized_runtime_smoke.sh
DOCKER_RUNTIME_DIR=${docker_dir} RUNTIME_DELIVERY_SUMMARY_DIR=${SUMMARY_DIR} RUNTIME_DELIVERY_BUNDLE_DIR=${BUNDLE_DIR} bash scripts/run_runtime_delivery_summary_local.sh
\`\`\`

## Artifacts

- \`$(realpath --relative-to="${PROJECT_ROOT}" "${SUMMARY_DIR}/SUMMARY.md")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${SUMMARY_DIR}/runtime-observability-drift-report.json")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${BUNDLE_DIR}/runtime-artifact-index.md")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${docker_dir}/SUMMARY.md")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${DOCKER_SMOKE_LOG}")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${COMBINED_SUMMARY_LOG}")\`
EOF

printf 'Full runtime delivery gate summary written to %s\n' "${SUMMARY_PATH}"
