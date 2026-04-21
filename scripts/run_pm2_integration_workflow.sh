#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

usage() {
    cat <<'EOF'
Usage:
  bash scripts/run_pm2_integration_workflow.sh gate
  bash scripts/run_pm2_integration_workflow.sh regression
  bash scripts/run_pm2_integration_workflow.sh all

Modes:
  gate        Run pre-commit frontend checks plus the standalone PM2 gate
  regression  Run the long PM2-backed integration regression chain
  all         Run gate first, then regression
EOF
}

clean_pm2() {
    pm2 stop all >/dev/null 2>&1 || true
    pm2 delete all >/dev/null 2>&1 || true
}

find_port_listeners() {
    local port="$1"

    ss -ltnp "( sport = :${port} )" 2>/dev/null | tail -n +2 || true
}

ensure_ports_free() {
    local occupied=0

    for port in 8020 3020; do
        local listeners
        listeners="$(find_port_listeners "${port}")"

        if [ -n "${listeners}" ]; then
            occupied=1
            echo "Port ${port} is already in use before PM2 startup:"
            printf '%s\n' "${listeners}"
        fi
    done

    if [ "${occupied}" -ne 0 ]; then
        echo "Preflight failed: required PM2 test ports are not free."
        return 1
    fi

    return 0
}

log_line_count() {
    local file_path="$1"
    if [ -f "$file_path" ]; then
        wc -l < "$file_path"
        return 0
    fi

    printf '0\n'
}

print_new_log_matches() {
    local file_path="$1"
    local start_line="$2"
    local pattern="$3"

    if [ ! -f "$file_path" ]; then
        return 0
    fi

    sed -n "$((start_line + 1)),\$p" "$file_path" | grep -Ei "$pattern" || true
}

print_new_log_tail() {
    local file_path="$1"
    local start_line="$2"
    local tail_lines="${3:-50}"

    if [ ! -f "$file_path" ]; then
        return 0
    fi

    sed -n "$((start_line + 1)),\$p" "$file_path" | tail -n "$tail_lines" || true
}

extract_count() {
    local summary_line="$1"
    local label="$2"
    local match

    match="$(printf '%s\n' "$summary_line" | grep -Eo "[0-9]+ ${label}" | tail -n 1 || true)"
    if [ -n "$match" ]; then
        printf '%s\n' "${match%% *}"
        return 0
    fi

    printf '0\n'
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

print_report_header() {
    echo "=== MYSTOCKS INTEGRATION TEST REPORT ==="
    echo "Mode: $1"
    echo "Date: $(date '+%Y-%m-%d %H:%M:%S %z')"
}

run_gate() {
    local type_check_command="npm run type-check"
    local frontend_test_command="npm run test"
    local gate_e2e_command="bash scripts/run_e2e_pm2.sh"

    print_report_header "gate"
    clean_pm2
    ensure_ports_free

    cd "${PROJECT_ROOT}/web/frontend"
    npm run type-check
    npm run test

    cd "${PROJECT_ROOT}"
    bash scripts/run_e2e_pm2.sh

    echo "Type Check Command: ${type_check_command}"
    echo "Frontend Test Command: ${frontend_test_command}"
    echo "Gate E2E Command: ${gate_e2e_command}"
    echo "Type Check Exit Code: 0"
    echo "Frontend Test Exit Code: 0"
    echo "Gate E2E Exit Code: 0"
    echo "Gate Result: PASS"
    echo "======================================"
}

run_regression() {
    local e2e_command="PLAYWRIGHT_EXTERNAL_FRONTEND=1 npm run test:e2e:business-smoke"
    local pytest_command="pytest --no-cov -q web/backend/tests/test_api_integration.py web/backend/tests/test_auth.py"
    local e2e_log
    local pytest_log
    local e2e_summary_line
    local pytest_summary_line
    local e2e_passed
    local e2e_failed
    local e2e_skipped
    local pytest_passed
    local pytest_failed
    local pytest_skipped
    local backend_out_log="/root/.pm2/logs/mystocks-backend-out.log"
    local backend_error_log="/root/.pm2/logs/mystocks-backend-error.log"
    local frontend_out_log="/root/.pm2/logs/mystocks-frontend-out.log"
    local frontend_error_log="/root/.pm2/logs/mystocks-frontend-error.log"
    local backend_out_start
    local backend_error_start
    local frontend_out_start
    local frontend_error_start

    e2e_log="$(mktemp /tmp/mystocks-e2e-XXXX.log)"
    pytest_log="$(mktemp /tmp/mystocks-pytest-XXXX.log)"

    print_report_header "regression"
    clean_pm2
    ensure_ports_free

    backend_out_start="$(log_line_count "${backend_out_log}")"
    backend_error_start="$(log_line_count "${backend_error_log}")"
    frontend_out_start="$(log_line_count "${frontend_out_log}")"
    frontend_error_start="$(log_line_count "${frontend_error_log}")"

    cd "${PROJECT_ROOT}"
    pm2 start ecosystem.test.config.js

    wait_for_url "http://localhost:8020/health" "Backend"
    wait_for_url "http://localhost:8020/api/health/ready" "Backend readiness"
    wait_for_url "http://localhost:3020/" "Frontend"

    cd "${PROJECT_ROOT}/web/frontend"
    set +e
    PLAYWRIGHT_EXTERNAL_FRONTEND=1 npm run test:e2e:business-smoke 2>&1 \
        | perl -pe 's/\e\[[0-9;]*[[:alpha:]]//g' \
        | tee "${e2e_log}"
    local e2e_status=("${PIPESTATUS[@]}")
    set -e
    E2E_EXIT_CODE="${e2e_status[0]}"

    cd "${PROJECT_ROOT}"
    set +e
    pytest --no-cov -q \
        web/backend/tests/test_api_integration.py \
        web/backend/tests/test_auth.py 2>&1 \
        | tee "${pytest_log}"
    local pytest_status=("${PIPESTATUS[@]}")
    set -e
    PYTEST_EXIT_CODE="${pytest_status[0]}"

    e2e_summary_line="$(grep -E "[0-9]+ passed" "${e2e_log}" | tail -n 1 || true)"
    pytest_summary_line="$(grep -E "([0-9]+ passed|[0-9]+ failed|[0-9]+ skipped)" "${pytest_log}" | tail -n 1 || true)"

    e2e_passed="$(extract_count "${e2e_summary_line}" "passed")"
    e2e_failed="$(extract_count "${e2e_summary_line}" "failed")"
    e2e_skipped="$(extract_count "${e2e_summary_line}" "skipped")"
    pytest_passed="$(extract_count "${pytest_summary_line}" "passed")"
    pytest_failed="$(extract_count "${pytest_summary_line}" "failed")"
    pytest_skipped="$(extract_count "${pytest_summary_line}" "skipped")"

    echo "PM2 Status:"
    pm2 list | grep "mystocks-" || true
    echo "Frontend: http://localhost:3020 | Backend: http://localhost:8020"
    echo "E2E Command: ${e2e_command}"
    echo "Pytest Command: ${pytest_command}"
    echo "E2E Summary: passed=${e2e_passed} failed=${e2e_failed} skipped=${e2e_skipped}"
    echo "Pytest Summary: passed=${pytest_passed} failed=${pytest_failed} skipped=${pytest_skipped}"
    echo "E2E Exit Code: ${E2E_EXIT_CODE}"
    echo "Pytest Exit Code: ${PYTEST_EXIT_CODE}"
    echo "Backend Error Scan:"
    print_new_log_matches "${backend_out_log}" "${backend_out_start}" "error|critical|traceback"
    print_new_log_matches "${backend_error_log}" "${backend_error_start}" "error|critical|traceback"
    echo "Frontend Error Scan:"
    print_new_log_matches "${frontend_out_log}" "${frontend_out_start}" "error|failed|fetch"
    print_new_log_matches "${frontend_error_log}" "${frontend_error_start}" "error|failed|fetch"
    echo "Recent Backend Logs:"
    print_new_log_tail "${backend_out_log}" "${backend_out_start}" 50
    print_new_log_tail "${backend_error_log}" "${backend_error_start}" 50
    echo "Recent Frontend Logs:"
    print_new_log_tail "${frontend_out_log}" "${frontend_out_start}" 50
    print_new_log_tail "${frontend_error_log}" "${frontend_error_start}" 50
    if [ "${E2E_EXIT_CODE}" -eq 0 ] && [ "${PYTEST_EXIT_CODE}" -eq 0 ]; then
        echo "Regression Result: PASS"
        echo "======================================"
        return 0
    fi

    echo "Regression Result: FAIL"
    echo "======================================"
    return 1
}

MODE="${1:-}"

case "${MODE}" in
    gate)
        run_gate
        ;;
    regression)
        run_regression
        ;;
    all)
        run_gate
        run_regression
        ;;
    *)
        usage
        exit 1
        ;;
esac
