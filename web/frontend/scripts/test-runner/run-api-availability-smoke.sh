#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REPO_ROOT="$(cd "${ROOT_DIR}/../.." && pwd)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/port-selection.sh"

TMP_FRONTEND_DIR="${TMP_FRONTEND_DIR:-/tmp/mystocks-frontend-e2e}"
NPM_CACHE_DIR="${NPM_CACHE_DIR:-/tmp/npm-cache}"
PLAYWRIGHT_BROWSERS_PATH="${PLAYWRIGHT_BROWSERS_PATH:-/tmp/pw-browsers}"
FRONTEND_PORT_WAS_SET="${FRONTEND_PORT+x}"
BACKEND_PORT_WAS_SET="${BACKEND_PORT+x}"
FRONTEND_BASE_URL_WAS_SET="${FRONTEND_BASE_URL+x}"
BACKEND_BASE_URL_WAS_SET="${BACKEND_BASE_URL+x}"

FRONTEND_PORT="${FRONTEND_PORT:-3020}"
FRONTEND_BACKUP_PORT="${FRONTEND_BACKUP_PORT:-3021}"
BACKEND_PORT="${BACKEND_PORT:-8020}"
BACKEND_BACKUP_PORT="${BACKEND_BACKUP_PORT:-8021}"
PLAYWRIGHT_GREP="${PLAYWRIGHT_GREP:-Data-Indicator|Watchlist-Screener}"
SMOKE_USERNAME="${SMOKE_USERNAME:-admin}"
SMOKE_PASSWORD="${SMOKE_PASSWORD:-admin123}"
START_BACKEND_IF_NEEDED="${START_BACKEND_IF_NEEDED:-false}"
BACKEND_WORKDIR="${BACKEND_WORKDIR:-${REPO_ROOT}/web/backend}"
BACKEND_LOG_FILE="${BACKEND_LOG_FILE:-/tmp/mystocks-api-availability-smoke-backend.log}"
POSTGRESQL_HOST="${POSTGRESQL_HOST:-localhost}"
POSTGRESQL_PORT="${POSTGRESQL_PORT:-5438}"
POSTGRESQL_USER="${POSTGRESQL_USER:-postgres}"
POSTGRESQL_PASSWORD="${POSTGRESQL_PASSWORD:-test_password}"
POSTGRESQL_DATABASE="${POSTGRESQL_DATABASE:-mystocks_test}"
JWT_SECRET_KEY="${JWT_SECRET_KEY:-test_secret_key_for_testing_only_do_not_use_in_production}"
ADMIN_INITIAL_PASSWORD="${ADMIN_INITIAL_PASSWORD:-admin123}"
BACKEND_PID=""

RESOLVED_FRONTEND_PORT="$(resolve_frontend_port "${FRONTEND_PORT}" "${FRONTEND_BACKUP_PORT}" "${FRONTEND_PORT_WAS_SET}")"
if [ "${RESOLVED_FRONTEND_PORT}" != "${FRONTEND_PORT}" ]; then
  echo "[smoke] frontend port ${FRONTEND_PORT} already in use, falling back to ${FRONTEND_BACKUP_PORT}"
  FRONTEND_PORT="${RESOLVED_FRONTEND_PORT}"
fi

if [ -z "${FRONTEND_BASE_URL_WAS_SET}" ]; then
  FRONTEND_BASE_URL="http://127.0.0.1:${FRONTEND_PORT}"
fi

if [ -z "${BACKEND_BASE_URL_WAS_SET}" ]; then
  BACKEND_BASE_URL="http://127.0.0.1:${BACKEND_PORT}"
fi

echo "[smoke] frontend source: ${ROOT_DIR}"
echo "[smoke] tmp frontend copy: ${TMP_FRONTEND_DIR}"
echo "[smoke] frontend url: ${FRONTEND_BASE_URL}"
echo "[smoke] backend url: ${BACKEND_BASE_URL}"

cleanup() {
  if [ -n "${BACKEND_PID}" ] && kill -0 "${BACKEND_PID}" >/dev/null 2>&1; then
    kill "${BACKEND_PID}" >/dev/null 2>&1 || true
    wait "${BACKEND_PID}" 2>/dev/null || true
  fi
}
trap cleanup EXIT

login_backend() {
  local output_file="$1"
  curl -sS -o "${output_file}" -w '%{http_code}' \
    -X POST "${BACKEND_BASE_URL}/api/v1/auth/login" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "username=${SMOKE_USERNAME}" \
  --data-urlencode "password=${SMOKE_PASSWORD}" || true
}

wait_for_backend_login() {
  local output_file="$1"
  local status=""
  for _ in $(seq 1 60); do
    status="$(login_backend "${output_file}")"
    if [ "${status}" = "200" ]; then
      printf '%s' "${status}"
      return 0
    fi
    sleep 1
  done
  printf '%s' "${status}"
  return 1
}

echo "[smoke] validating backend auth and target APIs"
LOGIN_BODY_FILE="$(mktemp)"
LOGIN_STATUS="$(login_backend "${LOGIN_BODY_FILE}")"

if [ "${LOGIN_STATUS}" != "200" ] && [ "${START_BACKEND_IF_NEEDED}" = "true" ]; then
  echo "[smoke] backend unavailable, starting local uvicorn"
  SPAWN_BACKEND_PORT="$(resolve_backend_spawn_port "${BACKEND_PORT}" "${BACKEND_BACKUP_PORT}" "${BACKEND_PORT_WAS_SET}")"
  if [ "${SPAWN_BACKEND_PORT}" != "${BACKEND_PORT}" ]; then
    echo "[smoke] backend port ${BACKEND_PORT} is occupied, spawning local backend on ${SPAWN_BACKEND_PORT}"
    BACKEND_PORT="${SPAWN_BACKEND_PORT}"
    if [ -z "${BACKEND_BASE_URL_WAS_SET}" ]; then
      BACKEND_BASE_URL="http://127.0.0.1:${BACKEND_PORT}"
      echo "[smoke] backend url updated to ${BACKEND_BASE_URL}"
    fi
  fi
  (
    cd "${BACKEND_WORKDIR}"
    TESTING=true \
    DEVELOPMENT_MODE=true \
    MOCK_AUTH_ENABLED=true \
    POSTGRESQL_HOST="${POSTGRESQL_HOST}" \
    POSTGRESQL_PORT="${POSTGRESQL_PORT}" \
    POSTGRESQL_USER="${POSTGRESQL_USER}" \
    POSTGRESQL_PASSWORD="${POSTGRESQL_PASSWORD}" \
    POSTGRESQL_DATABASE="${POSTGRESQL_DATABASE}" \
    JWT_SECRET_KEY="${JWT_SECRET_KEY}" \
    ADMIN_INITIAL_PASSWORD="${ADMIN_INITIAL_PASSWORD}" \
    BACKEND_PORT="${BACKEND_PORT}" \
    BACKEND_BACKUP_PORT="${BACKEND_BACKUP_PORT}" \
    PYTHONPATH="${REPO_ROOT}" \
    uvicorn app.main:app --host 127.0.0.1 --port "${BACKEND_PORT}" >"${BACKEND_LOG_FILE}" 2>&1
  ) &
  BACKEND_PID=$!

  LOGIN_STATUS="$(wait_for_backend_login "${LOGIN_BODY_FILE}")" || true
fi

if [ "${LOGIN_STATUS}" != "200" ]; then
  echo "[smoke] backend login failed with HTTP ${LOGIN_STATUS}"
  cat "${LOGIN_BODY_FILE}" || true
  if [ -f "${BACKEND_LOG_FILE}" ]; then
    tail -n 120 "${BACKEND_LOG_FILE}" || true
  fi
  rm -f "${LOGIN_BODY_FILE}"
  exit 1
fi

AUTH_TOKEN="$(node -e "const fs=require('fs');const data=JSON.parse(fs.readFileSync(process.argv[1],'utf8'));process.stdout.write(String(data?.data?.token||''))" "${LOGIN_BODY_FILE}")"
rm -f "${LOGIN_BODY_FILE}"

if [ -z "${AUTH_TOKEN}" ]; then
  echo "[smoke] backend login succeeded but token missing"
  exit 1
fi

for ENDPOINT in "/api/v1/indicators/registry" "/api/v1/data/stocks/basic?limit=1"; do
  STATUS="$(curl -sS -o /dev/null -w '%{http_code}' -H "Authorization: Bearer ${AUTH_TOKEN}" "${BACKEND_BASE_URL}${ENDPOINT}")"
  if [ "${STATUS}" != "200" ]; then
    echo "[smoke] endpoint check failed: ${ENDPOINT} -> HTTP ${STATUS}"
    exit 1
  fi
done

if ! command -v rsync >/dev/null 2>&1; then
  echo "[smoke] rsync not found, falling back to cp -a"
fi

rm -rf "${TMP_FRONTEND_DIR}"
mkdir -p "$(dirname "${TMP_FRONTEND_DIR}")" "${NPM_CACHE_DIR}" "${PLAYWRIGHT_BROWSERS_PATH}"

if command -v rsync >/dev/null 2>&1; then
  rsync -a --delete "${ROOT_DIR}/" "${TMP_FRONTEND_DIR}/"
else
  cp -a "${ROOT_DIR}" "${TMP_FRONTEND_DIR}"
fi

node - <<'NODE' "${TMP_FRONTEND_DIR}/tests/e2e/comprehensive-all-pages.spec.ts"
const fs = require('node:fs')
const filePath = process.argv[2]
let source = fs.readFileSync(filePath, 'utf8')
const needle = "    localStorage.setItem('auth_token', token);\n    localStorage.setItem('auth_user', JSON.stringify(user));\n    // Keep backward compatibility with legacy auth helpers.\n    localStorage.setItem('token', token);\n    localStorage.setItem('user', JSON.stringify(user));"
const replacement = "    localStorage.setItem('auth_token', token);\n    localStorage.setItem('auth_user', JSON.stringify(user));\n    localStorage.setItem('access_token', token);\n    // Keep backward compatibility with legacy auth helpers.\n    localStorage.setItem('token', token);\n    localStorage.setItem('user', JSON.stringify(user));"
if (source.includes(needle) && !source.includes(\"localStorage.setItem('access_token', token);\")) {
  source = source.replace(needle, replacement)
  fs.writeFileSync(filePath, source)
}
NODE

pushd "${TMP_FRONTEND_DIR}" >/dev/null

if [ ! -d node_modules ] || [ package-lock.json -nt node_modules ]; then
  echo "[smoke] installing frontend dependencies"
  PUPPETEER_SKIP_DOWNLOAD=true \
  PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 \
  npm_config_cache="${NPM_CACHE_DIR}" \
  npm ci
fi

echo "[smoke] ensuring Playwright chromium"
PLAYWRIGHT_BROWSERS_PATH="${PLAYWRIGHT_BROWSERS_PATH}" ./node_modules/.bin/playwright install chromium

echo "[smoke] running Playwright subset: ${PLAYWRIGHT_GREP}"
PLAYWRIGHT_BROWSERS_PATH="${PLAYWRIGHT_BROWSERS_PATH}" \
FRONTEND_PORT="${FRONTEND_PORT}" \
FRONTEND_BACKUP_PORT="${FRONTEND_BACKUP_PORT}" \
BACKEND_PORT="${BACKEND_PORT}" \
BACKEND_BACKUP_PORT="${BACKEND_BACKUP_PORT}" \
FRONTEND_BASE_URL="${FRONTEND_BASE_URL}" \
BACKEND_BASE_URL="${BACKEND_BASE_URL}" \
VITE_API_BASE_URL=/api \
VITE_USE_MOCK_DATA=true \
./node_modules/.bin/playwright test tests/e2e/comprehensive-all-pages.spec.ts \
  --config playwright.config.js \
  --project=chromium \
  --grep "${PLAYWRIGHT_GREP}"

echo "[smoke] completed"
