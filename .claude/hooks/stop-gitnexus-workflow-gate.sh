#!/usr/bin/env bash
set -uo pipefail

INPUT_JSON=$(cat 2>/dev/null || true)

if [ -z "$INPUT_JSON" ]; then
  echo '{}'
  exit 0
fi

if ! printf '%s' "$INPUT_JSON" | jq empty >/dev/null 2>&1; then
  echo '{}'
  exit 0
fi

STOP_HOOK_ACTIVE=$(printf '%s' "$INPUT_JSON" | jq -r '.stop_hook_active // false' 2>/dev/null || echo "false")
if [ "$STOP_HOOK_ACTIVE" = "true" ]; then
  echo '{}'
  exit 0
fi

PROJECT_ROOT=$(printf '%s' "$INPUT_JSON" | jq -r '.cwd // empty' 2>/dev/null || true)
if [ -z "$PROJECT_ROOT" ]; then
  PROJECT_ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
fi

GATE_SCRIPT="$PROJECT_ROOT/scripts/hooks/gitnexus_workflow_gate.py"
if [ ! -f "$GATE_SCRIPT" ]; then
  echo '{}'
  exit 0
fi

if ! printf '%s' "$INPUT_JSON" | python3 "$GATE_SCRIPT" stop-gate --project-root "$PROJECT_ROOT"; then
  exit 2
fi

echo '{}'
exit 0
