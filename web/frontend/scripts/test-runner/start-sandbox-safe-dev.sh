#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TMP_FRONTEND_DIR="${TMP_FRONTEND_DIR:-/tmp/mystocks-frontend-dev}"
NPM_CACHE_DIR="${NPM_CACHE_DIR:-/tmp/npm-cache}"
FRONTEND_PORT_WAS_SET="${FRONTEND_PORT+x}"
BACKEND_PORT_WAS_SET="${BACKEND_PORT+x}"
FRONTEND_BASE_URL_WAS_SET="${FRONTEND_BASE_URL+x}"
BACKEND_BASE_URL_WAS_SET="${BACKEND_BASE_URL+x}"

FRONTEND_PORT="${FRONTEND_PORT:-3020}"
FRONTEND_BACKUP_PORT="${FRONTEND_BACKUP_PORT:-3021}"
BACKEND_PORT="${BACKEND_PORT:-8020}"
BACKEND_BACKUP_PORT="${BACKEND_BACKUP_PORT:-8021}"
VITE_API_BASE_URL="${VITE_API_BASE_URL:-/api}"
VITE_USE_MOCK_DATA="${VITE_USE_MOCK_DATA:-false}"

port_is_listening() {
  ss -ltnH "( sport = :$1 )" 2>/dev/null | grep -q .
}

if [ -z "${FRONTEND_PORT_WAS_SET}" ] && port_is_listening "${FRONTEND_PORT}"; then
  echo "[sandbox-dev] frontend port ${FRONTEND_PORT} already in use, falling back to ${FRONTEND_BACKUP_PORT}"
  FRONTEND_PORT="${FRONTEND_BACKUP_PORT}"
fi

if [ -z "${BACKEND_PORT_WAS_SET}" ] && port_is_listening "${BACKEND_PORT}"; then
  echo "[sandbox-dev] backend port ${BACKEND_PORT} already in use, falling back to ${BACKEND_BACKUP_PORT}"
  BACKEND_PORT="${BACKEND_BACKUP_PORT}"
fi

if [ -z "${FRONTEND_BASE_URL_WAS_SET}" ]; then
  FRONTEND_BASE_URL="http://127.0.0.1:${FRONTEND_PORT}"
fi

if [ -z "${BACKEND_BASE_URL_WAS_SET}" ]; then
  BACKEND_BASE_URL="http://127.0.0.1:${BACKEND_PORT}"
fi

echo "[sandbox-dev] frontend source: ${ROOT_DIR}"
echo "[sandbox-dev] tmp frontend copy: ${TMP_FRONTEND_DIR}"
echo "[sandbox-dev] frontend url: ${FRONTEND_BASE_URL}"
echo "[sandbox-dev] backend url: ${BACKEND_BASE_URL}"

if ! command -v rsync >/dev/null 2>&1; then
  echo "[sandbox-dev] rsync not found, falling back to cp -a"
fi

rm -rf "${TMP_FRONTEND_DIR}"
mkdir -p "$(dirname "${TMP_FRONTEND_DIR}")" "${NPM_CACHE_DIR}"

if command -v rsync >/dev/null 2>&1; then
  rsync -a --delete "${ROOT_DIR}/" "${TMP_FRONTEND_DIR}/"
else
  cp -a "${ROOT_DIR}" "${TMP_FRONTEND_DIR}"
fi

pushd "${TMP_FRONTEND_DIR}" >/dev/null

if [ ! -d node_modules ] || [ package-lock.json -nt node_modules ]; then
  echo "[sandbox-dev] installing frontend dependencies"
  PUPPETEER_SKIP_DOWNLOAD=true \
  PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 \
  npm_config_cache="${NPM_CACHE_DIR}" \
  npm ci
fi

echo "[sandbox-dev] starting Vite in sandbox-safe copy"
FRONTEND_PORT="${FRONTEND_PORT}" \
FRONTEND_BACKUP_PORT="${FRONTEND_BACKUP_PORT}" \
BACKEND_PORT="${BACKEND_PORT}" \
BACKEND_BACKUP_PORT="${BACKEND_BACKUP_PORT}" \
FRONTEND_BASE_URL="${FRONTEND_BASE_URL}" \
BACKEND_BASE_URL="${BACKEND_BASE_URL}" \
VITE_API_BASE_URL="${VITE_API_BASE_URL}" \
VITE_USE_MOCK_DATA="${VITE_USE_MOCK_DATA}" \
npm run dev:no-types -- --host 127.0.0.1 --port "${FRONTEND_PORT}" --strictPort
