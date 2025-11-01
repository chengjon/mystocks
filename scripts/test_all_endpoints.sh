#!/bin/bash
# 综合API端点测试脚本
# 测试所有Web后端API功能

BASE_URL="http://localhost:8000"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "MyStocks Web API 综合测试"
echo "=========================================="
echo ""

# Test counter
TOTAL=0
PASSED=0
FAILED=0

test_endpoint() {
    local name=$1
    local url=$2
    local expected_code=${3:-200}

    TOTAL=$((TOTAL + 1))
    echo -n "Testing $name... "

    response=$(curl -s -o /dev/null -w "%{http_code}" "$url")

    if [ "$response" -eq "$expected_code" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $response)"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}✗ FAIL${NC} (Expected: $expected_code, Got: $response)"
        FAILED=$((FAILED + 1))
    fi
}

test_with_data() {
    local name=$1
    local url=$2

    TOTAL=$((TOTAL + 1))
    echo -n "Testing $name... "

    response=$(curl -s "$url")
    http_code=$(curl -s -o /dev/null -w "%{http_code}" "$url")

    if [ "$http_code" -eq 200 ]; then
        # Check if response contains data (handle both array and {data: []} formats)
        data_count=$(echo "$response" | python3 -c "import sys, json; data = json.load(sys.stdin); print(len(data) if isinstance(data, list) else len(data.get('data', [])))" 2>/dev/null || echo "0")

        if [ "$data_count" -gt 0 ]; then
            echo -e "${GREEN}✓ PASS${NC} (HTTP 200, $data_count records)"
            PASSED=$((PASSED + 1))
        else
            echo -e "${YELLOW}⚠ PARTIAL${NC} (HTTP 200, but 0 records)"
            PASSED=$((PASSED + 1))
        fi
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $http_code)"
        FAILED=$((FAILED + 1))
    fi
}

echo "=== 1. System Health Checks ==="
test_endpoint "System Health" "$BASE_URL/api/system/health"
test_endpoint "Adapters Health" "$BASE_URL/api/system/adapters/health"
test_endpoint "Market Health" "$BASE_URL/api/market/health"
echo ""

echo "=== 2. Market Data Endpoints ==="
test_with_data "Stock List" "$BASE_URL/api/market/stocks?limit=10"
test_with_data "ETF List" "$BASE_URL/api/market/etf/list?limit=10"
test_with_data "LHB Detail" "$BASE_URL/api/market/lhb?limit=10"
test_with_data "Fund Flow" "$BASE_URL/api/market/fund-flow?symbol=600519.SH"
test_with_data "Chip Race" "$BASE_URL/api/market/chip-race?limit=10"
test_endpoint "Real-time Quotes" "$BASE_URL/api/market/quotes"
echo ""

echo "=== 3. Authentication ==="
# Login test
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123")

TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

if [ -n "$TOKEN" ]; then
    echo -e "Login test... ${GREEN}✓ PASS${NC} (Token obtained)"
    TOTAL=$((TOTAL + 1))
    PASSED=$((PASSED + 1))

    # Test authenticated endpoint
    AUTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/auth/me" \
      -H "Authorization: Bearer $TOKEN")

    if [ "$AUTH_RESPONSE" -eq 200 ]; then
        echo -e "Get user info... ${GREEN}✓ PASS${NC} (HTTP 200)"
        TOTAL=$((TOTAL + 1))
        PASSED=$((PASSED + 1))
    else
        echo -e "Get user info... ${RED}✗ FAIL${NC} (HTTP $AUTH_RESPONSE)"
        TOTAL=$((TOTAL + 1))
        FAILED=$((FAILED + 1))
    fi
else
    echo -e "Login test... ${RED}✗ FAIL${NC} (No token received)"
    TOTAL=$((TOTAL + 1))
    FAILED=$((FAILED + 1))
fi

echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "Total Tests: $TOTAL"
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed! 🎉${NC}"
    exit 0
else
    PASS_RATE=$((PASSED * 100 / TOTAL))
    echo -e "${YELLOW}Pass Rate: $PASS_RATE%${NC}"
    exit 1
fi
