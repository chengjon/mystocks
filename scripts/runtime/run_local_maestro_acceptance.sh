#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

SNAPSHOT_DIR="/tmp/mongo-collab-snapshots-codex"

cd "${PROJECT_ROOT}"

echo "[1/4] coordctl work list"
python scripts/runtime/coordctl.py work list --output json >/tmp/maestro_work_list.json
echo "  wrote /tmp/maestro_work_list.json"

echo "[2/4] mongo smoke"
python scripts/runtime/smoke_mongo_multicli.py >/tmp/maestro_mongo_smoke.json
echo "  wrote /tmp/maestro_mongo_smoke.json"

echo "[3/4] graphiti preflight smoke"
python scripts/runtime/smoke_graphiti_preflight.py --actor-cli cli-preflight >/tmp/maestro_graphiti_preflight.json
echo "  wrote /tmp/maestro_graphiti_preflight.json"

echo "[4/4] export collab snapshots"
rm -rf /tmp/mongo-collab-snapshots-codex
python scripts/runtime/export_collab_snapshots.py --output-dir /tmp/mongo-collab-snapshots-codex >/tmp/maestro_snapshot_export.txt
echo "  wrote ${SNAPSHOT_DIR}"

echo "Local Maestro acceptance completed."
