#!/usr/bin/env bash
set -euo pipefail

# Generate large-file splitting inventory and backlog from repository root.
# Usage: scripts/dev/tools/generate_large_file_splitting_inventory.sh

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$ROOT_DIR"

OUTDIR="reports/plans/inventory"
mkdir -p "$OUTDIR"

EXCL=(
  -g '!archived/**'
  -g '!docs/**'
  -g '!node_modules/**'
  -g '!scripts/dev/development/**'
  -g '!scripts/tests/testing/**'
  -g '!web/frontend/src/views/converted.archive/**'
  -g '!web/frontend/src/layouts/archive/**'
  -g '!web/frontend/archives/**'
)

# Python source > 800
: > "$OUTDIR/python_source_gt800.tsv"
rg --files -g '*.py' "${EXCL[@]}" | while IFS= read -r f; do
  l=$(wc -l < "$f")
  b=$(basename "$f")
  if [[ "$f" != *"/tests/"* && "$f" != *"/test_"* && "$b" != test_*.py && "$b" != *_test.py ]]; then
    if (( l > 800 )); then printf '%s\t%s\n' "$l" "$f" >> "$OUTDIR/python_source_gt800.tsv"; fi
  fi
done
sort -nr "$OUTDIR/python_source_gt800.tsv" -o "$OUTDIR/python_source_gt800.tsv"

# Python test > 1000
: > "$OUTDIR/python_test_gt1000.tsv"
rg --files -g '*.py' "${EXCL[@]}" | while IFS= read -r f; do
  l=$(wc -l < "$f")
  b=$(basename "$f")
  if [[ "$f" == *"/tests/"* || "$f" == *"/test_"* || "$b" == test_*.py || "$b" == *_test.py ]]; then
    if (( l > 1000 )); then printf '%s\t%s\n' "$l" "$f" >> "$OUTDIR/python_test_gt1000.tsv"; fi
  fi
done
sort -nr "$OUTDIR/python_test_gt1000.tsv" -o "$OUTDIR/python_test_gt1000.tsv"

# Vue > 500
: > "$OUTDIR/vue_gt500.tsv"
rg --files -g '*.vue' "${EXCL[@]}" | while IFS= read -r f; do
  l=$(wc -l < "$f")
  if (( l > 500 )); then printf '%s\t%s\n' "$l" "$f" >> "$OUTDIR/vue_gt500.tsv"; fi
done
sort -nr "$OUTDIR/vue_gt500.tsv" -o "$OUTDIR/vue_gt500.tsv"

# TypeScript > 500 (excluding approved exceptions)
: > "$OUTDIR/ts_gt500.tsv"
rg --files -g '*.ts' "${EXCL[@]}" | while IFS= read -r f; do
  if [[ "$f" == 'web/frontend/src/api/types/generated-types.ts' ]]; then
    continue
  fi
  # Exclude declaration files by policy (*.d.ts are type declaration artifacts)
  if [[ "$f" == *.d.ts ]]; then
    continue
  fi
  l=$(wc -l < "$f")
  if (( l > 500 )); then printf '%s\t%s\n' "$l" "$f" >> "$OUTDIR/ts_gt500.tsv"; fi
done
sort -nr "$OUTDIR/ts_gt500.tsv" -o "$OUTDIR/ts_gt500.tsv"

# Backlog
BACKLOG="reports/plans/large_file_splitting_backlog.tsv"
{
  echo -e "wave\tcategory\tpriority\tthreshold\tlines\tpath\tstatus"
  awk -F'\t' '{l=$1+0; p=(l>1600?"P0":(l>1200?"P1":"P2")); printf("Wave1\tpython_source\t%s\t800\t%d\t%s\tTODO\n",p,l,$2)}' "$OUTDIR/python_source_gt800.tsv"
  awk -F'\t' '{l=$1+0; p=(l>1000?"P0":(l>750?"P1":"P2")); printf("Wave2\tvue\t%s\t500\t%d\t%s\tTODO\n",p,l,$2)}' "$OUTDIR/vue_gt500.tsv"
  awk -F'\t' '{l=$1+0; p=(l>1000?"P0":(l>750?"P1":"P2")); printf("Wave3\tts\t%s\t500\t%d\t%s\tTODO\n",p,l,$2)}' "$OUTDIR/ts_gt500.tsv"
  awk -F'\t' '{l=$1+0; p=(l>2000?"P0":(l>1500?"P1":"P2")); printf("Wave4\tpython_test\t%s\t1000\t%d\t%s\tTODO\n",p,l,$2)}' "$OUTDIR/python_test_gt1000.tsv"
} > "$BACKLOG"

PS=$(wc -l < "$OUTDIR/python_source_gt800.tsv" | tr -d ' ')
PT=$(wc -l < "$OUTDIR/python_test_gt1000.tsv" | tr -d ' ')
VU=$(wc -l < "$OUTDIR/vue_gt500.tsv" | tr -d ' ')
TS=$(wc -l < "$OUTDIR/ts_gt500.tsv" | tr -d ' ')
TOT=$((PS+PT+VU+TS))

cat <<SUMMARY
Generated inventory and backlog:
- $OUTDIR/python_source_gt800.tsv: $PS
- $OUTDIR/python_test_gt1000.tsv: $PT
- $OUTDIR/vue_gt500.tsv: $VU
- $OUTDIR/ts_gt500.tsv: $TS
- reports/plans/large_file_splitting_backlog.tsv: $TOT
SUMMARY
