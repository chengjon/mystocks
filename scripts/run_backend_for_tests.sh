#!/bin/bash
# Backend server startup script for testing
# Sets correct PYTHONPATH to resolve src module import issues

set -e

PROJECT_ROOT="/opt/claude/mystocks_spec"
BACKEND_DIR="${PROJECT_ROOT}/web/backend"

if [ -f "${PROJECT_ROOT}/.env" ]; then
    set -a
    # shellcheck disable=SC1090
    source "${PROJECT_ROOT}/.env"
    set +a
fi

: "${BACKEND_PORT:?Missing BACKEND_PORT in .env}"

# Set PYTHONPATH - critical for src module imports
export PYTHONPATH="${PROJECT_ROOT}:${BACKEND_DIR}:${PYTHONPATH}"

# Set environment variables for testing
export DEVELOPMENT_MODE="false"
export TESTING="true"

echo "========================================"
echo "Starting MyStocks Backend Server (Test Mode)"
echo "========================================"
echo "PYTHONPATH: ${PYTHONPATH}"
echo "Project Root: ${PROJECT_ROOT}"
echo "Backend Dir: ${BACKEND_DIR}"
echo "========================================"

cd "${BACKEND_DIR}"
python -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "${BACKEND_PORT}" \
    --reload \
    --log-level info
