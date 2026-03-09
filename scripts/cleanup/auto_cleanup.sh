#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/../.." && pwd)"

PROJECT_ROOT="${DEFAULT_PROJECT_ROOT}"
OUTPUT_FORMAT="text"
EXECUTE=0
BACKUP_STAMP=""

usage() {
    cat <<EOF
Usage: $(basename "$0") [--project-root PATH] [--format text|json] [--backup-stamp STAMP] [--execute]

Canonical repository auto cleanup entrypoint.
Default mode is dry-run.
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --project-root)
            PROJECT_ROOT="$2"
            shift 2
            ;;
        --format)
            OUTPUT_FORMAT="$2"
            shift 2
            ;;
        --backup-stamp)
            BACKUP_STAMP="$2"
            shift 2
            ;;
        --execute)
            EXECUTE=1
            shift
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            echo "Unknown argument: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

command=(
    python3
    "${DEFAULT_PROJECT_ROOT}/scripts/dev/cleanup_temp_files.py"
    --root-dir "${PROJECT_ROOT}"
    --format "${OUTPUT_FORMAT}"
)

if [[ -n "${BACKUP_STAMP}" ]]; then
    command+=(--backup-stamp "${BACKUP_STAMP}")
fi

if [[ "${EXECUTE}" -eq 1 ]]; then
    command+=(--execute)
fi

"${command[@]}"
