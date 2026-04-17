#!/bin/bash
# run_playwright_cli_tests.sh — PM2 + playwright-cli E2E route test runner
#
# Usage:
#   bash scripts/run_playwright_cli_tests.sh --quick    # P0-P1 (login + dashboard)
#   bash scripts/run_playwright_cli_tests.sh --smoke    # P0-P3 (+ market, data pages)
#   bash scripts/run_playwright_cli_tests.sh --full     # All 20 routes
#
# Prerequisites:
#   - PM2 services running (mystocks-frontend, mystocks-backend)
#   - playwright-cli installed (npm install -g @playwright/cli@latest)
#   - .env with FRONTEND_PORT, BACKEND_PORT

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPORT_DIR="${PROJECT_ROOT}/reports/playwright-cli"

# Source .env
if [ -f "${PROJECT_ROOT}/.env" ]; then
    set -a
    # shellcheck disable=SC1091
    source "${PROJECT_ROOT}/.env"
    set +a
fi

FRONTEND_PORT="${FRONTEND_PORT:-3020}"
BACKEND_PORT="${BACKEND_PORT:-8020}"
BASE_URL="http://localhost:${FRONTEND_PORT}"
AUTH_STATE_FILE="${REPORT_DIR}/auth-state.json"

# Source route definitions
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/playwright_cli_routes.sh"

# Parse mode
MODE="${1:---full}"
case "${MODE}" in
    --quick)  PRIORITIES="${PRIORITY_QUICK}" ;;
    --smoke)  PRIORITIES="${PRIORITY_SMOKE}" ;;
    --full)   PRIORITIES="${PRIORITY_FULL}" ;;
    *)        echo "Usage: $0 [--quick|--smoke|--full]"; exit 1 ;;
esac

mkdir -p "${REPORT_DIR}"

# --- Helpers ---

log() { echo "[$(date '+%H:%M:%S')] $*"; }

pass() { echo "  PASS: $*"; TOTAL_PASS=$((TOTAL_PASS + 1)); }
fail() { echo "  FAIL: $*"; TOTAL_FAIL=$((TOTAL_FAIL + 1)); FAILED_ROUTES+=("$1"); }

cleanup() {
    log "Cleaning up browser sessions..."
    playwright-cli close-all 2>/dev/null || true
}
trap cleanup EXIT

check_services() {
    log "Checking PM2 services..."

    if ! curl -sf "http://localhost:${BACKEND_PORT}/health" > /dev/null 2>&1; then
        log "ERROR: Backend not responding on :${BACKEND_PORT}"
        exit 1
    fi
    log "Backend healthy on :${BACKEND_PORT}"

    if ! curl -sf "${BASE_URL}" > /dev/null 2>&1; then
        log "ERROR: Frontend not responding on :${FRONTEND_PORT}"
        exit 1
    fi
    log "Frontend healthy on :${FRONTEND_PORT}"
}

ensure_browser() {
    log "Ensuring chromium browser is available..."
    # Use existing chromium if available
    local chromium="/root/.cache/ms-playwright/chromium-1200/chrome-linux64/chrome"
    if [ -x "${chromium}" ]; then
        export PLAYWRIGHT_MCP_EXECUTABLE_PATH="${chromium}"
        log "Using existing chromium: ${chromium}"
        return
    fi
    # Fallback: install via playwright-cli
    log "Installing chromium browser..."
    playwright-cli install-browser chromium 2>&1 || true
}

login_and_save_state() {
    if [ -f "${AUTH_STATE_FILE}" ]; then
        log "Reusing saved auth state: ${AUTH_STATE_FILE}"
        return
    fi

    log "Logging in and saving auth state..."
    playwright-cli open "${BASE_URL}/login" > /dev/null 2>&1

    # Fill login form using role-based locators (resilient to DOM changes)
    playwright-cli fill "getByRole('textbox', { name: 'ENTER USERNAME' })" "admin" > /dev/null 2>&1
    playwright-cli fill "getByRole('textbox', { name: 'ENTER PASSWORD' })" "admin123" > /dev/null 2>&1
    playwright-cli click "getByRole('button', { name: 'SIGN IN' })" > /dev/null 2>&1

    # Wait for redirect to dashboard
    sleep 3

    # Save auth state for reuse
    playwright-cli state-save "${AUTH_STATE_FILE}" > /dev/null 2>&1
    log "Auth state saved to ${AUTH_STATE_FILE}"
}

should_test() {
    local priority="$1"
    for p in ${PRIORITIES}; do
        if [ "${p}" = "${priority}" ]; then
            return 0
        fi
    done
    return 1
}

run_route_test() {
    local route="$1"
    local expected_title="$2"
    local priority="$3"
    local url

    if [ "${route}" = "login" ]; then
        url="${BASE_URL}/login"
    else
        url="${BASE_URL}/${route}"
    fi

    log "Testing [${priority}] ${route}..."

    # Navigate and get title via raw output
    playwright-cli goto "${url}" > /dev/null 2>&1
    local title
    title=$(playwright-cli --raw eval "document.title" 2>/dev/null || echo "")

    if echo "${title}" | grep -q "${expected_title}"; then
        pass "[${priority}] ${route} => \"${title}\""
    else
        fail "[${priority}] ${route} => expected \"${expected_title}\" in title, got \"${title}\""
    fi
}

# --- Main ---

log "=== MyStocks Playwright-CLI Route Tests ==="
log "Mode: ${MODE} | Priorities: ${PRIORITIES}"
log "Frontend: ${BASE_URL} | Backend: http://localhost:${BACKEND_PORT}"
echo ""

check_services
ensure_browser
login_and_save_state

TOTAL_PASS=0
TOTAL_FAIL=0
FAILED_ROUTES=()

for entry in "${ROUTES[@]}"; do
    IFS='|' read -r route expected_title priority <<< "${entry}"
    if should_test "${priority}"; then
        run_route_test "${route}" "${expected_title}" "${priority}"
    fi
done

# --- Report ---

echo ""
log "=== RESULTS ==="
log "Passed: ${TOTAL_PASS} | Failed: ${TOTAL_FAIL} | Total: $((TOTAL_PASS + TOTAL_FAIL))"

TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
REPORT_FILE="${REPORT_DIR}/test-report-${TIMESTAMP}.txt"
{
    echo "MyStocks Playwright-CLI Test Report"
    echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "Mode: ${MODE}"
    echo "Passed: ${TOTAL_PASS} | Failed: ${TOTAL_FAIL}"
    if [ ${#FAILED_ROUTES[@]} -gt 0 ]; then
        echo "Failed routes:"
        for r in "${FAILED_ROUTES[@]}"; do echo "  - ${r}"; done
    fi
    echo "Result: $([ ${TOTAL_FAIL} -eq 0 ] && echo "PASS" || echo "FAIL")"
} > "${REPORT_FILE}"
log "Report: ${REPORT_FILE}"

if [ ${TOTAL_FAIL} -gt 0 ]; then
    exit 1
fi
exit 0
