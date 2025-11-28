#!/bin/bash

# 端到端API修复验证脚本
# 验证以下内容：
# 1. 股票基本信息API数据获取逻辑修复
# 2. 错误处理和恢复机制完善
# 3. 业务API监控体系建立
# 4. 端到端数据一致性验证

set -e

# 配置
API_BASE_URL="${API_BASE_URL:-http://localhost:8000}"
AUTH_TOKEN="${AUTH_TOKEN:-}"
TEST_TIMEOUT=10

echo "========================================="
echo "API修复验证测试 - $(date)"
echo "========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试计数
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 辅助函数 - 增强版，验证响应体结构
test_api_enhanced() {
    local name=$1
    local endpoint=$2
    local method=${3:-GET}
    local expected_status=${4:-200}

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    echo -n "测试 [$method] $endpoint ... "

    # 构建curl命令（获取完整响应包括HTTP码）
    local curl_cmd="curl -s -X $method -w '\n%{http_code}'"
    if [ -n "$AUTH_TOKEN" ]; then
        curl_cmd="$curl_cmd -H 'Authorization: Bearer $AUTH_TOKEN'"
    fi
    curl_cmd="$curl_cmd '$API_BASE_URL$endpoint'"

    # 执行请求并分离响应体和HTTP码
    local response=$(eval $curl_cmd 2>/dev/null || echo "")
    local http_code=$(echo "$response" | tail -n 1)
    local response_body=$(echo "$response" | sed '$d')

    # 1. 首先检查HTTP状态码
    if [ "$http_code" != "$expected_status" ]; then
        echo -e "${RED}✗ 失败 - HTTP状态码 (期望 $expected_status，得到 $http_code)${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        echo "   响应: $response_body" | head -c 100
        echo ""
        return 1
    fi

    # 2. 对于200响应，验证响应体结构
    if [ "$http_code" = "200" ]; then
        # 检查是否包含"success"字段并且为true
        if echo "$response_body" | grep -q '"success".*true'; then
            # 响应正常
            echo -e "${GREEN}✓ 成功 (HTTP $http_code, success=true)${NC}"
            PASSED_TESTS=$((PASSED_TESTS + 1))
            return 0
        elif echo "$response_body" | grep -q '"success".*false'; then
            # ERROR: HTTP 200但success=false表示假阳性！
            echo -e "${RED}✗ 失败 - 假阳性错误 (HTTP 200但success=false)${NC}"
            FAILED_TESTS=$((FAILED_TESTS + 1))
            echo "   错误信息: $(echo "$response_body" | grep -o '"msg":"[^"]*"' | head -c 80)"
            echo ""
            return 1
        else
            # 无法解析响应
            echo -e "${RED}✗ 失败 - 无效的JSON响应${NC}"
            FAILED_TESTS=$((FAILED_TESTS + 1))
            echo "   响应: $response_body" | head -c 100
            echo ""
            return 1
        fi
    fi

    # 对于其他预期状态码，只检查码即可
    echo -e "${GREEN}✓ 成功 (HTTP $http_code)${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    return 0
}

# 保留原始函数用于向后兼容
test_api() {
    test_api_enhanced "$@"
}

# ========================================
# 1. 股票基本信息API测试
# ========================================
echo ""
echo -e "${YELLOW}=== 1. 股票基本信息API修复验证 ===${NC}"

test_api "获取股票基本信息 (默认)" "/api/data/stocks/basic" "GET" "200"
test_api "获取股票基本信息 (自定义limit)" "/api/data/stocks/basic?limit=50" "GET" "200"
test_api "股票搜索" "/api/data/stocks/search?keyword=平安" "GET" "200"
test_api "获取行业列表" "/api/data/stocks/industries" "GET" "200"
test_api "获取概念列表" "/api/data/stocks/concepts" "GET" "200"

# ========================================
# 2. 错误处理验证
# ========================================
echo ""
echo -e "${YELLOW}=== 2. 错误处理机制验证 ===${NC}"

test_api "无效limit参数处理" "/api/data/stocks/basic?limit=0" "GET" "200"
test_api "超大limit参数处理" "/api/data/stocks/basic?limit=10000" "GET" "200"
test_api "搜索关键词太短" "/api/data/stocks/search?keyword=a" "GET" "200"

# ========================================
# 3. K线数据API测试
# ========================================
echo ""
echo -e "${YELLOW}=== 3. K线数据API验证 ===${NC}"

test_api "获取K线数据" "/api/data/stocks/kline?symbol=000001.SZ&start_date=2025-01-01&end_date=2025-01-31&period=day" "GET" "200"
test_api "获取日线数据" "/api/data/stocks/daily?symbol=000001.SZ" "GET" "200"

# ========================================
# 4. 监控和健康检查API测试
# ========================================
echo ""
echo -e "${YELLOW}=== 4. 监控体系验证 ===${NC}"

if [ -n "$AUTH_TOKEN" ]; then
    test_api "健康检查" "/api/monitoring/health" "GET" "200"
    test_api "监控仪表板" "/api/monitoring/dashboard" "GET" "200"
    test_api "获取指标记录" "/api/monitoring/metrics?limit=10" "GET" "200"
else
    echo -n "健康检查 ... "
    echo -e "${YELLOW}⊘ 跳过（未提供AUTH_TOKEN）${NC}"
    echo -n "监控仪表板 ... "
    echo -e "${YELLOW}⊘ 跳过（未提供AUTH_TOKEN）${NC}"
fi

# ========================================
# 5. 市场数据API测试
# ========================================
echo ""
echo -e "${YELLOW}=== 5. 市场数据API验证 ===${NC}"

test_api "市场概览" "/api/data/markets/overview" "GET" "200"
test_api "涨跌分布" "/api/data/markets/price-distribution" "GET" "200"
test_api "热门行业" "/api/data/markets/hot-industries" "GET" "200"
test_api "热门概念" "/api/data/markets/hot-concepts" "GET" "200"

# ========================================
# 总结
# ========================================
echo ""
echo "========================================="
echo "测试总结："
echo "========================================="
echo "总测试数: $TOTAL_TESTS"
echo -e "${GREEN}通过: $PASSED_TESTS${NC}"
if [ $FAILED_TESTS -gt 0 ]; then
    echo -e "${RED}失败: $FAILED_TESTS${NC}"
else
    echo -e "${GREEN}失败: 0${NC}"
fi

echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✓ 所有测试通过！${NC}"
    exit 0
else
    echo -e "${RED}✗ 有测试失败，请检查错误日志${NC}"
    exit 1
fi
