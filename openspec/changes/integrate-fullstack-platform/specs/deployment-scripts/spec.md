# Specification: Deployment Scripts

## Overview
The deployment scripts provide automated, reliable startup and management of the complete MyStocks platform, ensuring all services (database, backend, frontend) start in the correct order with proper error handling and graceful shutdown.

## Requirements

### ADDED Requirements

#### Single Command Startup
**Scenario**: Developer wants to run the complete platform locally
- **GIVEN** all components are properly configured
- **WHEN** developer runs `./run_platform.sh`
- **THEN** all services start automatically
- **AND** startup progress is clearly displayed
- **AND** services start in correct dependency order
- **AND** URLs for accessing the application are shown

#### Service Orchestration
**Scenario**: Platform has multiple interdependent services
- **GIVEN** database, backend, and frontend services exist
- **WHEN** startup script runs
- **THEN** database starts first
- **AND** backend waits for database readiness
- **AND** frontend starts after backend is ready
- **AND** health checks verify each service before proceeding

#### Graceful Shutdown
**Scenario**: Developer stops the platform
- **GIVEN** all services are running
- **WHEN** developer presses Ctrl+C
- **THEN** shutdown signal sent to all services
- **AND** services stop in reverse dependency order
- **AND** cleanup operations complete successfully
- **AND** no zombie processes remain

#### Error Recovery
**Scenario**: One service fails to start
- **GIVEN** backend fails to start due to database connection issue
- **WHEN** startup script detects failure
- **THEN** clear error message displayed
- **AND** running services stopped gracefully
- **AND** troubleshooting suggestions provided
- **AND** script exits with appropriate error code

#### Development vs Production
**Scenario**: Script runs in different environments
- **GIVEN** development environment
- **WHEN** script runs
- **THEN** hot reload enabled for frontend
- **AND** debug logging enabled for backend
- **AND** development database used
- **AND** in production uses optimized settings

## Implementation Details

### Startup Script Architecture

```bash
#!/bin/bash
# run_platform.sh - MyStocks Platform Startup Script

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
VITE_APP_ENV=development
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

# Signal handling
trap cleanup SIGINT SIGTERM

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

# Main execution
main() {
    log_info "🚀 Starting MyStocks Quantitative Trading Platform..."
    log_info "=================================================="

    # Run prerequisites check
    check_prerequisites

    # Start services in order
    start_database || error_exit "Failed to start database"
    start_backend || error_exit "Failed to start backend"
    start_frontend || error_exit "Failed to start frontend"

    # Success message
    echo ""
    log_info "✅ MyStocks Platform started successfully!"
    log_info "=================================================="
    log_info "📊 Frontend: http://localhost:$FRONTEND_PORT"
    log_info "🔧 Backend API: http://localhost:$BACKEND_PORT"
    log_info "📖 API Docs: http://localhost:$BACKEND_PORT/docs"
    log_info "🛑 Press Ctrl+C to stop all services"
    echo ""

    # Keep script running
    wait
}

# Run main function
main "$@"
```

### Docker Compose Integration

```yaml
# docker-compose.yml (for production deployment)
version: '3.8'

services:
  tdengine:
    image: tdengine/tdengine:3.0.4.0
    container_name: mystocks-tdengine
    ports:
      - "6030:6030"
      - "6041:6041"
    environment:
      - TAOS_ADAPTER=true
    volumes:
      - tdengine-data:/var/lib/taos
      - tdengine-log:/var/log/taos
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "taos", "-s", "show databases;"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:15
    container_name: mystocks-postgres
    environment:
      - POSTGRES_DB=mystocks
      - POSTGRES_USER=mystocks
      - POSTGRES_PASSWORD=mystocks123
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped
    depends_on:
      - tdengine

  redis:
    image: redis:7-alpine
    container_name: mystocks-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped

volumes:
  tdengine-data:
  tdengine-log:
  postgres-data:
  redis-data:
```

### Health Check Scripts

```bash
#!/bin/bash
# health_check.sh - Comprehensive health checks for all services

check_database() {
    echo "Checking TDengine..."
    if curl -s "http://localhost:6030/rest/sql" \
        -H "Authorization: Basic cm9vdDp0YW9zZGF0YQ==" \
        -d "sql=show databases" >/dev/null 2>&1; then
        echo "✅ TDengine is healthy"
        return 0
    else
        echo "❌ TDengine is not responding"
        return 1
    fi
}

check_backend() {
    echo "Checking FastAPI backend..."
    if curl -s "http://localhost:8000/health" | grep -q "ok"; then
        echo "✅ Backend is healthy"

        # Check API endpoints count
        api_count=$(curl -s "http://localhost:8000/openapi.json" | jq '.paths | length' 2>/dev/null || echo "0")
        echo "📊 API endpoints available: $api_count"
        return 0
    else
        echo "❌ Backend is not responding"
        return 1
    fi
}

check_frontend() {
    echo "Checking Vue frontend..."
    if curl -s "http://localhost:3000" | grep -q "MyStocks"; then
        echo "✅ Frontend is healthy"
        return 0
    else
        echo "❌ Frontend is not responding"
        return 1
    fi
}

# Run all checks
main() {
    echo "🏥 MyStocks Platform Health Check"
    echo "=================================="

    local failed=0

    check_database || ((failed++))
    check_backend || ((failed++))
    check_frontend || ((failed++))

    echo ""
    if [ $failed -eq 0 ]; then
        echo "🎉 All services are healthy!"
        exit 0
    else
        echo "⚠️  $failed service(s) are not healthy"
        exit 1
    fi
}

main "$@"
```

### Process Management

```bash
#!/bin/bash
# manage_services.sh - Advanced service management

SERVICE_NAME=""
ACTION=""

show_usage() {
    cat << EOF
MyStocks Service Manager

Usage: $0 <service> <action>

Services:
  database    - TDengine database
  backend     - FastAPI backend
  frontend    - Vue frontend
  all         - All services

Actions:
  start       - Start service
  stop        - Stop service
  restart     - Restart service
  status      - Show service status
  logs        - Show service logs

Examples:
  $0 backend start
  $0 all stop
  $0 frontend logs
EOF
}

get_service_info() {
    local service=$1

    case $service in
        database)
            echo "TDengine database"
            echo "taosd"
            echo "6030"
            ;;
        backend)
            echo "FastAPI backend"
            echo "uvicorn"
            echo "8000"
            ;;
        frontend)
            echo "Vue frontend"
            echo "vite"
            echo "3000"
            ;;
        *)
            echo "Unknown service: $service"
            return 1
            ;;
    esac
}

check_service_running() {
    local service=$1
    local process_name

    read -r _ process_name _ <<< "$(get_service_info "$service")"

    if pgrep -f "$process_name" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

start_service() {
    local service=$1

    if check_service_running "$service"; then
        log_warn "Service $service is already running"
        return 0
    fi

    log_info "Starting $service..."

    case $service in
        database)
            # Start TDengine
            sudo systemctl start taosd 2>/dev/null || taosd >/dev/null 2>&1 &
            sleep 3
            ;;
        backend)
            cd "$PROJECT_ROOT/web/backend"
            source venv/bin/activate
            nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
            ;;
        frontend)
            cd "$PROJECT_ROOT/web/frontend"
            nohup npm run dev > frontend.log 2>&1 &
            ;;
    esac

    # Wait for service to start
    local attempts=0
    while [ $attempts -lt 10 ]; do
        if check_service_running "$service"; then
            log_info "Service $service started successfully"
            return 0
        fi
        sleep 2
        ((attempts++))
    done

    log_error "Failed to start service $service"
    return 1
}

stop_service() {
    local service=$1
    local process_name

    read -r _ process_name _ <<< "$(get_service_info "$service")"

    if ! check_service_running "$service"; then
        log_warn "Service $service is not running"
        return 0
    fi

    log_info "Stopping $service..."
    pkill -f "$process_name" 2>/dev/null || true

    # Wait for service to stop
    local attempts=0
    while [ $attempts -lt 5 ]; do
        if ! check_service_running "$service"; then
            log_info "Service $service stopped successfully"
            return 0
        fi
        sleep 1
        ((attempts++))
    done

    log_error "Failed to stop service $service"
    return 1
}

show_status() {
    local service=$1
    local display_name process_name port

    read -r display_name process_name port <<< "$(get_service_info "$service")"

    echo "Service: $display_name"
    echo "Process: $process_name"
    echo "Port: $port"

    if check_service_running "$service"; then
        echo "Status: ✅ Running"

        # Show additional info
        case $service in
            backend)
                if curl -s "http://localhost:$port/health" >/dev/null 2>&1; then
                    echo "Health: ✅ Healthy"
                else
                    echo "Health: ❌ Unhealthy"
                fi
                ;;
            frontend)
                if curl -s "http://localhost:$port" >/dev/null 2>&1; then
                    echo "Health: ✅ Healthy"
                else
                    echo "Health: ❌ Unhealthy"
                fi
                ;;
        esac
    else
        echo "Status: ❌ Stopped"
    fi
    echo ""
}

show_logs() {
    local service=$1

    case $service in
        backend)
            if [ -f "$PROJECT_ROOT/web/backend/backend.log" ]; then
                tail -f "$PROJECT_ROOT/web/backend/backend.log"
            else
                echo "No backend log file found"
            fi
            ;;
        frontend)
            if [ -f "$PROJECT_ROOT/web/frontend/frontend.log" ]; then
                tail -f "$PROJECT_ROOT/web/frontend/frontend.log"
            else
                echo "No frontend log file found"
            fi
            ;;
        database)
            echo "Database logs are typically in /var/log/taos/"
            echo "Use: sudo tail -f /var/log/taos/taosdlog.0"
            ;;
    esac
}

main() {
    if [ $# -ne 2 ]; then
        show_usage
        exit 1
    fi

    SERVICE_NAME=$1
    ACTION=$2

    case $ACTION in
        start|stop|restart|status|logs)
            ;;
        *)
            echo "Invalid action: $ACTION"
            show_usage
            exit 1
            ;;
    esac

    case $SERVICE_NAME in
        database|backend|frontend)
            ;;
        all)
            case $ACTION in
                start)
                    start_service database
                    start_service backend
                    start_service frontend
                    ;;
                stop)
                    stop_service frontend
                    stop_service backend
                    # Don't stop database automatically
                    ;;
                restart)
                    stop_service frontend
                    stop_service backend
                    start_service backend
                    start_service frontend
                    ;;
                status)
                    show_status database
                    show_status backend
                    show_status frontend
                    ;;
                *)
                    echo "Action '$ACTION' not supported for 'all' services"
                    exit 1
                    ;;
            esac
            exit 0
            ;;
        *)
            echo "Invalid service: $SERVICE_NAME"
            show_usage
            exit 1
            ;;
    esac

    # Handle individual services
    case $ACTION in
        start)
            start_service "$SERVICE_NAME"
            ;;
        stop)
            stop_service "$SERVICE_NAME"
            ;;
        restart)
            stop_service "$SERVICE_NAME"
            sleep 2
            start_service "$SERVICE_NAME"
            ;;
        status)
            show_status "$SERVICE_NAME"
            ;;
        logs)
            show_logs "$SERVICE_NAME"
            ;;
    esac
}

main "$@"
```

## Performance Metrics

### Startup Time Targets
- Database: < 10 seconds
- Backend: < 15 seconds (after database ready)
- Frontend: < 20 seconds (after backend ready)
- Total: < 45 seconds

### Resource Usage Limits
- Memory: < 2GB total for all services
- CPU: < 50% average during normal operation
- Disk: < 5GB for logs and temporary files

### Reliability Targets
- Startup success rate: > 95%
- Service availability: > 99.5%
- Mean time to recovery: < 30 seconds

## Cross-references
- **routing-system**: Deployment scripts test complete routing functionality
- **api-connectivity**: Scripts validate end-to-end API communication
- **environment-config**: Scripts use environment-specific configurations