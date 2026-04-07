#!/usr/bin/env bash

set -euo pipefail

INPUT_JSON=$(cat 2>/dev/null || true)

if [[ -z "$INPUT_JSON" ]]; then
  echo '{}'
  exit 0
fi

if ! echo "$INPUT_JSON" | jq empty >/dev/null 2>&1; then
  echo '{}'
  exit 0
fi

STOP_HOOK_ACTIVE=$(echo "$INPUT_JSON" | jq -r '.stop_hook_active // false' 2>/dev/null || echo "false")
if [[ "$STOP_HOOK_ACTIVE" == "true" ]]; then
  echo '{}'
  exit 0
fi

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GATE_SCRIPT="$HOOK_DIR/../../scripts/compliance/deletion_evidence_gate.py"
PROJECT_ROOT="${DELETION_EVIDENCE_GATE_ROOT_DIR:-${CLAUDE_PROJECT_DIR:-$(cd "$HOOK_DIR/../.." && pwd)}}"

if [[ ! -f "$GATE_SCRIPT" ]]; then
  echo '{}'
  exit 0
fi

args=(--root-dir "$PROJECT_ROOT" --format json --scope worktree)
if [[ -n "${DELETION_EVIDENCE_GATE_TODAY:-}" ]]; then
  args+=(--today "$DELETION_EVIDENCE_GATE_TODAY")
fi

REPORT="$(python3 "$GATE_SCRIPT" "${args[@]}" 2>/dev/null || true)"
if [[ -z "$REPORT" ]]; then
  echo '{}'
  exit 0
fi

ERROR_COUNT="$(echo "$REPORT" | jq -r '.summary.errors // 0' 2>/dev/null || echo 0)"
if [[ "$ERROR_COUNT" == "0" ]]; then
  echo '{}'
  exit 0
fi

DETAILS="$(echo "$REPORT" | jq -r '
  [.errors[] | select(.kind != "internal") | "- \(.kind): \(.path) — \(.message)"]
  | join("\n")
' 2>/dev/null || true)"

if [[ -z "$DETAILS" ]]; then
  DETAILS="Deletion evidence gate detected governed deletions without valid authorization."
fi

jq -n \
  --arg reason "❌ Deletion evidence gate failed. Governed deletions require pre-existing exact-path evidence or a valid emergency waiver.\n\n$DETAILS" \
  '{
    decision: "block",
    reason: $reason
  }'
