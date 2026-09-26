#!/usr/bin/env bash
set -euo pipefail

SRC_ROOT="${SRC_ROOT:-/opt/claude/mystocks_spec}"
DST_ROOT="${DST_ROOT:-/opt/mydoc/cliproxyapi/opencode}"
STAMP="$(date +%Y%m%d-%H%M%S)"

SRC_OPENCODE_JSON="$SRC_ROOT/opencode.json"
SRC_OMO_JSON="$SRC_ROOT/.config/oh-my-opencode.noco.json"
SRC_MODEL_DEFAULTS_DIR="$SRC_ROOT/.config/opencode/model_defaults"
SRC_SYNC_SCRIPT="$SRC_ROOT/scripts/opencode/sync_opencode_model_catalog.py"
SRC_GUIDE="$SRC_ROOT/docs/guides/ai-tools/OMO_SETUP_GUIDE.md"

DST_OPENCODE_JSON="$DST_ROOT/mystocks-opencode.json"
DST_OMO_JSON="$DST_ROOT/mystocks-oh-my-opencode.noco.json"
DST_SYNC_SCRIPT="$DST_ROOT/mystocks-sync_opencode_model_catalog.py"
DST_GUIDE="$DST_ROOT/OMO_SETUP_GUIDE.mystocks.md"
DST_README="$DST_ROOT/README_MYSTOCKS_OPENCODE.md"
DST_MIGRATION_SCRIPT="$DST_ROOT/migrate_mystocks_opencode_assets.sh"

OLD_PREFIX="$SRC_ROOT/.config/opencode/model_defaults"
NEW_PREFIX="$DST_ROOT"

usage() {
  cat <<USAGE
Usage:
  bash $(basename "$0") [--check-only]

Env overrides:
  SRC_ROOT=/opt/claude/mystocks_spec
  DST_ROOT=/opt/mydoc/cliproxyapi/opencode
USAGE
}

CHECK_ONLY=0
if [[ "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi
if [[ "${1:-}" == "--check-only" ]]; then
  CHECK_ONLY=1
fi

if [[ ! -d "$SRC_ROOT" ]]; then
  echo "ERROR: SRC_ROOT not found: $SRC_ROOT" >&2
  exit 1
fi
if [[ ! -d "$DST_ROOT" ]]; then
  echo "ERROR: DST_ROOT not found: $DST_ROOT" >&2
  echo "Hint: create it first, or export DST_ROOT to an existing writable directory." >&2
  exit 1
fi

if [[ ! -w "$DST_ROOT" ]]; then
  echo "ERROR: DST_ROOT is not writable: $DST_ROOT" >&2
  echo "Run with proper permission, e.g. sudo bash $0" >&2
  exit 1
fi

if [[ "$CHECK_ONLY" -eq 1 ]]; then
  echo "CHECK OK: source and destination are accessible."
  echo "SRC_ROOT=$SRC_ROOT"
  echo "DST_ROOT=$DST_ROOT"
  exit 0
fi

backup_if_exists() {
  local f="$1"
  if [[ -f "$f" ]]; then
    cp "$f" "$f.bak.$STAMP"
  fi
}

backup_if_exists "$DST_OPENCODE_JSON"
backup_if_exists "$DST_OMO_JSON"
backup_if_exists "$DST_SYNC_SCRIPT"
backup_if_exists "$DST_GUIDE"

cp "$SRC_OPENCODE_JSON" "$DST_OPENCODE_JSON"
cp "$SRC_OMO_JSON" "$DST_OMO_JSON"
cp "$SRC_SYNC_SCRIPT" "$DST_SYNC_SCRIPT"
cp "$SRC_GUIDE" "$DST_GUIDE"

# Copy model default files into target root (no subdirectory creation needed).
for f in "$SRC_MODEL_DEFAULTS_DIR"/*; do
  [[ -f "$f" ]] || continue
  cp "$f" "$DST_ROOT/$(basename "$f")"
done

# Rewrite model ref prefixes in generated configs and helper files.
for f in "$DST_OPENCODE_JSON" "$DST_OMO_JSON" "$DST_ROOT/model-stack.env" "$DST_ROOT/README.md"; do
  if [[ -f "$f" ]]; then
    sed -i "s|$OLD_PREFIX|$NEW_PREFIX|g" "$f"
  fi
done

# Rewrite absolute constants and file refs in sync script.
sed -i "s|Path(\"$SRC_ROOT/.config/opencode/model_defaults/model-catalog.json\")|Path(\"$DST_ROOT/model-catalog.json\")|g" "$DST_SYNC_SCRIPT"
sed -i "s|Path(\"$SRC_ROOT/opencode.json\")|Path(\"$DST_OPENCODE_JSON\")|g" "$DST_SYNC_SCRIPT"
sed -i "s|Path(\"$SRC_ROOT/.config/oh-my-opencode.noco.json\")|Path(\"$DST_OMO_JSON\")|g" "$DST_SYNC_SCRIPT"
sed -i "s|$OLD_PREFIX|$NEW_PREFIX|g" "$DST_SYNC_SCRIPT"

# Keep migration script in target for future one-command sync.
cp "$0" "$DST_MIGRATION_SCRIPT"
chmod +x "$DST_MIGRATION_SCRIPT" "$DST_SYNC_SCRIPT"

cat > "$DST_README" <<README
# MyStocks OpenCode/OMO Migration Bundle

Migrated from:
- $SRC_ROOT

## Main files
- $DST_OPENCODE_JSON
- $DST_OMO_JSON
- $DST_SYNC_SCRIPT
- $DST_GUIDE
- $DST_ROOT/model-catalog.json
- $DST_ROOT/model-stack.env
- $DST_ROOT/main.model
- $DST_ROOT/small.model
- $DST_ROOT/gmn.base_url
- $DST_ROOT/glm.base_url
- $DST_ROOT/glm.api_key
- $DST_ROOT/omo.*.model

## Update workflow
1. Edit only:
   $DST_ROOT/model-catalog.json
2. Generate configs:
   python3 $DST_SYNC_SCRIPT
3. Optional OpenCode binding:
   export OPENCODE_CONFIG=$DST_OPENCODE_JSON

## Re-run migration
bash $DST_MIGRATION_SCRIPT
README

# Sanity checks
jq empty "$DST_OPENCODE_JSON" "$DST_OMO_JSON" "$DST_ROOT/model-catalog.json" >/dev/null
python3 -m py_compile "$DST_SYNC_SCRIPT"

printf "Migration completed: %s\n" "$DST_ROOT"
printf "Generated: %s\n" "$DST_OPENCODE_JSON"
printf "Generated: %s\n" "$DST_OMO_JSON"
