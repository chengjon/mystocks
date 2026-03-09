#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/../.." && pwd)"

PROJECT_ROOT="${DEFAULT_PROJECT_ROOT}"
OUTPUT_FORMAT="text"

usage() {
    cat <<EOF
Usage: $(basename "$0") [--project-root PATH] [--format text|json]

Canonical repository file-size monitor.
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

python3 "${DEFAULT_PROJECT_ROOT}/scripts/compliance/file_size_guardrail.py" \
    --root-dir "${PROJECT_ROOT}" \
    --format "${OUTPUT_FORMAT}"
