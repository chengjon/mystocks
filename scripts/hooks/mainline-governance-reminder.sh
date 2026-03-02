#!/usr/bin/env bash
set -uo pipefail

# Mainline governance reminder hook (non-blocking)
# Purpose: remind developers to keep PR/task-card governance chain complete.

ROOT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT_DIR" 2>/dev/null || exit 0

# Staged files only (pre-commit context)
STAGED_FILES="$(git diff --cached --name-only || true)"
if [ -z "$STAGED_FILES" ]; then
  exit 0
fi

# Files considered governance/meta (do not count as effective changes)
is_governance_meta() {
  local path="$1"
  [[ "$path" =~ ^governance/mainline/task-cards/.*\.ya?ml$ ]] \
    || [[ "$path" == "governance/mainline/reports/mainline-governance-report.json" ]] \
    || [[ "$path" == "governance/mainline/templates/ai-task-card.yaml" ]] \
    || [[ "$path" == "governance/mainline/schemas/ai-task-card.schema.json" ]] \
    || [[ "$path" == ".github/workflows/mainline-governance.yml" ]] \
    || [[ "$path" == ".github/pull_request_template.md" ]] \
    || [[ "$path" == "governance/mainline/spec/ai-development-mainline-governance-spec.md" ]] \
    || [[ "$path" == "governance/mainline/README.md" ]]
}

HAS_EFFECTIVE_CHANGE=false
HAS_TASK_CARD=false
TASK_CARDS=()

while IFS= read -r file; do
  [ -z "$file" ] && continue

  if [[ "$file" =~ ^governance/mainline/task-cards/.*\.ya?ml$ ]]; then
    HAS_TASK_CARD=true
    TASK_CARDS+=("$file")
    continue
  fi

  if ! is_governance_meta "$file"; then
    HAS_EFFECTIVE_CHANGE=true
  fi
done <<< "$STAGED_FILES"

warn() {
  printf "\n⚠️  [Mainline Governance Reminder] %s\n" "$1"
}

if [ "$HAS_EFFECTIVE_CHANGE" = true ] && [ "$HAS_TASK_CARD" = false ]; then
  warn "检测到有效代码改动，但暂未发现暂存区中的任务卡（governance/mainline/task-cards/pr-<PR号>.yaml）。"
  printf "   建议：补充/更新任务卡后再提交，避免 PR 阶段门禁失败。\n"
fi

for card in "${TASK_CARDS[@]}"; do
  [ -f "$card" ] || continue

  card_text="$(cat "$card")"

  for token in "mainline:" "task_type:" "change_id:" "approval_status:" "allowed_paths:" "six_line_summary:"; do
    if ! grep -q "$token" <<< "$card_text"; then
      warn "任务卡 $card 缺少关键字段片段：$token"
    fi
  done

  if grep -qE '^\s*task_type:\s*"?feature"?' "$card"; then
    if ! grep -qE '^\s*approval_status:\s*"?approved"?' "$card"; then
      warn "任务卡 $card 为 feature，但 approval_status 不是 approved（PR 门禁会失败）。"
    fi
  fi

done

# Non-blocking reminder only
exit 0
