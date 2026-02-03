#!/bin/bash
# =============================================================================
# MyStocks Test Environment - tmux + lnav Setup Script
# 
# This script creates a tmux session with:
# - Left pane: Services (frontend + backend)
# - Right pane: lnav log monitoring
# 
# Usage:
#   ./setup-test-session.sh           # Create new session
#   ./setup-test-session.sh attach    # Attach to existing session
#   ./setup-test-session.sh kill      # Kill the session
# =============================================================================

set -e

SESSION_NAME="mystocks-test"
PROJECT_DIR="/opt/claude/mystocks_spec"
FRONTEND_DIR="${PROJECT_DIR}/web/frontend"
BACKEND_DIR="${PROJECT_DIR}/web/backend"
TEST_LOG_DIR="${PROJECT_DIR}/logs/tests"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${BLUE}[TMUX]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }

# Check tmux
if ! command -v tmux &> /dev/null; then
    echo "tmux not found. Installing..."
    apt-get update && apt-get install -y tmux
fi

# Check lnav
if ! command -v lnav &> /dev/null; then
    echo "lnav not found. Installing..."
    apt-get update && apt-get install -y lnav
fi

# Create logs directory
mkdir -p "${TEST_LOG_DIR}"

# Kill existing session
kill_session() {
    log "Killing existing session: ${SESSION_NAME}"
    tmux kill-session -t "${SESSION_NAME}" 2>/dev/null || true
    success "Session killed"
}

# Create new session
create_session() {
    log "Creating tmux session: ${SESSION_NAME}"
    
    # Kill existing if any
    tmux kill-session -t "${SESSION_NAME}" 2>/dev/null || true
    
    # Create new session with initial command
    # Using -d to detach immediately, then we'll send commands
    tmux new-session -d -s "${SESSION_NAME}" -x 120 -y 40
    
    # Split into left (services) and right (logs) panes
    tmux split-window -h -t "${SESSION_NAME}:0.0"
    
    # Configure left pane (services)
    tmux send-keys -t "${SESSION_NAME}:0.0" "cd ${BACKEND_DIR}" Enter
    tmux send-keys -t "${SESSION_NAME}:0.0" "echo 'Starting backend...'" Enter
    tmux send-keys -t "${SESSION_NAME}:0.0" "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" Enter
    
    # Wait a bit for backend to start
    sleep 3
    
    # Configure right pane (logs with lnav)
    tmux send-keys -t "${SESSION_NAME}:0.1" "cd ${TEST_LOG_DIR}" Enter
    tmux send-keys -t "${SESSION_NAME}:0.1" "echo 'Waiting for logs...'" Enter
    tmux send-keys -t "${SESSION_NAME}:0.1" "lnav" Enter
    
    success "Session created"
}

# Attach to session
attach_session() {
    if tmux has-session -t "${SESSION_NAME}" 2>/dev/null; then
        log "Attaching to session: ${SESSION_NAME}"
        echo ""
        echo "=============================================="
        echo "  tmux session: ${SESSION_NAME}"
        echo "=============================================="
        echo ""
        echo "Navigation:"
        echo "  Ctrl+b, then arrow keys - Navigate panes"
        echo "  Ctrl+b, d - Detach session"
        echo "  Ctrl+b, x - Kill current pane"
        echo ""
        echo "Panes:"
        echo "  Left:  Services (backend running)"
        echo "  Right: lnav log viewer"
        echo ""
        tmux attach-session -t "${SESSION_NAME}"
    else
        echo "Session ${SESSION_NAME} not found. Run without arguments to create it."
    fi
}

# Main
case "${1:-}" in
    attach|a)
        attach_session
        ;;
    kill|k)
        kill_session
        ;;
    *)
        create_session
        echo ""
        echo "=============================================="
        echo "  tmux session '${SESSION_NAME}' created!"
        echo "=============================================="
        echo ""
        echo "To view logs in real-time:"
        echo "  1. Attach: ./setup-test-session.sh attach"
        echo "  2. In lnav (right pane), press :filter-in to filter"
        echo ""
        echo "Quick lnav commands:"
        echo "  /ERROR     - Search for errors"
        echo "  :filter-in ADAPTER_CALL - Filter adapter logs"
        echo "  q          - Quit lnav"
        echo ""
        echo "To start frontend (in left pane):"
        echo "  cd ${FRONTEND_DIR}"
        echo "  npm run dev -- --port 3002"
        echo ""
        echo "Attach now? [y/N]"
        read -r answer
        if [[ "$answer" =~ ^[Yy]$ ]]; then
            attach_session
        fi
        ;;
esac
