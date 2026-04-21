#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TIMESTAMP="$(date '+%Y%m%d-%H%M%S')"
REPORT_DIR="${PROJECT_ROOT}/reports/analysis/docker-runtime-smoke/${TIMESTAMP}"
SUMMARY_PATH="${REPORT_DIR}/SUMMARY.md"
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

COMPOSE_FILE="${COMPOSE_FILE:-${PROJECT_ROOT}/web/docker-compose.yml}"
COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-mystocks-runtime-smoke}"
CLEANUP_CONTAINERS="${CLEANUP_CONTAINERS:-1}"
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
compose_cmd build backend frontend 2>&1 | tee "${BUILD_LOG_PATH}"
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
- Redis image: \`${REDIS_IMAGE}\`
- Internal dependency ports: PostgreSQL \`${POSTGRES_PUBLISHED_PORT}\`, Redis \`${REDIS_PUBLISHED_PORT}\`, TDengine \`${TDENGINE_PUBLISHED_PORT}\`
- Service URLs:
  - \`mystocks-backend\`: \`http://localhost:${BACKEND_PORT}\`
  - \`mystocks-frontend\`: \`http://localhost:${FRONTEND_PORT}\`

## Commands

\`\`\`bash
docker compose -p ${COMPOSE_PROJECT_NAME} -f ${COMPOSE_FILE#${PROJECT_ROOT}/} config
docker compose -p ${COMPOSE_PROJECT_NAME} -f ${COMPOSE_FILE#${PROJECT_ROOT}/} build backend frontend
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

printf 'Docker runtime smoke summary written to %s\n' "${SUMMARY_PATH}"
