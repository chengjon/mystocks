#!/bin/bash
# API Verification Command Templates
# Usage: source this file to load API verification functions

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default configuration
export MYSTOCKS_URL="${MYSTOCKS_URL:-http://localhost:8000}"
export MYSTOCKS_USER="${MYSTOCKS_USER:-admin}"
export MYSTOCKS_PASS="${MYSTOCKS_PASS:-admin123}"

# ============================================================================
# Authentication Templates
# ============================================================================

# Template: Get access token
function api_get_token() {
    echo "Getting access token..."
    http POST "$MYSTOCKS_URL/api/auth/login" \
        username="$MYSTOCKS_USER" \
        password="$MYSTOCKS_PASS" | jq -r '.access_token'
}

# Template: Test authentication endpoint
function api_test_auth() {
    echo "Testing authentication..."
    local response=$(http POST "$MYSTOCKS_URL/api/auth/login" \
        username="$MYSTOCKS_USER" \
        password="$MYSTOCKS_PASS")

    echo "$response" | jq

    if echo "$response" | jq -e '.access_token' > /dev/null; then
        echo -e "${GREEN}✅ Authentication successful${NC}"
        return 0
    else
        echo -e "${RED}❌ Authentication failed${NC}"
        return 1
    fi
}

# ============================================================================
# Dashboard API Templates
# ============================================================================

# Template: Test dashboard summary API
function api_test_dashboard_summary() {
    local token=${1:-$(api_get_token)}

    echo "Testing dashboard summary API..."
    http GET "$MYSTOCKS_URL/api/data/dashboard/summary" \
        Authorization:"Bearer $token"
}

# Template: Verify dashboard summary returns data
function api_verify_dashboard_summary() {
    local token=${1:-$(api_get_token)}

    echo "Verifying dashboard summary data..."
    local response=$(http GET "$MYSTOCKS_URL/api/data/dashboard/summary" \
        Authorization:"Bearer $token")

    if echo "$response" | jq -e '.data != null' > /dev/null; then
        echo -e "${GREEN}✅ Dashboard summary has data${NC}"
        echo "Record count: $(echo "$response" | jq '.data | length')"
        return 0
    else
        echo -e "${RED}❌ Dashboard summary has no data${NC}"
        return 1
    fi
}

# ============================================================================
# Market Data API Templates
# ============================================================================

# Template: Test dragon tiger (龙虎榜) API
function api_test_dragon_tiger() {
    local limit=${1:-10}
    local token=${2:-$(api_get_token)}

    echo "Testing dragon tiger API (limit=$limit)..."
    http GET "$MYSTOCKS_URL/api/market/dragon-tiger?limit=$limit" \
        Authorization:"Bearer $token"
}

# Template: Verify dragon tiger returns correct number of records
function api_verify_dragon_tiger() {
    local limit=${1:-10}
    local token=${2:-$(api_get_token)}

    echo "Verifying dragon tiger API (limit=$limit)..."
    local response=$(http GET "$MYSTOCKS_URL/api/market/dragon-tiger?limit=$limit" \
        Authorization:"Bearer $token")

    local actual_count=$(echo "$response" | jq '.data | length')

    if [ "$actual_count" -eq "$limit" ] || [ "$actual_count" -lt "$limit" ]; then
        echo -e "${GREEN}✅ Dragon tiger API returned $actual_count records (expected ≤ $limit)${NC}"
        return 0
    else
        echo -e "${RED}❌ Dragon tiger API returned $actual_count records (expected ≤ $limit)${NC}"
        return 1
    fi
}

# Template: Test ETF data API
function api_test_etf_data() {
    local limit=${1:-10}
    local token=${2:-$(api_get_token)}

    echo "Testing ETF data API (limit=$limit)..."
    http GET "$MYSTOCKS_URL/api/market/etf-data?limit=$limit" \
        Authorization:"Bearer $token"
}

# Template: Verify ETF data structure
function api_verify_etf_data() {
    local limit=${1:-10}
    local token=${2:-$(api_get_token)}

    echo "Verifying ETF data API (limit=$limit)..."
    local response=$(http GET "$MYSTOCKS_URL/api/market/etf-data?limit=$limit" \
        Authorization:"Bearer $token")

    if echo "$response" | jq -e '.data != null and (.data | length) > 0' > /dev/null; then
        echo -e "${GREEN}✅ ETF data API has data${NC}"
        echo "Record count: $(echo "$response" | jq '.data | length')"
        return 0
    else
        echo -e "${RED}❌ ETF data API has no data${NC}"
        return 1
    fi
}

# Template: Test fund flow (资金流向) API
function api_test_fund_flow() {
    local industry_type=${1:-csrc}
    local limit=${2:-10}
    local token=${3:-$(api_get_token)}

    echo "Testing fund flow API (industry_type=$industry_type, limit=$limit)..."
    http GET "$MYSTOCKS_URL/api/market/fund-flow?industry_type=$industry_type&limit=$limit" \
        Authorization:"Bearer $token"
}

# Template: Verify fund flow data
function api_verify_fund_flow() {
    local industry_type=${1:-csrc}
    local limit=${2:-10}
    local token=${3:-$(api_get_token)}

    echo "Verifying fund flow API (industry_type=$industry_type, limit=$limit)..."
    local response=$(http GET "$MYSTOCKS_URL/api/market/fund-flow?industry_type=$industry_type&limit=$limit" \
        Authorization:"Bearer $token")

    if echo "$response" | jq -e '.data != null and (.data | length) > 0' > /dev/null; then
        echo -e "${GREEN}✅ Fund flow API has data${NC}"
        echo "Record count: $(echo "$response" | jq '.data | length')"
        return 0
    else
        echo -e "${RED}❌ Fund flow API has no data${NC}"
        return 1
    fi
}

# Template: Test chip race (竞价抢筹) API
function api_test_chip_race() {
    local limit=${1:-10}
    local token=${2:-$(api_get_token)}

    echo "Testing chip race API (limit=$limit)..."
    http GET "$MYSTOCKS_URL/api/market/chip-race?limit=$limit" \
        Authorization:"Bearer $token"
}

# Template: Verify chip race data
function api_verify_chip_race() {
    local limit=${1:-10}
    local token=${2:-$(api_get_token)}

    echo "Verifying chip race API (limit=$limit)..."
    local response=$(http GET "$MYSTOCKS_URL/api/market/chip-race?limit=$limit" \
        Authorization:"Bearer $token")

    if echo "$response" | jq -e '.data != null and (.data | length) > 0' > /dev/null; then
        echo -e "${GREEN}✅ Chip race API has data${NC}"
        echo "Record count: $(echo "$response" | jq '.data | length')"
        return 0
    else
        echo -e "${RED}❌ Chip race API has no data${NC}"
        return 1
    fi
}

# ============================================================================
# Error Scenario Testing Templates
# ============================================================================

# Template: Test invalid token returns 401
function api_test_invalid_token() {
    local endpoint=${1:-/api/data/dashboard/summary}

    echo "Testing invalid token on $endpoint..."
    local response=$(http GET "$MYSTOCKS_URL$endpoint" \
        Authorization:"Bearer invalid_token" 2>&1)

    if echo "$response" | grep -q "HTTP/1.1 401"; then
        echo -e "${GREEN}✅ Invalid token correctly returns 401${NC}"
        return 0
    else
        echo -e "${RED}❌ Invalid token did not return 401${NC}"
        return 1
    fi
}

# Template: Test missing token returns 401
function api_test_missing_token() {
    local endpoint=${1:-/api/data/dashboard/summary}

    echo "Testing missing token on $endpoint..."
    local response=$(http GET "$MYSTOCKS_URL$endpoint" 2>&1)

    if echo "$response" | grep -q "HTTP/1.1 401"; then
        echo -e "${GREEN}✅ Missing token correctly returns 401${NC}"
        return 0
    else
        echo -e "${RED}❌ Missing token did not return 401${NC}"
        return 1
    fi
}

# Template: Test invalid endpoint returns 404
function api_test_invalid_endpoint() {
    local token=${1:-$(api_get_token)}

    echo "Testing invalid endpoint..."
    local response=$(http GET "$MYSTOCKS_URL/api/nonexistent/endpoint" \
        Authorization:"Bearer $token" 2>&1)

    if echo "$response" | grep -q "HTTP/1.1 404"; then
        echo -e "${GREEN}✅ Invalid endpoint correctly returns 404${NC}"
        return 0
    else
        echo -e "${RED}❌ Invalid endpoint did not return 404${NC}"
        return 1
    fi
}

# ============================================================================
# Batch Testing Templates
# ============================================================================

# Template: Test all market data APIs
function api_test_all_market_apis() {
    local token=$(api_get_token)

    echo ""
    echo "========================================="
    echo "Testing All Market Data APIs"
    echo "========================================="

    api_test_dragon_tiger 5 "$token"
    echo ""

    api_test_etf_data 5 "$token"
    echo ""

    api_test_fund_flow csrc 5 "$token"
    echo ""

    api_test_chip_race 5 "$token"
}

# Template: Verify all market data APIs
function api_verify_all_market_apis() {
    local token=$(api_get_token)
    local failed=0

    echo ""
    echo "========================================="
    echo "Verifying All Market Data APIs"
    echo "========================================="
    echo ""

    api_verify_dragon_tiger 5 "$token" || ((failed++))
    echo ""

    api_verify_etf_data 5 "$token" || ((failed++))
    echo ""

    api_verify_fund_flow csrc 5 "$token" || ((failed++))
    echo ""

    api_verify_chip_race 5 "$token" || ((failed++))
    echo ""

    echo "========================================="
    if [ $failed -eq 0 ]; then
        echo -e "${GREEN}✅ All APIs verified successfully!${NC}"
        return 0
    else
        echo -e "${RED}❌ $failed API(s) failed verification${NC}"
        return 1
    fi
}

# Template: Run smoke test on all critical APIs
function api_smoke_test() {
    echo ""
    echo "========================================="
    echo "Running API Smoke Test"
    echo "========================================="
    echo ""

    local failed=0

    # Test authentication
    api_test_auth || ((failed++))
    echo ""

    local token=$(api_get_token)

    # Test dashboard
    api_verify_dashboard_summary "$token" || ((failed++))
    echo ""

    # Test market APIs
    api_verify_dragon_tiger 5 "$token" || ((failed++))
    echo ""

    api_verify_etf_data 5 "$token" || ((failed++))
    echo ""

    # Test error scenarios
    api_test_invalid_token || ((failed++))
    echo ""

    echo "========================================="
    if [ $failed -eq 0 ]; then
        echo -e "${GREEN}✅ All smoke tests passed!${NC}"
        return 0
    else
        echo -e "${RED}❌ $failed test(s) failed${NC}"
        return 1
    fi
}

# ============================================================================
# Helper Functions
# ============================================================================

# Template: Pretty print JSON response
function api_pretty_json() {
    echo "$1" | jq '.'
}

# Template: Extract status code from response
function api_extract_status() {
    echo "$1" | grep "HTTP/" | awk '{print $2}'
}

# Template: Check if API is healthy
function api_health_check() {
    echo "Checking API health..."
    local response=$(http GET "$MYSTOCKS_URL/health" 2>&1)

    if echo "$response" | grep -q "HTTP/1.1 200"; then
        echo -e "${GREEN}✅ API is healthy${NC}"
        return 0
    else
        echo -e "${RED}❌ API is not responding${NC}"
        return 1
    fi
}

# ============================================================================
# Usage Examples
# ============================================================================

# Print usage examples
function api_usage_examples() {
    cat << 'EOF'
========================================
API Templates Usage Examples
========================================

1. Get access token:
   TOKEN=$(api_get_token)

2. Test dashboard summary:
   api_test_dashboard_summary

3. Verify dashboard has data:
   api_verify_dashboard_summary

4. Test dragon tiger API:
   api_test_dragon_tiger 10

5. Verify dragon tiger data:
   api_verify_dragon_tiger 10

6. Test all market APIs:
   api_test_all_market_apis

7. Verify all market APIs:
   api_verify_all_market_apis

8. Run smoke test:
   api_smoke_test

9. Health check:
   api_health_check

10. Test error scenarios:
    api_test_invalid_token
    api_test_missing_token
    api_test_invalid_endpoint

========================================
EOF
}

# Print loaded message
echo "✅ API templates loaded. Run 'api_usage_examples' to see usage."
