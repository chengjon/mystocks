#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_PROJECT_ROOT="$(cd -- "${SCRIPT_DIR}/../.." && pwd)"

PROJECT_ROOT="${DEFAULT_PROJECT_ROOT}"
RETENTION_DAYS=7
DRY_RUN=0

usage() {
    cat <<EOF
Usage: $(basename "$0") [--project-root PATH] [--retention-days DAYS] [--dry-run]

Rotate expired application logs from:
  var/log/app/
to:
  archive/logs/app/
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --project-root)
            PROJECT_ROOT="$2"
            shift 2
            ;;
        --retention-days)
            RETENTION_DAYS="$2"
            shift 2
            ;;
        --dry-run|-n)
            DRY_RUN=1
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

LOG_DIR="${PROJECT_ROOT}/var/log/app"
ARCHIVE_DIR="${PROJECT_ROOT}/archive/logs/app"

mode_label="EXECUTE"
if [[ "${DRY_RUN}" -eq 1 ]]; then
    mode_label="DRY-RUN"
fi

echo "log rotation mode: ${mode_label}"
echo "project_root: ${PROJECT_ROOT}"
echo "log_dir: ${LOG_DIR}"
echo "archive_dir: ${ARCHIVE_DIR}"
echo "retention_days: ${RETENTION_DAYS}"

if [[ ! -d "${LOG_DIR}" ]]; then
    echo "status: log directory does not exist; nothing to rotate"
    echo "rotated: 0"
    echo "active_logs: 0"
    echo "archived_logs: 0"
    exit 0
fi

if [[ "${DRY_RUN}" -eq 0 ]]; then
    mkdir -p "${ARCHIVE_DIR}"
fi

rotated_count=0

while IFS= read -r -d '' logfile; do
    target_path="${ARCHIVE_DIR}/$(basename "${logfile}")"

    if [[ "${DRY_RUN}" -eq 1 ]]; then
        echo "[DRY-RUN] rotate ${logfile} -> ${target_path}"
    else
        mv "${logfile}" "${target_path}"
        echo "rotated ${logfile} -> ${target_path}"
    fi

    rotated_count=$((rotated_count + 1))
done < <(find "${LOG_DIR}" -maxdepth 1 -name "*.log" -type f -mtime +"${RETENTION_DAYS}" -print0)

active_logs=$(find "${LOG_DIR}" -maxdepth 1 -name "*.log" -type f | wc -l | tr -d ' ')
archived_logs=0
if [[ -d "${ARCHIVE_DIR}" ]]; then
    archived_logs=$(find "${ARCHIVE_DIR}" -maxdepth 1 -name "*.log" -type f | wc -l | tr -d ' ')
fi

echo "rotated: ${rotated_count}"
echo "active_logs: ${active_logs}"
echo "archived_logs: ${archived_logs}"
