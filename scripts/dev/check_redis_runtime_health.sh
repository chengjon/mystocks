#!/usr/bin/env bash
set -euo pipefail

HOST="${REDIS_HOST:-localhost}"
PORT="${REDIS_PORT:-6379}"
PASSWORD="${REDIS_PASSWORD:-}"
APP_CACHE_DB="${REDIS_APP_CACHE_DB:-${REDIS_DB:-1}}"
MONITORING_DB="${REDIS_MONITORING_DB:-${REDIS_DB:-0}}"
CONTAINER_NAME="${REDIS_CONTAINER_NAME:-mystocks-redis}"

run_redis_cli() {
  local db="$1"
  shift
  local cmd=(redis-cli -h "${HOST}" -p "${PORT}" -n "${db}")
  if [[ -n "${PASSWORD}" ]]; then
    cmd+=( -a "${PASSWORD}" )
  fi
  cmd+=( "$@" )
  "${cmd[@]}"
}

if command -v redis-cli >/dev/null 2>&1; then
  run_redis_cli "${APP_CACHE_DB}" ping
  run_redis_cli "${MONITORING_DB}" ping
  exit 0
fi

if command -v docker >/dev/null 2>&1; then
  docker exec "${CONTAINER_NAME}" redis-cli -n "${APP_CACHE_DB}" ping
  docker exec "${CONTAINER_NAME}" redis-cli -n "${MONITORING_DB}" ping
  exit 0
fi

echo "redis-cli not found on host and docker fallback unavailable" >&2
exit 127
