#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TIMESTAMP="$(date '+%Y%m%d-%H%M%S')"
REPORT_DIR="${PROJECT_ROOT}/reports/analysis/api-monitoring-auth-gate/${TIMESTAMP}"
TEXT_REPORT="${REPORT_DIR}/benchmark.txt"
JSON_REPORT="${REPORT_DIR}/benchmark.json"
SUMMARY_PATH="${REPORT_DIR}/SUMMARY.md"
HEADERS_FILE="${REPORT_DIR}/auth-headers.json"
LOGIN_RESPONSE_PATH="${REPORT_DIR}/login-response.json"
METRICS_BASELINE_RAW_PATH="${REPORT_DIR}/metrics.baseline.raw.txt"
METRICS_RAW_PATH="${REPORT_DIR}/metrics.raw.txt"
METRICS_HEALTH_PATH="${REPORT_DIR}/metrics-health.json"
METRICS_SUMMARY_PATH="${REPORT_DIR}/metrics-summary.json"
GRAPHITI_CLOSEOUT_REPORT="${REPORT_DIR}/monitoring-auth-performance-gate-graphiti-closeout.json"
ENDPOINTS_FILE="${PROJECT_ROOT}/tests/performance/monitoring_auth_endpoints.json"

mkdir -p "${REPORT_DIR}"

clean_pm2() {
    pm2 stop all >/dev/null 2>&1 || true
    pm2 delete all >/dev/null 2>&1 || true
}

wait_for_url() {
    local url="$1"
    local label="$2"
    local max_retries="${3:-40}"

    for _ in $(seq 1 "$max_retries"); do
        if curl --noproxy '*' --silent --fail --max-time 10 "$url" >/dev/null; then
            echo "$label is READY"
            return 0
        fi
        sleep 2
    done

    echo "$label health check failed: $url"
    return 1
}

cd "${PROJECT_ROOT}"
clean_pm2
pm2 start ecosystem.test.config.js >/dev/null

wait_for_url "http://localhost:8020/health" "Backend"
wait_for_url "http://localhost:8020/api/health/ready" "Backend readiness"
wait_for_url "http://localhost:3020/" "Frontend"

curl --noproxy '*' --silent "http://localhost:8020/metrics" > "${METRICS_BASELINE_RAW_PATH}"

curl --noproxy '*' --silent --show-error \
    -X POST "http://localhost:8020/api/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    --data "username=admin&password=admin123" \
    > "${LOGIN_RESPONSE_PATH}"

TOKEN="$(
python - <<'PY' "${LOGIN_RESPONSE_PATH}"
import json
import sys

payload = json.load(open(sys.argv[1], encoding="utf-8"))
token = payload.get("data", {}).get("token", "")
if not token:
    raise SystemExit("Missing auth token in login response")
print(token)
PY
)"

python - <<'PY' "${HEADERS_FILE}" "${TOKEN}"
import json
import sys
from pathlib import Path

Path(sys.argv[1]).write_text(
    json.dumps({"Authorization": f"Bearer {sys.argv[2]}"}, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
PY

python tests/performance/benchmark.py \
    --url "http://localhost:8020" \
    --users 5 \
    --iterations 20 \
    --endpoints-file "${ENDPOINTS_FILE}" \
    --headers-file "${HEADERS_FILE}" \
    --output "${TEXT_REPORT}" \
    --json-output "${JSON_REPORT}"

curl --noproxy '*' --silent "http://localhost:8020/api/metrics/health" > "${METRICS_HEALTH_PATH}"
curl --noproxy '*' --silent "http://localhost:8020/metrics" > "${METRICS_RAW_PATH}"

python scripts/dev/quality_gate/summarize_metrics_snapshot.py \
    --metrics-file "${METRICS_RAW_PATH}" \
    --baseline-metrics-file "${METRICS_BASELINE_RAW_PATH}" \
    --health-file "${METRICS_HEALTH_PATH}" \
    --output "${METRICS_SUMMARY_PATH}"

python - <<'PY' "${JSON_REPORT}" "${SUMMARY_PATH}" "${METRICS_SUMMARY_PATH}" "${LOGIN_RESPONSE_PATH}"
import json
import sys
from pathlib import Path

json_path = Path(sys.argv[1])
summary_path = Path(sys.argv[2])
metrics_summary_path = Path(sys.argv[3])
login_response_path = Path(sys.argv[4])

data = json.loads(json_path.read_text(encoding="utf-8"))
metrics_snapshot = json.loads(metrics_summary_path.read_text(encoding="utf-8"))
login_payload = json.loads(login_response_path.read_text(encoding="utf-8"))
slo = data["slo_status"]
prometheus = metrics_snapshot["prometheus_snapshot"]
slow_request_endpoints = prometheus.get("slow_request_endpoints_delta") or prometheus.get("slow_request_endpoints", [])
user = login_payload.get("data", {}).get("user", {})

lines = [
    "# Monitoring Auth Performance Baseline",
    "",
    f"- Generated at: `{data['generated_at']}`",
    "- Service URLs:",
    "  - `mystocks-backend`: `http://localhost:8020`",
    "  - `mystocks-frontend`: `http://localhost:3020`",
    f"- Auth user: `{user.get('username', 'unknown')}` / role `{user.get('role', 'unknown')}`",
    f"- Concurrency: `{data['concurrent_users']}`",
    f"- Iterations per endpoint: `{data['iterations']}`",
    f"- SLO status (`P95 <= 300ms`, `error_rate <= 0.1%`): `{'COMPLIANT' if slo['compliant'] else 'NON-COMPLIANT'}`",
]

if slo.get("violations"):
    lines.append("- Violations:")
    lines.extend([f"  - {item}" for item in slo["violations"]])

lines.extend([
    "",
    "## Observability Snapshot",
    "",
    f"- `/api/metrics/health`: `{metrics_snapshot['metrics_health'].get('status', 'unknown')}`",
    f"- Prometheus `http_requests_total`: `{prometheus['http_requests_total']}`",
    f"- Prometheus `http_requests_total` delta during run: `{prometheus['http_requests_total_delta']}`",
    f"- Prometheus `slow_http_requests_total`: `{prometheus['slow_http_requests_total']}`",
    f"- Prometheus `slow_http_requests_total` delta during run: `{prometheus['slow_http_requests_total_delta']}`",
    f"- API health gauges: `{prometheus['api_health_status']}`",
    f"- DB active connections: `{prometheus['db_connections_active']}`",
    "",
    "### Slow Request Samples",
    "",
    *(
        [f"- `{item['method']} {item['endpoint']}` count=`{item['count']}`" for item in slow_request_endpoints[:5]]
        if slow_request_endpoints
        else ["- `none`"]
    ),
    "",
    "## Endpoint Results",
    "",
])

for item in data["endpoints"]:
    status = "OK" if item["p95_ms"] <= 300 and item["error_rate_percent"] <= 0.1 else "CHECK"
    lines.append(
        f"- `{item['method']} {item['endpoint']}`: avg={item['avg_ms']}ms p95={item['p95_ms']}ms error={item['error_rate_percent']}% [{status}]"
    )

lines.extend([
    "",
    "## Artifacts",
    "",
    f"- `{json_path.relative_to(json_path.parents[3])}`",
    f"- `{metrics_summary_path.relative_to(metrics_summary_path.parents[3])}`",
    f"- `{login_response_path.relative_to(login_response_path.parents[3])}`",
])

summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
PY

if [ "${DISABLE_QUALITY_GATE_GRAPHITI_CLOSEOUT:-0}" = "1" ]; then
    cat > "${GRAPHITI_CLOSEOUT_REPORT}" <<EOF
{
  "status": "skipped_disabled",
  "reason": "DISABLE_QUALITY_GATE_GRAPHITI_CLOSEOUT=1",
  "report_dir": "${REPORT_DIR}",
  "gate_kind": "monitoring-auth-performance-gate"
}
EOF
else
    python "${PROJECT_ROOT}/scripts/runtime/record_quality_gate_closeout.py" \
        --gate-kind monitoring-auth-performance-gate \
        --project-root "${PROJECT_ROOT}" \
        --report-dir "${REPORT_DIR}" \
        --output json > "${GRAPHITI_CLOSEOUT_REPORT}"
fi

printf -- '- `%s`\n' "$(realpath --relative-to="${PROJECT_ROOT}" "${GRAPHITI_CLOSEOUT_REPORT}")" >> "${SUMMARY_PATH}"

printf 'Monitoring auth performance baseline written to %s\n' "${SUMMARY_PATH}"
