#!/usr/bin/env bash
set -euo pipefail

SRC_ROOT="/opt/claude/mystocks_spec/docs/guides"
DST_ROOT="/opt/mydoc/cliproxyapi/opencode"
STAMP="$(date +%Y%m%d-%H%M%S)"

SRC_PROD_GUIDE="$SRC_ROOT/OpenCode生产级配置与固化指南.md"
SRC_OMO_GUIDE="$SRC_ROOT/OMO_SETUP_GUIDE.md"

DST_PROD_GUIDE="$DST_ROOT/OpenCode生产级配置与固化指南.md"
DST_OMO_GUIDE="$DST_ROOT/OMO_SETUP_GUIDE.mystocks.md"

usage() {
  cat <<USAGE
Usage:
  bash $(basename "$0") [--check-only]

What it updates:
  $DST_PROD_GUIDE
  $DST_OMO_GUIDE

If permission denied, run with sudo:
  sudo bash $0
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

for f in "$SRC_PROD_GUIDE" "$SRC_OMO_GUIDE" "$DST_PROD_GUIDE" "$DST_OMO_GUIDE"; do
  if [[ ! -e "$f" ]]; then
    echo "ERROR: missing file: $f" >&2
    exit 1
  fi
done

if [[ ! -w "$DST_ROOT" ]]; then
  echo "ERROR: destination not writable: $DST_ROOT" >&2
  echo "Try: sudo bash $0" >&2
  exit 1
fi

if [[ "$CHECK_ONLY" -eq 1 ]]; then
  echo "CHECK OK"
  echo "source: $SRC_PROD_GUIDE"
  echo "source: $SRC_OMO_GUIDE"
  echo "target: $DST_PROD_GUIDE"
  echo "target: $DST_OMO_GUIDE"
  exit 0
fi

cp "$DST_PROD_GUIDE" "$DST_PROD_GUIDE.bak.$STAMP"
cp "$DST_OMO_GUIDE" "$DST_OMO_GUIDE.bak.$STAMP"

cp "$SRC_PROD_GUIDE" "$DST_PROD_GUIDE"
cp "$SRC_OMO_GUIDE" "$DST_OMO_GUIDE"

echo "Updated: $DST_PROD_GUIDE"
echo "Updated: $DST_OMO_GUIDE"
echo "Backup suffix: .bak.$STAMP"
