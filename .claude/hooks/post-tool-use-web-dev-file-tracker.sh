#!/usr/bin/env bash

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-$(cd "${SCRIPT_DIR}/../.." && pwd)}"
WEB_DEV_LOG="${PROJECT_ROOT}/var/log/web-dev/tracing/web-edit-tracker.jsonl"

mkdir -p "$(dirname "${WEB_DEV_LOG}")"

INPUT_JSON="$(cat 2>/dev/null || true)"
if [ -z "${INPUT_JSON}" ]; then
    exit 0
fi

if ! printf '%s' "${INPUT_JSON}" | jq empty >/dev/null 2>&1; then
    exit 0
fi

TOOL_NAME="$(printf '%s' "${INPUT_JSON}" | jq -r '.tool_name // "Unknown"' 2>/dev/null || echo "Unknown")"
FILE_PATH="$(printf '%s' "${INPUT_JSON}" | jq -r '.tool_input.file_path // empty' 2>/dev/null || echo "")"
SESSION_ID="$(printf '%s' "${INPUT_JSON}" | jq -r '.session_id // "unknown"' 2>/dev/null || echo "unknown")"
CWD="$(printf '%s' "${INPUT_JSON}" | jq -r '.cwd // empty' 2>/dev/null || echo "")"

if [ -z "${FILE_PATH}" ]; then
    exit 0
fi

case "${TOOL_NAME}" in
    Edit|Write)
        ;;
    *)
        exit 0
        ;;
esac

LOWER_PATH="$(printf '%s' "${FILE_PATH}" | tr '[:upper:]' '[:lower:]')"

case "${LOWER_PATH}" in
    *.ts|*.tsx|*.js|*.jsx|*.vue|*.scss|*.css|*.html|*.json|*.yml|*.yaml|\
    web/frontend/*|docs/guides/hooks/*)
        ;;
    *)
        exit 0
        ;;
esac

if [[ "${FILE_PATH}" = /* ]]; then
    ABSOLUTE_PATH="${FILE_PATH}"
else
    BASE_DIR="${CWD:-${PROJECT_ROOT}}"
    ABSOLUTE_PATH="${BASE_DIR}/${FILE_PATH}"
fi

TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

jq -cn \
    --arg timestamp "${TIMESTAMP}" \
    --arg file_path "${FILE_PATH}" \
    --arg absolute_path "${ABSOLUTE_PATH}" \
    --arg tool "${TOOL_NAME}" \
    --arg session_id "${SESSION_ID}" \
    '{
        timestamp: $timestamp,
        file_path: $file_path,
        absolute_path: $absolute_path,
        tool: $tool,
        session_id: $session_id
    }' >> "${WEB_DEV_LOG}" || true

exit 0
