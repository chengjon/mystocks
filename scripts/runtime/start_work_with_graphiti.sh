#!/usr/bin/env bash

set -euo pipefail

TASK_PATH="${GRAPHITI_START_WORK_TASK_PATH:-${GRAPHITI_PREFLIGHT_TASK_PATH:-TASK.md}}"
ACTOR_CLI="${GRAPHITI_START_WORK_ACTOR_CLI:-${GRAPHITI_PREFLIGHT_ACTOR_CLI:-}}"
MAX_WAIT_SECONDS="${GRAPHITI_START_WORK_MAX_WAIT_SECONDS:-${GRAPHITI_PREFLIGHT_MAX_WAIT_SECONDS:-60}}"
WRITE_MEMORY="${GRAPHITI_START_WORK_WRITE_MEMORY:-${GRAPHITI_PREFLIGHT_WRITE_MEMORY:-0}}"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --task-path)
      TASK_PATH="$2"
      shift 2
      ;;
    --actor-cli)
      ACTOR_CLI="$2"
      shift 2
      ;;
    --max-wait-seconds)
      MAX_WAIT_SECONDS="$2"
      shift 2
      ;;
    --write-memory)
      WRITE_MEMORY=1
      shift
      ;;
    --no-write-memory)
      WRITE_MEMORY=0
      shift
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if [ ! -f "$TASK_PATH" ]; then
  echo "TASK file not found: $TASK_PATH" >&2
  exit 1
fi

WORK_ITEM_ID=$(python - "$TASK_PATH" <<'PY'
import re
import sys
from pathlib import Path

task_path = Path(sys.argv[1])
text = task_path.read_text(encoding="utf-8")
patterns = [
    r"Issue Identifier:\s*`([^`]+)`",
    r"Issue Identifier:\s*([A-Za-z0-9._-]+)",
]
for pattern in patterns:
    match = re.search(pattern, text)
    if match:
        print(match.group(1).strip())
        raise SystemExit(0)
raise SystemExit(1)
PY
)

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"

if [ -z "$ACTOR_CLI" ]; then
  BRANCH_NAME=$(git branch --show-current 2>/dev/null || true)
  if [ -n "$BRANCH_NAME" ] && [ "$BRANCH_NAME" != "main" ]; then
    ACTOR_CLI="$BRANCH_NAME"
  else
    ACTOR_CLI="main"
  fi
fi

COMMAND_PREFIX="${GRAPHITI_START_WORK_COMMAND:-${GRAPHITI_PREFLIGHT_COMMAND:-python \"$PROJECT_DIR/scripts/runtime/coordctl.py\" graphiti preflight}}"
eval "set -- $COMMAND_PREFIX"
COMMAND=("$@" "$WORK_ITEM_ID" --actor-cli "$ACTOR_CLI" --task-path "$TASK_PATH" --max-wait-seconds "$MAX_WAIT_SECONDS" --output json)

if [ "$WRITE_MEMORY" = "1" ]; then
  COMMAND+=(--write-memory)
fi

"${COMMAND[@]}"
