#!/bin/bash
##############################################################################
# 问财API测试脚本
#
# 测试所有问财API端点是否正常工作
#
# 作者: MyStocks Backend Team
# 创建日期: 2025-10-17
# 使用方法: bash scripts/test_wencai_api.sh [base_url]
##############################################################################

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
BASE_URL="${1:-http://localhost:8000}"
API_PREFIX="/api/market/wencai"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  问财API端点测试${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}测试地址: $BASE_URL${NC}"
echo

# 测试计数器
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 测试函数
test_endpoint() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local expected_status="${5:-200}"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "${YELLOW}[Test $TOTAL_TESTS] $name${NC}"

    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$BASE_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$BASE_URL$endpoint")
    fi

    # 分离响应体和状态码
    body=$(echo "$response" | head -n -1)
    status=$(echo "$response" | tail -n 1)

    # 验证状态码
    if [ "$status" = "$expected_status" ]; then
        echo -e "${GREEN}✅ PASSED${NC} (HTTP $status)"
        PASSED_TESTS=$((PASSED_TESTS + 1))

        # 显示响应（截取前200字符）
        if [ -n "$body" ]; then
            echo -e "${BLUE}Response:${NC} $(echo "$body" | cut -c1-200)..."
        fi
    else
        echo -e "${RED}❌ FAILED${NC} (Expected $expected_status, got $status)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        echo -e "${RED}Response:${NC} $body"
    fi

    echo
}

# ============================================================================
# 测试用例
# ============================================================================

# Test 1: 健康检查
test_endpoint \
    "健康检查" \
    "GET" \
    "$API_PREFIX/health" \
    "" \
    "200"

# Test 2: 获取所有查询列表
test_endpoint \
    "获取所有查询列表" \
    "GET" \
    "$API_PREFIX/queries" \
    "" \
    "200"

# Test 3: 获取指定查询信息
test_endpoint \
    "获取指定查询信息 (qs_9)" \
    "GET" \
    "$API_PREFIX/queries/qs_9" \
    "" \
    "200"

# Test 4: 获取不存在的查询 (应该返回404)
test_endpoint \
    "获取不存在的查询 (qs_99)" \
    "GET" \
    "$API_PREFIX/queries/qs_99" \
    "" \
    "404"

# Test 5: 执行查询 (可能需要较长时间)
echo -e "${YELLOW}⚠️  以下测试将实际调用问财API，可能需要10-30秒...${NC}"
read -p "是否继续？(y/n) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    test_endpoint \
        "执行查询 (qs_9, 1页)" \
        "POST" \
        "$API_PREFIX/query" \
        '{"query_name":"qs_9","pages":1}' \
        "200"

    # Test 6: 获取查询结果
    test_endpoint \
        "获取查询结果 (qs_9, limit=10)" \
        "GET" \
        "$API_PREFIX/results/qs_9?limit=10" \
        "" \
        "200"

    # Test 7: 获取查询历史
    test_endpoint \
        "获取查询历史 (qs_9, 7天)" \
        "GET" \
        "$API_PREFIX/history/qs_9?days=7" \
        "" \
        "200"

    # Test 8: 刷新查询（后台任务）
    test_endpoint \
        "刷新查询 (qs_9, 后台任务)" \
        "POST" \
        "$API_PREFIX/refresh/qs_9?pages=1" \
        "" \
        "200"
else
    echo -e "${YELLOW}跳过实际API调用测试${NC}"
    echo
fi

# Test 9: 无效请求（参数错误）
test_endpoint \
    "无效请求 (query_name格式错误)" \
    "POST" \
    "$API_PREFIX/query" \
    '{"query_name":"invalid","pages":1}' \
    "400"

# Test 10: API文档可访问性
test_endpoint \
    "API文档可访问性" \
    "GET" \
    "/api/docs" \
    "" \
    "200"

# ============================================================================
# 测试结果汇总
# ============================================================================

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  测试结果汇总${NC}"
echo -e "${BLUE}========================================${NC}"
echo
echo -e "总测试数: ${BLUE}$TOTAL_TESTS${NC}"
echo -e "通过: ${GREEN}$PASSED_TESTS${NC}"
echo -e "失败: ${RED}$FAILED_TESTS${NC}"
echo

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✅ 所有测试通过！${NC}"
    exit 0
else
    echo -e "${RED}❌ 有 $FAILED_TESTS 个测试失败${NC}"
    exit 1
fi
