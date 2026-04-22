#!/usr/bin/env bash
set -euo pipefail

INPUT_JSON=$(cat)

if [ -z "$INPUT_JSON" ]; then
  echo '{}'
  exit 0
fi

if ! echo "$INPUT_JSON" | jq empty >/dev/null 2>&1; then
  echo '{}'
  exit 0
fi

STOP_HOOK_ACTIVE=$(echo "$INPUT_JSON" | jq -r '.stop_hook_active // false' 2>/dev/null || echo "false")
if [ "$STOP_HOOK_ACTIVE" = "true" ]; then
  echo '{}'
  exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY_SCRIPT="$SCRIPT_DIR/record_graphiti_closeout.py"

if [ ! -f "$PY_SCRIPT" ]; then
  echo '{}'
  exit 0
fi

TMP_INPUT=$(mktemp)
echo "$INPUT_JSON" > "$TMP_INPUT"

PROJECT_ROOT=$(echo "$INPUT_JSON" | jq -r '.cwd // empty' 2>/dev/null || true)
if [ -z "$PROJECT_ROOT" ]; then
  PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
fi

if [ "${GRAPHITI_CLOSEOUT_SYNC:-0}" = "1" ]; then
  python3 "$PY_SCRIPT" \
    --event-json "$TMP_INPUT" \
    --project-root "$PROJECT_ROOT" \
    >/dev/null 2>&1 || true
else
  nohup python3 "$PY_SCRIPT" \
    --event-json "$TMP_INPUT" \
    --project-root "$PROJECT_ROOT" \
    >/dev/null 2>&1 &
fi

echo '{}'
exit 0
