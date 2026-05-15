#!/usr/bin/env bash
set -uo pipefail

INPUT_JSON=$(cat 2>/dev/null || true)

if [ -z "$INPUT_JSON" ]; then
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

printf '%s' "$INPUT_JSON" \
  | python3 "$GATE_SCRIPT" record-evidence --project-root "$PROJECT_ROOT" >/dev/null 2>&1 || true

echo '{}'
exit 0
