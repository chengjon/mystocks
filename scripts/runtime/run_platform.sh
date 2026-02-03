#!/bin/bash
# MyStocks Platform Startup Script
# Integrates all components into a production-ready fullstack application

set -e  # Exit on any error

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_PORT=8000
FRONTEND_PORT=3000
DB_HOST=localhost
DB_PORT=6030  # TDengine default

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Process IDs
BACKEND_PID=""
FRONTEND_PID=""
DB_PID=""

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Health check functions
check_port_available() {
    local port=$1
    local service_name=$2

    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_error "Port $port is already in use by $service_name"
        return 1
    fi
    return 0
}

wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1

    log_info "Waiting for $service_name to be ready..."

    while [ $attempt -le $max_attempts ]; do
        if curl -s --max-time 5 "$url" >/dev/null 2>&1; then
            log_info "$service_name is ready!"
            return 0
        fi

        log_debug "Attempt $attempt/$max_attempts: $service_name not ready yet"
        sleep 2
        ((attempt++))
    done

    log_error "$service_name failed to start within $(($max_attempts * 2)) seconds"
    return 1
}

# Service management functions
start_database() {
    log_info "Checking database..."

    # Check if TDengine is running
    if pgrep -f "taosd" >/dev/null 2>&1; then
        log_info "TDengine is already running"
        return 0
    fi

    # Check if Docker is available and TDengine container exists
    if command -v docker >/dev/null 2>&1; then
        if docker ps -a --format 'table {{.Names}}' | grep -q "mystocks-tdengine"; then
            log_info "Starting TDengine container..."
            docker start mystocks-tdengine
            wait_for_service "http://localhost:$DB_PORT" "TDengine"
            return $?
        fi
    fi

    log_warn "TDengine not found. Please ensure TDengine is installed and running."
    log_warn "Installation guide: https://docs.tdengine.com/"
    log_warn "Or use Docker: docker run -d -p 6030:6030 -p 6041:6041 tdengine/tdengine"
    return 1
}

start_backend() {
    log_info "Starting FastAPI backend..."

    # Check port availability
    check_port_available $BACKEND_PORT "backend"
    if [ $? -ne 0 ]; then
        return 1
    fi

    # Navigate to backend directory
    cd "$PROJECT_ROOT/web/backend"

    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        log_error "Python virtual environment not found. Run 'python -m venv venv' first."
        return 1
    fi

    # Activate virtual environment
    source venv/bin/activate

    # Install/update dependencies if needed
    if [ ! -f ".deps_installed" ] || [ requirements.txt -nt .deps_installed ]; then
        log_info "Installing Python dependencies..."
        pip install -r requirements.txt
        touch .deps_installed
    fi

    # Set environment variables
    export PYTHONPATH="$PROJECT_ROOT/web/backend"
    export DATABASE_URL="taos://root:taosdata@localhost:$DB_PORT/mystocks"

    # Start backend in background
    log_info "Starting FastAPI server on port $BACKEND_PORT..."
    nohup python -m uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload > backend.log 2>&1 &
    BACKEND_PID=$!

    # Wait for backend to be ready
    wait_for_service "http://localhost:$BACKEND_PORT/health" "FastAPI backend"

    cd "$PROJECT_ROOT"
    return $?
}

start_frontend() {
    log_info "Starting Vue frontend..."

    # Check port availability
    check_port_available $FRONTEND_PORT "frontend"
    if [ $? -ne 0 ]; then
        return 1
    fi

    # Navigate to frontend directory
    cd "$PROJECT_ROOT/web/frontend"

    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        log_info "Installing Node.js dependencies..."
        npm install
    fi

    # Check if .env.development exists
    if [ ! -f ".env.development" ]; then
        log_info "Creating development environment file..."
        cat > .env.development << EOF
VITE_API_BASE_URL=http://localhost:$BACKEND_PORT
VITE_API_TIMEOUT=10000
VITE_API_RETRY_ATTEMPTS=3
VITE_APP_ENV=development
VITE_APP_TITLE=MyStocks Development
VITE_DEBUG=true
VITE_LOG_LEVEL=debug
EOF
    fi

    # Start frontend in background
    log_info "Starting Vite dev server on port $FRONTEND_PORT..."
    nohup npm run dev -- --port $FRONTEND_PORT > frontend.log 2>&1 &
    FRONTEND_PID=$!

    # Wait for frontend to be ready
    wait_for_service "http://localhost:$FRONTEND_PORT" "Vue frontend"

    cd "$PROJECT_ROOT"
    return $?
}

# Cleanup function
cleanup() {
    log_info "Shutting down services..."

    # Stop frontend
    if [ -n "$FRONTEND_PID" ]; then
        log_debug "Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null || true
    fi

    # Stop backend
    if [ -n "$BACKEND_PID" ]; then
        log_debug "Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null || true
    fi

    # Note: Database is not stopped automatically to preserve data

    log_info "Services stopped successfully"
}

# Error handling
error_exit() {
    local message=$1
    log_error "$message"
    cleanup
    exit 1
}

# Prerequisites check
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check if required commands exist
    local required_commands=("curl" "python3" "node" "npm")
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            error_exit "$cmd is required but not installed. Please install $cmd first."
        fi
    done

    # Check if ports are available
    check_port_available $BACKEND_PORT "backend service"
    check_port_available $FRONTEND_PORT "frontend service"

    log_info "Prerequisites check passed"
}

# Display help
show_help() {
    cat << EOF
MyStocks Platform Startup Script

This script starts all components of the MyStocks quantitative trading platform:
- TDengine Database (port $DB_PORT)
- FastAPI Backend (port $BACKEND_PORT)
- Vue Frontend (port $FRONTEND_PORT)

USAGE:
    $0 [OPTIONS]

OPTIONS:
    -h, --help          Show this help message
    --no-db            Skip database startup (assume it's already running)
    --prod             Use production environment settings
    --backend-only     Start only backend service
    --frontend-only    Start only frontend service

ENVIRONMENT VARIABLES:
    BACKEND_PORT       Backend service port (default: $BACKEND_PORT)
    FRONTEND_PORT      Frontend service port (default: $FRONTEND_PORT)
    DB_PORT           Database port (default: $DB_PORT)

EXAMPLES:
    $0                    # Start all services
    $0 --backend-only     # Start only backend
    $0 --no-db           # Start without database
    BACKEND_PORT=8001 $0  # Use custom backend port

SERVICES STARTUP ORDER:
    1. Database (TDengine)
    2. Backend (FastAPI)
    3. Frontend (Vue)

HEALTH CHECKS:
    - Database: http://localhost:$DB_PORT
    - Backend: http://localhost:$BACKEND_PORT/health
    - Frontend: http://localhost:$FRONTEND_PORT

LOGS:
    - Backend: web/backend/backend.log
    - Frontend: web/frontend/frontend.log

Press Ctrl+C to stop all services gracefully.

EOF
}

# Parse command line arguments
SKIP_DB=false
BACKEND_ONLY=false
FRONTEND_ONLY=false
PROD_ENV=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        --no-db)
            SKIP_DB=true
            shift
            ;;
        --backend-only)
            BACKEND_ONLY=true
            shift
            ;;
        --frontend-only)
            FRONTEND_ONLY=true
            shift
            ;;
        --prod)
            PROD_ENV=true
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Override ports from environment if set
BACKEND_PORT=${BACKEND_PORT:-8000}
FRONTEND_PORT=${FRONTEND_PORT:-3000}
DB_PORT=${DB_PORT:-6030}

# Main execution
main() {
    log_info "🚀 Starting MyStocks Quantitative Trading Platform..."
    log_info "=================================================="

    # Show help if no arguments
    if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
        show_help
        exit 0
    fi

    # Run prerequisites check
    check_prerequisites

    # Determine what to start
    if [ "$BACKEND_ONLY" = true ]; then
        log_info "Starting backend only..."
        start_backend || error_exit "Failed to start backend"
    elif [ "$FRONTEND_ONLY" = true ]; then
        log_info "Starting frontend only..."
        start_frontend || error_exit "Failed to start frontend"
    else
        # Start services in order
        if [ "$SKIP_DB" = false ]; then
            start_database || error_exit "Failed to start database"
        else
            log_info "Skipping database startup (--no-db flag set)"
        fi
        start_backend || error_exit "Failed to start backend"
        start_frontend || error_exit "Failed to start frontend"
    fi

    # Success message
    echo ""
    log_info "✅ MyStocks Platform started successfully!"
    log_info "=================================================="

    if [ "$BACKEND_ONLY" = false ] && [ "$FRONTEND_ONLY" = false ]; then
        log_info "🌐 Frontend: http://localhost:$FRONTEND_PORT"
        log_info "🔧 Backend API: http://localhost:$BACKEND_PORT"
        log_info "📖 API Docs: http://localhost:$BACKEND_PORT/docs"
    elif [ "$BACKEND_ONLY" = true ]; then
        log_info "🔧 Backend API: http://localhost:$BACKEND_PORT"
        log_info "📖 API Docs: http://localhost:$BACKEND_PORT/docs"
    elif [ "$FRONTEND_ONLY" = true ]; then
        log_info "🌐 Frontend: http://localhost:$FRONTEND_PORT"
    fi

    log_info "🛑 Press Ctrl+C to stop all services"
    echo ""

    # Keep script running
    wait
}

# Signal handling
trap cleanup SIGINT SIGTERM

# Run main function with all arguments
main "$@"