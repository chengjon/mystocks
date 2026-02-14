#!/bin/bash
# Start Backend Server with correct PYTHONPATH and Module Context

# Get project root (2 levels up from web/backend)
PROJECT_ROOT=$(cd "$(dirname "$0")/../.." && pwd)

# Add project root to PYTHONPATH so 'src' module can be found
export PYTHONPATH=$PROJECT_ROOT:$PYTHONPATH

echo "🚀 Starting Backend Server from Project Root..."
echo "ROOT: $PROJECT_ROOT"
echo "PYTHONPATH: $PYTHONPATH"

# Run Uvicorn as a module from the project root
# This fixes the relative import issue (Issue 1) AND the missing src module (Issue 2)
cd "$PROJECT_ROOT"
exec python3 -m uvicorn web.backend.app.main:app --host 0.0.0.0 --port 8000
