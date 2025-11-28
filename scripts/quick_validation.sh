#!/bin/bash

# 快速验证脚本 - 检查所有修复是否到位
echo "========================================="
echo "MyStocks API 修复快速验证"
echo "========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

CHECKS_PASSED=0
CHECKS_FAILED=0

check_file() {
    local file=$1
    local description=$2

    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $description"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo -e "${RED}✗${NC} 缺少文件: $file"
        CHECKS_FAILED=$((CHECKS_FAILED + 1))
    fi
}

check_function() {
    local file=$1
    local function=$2
    local description=$3

    if grep -q "def $function\|class $function" "$file" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $description"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        echo -e "${RED}✗${NC} 未找到: $function in $file"
        CHECKS_FAILED=$((CHECKS_FAILED + 1))
    fi
}

echo -e "${YELLOW}1. 检查核心修复文件${NC}"
check_file "/opt/claude/mystocks_spec/web/backend/app/core/data_validator.py" "数据验证模块"
check_file "/opt/claude/mystocks_spec/web/backend/app/core/api_monitoring.py" "API监控模块"
check_file "/opt/claude/mystocks_spec/web/backend/app/middleware/monitoring_middleware.py" "监控中间件"
check_file "/opt/claude/mystocks_spec/web/backend/app/api/monitoring.py" "监控API端点"

echo ""
echo -e "${YELLOW}2. 检查验证脚本${NC}"
check_file "/opt/claude/mystocks_spec/scripts/test_api_fixes.sh" "API修复验证脚本"
check_file "/opt/claude/mystocks_spec/scripts/test_data_consistency.py" "数据一致性验证脚本"
check_file "/opt/claude/mystocks_spec/scripts/quick_validation.sh" "快速验证脚本"

echo ""
echo -e "${YELLOW}3. 检查文档${NC}"
check_file "/opt/claude/mystocks_spec/docs/api/API_FIXES_SUMMARY.md" "API修复文档"

echo ""
echo -e "${YELLOW}4. 检查代码修复${NC}"
check_function "/opt/claude/mystocks_spec/web/backend/app/api/data.py" "get_stocks_basic" "股票基本信息API修复"
check_function "/opt/claude/mystocks_spec/web/backend/app/core/data_validator.py" "StockDataValidator" "数据验证器实现"
check_function "/opt/claude/mystocks_spec/web/backend/app/core/api_monitoring.py" "APIMonitor" "API监控器实现"

echo ""
echo -e "${YELLOW}5. 检查关键修改${NC}"

# 检查limit参数修复
if grep -q "query_limit = min(limit \* 5, 5000)" /opt/claude/mystocks_spec/web/backend/app/api/data.py; then
    echo -e "${GREEN}✓${NC} limit参数修复已应用"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo -e "${RED}✗${NC} limit参数修复未找到"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
fi

# 检查错误处理增强
if grep -q "is_db_error = any(keyword in error_detail.lower()" /opt/claude/mystocks_spec/web/backend/app/api/data.py; then
    echo -e "${GREEN}✓${NC} 错误处理增强已应用"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo -e "${RED}✗${NC} 错误处理增强未找到"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
fi

# 检查数据验证集成
if grep -q "validation_result = StockDataValidator.validate_stocks_basic" /opt/claude/mystocks_spec/web/backend/app/api/data.py; then
    echo -e "${GREEN}✓${NC} 数据验证已集成到API"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo -e "${RED}✗${NC} 数据验证未集成到API"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
fi

# 检查监控集成
if grep -q "monitor = get_monitor()" /opt/claude/mystocks_spec/web/backend/app/api/data.py; then
    echo -e "${GREEN}✓${NC} 监控已集成到API"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo -e "${RED}✗${NC} 监控未集成到API"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
fi

echo ""
echo "========================================="
echo "验证总结"
echo "========================================="
echo -e "通过: ${GREEN}$CHECKS_PASSED${NC}"
echo -e "失败: ${RED}$CHECKS_FAILED${NC}"
echo "========================================="

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ 所有修复验证通过！${NC}"
    echo ""
    echo "后续步骤："
    echo "1. 启动后端服务: python /opt/claude/mystocks_spec/web/backend/start_server.py"
    echo "2. 运行API测试: bash /opt/claude/mystocks_spec/scripts/test_api_fixes.sh"
    echo "3. 运行数据一致性检查: python3 /opt/claude/mystocks_spec/scripts/test_data_consistency.py"
    exit 0
else
    echo -e "${RED}✗ 有修复未完成，请检查上面的错误${NC}"
    exit 1
fi
