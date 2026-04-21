#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
TIMESTAMP="$(date '+%Y%m%d-%H%M%S')"
REPORT_DIR="${PROJECT_ROOT}/reports/analysis/api-performance-gate/${TIMESTAMP}"
TEXT_REPORT="${REPORT_DIR}/benchmark.txt"
JSON_REPORT="${REPORT_DIR}/benchmark.json"
SUMMARY_PATH="${REPORT_DIR}/SUMMARY.md"
PM2_STATUS_PATH="${REPORT_DIR}/pm2-status.txt"
METRICS_HEAD_PATH="${REPORT_DIR}/metrics-head.txt"
METRICS_BASELINE_RAW_PATH="${REPORT_DIR}/metrics.baseline.raw.txt"
METRICS_RAW_PATH="${REPORT_DIR}/metrics.raw.txt"
METRICS_HEALTH_PATH="${REPORT_DIR}/metrics-health.json"
METRICS_SUMMARY_PATH="${REPORT_DIR}/metrics-summary.json"
ENDPOINTS_FILE="${PROJECT_ROOT}/tests/performance/api_smoke_endpoints.json"

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

pm2 ls --no-color > "${PM2_STATUS_PATH}"
curl --noproxy '*' --silent "http://localhost:8020/metrics" > "${METRICS_BASELINE_RAW_PATH}"

python tests/performance/benchmark.py \
    --url "http://localhost:8020" \
    --users 5 \
    --iterations 20 \
    --endpoints-file "${ENDPOINTS_FILE}" \
    --output "${TEXT_REPORT}" \
    --json-output "${JSON_REPORT}"

curl --noproxy '*' --silent "http://localhost:8020/api/metrics/health" > "${METRICS_HEALTH_PATH}"
curl --noproxy '*' --silent "http://localhost:8020/metrics" > "${METRICS_RAW_PATH}"
sed -n '1,40p' "${METRICS_RAW_PATH}" > "${METRICS_HEAD_PATH}"

python scripts/dev/quality_gate/summarize_metrics_snapshot.py \
    --metrics-file "${METRICS_RAW_PATH}" \
    --baseline-metrics-file "${METRICS_BASELINE_RAW_PATH}" \
    --health-file "${METRICS_HEALTH_PATH}" \
    --output "${METRICS_SUMMARY_PATH}"

python - <<'PY' "${JSON_REPORT}" "${SUMMARY_PATH}" "${REPORT_DIR}" "${PM2_STATUS_PATH}" "${METRICS_SUMMARY_PATH}"
import json
import sys
from pathlib import Path

json_path = Path(sys.argv[1])
summary_path = Path(sys.argv[2])
report_dir = Path(sys.argv[3])
pm2_status_path = Path(sys.argv[4])
metrics_summary_path = Path(sys.argv[5])

data = json.loads(json_path.read_text(encoding="utf-8"))
slo = data["slo_status"]
endpoints = data["endpoints"]
violations = slo.get("violations", [])
metrics_snapshot = json.loads(metrics_summary_path.read_text(encoding="utf-8"))
prometheus = metrics_snapshot["prometheus_snapshot"]
metrics_health = metrics_snapshot["metrics_health"]
slow_request_endpoints = prometheus.get("slow_request_endpoints_delta") or prometheus.get("slow_request_endpoints", [])

def status_line(item):
    status = "OK" if item["p95_ms"] <= 300 and item["error_rate_percent"] <= 0.1 else "CHECK"
    return f"- `{item['method']} {item['endpoint']}`: avg={item['avg_ms']}ms p95={item['p95_ms']}ms error={item['error_rate_percent']}% [{status}]"

summary = [
    "# API Performance Baseline",
    "",
    f"- Generated at: `{data['generated_at']}`",
    f"- Backend URL: `{data['base_url']}`",
    "- Service URLs:",
    "  - `mystocks-backend`: `http://localhost:8020`",
    "  - `mystocks-frontend`: `http://localhost:3020`",
    f"- Concurrency: `{data['concurrent_users']}`",
    f"- Iterations per endpoint: `{data['iterations']}`",
    f"- Overall average response time: `{data['summary']['overall_avg_ms']}ms`",
    f"- Overall average P95 response time: `{data['summary']['overall_p95_ms']}ms`",
    f"- SLO status (`P95 <= 300ms`, `error_rate <= 0.1%`): `{'COMPLIANT' if slo['compliant'] else 'NON-COMPLIANT'}`",
]

if violations:
    summary.append("- Violations:")
    summary.extend([f"  - {item}" for item in violations])

summary.extend([
    "",
    "## Observability Snapshot",
    "",
    f"- `/api/metrics/health`: `{metrics_health.get('status', 'unknown')}`",
    f"- Prometheus `http_requests_total`: `{prometheus['http_requests_total']}`",
    f"- Prometheus `http_requests_total` delta during run: `{prometheus['http_requests_total_delta']}`",
    f"- Prometheus `slow_http_requests_total`: `{prometheus['slow_http_requests_total']}`",
    f"- Prometheus `slow_http_requests_total` delta during run: `{prometheus['slow_http_requests_total_delta']}`",
    f"- Prometheus `http_requests_active` max sample: `{prometheus['active_requests_max']}`",
    f"- Prometheus `http_requests_in_progress` max sample: `{prometheus['requests_in_progress_max']}`",
    f"- Process resident memory: `{int(prometheus['process_resident_memory_bytes'])}` bytes",
    f"- Process CPU time: `{prometheus['process_cpu_seconds_total']}` seconds",
    f"- API health gauges: `{prometheus['api_health_status']}`",
    f"- DB active connections: `{prometheus['db_connections_active']}`",
    f"- Cache counters: `hits={prometheus['cache_hits_total']}` `misses={prometheus['cache_misses_total']}` `hit_ratio={prometheus['cache_hit_ratio']}`",
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
    *[status_line(item) for item in endpoints],
    "",
    "## Artifacts",
    "",
    f"- `{json_path.relative_to(report_dir.parents[3])}`",
    f"- `{(report_dir / 'benchmark.txt').relative_to(report_dir.parents[3])}`",
    f"- `{pm2_status_path.relative_to(report_dir.parents[3])}`",
    f"- `{(report_dir / 'metrics-head.txt').relative_to(report_dir.parents[3])}`",
    f"- `{metrics_summary_path.relative_to(report_dir.parents[3])}`",
])

summary_path.write_text("\n".join(summary) + "\n", encoding="utf-8")
PY

printf 'API performance baseline written to %s\n' "${SUMMARY_PATH}"
