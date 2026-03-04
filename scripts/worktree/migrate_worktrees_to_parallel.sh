#!/usr/bin/env bash
set -euo pipefail

# Migrate worktrees from in-repo .worktrees/ to a parallel directory layout.
#
# Examples:
#   bash scripts/worktree/migrate_worktrees_to_parallel.sh --target-root /opt/claude
#
# Optional:
#   --source-root .worktrees
#   --names mystocks_spec1,mystocks_spec2,mystocks_spec3,mystocks_spec4

SOURCE_ROOT=".worktrees"
TARGET_ROOT="/opt/claude"
NAMES="mystocks_spec1,mystocks_spec2,mystocks_spec3,mystocks_spec4"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source-root)
      SOURCE_ROOT="$2"
      shift 2
      ;;
    --target-root)
      TARGET_ROOT="$2"
      shift 2
      ;;
    --names)
      NAMES="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1"
      exit 1
      ;;
  esac
done

IFS=',' read -r -a WORKTREE_NAMES <<< "$NAMES"

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

echo "[INFO] repo_root=$repo_root"
echo "[INFO] source_root=$SOURCE_ROOT"
echo "[INFO] target_root=$TARGET_ROOT"
echo "[INFO] names=${WORKTREE_NAMES[*]}"

for name in "${WORKTREE_NAMES[@]}"; do
  src="${SOURCE_ROOT}/${name}"
  dst="${TARGET_ROOT}/${name}"

  if [[ ! -d "$src" ]]; then
    echo "[WARN] skip $name: source not found: $src"
    continue
  fi

  if [[ -e "$dst" ]]; then
    echo "[ERROR] target exists: $dst"
    exit 1
  fi

  echo "[INFO] moving $src -> $dst"
  git worktree move "$src" "$dst"

  task_file=".multi-cli-tasks/${name}/TASK.md"
  if [[ -f "$task_file" ]]; then
    sed -i "s#\\*\\*Worktree\\*\\*: .*#**Worktree**: \`${dst}\`#g" "$task_file"
  fi
done

plan_file=".multi-cli-tasks/WORKTREE_EXECUTION_PLAN_2026-03-05.md"
if [[ -f "$plan_file" ]]; then
  for name in "${WORKTREE_NAMES[@]}"; do
    sed -i "s#\\.worktrees/${name}#${TARGET_ROOT}/${name}#g" "$plan_file"
  done
fi

echo "[INFO] migration completed"
echo "[INFO] verify:"
echo "  git worktree list"
echo "  git status --short .multi-cli-tasks"
