#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
FRONTEND_DIR="${PROJECT_ROOT}/web/frontend"
BACKEND_DIR="${PROJECT_ROOT}/web/backend"

BACKEND_APP="mystocks-backend"
FRONTEND_APP="mystocks-frontend"

load_env_file() {
    local env_path="$1"
    if [ -f "${env_path}" ]; then
        set -a
        # shellcheck disable=SC1090
        source "${env_path}"
        set +a
    fi
}

ensure_local_playwright() {
    if [ -x "${FRONTEND_DIR}/node_modules/.bin/playwright" ]; then
        export PLAYWRIGHT_BIN="${FRONTEND_DIR}/node_modules/.bin/playwright"
        export PATH="${FRONTEND_DIR}/node_modules/.bin:${PATH}"
        export NODE_PATH="${FRONTEND_DIR}/node_modules${NODE_PATH:+:${NODE_PATH}}"
        return
    fi

    echo "Missing local Playwright binary at ${FRONTEND_DIR}/node_modules/.bin/playwright"
    echo "Run: npm --prefix web/frontend ci"
    exit 1
}

cleanup() {
    if [ "${KEEP_PM2_SERVICES:-0}" = "1" ]; then
        return
    fi

    pm2 delete "${BACKEND_APP}" >/dev/null 2>&1 || true
    pm2 delete "${FRONTEND_APP}" >/dev/null 2>&1 || true
}

wait_for_http() {
    local url="$1"
    local label="$2"
    local retries="$3"

    for _ in $(seq 1 "${retries}"); do
        if curl -sf "${url}" >/dev/null; then
            echo "${label}"
            return 0
        fi
        sleep 2
    done

    return 1
}

trap cleanup EXIT

load_env_file "${PROJECT_ROOT}/.env"
load_env_file "${FRONTEND_DIR}/.env"
load_env_file "${PROJECT_ROOT}/.env.example"

: "${BACKEND_PORT:=8020}"
: "${BACKEND_BACKUP_PORT:=8021}"
: "${FRONTEND_PORT:=3020}"
: "${FRONTEND_BACKUP_PORT:=3021}"

TARGET_BACKEND_PORT="${BACKEND_PORT}"
TARGET_FRONTEND_PORT="${FRONTEND_PORT}"
TARGET_FRONTEND_BACKUP_PORT="${FRONTEND_BACKUP_PORT}"

export NPM_CONFIG_CACHE="${NPM_CONFIG_CACHE:-${PROJECT_ROOT}/.cache/npm}"
export PLAYWRIGHT_BROWSERS_PATH="${PLAYWRIGHT_BROWSERS_PATH:-/tmp/ms-playwright}"
mkdir -p "${NPM_CONFIG_CACHE}" "${PLAYWRIGHT_BROWSERS_PATH}"

ensure_local_playwright

export DEVELOPMENT_MODE="${DEVELOPMENT_MODE:-true}"
export PYTHONPATH="${PYTHONPATH:-${PROJECT_ROOT}}"
export POSTGRESQL_HOST="${POSTGRESQL_HOST:-127.0.0.1}"
export POSTGRESQL_PORT="${POSTGRESQL_PORT:-5432}"
export POSTGRESQL_USER="${POSTGRESQL_USER:-postgres}"
export POSTGRESQL_PASSWORD="${POSTGRESQL_PASSWORD:-postgres}"
export POSTGRESQL_DATABASE="${POSTGRESQL_DATABASE:-postgres}"
export JWT_SECRET_KEY="${JWT_SECRET_KEY:-test-secret-for-pm2}"
export VITE_API_BASE_URL="${VITE_API_BASE_URL:-http://localhost:${TARGET_BACKEND_PORT}}"
export VITE_WS_URL="${VITE_WS_URL:-ws://localhost:${TARGET_BACKEND_PORT}}"

echo "--- Starting Services ---"
pm2 delete "${BACKEND_APP}" >/dev/null 2>&1 || true
pm2 delete "${FRONTEND_APP}" >/dev/null 2>&1 || true

pm2 start python3 \
    --name "${BACKEND_APP}" \
    --cwd "${BACKEND_DIR}" \
    -- \
    -m uvicorn app.main:app --host 0.0.0.0 --port "${TARGET_BACKEND_PORT}"

pm2 start npm \
    --name "${FRONTEND_APP}" \
    --cwd "${FRONTEND_DIR}" \
    -- \
    run dev:no-types -- --host 0.0.0.0 --port "${TARGET_FRONTEND_PORT}" --strictPort

MAX_RETRIES=20

if ! wait_for_http "http://localhost:${TARGET_BACKEND_PORT}/health" "Backend is READY" "${MAX_RETRIES}"; then
    echo "Backend Timeout"
    pm2 logs "${BACKEND_APP}" --lines 80 --nostream || true
    exit 1
fi

FOUND_PORT=""
for _ in $(seq 1 "${MAX_RETRIES}"); do
    for port in "${TARGET_FRONTEND_PORT}" "${TARGET_FRONTEND_BACKUP_PORT}"; do
        if curl -sf "http://localhost:${port}" >/dev/null; then
            FOUND_PORT="${port}"
            echo "Frontend FOUND on ${FOUND_PORT}"
            break 2
        fi
    done
    sleep 2
done

if [ -z "${FOUND_PORT}" ]; then
    echo "Frontend Timeout"
    pm2 logs "${FRONTEND_APP}" --lines 80 --nostream || true
    exit 1
fi

echo "Warming up for 5s..."
sleep 5

echo "--- Running Tests on http://localhost:${FOUND_PORT} ---"
export BASE_URL="http://localhost:${FOUND_PORT}"

if "${PLAYWRIGHT_BIN}" test tests/navigation-consistency.spec.ts --config="${PROJECT_ROOT}/playwright.config.ts" --project=chromium; then
    TEST_EXIT_CODE=0
else
    TEST_EXIT_CODE=$?
fi

exit "${TEST_EXIT_CODE}"
