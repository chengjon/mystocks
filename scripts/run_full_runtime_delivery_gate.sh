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

python - <<'PY' "${SUMMARY_DIR}/summary.json" "${SUMMARY_DIR}/runtime-observability-drift-report.json" "${SUMMARY_DIR}/monitoring-rule-metric-reference-report.json" "${BUNDLE_DIR}/runtime-artifact-manifest.json" "${BUNDLE_DIR}/runtime-artifact-index.md" "${docker_dir}/SUMMARY.md" "${SUMMARY_PATH}" "${MANIFEST_PATH}"
import json
import sys
from pathlib import Path

runtime_summary_path = Path(sys.argv[1]).resolve()
drift_report_path = Path(sys.argv[2]).resolve()
monitoring_rule_report_path = Path(sys.argv[3]).resolve()
bundle_manifest_path = Path(sys.argv[4]).resolve()
bundle_index_path = Path(sys.argv[5]).resolve()
docker_summary_path = Path(sys.argv[6]).resolve()
gate_summary_path = Path(sys.argv[7]).resolve()
manifest_path = Path(sys.argv[8]).resolve()

runtime_summary = json.loads(runtime_summary_path.read_text(encoding="utf-8"))
drift_report = json.loads(drift_report_path.read_text(encoding="utf-8"))
monitoring_rule_report = json.loads(monitoring_rule_report_path.read_text(encoding="utf-8"))

manifest = {
    "generated_at": runtime_summary.get("generated_at"),
    "overall_gate_status": runtime_summary.get("overall_gate_status"),
    "runtime_observability_drift_pass": drift_report.get("pass"),
    "runtime_observability_drift_violations": len(drift_report.get("violations", [])),
    "runtime_observability_drift_not_measured": len(drift_report.get("not_measured", [])),
    "monitoring_rule_metric_reference_pass": monitoring_rule_report.get("pass"),
    "monitoring_rule_metric_reference_violations": len(monitoring_rule_report.get("violations", [])),
    "paths": {
        "gate_summary": str(gate_summary_path),
        "runtime_summary_json": str(runtime_summary_path),
        "runtime_drift_report": str(drift_report_path),
        "monitoring_rule_metric_reference_report": str(monitoring_rule_report_path),
        "runtime_bundle_manifest": str(bundle_manifest_path),
        "runtime_bundle_index": str(bundle_index_path),
        "docker_smoke_summary": str(docker_summary_path),
    },
}

manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY

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
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${SUMMARY_DIR}/monitoring-rule-metric-reference-report.json")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${BUNDLE_DIR}/runtime-artifact-index.md")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${MANIFEST_PATH}")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${docker_dir}/SUMMARY.md")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${DOCKER_SMOKE_LOG}")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${COMBINED_SUMMARY_LOG}")\`
EOF

printf 'Full runtime delivery gate summary written to %s\n' "${SUMMARY_PATH}"
