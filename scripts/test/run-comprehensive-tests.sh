#!/bin/bash
# =============================================================================
# MyStocks Comprehensive Test Runner
# 
# This script:
# 1. Starts frontend and backend services via PM2
# 2. Waits for services to be ready
# 3. Runs comprehensive E2E tests via Playwright
# 4. Monitors logs via lnav
# 5. Reports results and issues
# =============================================================================

set -e  # Exit on error

# Configuration
PROJECT_DIR="/opt/claude/mystocks_spec"
FRONTEND_DIR="${PROJECT_DIR}/web/frontend"
BACKEND_DIR="${PROJECT_DIR}/web/backend"
TEST_LOG_DIR="${PROJECT_DIR}/logs/tests"
FRONTEND_PORT=3002
BACKEND_PORT=8000

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# Helper Functions
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

cleanup() {
    log_info "Cleaning up..."
    # Keep services running for inspection, just stop test-related processes
}

trap cleanup EXIT

# =============================================================================
# Step 1: Check Prerequisites
# =============================================================================
echo "=============================================="
echo "  MyStocks Comprehensive E2E Test Runner"
echo "=============================================="
echo ""

log_info "Checking prerequisites..."

# Check PM2
if ! command -v pm2 &> /dev/null; then
    log_error "PM2 not found. Installing..."
    npm install -g pm2
fi

# Check Playwright
if ! command -v npx &> /dev/null; then
    log_error "npx not found"
    exit 1
fi

# Check frontend dependencies
if [ ! -d "${FRONTEND_DIR}/node_modules" ]; then
    log_warning "Frontend dependencies not installed. Installing..."
    cd "${FRONTEND_DIR}" && npm install
fi

# Create test logs directory
mkdir -p "${TEST_LOG_DIR}"

# =============================================================================
# Step 2: Start Services via PM2
# =============================================================================
echo ""
log_info "Step 1: Starting services via PM2..."

# Stop existing services
log_info "Stopping existing services..."
pm2 stop all 2>/dev/null || true
pm2 delete all 2>/dev/null || true

# Start backend service
log_info "Starting backend service (port ${BACKEND_PORT})..."
cd "${BACKEND_DIR}"
pm2 start ecosystem.config.js --name "mystocks-backend" || {
    log_warning "PM2 ecosystem config failed, starting manually..."
    pm2 start python3 --name "mystocks-backend" -- \
        -m uvicorn app.main:app --host 0.0.0.0 --port ${BACKEND_PORT} --reload
}

# Start frontend service
log_info "Starting frontend service (port ${FRONTEND_PORT})..."
cd "${FRONTEND_DIR}"
pm2 start npm --name "mystocks-frontend" -- run dev -- --port ${FRONTEND_PORT}

# Wait for services to start
log_info "Waiting for services to start..."
sleep 10

# Check service status
echo ""
log_info "Service status:"
pm2 list

# =============================================================================
# Step 3: Wait for Services to be Ready
# =============================================================================
echo ""
log_info "Step 2: Waiting for services to be ready..."

max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    # Check backend
    backend_ready=false
    if curl -s "http://localhost:${BACKEND_PORT}/api/health" > /dev/null 2>&1; then
        backend_ready=true
        log_success "Backend is ready"
    fi
    
    # Check frontend
    frontend_ready=false
    if curl -s "http://localhost:${FRONTEND_PORT}" > /dev/null 2>&1; then
        frontend_ready=true
        log_success "Frontend is ready"
    fi
    
    if $backend_ready && $frontend_ready; then
        break
    fi
    
    attempt=$((attempt + 1))
    echo -n "."
    sleep 2
done
echo ""

if [ $attempt -eq $max_attempts ]; then
    log_warning "Services may not be fully ready, continuing with tests..."
fi

# =============================================================================
# Step 4: Run Playwright Tests
# =============================================================================
echo ""
log_info "Step 3: Running Playwright comprehensive tests..."

cd "${FRONTEND_DIR}"

# Run the comprehensive test
TEST_START_TIME=$(date +%s)

npx playwright test tests/comprehensive-all-pages.spec.ts \
    --project=chromium \
    --reporter=list \
    --timeout=60000 \
    2>&1 | tee "${TEST_LOG_DIR}/test-output.log"

TEST_END_TIME=$(date +%s)
TEST_DURATION=$((TEST_END_TIME - TEST_START_TIME))

# =============================================================================
# Step 5: Collect and Analyze Logs
# =============================================================================
echo ""
log_info "Step 4: Analyzing test results..."

# Copy PM2 logs to test directory
pm2 logs --nostream --lines 100 2>/dev/null | tail -50 > "${TEST_LOG_DIR}/pm2-logs.log" || true

# Check for errors in test output
ERROR_COUNT=$(grep -c "FAILED\|✗\|Error:" "${TEST_LOG_DIR}/test-output.log" 2>/dev/null || echo "0")
PASS_COUNT=$(grep -c "PASSED\|✓" "${TEST_LOG_DIR}/test-output.log" 2>/dev/null || echo "0")

echo ""
echo "=============================================="
echo "  Test Results Summary"
echo "=============================================="
echo "  Duration: ${TEST_DURATION} seconds"
echo "  Passed: ${PASS_COUNT}"
echo "  Failed/Errors: ${ERROR_COUNT}"
echo "=============================================="

# =============================================================================
# Step 6: Generate Report
# =============================================================================
echo ""
log_info "Step 5: Generating test report..."

REPORT_FILE="${TEST_LOG_DIR}/test-report-$(date +%Y%m%d-%H%M%S).md"

cat > "${REPORT_FILE}" << EOF
# MyStocks Comprehensive E2E Test Report

**Date:** $(date)
**Duration:** ${TEST_DURATION} seconds

## Test Configuration

- **Frontend:** http://localhost:${FRONTEND_PORT}
- **Backend:** http://localhost:${BACKEND_PORT}
- **Test File:** comprehensive-all-pages.spec.ts
- **Pages Tested:** 43 pages across all domains

## Results Summary

- **Passed:** ${PASS_COUNT}
- **Failed/Errors:** ${ERROR_COUNT}

## Pages Tested

### Authentication
- [ ] Login

### Dashboard
- [ ] Dashboard

### Market Domain (10 pages)
- [ ] Realtime
- [ ] Technical
- [ ] Fund Flow
- [ ] ETF
- [ ] Concept
- [ ] Auction
- [ ] Long Hu Bang
- [ ] Institution
- [ ] Wencai
- [ ] Screener

### Stock Management (2 pages)
- [ ] Stock Management
- [ ] Portfolio

### Trading Domain (4 pages)
- [ ] Signals
- [ ] History
- [ ] Positions
- [ ] Attribution

### Strategy Domain (5 pages)
- [ ] Design
- [ ] Management
- [ ] Backtest
- [ ] GPU Backtest
- [ ] Optimization

### Risk Domain (5 pages)
- [ ] Overview
- [ ] Alerts
- [ ] Indicators
- [ ] Sentiment
- [ ] Announcement

### System Domain (5 pages)
- [ ] Monitoring
- [ ] Settings
- [ ] Data Update
- [ ] Data Quality
- [ ] API Health

## Issues Found

$(grep -A2 "FAILED\|✗" "${TEST_LOG_DIR}/test-output.log" 2>/dev/null || echo "None")

## Logs

- Test output: ${TEST_LOG_DIR}/test-output.log
- PM2 logs: ${TEST_LOG_DIR}/pm2-logs.log

## Recommendations

1. Review any failed tests and fix underlying issues
2. Ensure all mock APIs return expected data
3. Verify authentication flow works correctly
4. Check for console errors on problematic pages

EOF

log_success "Report saved to: ${REPORT_FILE}"

# =============================================================================
# Step 7: Instructions for Next Steps
# =============================================================================
echo ""
echo "=============================================="
echo "  Test Run Complete!"
echo "=============================================="
echo ""
echo "Next steps:"
echo "1. Review the test report: ${REPORT_FILE}"
echo "2. Check logs with: lnav ${TEST_LOG_DIR}/test-output.log"
echo "3. View PM2 logs: pm2 logs"
echo "4. Fix any issues found"
echo "5. Re-run tests"
echo ""
echo "Quick commands:"
echo "  # View test logs"
echo "  lnav ${TEST_LOG_DIR}/test-output.log"
echo ""
echo "  # Restart services"
echo "  pm2 restart all"
echo ""
echo "  # Run tests again"
echo "  npm run test:e2e:comprehensive"
echo ""

exit 0
