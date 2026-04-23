#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TIMESTAMP="$(date '+%Y%m%d-%H%M%S')"
REPORT_DIR="${PROJECT_ROOT}/reports/analysis/docker-runtime-smoke/${TIMESTAMP}"
SUMMARY_PATH="${REPORT_DIR}/SUMMARY.md"
DOCKER_RUNTIME_JSON_PATH="${REPORT_DIR}/docker-runtime-smoke.json"
COMPOSE_RENDERED_PATH="${REPORT_DIR}/compose.rendered.yaml"
BUILD_LOG_PATH="${REPORT_DIR}/build.log"
PS_LOG_PATH="${REPORT_DIR}/compose-ps.txt"
BACKEND_HEALTH_PATH="${REPORT_DIR}/backend-health.json"
BACKEND_READINESS_PATH="${REPORT_DIR}/backend-readiness.json"
FRONTEND_INDEX_PATH="${REPORT_DIR}/frontend-index.html"
METRICS_BASELINE_RAW_PATH="${REPORT_DIR}/metrics.baseline.raw.txt"
METRICS_RAW_PATH="${REPORT_DIR}/metrics.raw.txt"
METRICS_HEALTH_PATH="${REPORT_DIR}/metrics-health.json"
METRICS_SUMMARY_PATH="${REPORT_DIR}/metrics-summary.json"
BACKEND_LOG_PATH="${REPORT_DIR}/backend.log"
FRONTEND_LOG_PATH="${REPORT_DIR}/frontend.log"
GRAPHITI_CLOSEOUT_REPORT="${REPORT_DIR}/docker-runtime-smoke-graphiti-closeout.json"

COMPOSE_FILE="${COMPOSE_FILE:-${PROJECT_ROOT}/web/docker-compose.yml}"
COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-mystocks-runtime-smoke}"
CLEANUP_CONTAINERS="${CLEANUP_CONTAINERS:-1}"
BUILD_TIMEOUT_SECONDS="${BUILD_TIMEOUT_SECONDS:-900}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-postgres}"
POSTGRES_PUBLISHED_PORT="${POSTGRES_PUBLISHED_PORT:-15432}"
REDIS_PASSWORD="${REDIS_PASSWORD:-}"
REDIS_IMAGE="${REDIS_IMAGE:-redis:7-alpine}"
REDIS_PUBLISHED_PORT="${REDIS_PUBLISHED_PORT:-16379}"
TDENGINE_PASSWORD="${TDENGINE_PASSWORD:-taosdata}"
TDENGINE_PUBLISHED_PORT="${TDENGINE_PUBLISHED_PORT:-16030}"
BACKEND_PORT="${BACKEND_PORT:-8021}"
FRONTEND_PORT="${FRONTEND_PORT:-3021}"

mkdir -p "${REPORT_DIR}"

if [ "${REDIS_IMAGE}" = "redis:7-alpine" ] && docker image inspect redis:latest >/dev/null 2>&1; then
    REDIS_IMAGE="redis:latest"
fi

export REDIS_IMAGE
export POSTGRES_PUBLISHED_PORT
export REDIS_PUBLISHED_PORT
export TDENGINE_PUBLISHED_PORT
export BACKEND_PORT
export FRONTEND_PORT

wait_for_url() {
    local url="$1"
    local label="$2"
    local max_retries="${3:-60}"

    for _ in $(seq 1 "${max_retries}"); do
        if curl --noproxy '*' --silent --fail --max-time 10 "${url}" >/dev/null; then
            echo "${label} is READY"
            return 0
        fi
        sleep 2
    done

    echo "${label} health check failed: ${url}"
    return 1
}

compose_cmd() {
    docker compose -p "${COMPOSE_PROJECT_NAME}" -f "${COMPOSE_FILE}" "$@"
}

cleanup() {
    compose_cmd logs backend > "${BACKEND_LOG_PATH}" 2>&1 || true
    compose_cmd logs frontend > "${FRONTEND_LOG_PATH}" 2>&1 || true
    compose_cmd ps > "${PS_LOG_PATH}" 2>&1 || true

    if [ "${CLEANUP_CONTAINERS}" = "1" ]; then
        compose_cmd down -v --remove-orphans >/dev/null 2>&1 || true
    fi
}

trap cleanup EXIT

cd "${PROJECT_ROOT}"

docker --version >/dev/null
docker compose version >/dev/null

compose_cmd config > "${COMPOSE_RENDERED_PATH}"
if ! timeout --preserve-status "${BUILD_TIMEOUT_SECONDS}" \
    docker compose -p "${COMPOSE_PROJECT_NAME}" -f "${COMPOSE_FILE}" build backend frontend 2>&1 | tee "${BUILD_LOG_PATH}"; then
    if grep -q "timed out" "${BUILD_LOG_PATH}" 2>/dev/null; then
        printf 'Docker build timed out after %ss. See %s\n' "${BUILD_TIMEOUT_SECONDS}" "${BUILD_LOG_PATH}" >&2
    else
        printf 'Docker build failed. See %s\n' "${BUILD_LOG_PATH}" >&2
    fi
    exit 1
fi
compose_cmd up -d postgresql redis backend frontend >/dev/null

wait_for_url "http://localhost:${BACKEND_PORT}/health" "Backend /health"
wait_for_url "http://localhost:${BACKEND_PORT}/api/health/ready" "Backend /api/health/ready"
wait_for_url "http://localhost:${FRONTEND_PORT}/" "Frontend /"

curl --noproxy '*' --silent "http://localhost:${BACKEND_PORT}/metrics" > "${METRICS_BASELINE_RAW_PATH}"
curl --noproxy '*' --silent --fail "http://localhost:${BACKEND_PORT}/health" > "${BACKEND_HEALTH_PATH}"
curl --noproxy '*' --silent --fail "http://localhost:${BACKEND_PORT}/api/health/ready" > "${BACKEND_READINESS_PATH}"
curl --noproxy '*' --silent --fail "http://localhost:${FRONTEND_PORT}/" > "${FRONTEND_INDEX_PATH}"
curl --noproxy '*' --silent --fail "http://localhost:${BACKEND_PORT}/api/metrics/health" > "${METRICS_HEALTH_PATH}"
curl --noproxy '*' --silent --fail "http://localhost:${BACKEND_PORT}/metrics" > "${METRICS_RAW_PATH}"

python "${PROJECT_ROOT}/scripts/dev/quality_gate/summarize_metrics_snapshot.py" \
    --metrics-file "${METRICS_RAW_PATH}" \
    --baseline-metrics-file "${METRICS_BASELINE_RAW_PATH}" \
    --health-file "${METRICS_HEALTH_PATH}" \
    --output "${METRICS_SUMMARY_PATH}"

METRICS_HEALTH_STATUS="$(
python - <<'PY' "${METRICS_SUMMARY_PATH}"
import json
import sys

payload = json.load(open(sys.argv[1], encoding="utf-8"))
print(payload.get("metrics_health", {}).get("status", "unknown"))
PY
)"

PROM_HTTP_DELTA="$(
python - <<'PY' "${METRICS_SUMMARY_PATH}"
import json
import sys

payload = json.load(open(sys.argv[1], encoding="utf-8"))
print(payload.get("prometheus_snapshot", {}).get("http_requests_total_delta", "n/a"))
PY
)"

PROM_SLOW_DELTA="$(
python - <<'PY' "${METRICS_SUMMARY_PATH}"
import json
import sys

payload = json.load(open(sys.argv[1], encoding="utf-8"))
print(payload.get("prometheus_snapshot", {}).get("slow_http_requests_total_delta", "n/a"))
PY
)"

cat > "${SUMMARY_PATH}" <<EOF
# Docker Runtime Smoke

- Generated at: \`$(date '+%Y-%m-%d %H:%M:%S %z')\`
- Compose file: \`${COMPOSE_FILE#${PROJECT_ROOT}/}\`
- Compose project: \`${COMPOSE_PROJECT_NAME}\`
- Build timeout: \`${BUILD_TIMEOUT_SECONDS}s\`
- Redis image: \`${REDIS_IMAGE}\`
- Internal dependency ports: PostgreSQL \`${POSTGRES_PUBLISHED_PORT}\`, Redis \`${REDIS_PUBLISHED_PORT}\`, TDengine \`${TDENGINE_PUBLISHED_PORT}\`
- Backup smoke service URLs:
  - \`mystocks-backend\`: \`http://localhost:${BACKEND_PORT}\`
  - \`mystocks-frontend\`: \`http://localhost:${FRONTEND_PORT}\`

## Commands

\`\`\`bash
docker compose -p ${COMPOSE_PROJECT_NAME} -f ${COMPOSE_FILE#${PROJECT_ROOT}/} config
timeout --preserve-status ${BUILD_TIMEOUT_SECONDS} docker compose -p ${COMPOSE_PROJECT_NAME} -f ${COMPOSE_FILE#${PROJECT_ROOT}/} build backend frontend
docker compose -p ${COMPOSE_PROJECT_NAME} -f ${COMPOSE_FILE#${PROJECT_ROOT}/} up -d postgresql redis backend frontend
curl --noproxy '*' http://localhost:${BACKEND_PORT}/health
curl --noproxy '*' http://localhost:${BACKEND_PORT}/api/health/ready
curl --noproxy '*' http://localhost:${FRONTEND_PORT}/
\`\`\`

## Results

- Backend health: \`PASS\`
- Backend readiness: \`PASS\`
- Frontend index: \`PASS\`

## Observability Snapshot

- \`/api/metrics/health\`: \`${METRICS_HEALTH_STATUS}\`
- Prometheus \`http_requests_total\` delta during run: \`${PROM_HTTP_DELTA}\`
- Prometheus \`slow_http_requests_total\` delta during run: \`${PROM_SLOW_DELTA}\`

## Artifacts

- \`$(realpath --relative-to="${PROJECT_ROOT}" "${COMPOSE_RENDERED_PATH}")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${BUILD_LOG_PATH}")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${PS_LOG_PATH}")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${BACKEND_HEALTH_PATH}")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${BACKEND_READINESS_PATH}")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${FRONTEND_INDEX_PATH}")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${METRICS_HEALTH_PATH}")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${METRICS_RAW_PATH}")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${METRICS_SUMMARY_PATH}")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${BACKEND_LOG_PATH}")\`
- \`$(realpath --relative-to="${PROJECT_ROOT}" "${FRONTEND_LOG_PATH}")\`
EOF

python - <<'PY' "${DOCKER_RUNTIME_JSON_PATH}" "${COMPOSE_FILE}" "${COMPOSE_PROJECT_NAME}" "${BUILD_TIMEOUT_SECONDS}" "${REDIS_IMAGE}" "${POSTGRES_PUBLISHED_PORT}" "${REDIS_PUBLISHED_PORT}" "${TDENGINE_PUBLISHED_PORT}" "${BACKEND_PORT}" "${FRONTEND_PORT}" "${COMPOSE_RENDERED_PATH}" "${BUILD_LOG_PATH}" "${PS_LOG_PATH}" "${BACKEND_HEALTH_PATH}" "${BACKEND_READINESS_PATH}" "${FRONTEND_INDEX_PATH}" "${METRICS_HEALTH_PATH}" "${METRICS_RAW_PATH}" "${METRICS_SUMMARY_PATH}" "${BACKEND_LOG_PATH}" "${FRONTEND_LOG_PATH}"
import json
import sys
from pathlib import Path

output_path = Path(sys.argv[1])
compose_file = sys.argv[2]
compose_project_name = sys.argv[3]
build_timeout_seconds = int(sys.argv[4])
redis_image = sys.argv[5]
postgres_port = int(sys.argv[6])
redis_port = int(sys.argv[7])
tdengine_port = int(sys.argv[8])
backend_port = int(sys.argv[9])
frontend_port = int(sys.argv[10])
compose_rendered_path = Path(sys.argv[11]).resolve()
build_log_path = Path(sys.argv[12]).resolve()
ps_log_path = Path(sys.argv[13]).resolve()
backend_health_path = Path(sys.argv[14]).resolve()
backend_readiness_path = Path(sys.argv[15]).resolve()
frontend_index_path = Path(sys.argv[16]).resolve()
metrics_health_path = Path(sys.argv[17]).resolve()
metrics_raw_path = Path(sys.argv[18]).resolve()
metrics_summary_path = Path(sys.argv[19]).resolve()
backend_log_path = Path(sys.argv[20]).resolve()
frontend_log_path = Path(sys.argv[21]).resolve()

metrics_summary = json.loads(metrics_summary_path.read_text(encoding="utf-8"))
metrics_health = json.loads(metrics_health_path.read_text(encoding="utf-8"))

payload = {
    "metric_version": "v1",
    "compose": {
        "file": compose_file,
        "project_name": compose_project_name,
        "build_timeout_seconds": build_timeout_seconds,
        "redis_image": redis_image,
    },
    "dependency_ports": {
        "postgresql": postgres_port,
        "redis": redis_port,
        "tdengine": tdengine_port,
    },
    "service_urls": {
        "backend": f"http://localhost:{backend_port}",
        "frontend": f"http://localhost:{frontend_port}",
    },
    "service_url_roles": {
        "backend": "backup_smoke",
        "frontend": "backup_smoke",
    },
    "service_role": "backup_smoke",
    "checks": {
        "backend_health": "PASS",
        "backend_readiness": "PASS",
        "frontend_index": "PASS",
    },
    "metrics_health": metrics_health.get("status", "unknown"),
    "prometheus_snapshot": metrics_summary.get("prometheus_snapshot", {}),
    "artifacts": {
        "compose_rendered": str(compose_rendered_path),
        "build_log": str(build_log_path),
        "compose_ps": str(ps_log_path),
        "backend_health": str(backend_health_path),
        "backend_readiness": str(backend_readiness_path),
        "frontend_index": str(frontend_index_path),
        "metrics_health": str(metrics_health_path),
        "metrics_raw": str(metrics_raw_path),
        "metrics_summary": str(metrics_summary_path),
        "backend_log": str(backend_log_path),
        "frontend_log": str(frontend_log_path),
        "summary_markdown": str((output_path.parent / "SUMMARY.md").resolve()),
    },
}

output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY

if [ "${DISABLE_QUALITY_GATE_GRAPHITI_CLOSEOUT:-0}" = "1" ]; then
    cat > "${GRAPHITI_CLOSEOUT_REPORT}" <<EOF
{
  "status": "skipped_disabled",
  "reason": "DISABLE_QUALITY_GATE_GRAPHITI_CLOSEOUT=1",
  "report_dir": "${REPORT_DIR}",
  "gate_kind": "docker-runtime-smoke"
}
EOF
else
    python "${PROJECT_ROOT}/scripts/runtime/record_quality_gate_closeout.py" \
        --gate-kind docker-runtime-smoke \
        --project-root "${PROJECT_ROOT}" \
        --report-dir "${REPORT_DIR}" \
        --output json > "${GRAPHITI_CLOSEOUT_REPORT}"
fi

printf -- '- `%s`\n' "$(realpath --relative-to="${PROJECT_ROOT}" "${GRAPHITI_CLOSEOUT_REPORT}")" >> "${SUMMARY_PATH}"

printf 'Docker runtime smoke summary written to %s\n' "${SUMMARY_PATH}"
