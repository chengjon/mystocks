#!/bin/bash
# Backend server startup script for testing
# Sets correct PYTHONPATH to resolve src module import issues

set -e

PROJECT_ROOT="/opt/claude/mystocks_spec"
BACKEND_DIR="${PROJECT_ROOT}/web/backend"

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
    --port 8000 \
    --reload \
    --log-level info
