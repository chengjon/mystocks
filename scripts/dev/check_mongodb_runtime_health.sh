#!/usr/bin/env bash
set -euo pipefail

HOST="${MONGODB_HOST:-}"
PORT="${MONGODB_PORT:-}"
USERNAME="${MONGODB_ROOT_USERNAME:-${USERNAME:-}}"
PASSWORD="${MONGODB_ROOT_PASSWORD:-${PASSWORD:-}}"
AUTH_SOURCE="${MONGODB_AUTH_SOURCE:-admin}"
CONTAINER_NAME="${MONGODB_CONTAINER_NAME:-mystocks-mongodb}"

if [[ -z "${HOST}" || -z "${PORT}" ]]; then
  LEGACY_TARGET="${MONGODB_IP:-}"
  if [[ -n "${LEGACY_TARGET}" ]]; then
    if [[ "${LEGACY_TARGET}" == *:* ]]; then
      HOST="${HOST:-${LEGACY_TARGET%%:*}}"
      PORT="${PORT:-${LEGACY_TARGET##*:}}"
    else
      HOST="${HOST:-${LEGACY_TARGET}}"
    fi
  fi
fi

HOST="${HOST:-localhost}"
PORT="${PORT:-27017}"

CMD=(
  mongosh
  --host "${HOST}"
  --port "${PORT}"
  --quiet
)

if [[ -n "${USERNAME}" ]]; then
  CMD+=( -u "${USERNAME}" )
fi

if [[ -n "${PASSWORD}" ]]; then
  CMD+=( -p "${PASSWORD}" )
fi

if [[ -n "${USERNAME}" || -n "${PASSWORD}" ]]; then
  CMD+=( --authenticationDatabase "${AUTH_SOURCE}" )
fi

CMD+=( --eval "db.adminCommand({ ping: 1 })" )

if command -v mongosh >/dev/null 2>&1; then
  "${CMD[@]}"
  exit 0
fi

if command -v docker >/dev/null 2>&1; then
  docker exec "${CONTAINER_NAME}" "${CMD[@]}"
  exit 0
fi

echo "mongosh not found on host and docker fallback unavailable" >&2
exit 127
