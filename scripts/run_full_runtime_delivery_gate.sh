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
MANIFEST_PATH="${REPORT_DIR}/runtime-delivery-gate-manifest.json"
GRAPHITI_CLOSEOUT_REPORT="${REPORT_DIR}/runtime-delivery-gate-graphiti-closeout.json"
CHILD_GATE_CLOSEOUT_VALIDATION_REPORT="${REPORT_DIR}/runtime-child-gate-closeout-validation.json"

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
        BUILD_TIMEOUT_SECONDS="${BUILD_TIMEOUT_SECONDS:-900}" \
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

frontend_dir="${FRONTEND_RUNTIME_DIR:-$(resolve_latest_dir "${PROJECT_ROOT}/reports/analysis/frontend-runtime-gate/*")}"
api_dir="${API_PERFORMANCE_DIR:-$(resolve_latest_dir "${PROJECT_ROOT}/reports/analysis/api-performance-gate/*")}"

if [ -z "${frontend_dir}" ] || [ -z "${api_dir}" ]; then
    printf 'Full runtime delivery gate requires frontend/api gate dirs to validate child closeouts\n' >&2
    exit 1
fi

if [ "${DISABLE_RUNTIME_CHILD_GATE_CLOSEOUT_VALIDATION:-0}" = "1" ]; then
    cat > "${CHILD_GATE_CLOSEOUT_VALIDATION_REPORT}" <<EOF
{
  "pass": false,
  "status": "skipped_disabled",
  "reason": "DISABLE_RUNTIME_CHILD_GATE_CLOSEOUT_VALIDATION=1",
  "items": []
}
EOF
else
    python "${PROJECT_ROOT}/scripts/runtime/validate_runtime_child_gate_closeouts.py" \
        --frontend-closeout-json "${frontend_dir}/frontend-runtime-gate-graphiti-closeout.json" \
        --api-closeout-json "${api_dir}/api-performance-gate-graphiti-closeout.json" \
        --docker-closeout-json "${docker_dir}/docker-runtime-smoke-graphiti-closeout.json" \
        --output "${CHILD_GATE_CLOSEOUT_VALIDATION_REPORT}" \
        --fail-on-invalid
fi

python - <<'PY' "${SUMMARY_DIR}/summary.json" "${SUMMARY_DIR}/runtime-observability-drift-report.json" "${SUMMARY_DIR}/api-performance-drift-report.json" "${SUMMARY_DIR}/monitoring-rule-metric-reference-report.json" "${SUMMARY_DIR}/backend-runtime-dependency-report.json" "${SUMMARY_DIR}/container-deployment-contract-report.json" "${SUMMARY_DIR}/deployment-env-contract-report.json" "${BUNDLE_DIR}/runtime-artifact-manifest.json" "${BUNDLE_DIR}/runtime-artifact-index.md" "${docker_dir}/SUMMARY.md" "${docker_dir}/docker-runtime-smoke.json" "${SUMMARY_PATH}" "${MANIFEST_PATH}" "${GRAPHITI_CLOSEOUT_REPORT}" "${CHILD_GATE_CLOSEOUT_VALIDATION_REPORT}"
import json
import sys
from pathlib import Path

runtime_summary_path = Path(sys.argv[1]).resolve()
drift_report_path = Path(sys.argv[2]).resolve()
api_performance_drift_report_path = Path(sys.argv[3]).resolve()
monitoring_rule_report_path = Path(sys.argv[4]).resolve()
backend_runtime_dependency_report_path = Path(sys.argv[5]).resolve()
container_deployment_contract_report_path = Path(sys.argv[6]).resolve()
deployment_env_contract_report_path = Path(sys.argv[7]).resolve()
bundle_manifest_path = Path(sys.argv[8]).resolve()
bundle_index_path = Path(sys.argv[9]).resolve()
docker_summary_path = Path(sys.argv[10]).resolve()
docker_runtime_report_path = Path(sys.argv[11]).resolve()
gate_summary_path = Path(sys.argv[12]).resolve()
manifest_path = Path(sys.argv[13]).resolve()
graphiti_closeout_report_path = Path(sys.argv[14]).resolve()
child_gate_closeout_validation_report_path = Path(sys.argv[15]).resolve()

runtime_summary = json.loads(runtime_summary_path.read_text(encoding="utf-8"))
drift_report = json.loads(drift_report_path.read_text(encoding="utf-8"))
api_performance_drift_report = (
    json.loads(api_performance_drift_report_path.read_text(encoding="utf-8"))
    if api_performance_drift_report_path.exists()
    else None
)
monitoring_rule_report = json.loads(monitoring_rule_report_path.read_text(encoding="utf-8"))
backend_runtime_dependency_report = json.loads(backend_runtime_dependency_report_path.read_text(encoding="utf-8"))
container_deployment_contract_report = json.loads(container_deployment_contract_report_path.read_text(encoding="utf-8"))
deployment_env_contract_report = json.loads(deployment_env_contract_report_path.read_text(encoding="utf-8"))
docker_runtime_report = (
    json.loads(docker_runtime_report_path.read_text(encoding="utf-8"))
    if docker_runtime_report_path.exists()
    else None
)
child_gate_closeout_validation_report = (
    json.loads(child_gate_closeout_validation_report_path.read_text(encoding="utf-8"))
    if child_gate_closeout_validation_report_path.exists()
    else None
)

manifest = {
    "generated_at": runtime_summary.get("generated_at"),
    "overall_gate_status": runtime_summary.get("overall_gate_status"),
    "runtime_observability_drift_pass": drift_report.get("pass"),
    "runtime_observability_drift_violations": len(drift_report.get("violations", [])),
    "runtime_observability_drift_not_measured": len(drift_report.get("not_measured", [])),
    "api_performance_drift_pass": None if api_performance_drift_report is None else api_performance_drift_report.get("pass"),
    "api_performance_drift_violations": 0 if api_performance_drift_report is None else len(api_performance_drift_report.get("violations", [])),
    "monitoring_rule_metric_reference_pass": monitoring_rule_report.get("pass"),
    "monitoring_rule_metric_reference_violations": len(monitoring_rule_report.get("violations", [])),
    "backend_runtime_dependency_pass": backend_runtime_dependency_report.get("pass"),
    "backend_runtime_dependency_violations": len(backend_runtime_dependency_report.get("violations", [])),
    "container_deployment_contract_pass": container_deployment_contract_report.get("pass"),
    "container_deployment_contract_violations": len(container_deployment_contract_report.get("violations", [])),
    "deployment_env_contract_pass": deployment_env_contract_report.get("pass"),
    "deployment_env_contract_violations": len(deployment_env_contract_report.get("violations", [])),
    "child_gate_closeouts_pass": None if child_gate_closeout_validation_report is None else child_gate_closeout_validation_report.get("pass"),
    "child_gate_closeouts_valid_count": 0 if child_gate_closeout_validation_report is None else child_gate_closeout_validation_report.get("valid_count"),
    "child_gate_closeouts_invalid_count": 0 if child_gate_closeout_validation_report is None else child_gate_closeout_validation_report.get("invalid_count"),
    "docker_runtime_smoke_checks": None if docker_runtime_report is None else docker_runtime_report.get("checks"),
    "docker_runtime_service_role": None if docker_runtime_report is None else docker_runtime_report.get("service_role"),
    "docker_runtime_service_url_roles": None if docker_runtime_report is None else docker_runtime_report.get("service_url_roles"),
    "paths": {
        "gate_summary": str(gate_summary_path),
        "runtime_summary_json": str(runtime_summary_path),
        "runtime_drift_report": str(drift_report_path),
        "api_performance_drift_report": None if api_performance_drift_report is None else str(api_performance_drift_report_path),
        "monitoring_rule_metric_reference_report": str(monitoring_rule_report_path),
        "backend_runtime_dependency_report": str(backend_runtime_dependency_report_path),
        "container_deployment_contract_report": str(container_deployment_contract_report_path),
        "deployment_env_contract_report": str(deployment_env_contract_report_path),
        "child_gate_closeout_validation_report": None if child_gate_closeout_validation_report is None else str(child_gate_closeout_validation_report_path),
        "runtime_bundle_manifest": str(bundle_manifest_path),
        "runtime_bundle_index": str(bundle_index_path),
        "docker_smoke_summary": str(docker_summary_path),
        "docker_smoke_report": None if docker_runtime_report is None else str(docker_runtime_report_path),
        "graphiti_closeout_report": str(graphiti_closeout_report_path),
    },
}

manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY

if [ "${DISABLE_RUNTIME_GATE_GRAPHITI_CLOSEOUT:-0}" = "1" ]; then
    cat > "${GRAPHITI_CLOSEOUT_REPORT}" <<EOF
{
  "status": "skipped_disabled",
  "reason": "DISABLE_RUNTIME_GATE_GRAPHITI_CLOSEOUT=1",
  "manifest_path": "${MANIFEST_PATH}",
  "runtime_summary_path": "${SUMMARY_DIR}/summary.json",
  "gate_summary_path": "${SUMMARY_PATH}"
}
EOF
else
    python "${PROJECT_ROOT}/scripts/runtime/record_runtime_delivery_gate_closeout.py" \
        --project-root "${PROJECT_ROOT}" \
        --manifest-path "${MANIFEST_PATH}" \
        --summary-json "${SUMMARY_DIR}/summary.json" \
        --gate-summary-path "${SUMMARY_PATH}" \
        --output json > "${GRAPHITI_CLOSEOUT_REPORT}"
fi

cat > "${SUMMARY_PATH}" <<EOF
# Full Runtime Delivery Gate

- Generated at: \`$(date '+%Y-%m-%d %H:%M:%S %z')\`
- Service URLs:
  - \`mystocks-backend\`: \`http://localhost:8020\`
  - \`mystocks-frontend\`: \`http://localhost:3020\`
- Backup smoke URLs (container-only, not canonical PM2 runtime):
  - \`mystocks-backend\`: \`http://localhost:8021\`
  - \`mystocks-frontend\`: \`http://localhost:3021\`

## Commands

\`\`\`bash
BUILD_TIMEOUT_SECONDS=${BUILD_TIMEOUT_SECONDS:-900} POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-postgres} TDENGINE_PASSWORD=${TDENGINE_PASSWORD:-taosdata} bash scripts/run_containerized_runtime_smoke.sh
DOCKER_RUNTIME_DIR=${docker_dir} RUNTIME_DELIVERY_SUMMARY_DIR=${SUMMARY_DIR} RUNTIME_DELIVERY_BUNDLE_DIR=${BUNDLE_DIR} bash scripts/run_runtime_delivery_summary_local.sh
\`\`\`

## Artifacts

- \`$(realpath --relative-to="${PROJECT_ROOT}" "${SUMMARY_DIR}/SUMMARY.md")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${SUMMARY_DIR}/runtime-observability-drift-report.json")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${SUMMARY_DIR}/api-performance-drift-report.json")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${SUMMARY_DIR}/monitoring-rule-metric-reference-report.json")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${SUMMARY_DIR}/backend-runtime-dependency-report.json")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${SUMMARY_DIR}/container-deployment-contract-report.json")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${SUMMARY_DIR}/deployment-env-contract-report.json")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${CHILD_GATE_CLOSEOUT_VALIDATION_REPORT}")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${BUNDLE_DIR}/runtime-artifact-index.md")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${MANIFEST_PATH}")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${GRAPHITI_CLOSEOUT_REPORT}")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${docker_dir}/SUMMARY.md")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${docker_dir}/docker-runtime-smoke.json")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${DOCKER_SMOKE_LOG}")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${COMBINED_SUMMARY_LOG}")\`
EOF

printf 'Full runtime delivery gate summary written to %s\n' "${SUMMARY_PATH}"
