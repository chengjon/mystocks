#!/bin/bash

################################################################################
# Quickstart Validation Script
#
# Purpose: Verifies that the development environment is properly set up
#          and that all required tools and documentation are available.
#
# Usage: ./scripts/validate_quickstart.sh
#
# Exit Codes:
#   0 - All checks passed
#   1 - One or more checks failed
################################################################################

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# Check result function
check_result() {
    local name="$1"
    local result="$2"
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    if [ "$result" = "0" ]; then
        echo -e "${GREEN}✓${NC} $name"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "${RED}✗${NC} $name"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
}

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  MyStocks 开发环境验证工具                                 ║${NC}"
echo -e "${BLUE}║  Quickstart Validation Script                              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

################################################################################
# Phase 1: Tool Installation Checks
################################################################################

echo -e "${YELLOW}[Phase 1]${NC} 检查必需工具安装..."
echo ""

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    check_result "Python3 (版本: $PYTHON_VERSION)" 0
else
    check_result "Python3" 1
fi

# Check pip
if command -v pip3 &> /dev/null; then
    check_result "pip3" 0
else
    check_result "pip3" 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version 2>&1)
    check_result "Node.js (版本: $NODE_VERSION)" 0
else
    check_result "Node.js" 1
fi

# Check npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version 2>&1)
    check_result "npm (版本: $NPM_VERSION)" 0
else
    check_result "npm" 1
fi

# Check httpie
if command -v http &> /dev/null; then
    check_result "httpie (API 测试工具)" 0
else
    check_result "httpie (可选 - 用于 API 验证)" 0
    echo -e "  ${YELLOW}提示:${NC} 安装命令: pip3 install httpie"
fi

# Check pgcli
if command -v pgcli &> /dev/null; then
    check_result "pgcli (PostgreSQL 客户端)" 0
else
    check_result "pgcli (可选 - 用于数据库验证)" 0
    echo -e "  ${YELLOW}提示:${NC} 安装命令: pip3 install pgcli"
fi

# Check pytest
if python3 -c "import pytest" &> /dev/null; then
    PYTEST_VERSION=$(python3 -c "import pytest; print(pytest.__version__)" 2>&1)
    check_result "pytest (版本: $PYTEST_VERSION)" 0
else
    check_result "pytest" 1
fi

# Check playwright
if python3 -c "import playwright" &> /dev/null; then
    check_result "playwright (集成测试工具)" 0
else
    check_result "playwright (可选 - 用于集成测试)" 0
    echo -e "  ${YELLOW}提示:${NC} 安装命令: pip3 install playwright && playwright install"
fi

echo ""

################################################################################
# Phase 2: Documentation Checks
################################################################################

echo -e "${YELLOW}[Phase 2]${NC} 检查文档完整性..."
echo ""

DOCS_MISSING=0

# Core documentation
CORE_DOCS=(
    "docs/development-process/README.md:开发流程快速入门"
    "docs/development-process/INDEX.md:文档索引"
    "docs/development-process/definition-of-done.md:完成标准定义"
    "docs/development-process/onboarding-checklist.md:新人上手清单"
    "docs/development-process/tool-selection-guide.md:工具选型指南"
    "docs/development-process/tool-comparison.md:工具对比分析"
    "docs/development-process/manual-verification-guide.md:手动验证指南"
    "docs/development-process/troubleshooting.md:故障排查指南"
)

for doc_entry in "${CORE_DOCS[@]}"; do
    IFS=':' read -r doc_path doc_name <<< "$doc_entry"
    if [ -f "$doc_path" ]; then
        check_result "文档: $doc_name" 0
    else
        check_result "文档: $doc_name" 1
        DOCS_MISSING=$((DOCS_MISSING + 1))
    fi
done

# Spec documentation
SPEC_DOCS=(
    "specs/006-web-90-1/contracts/tool-selection-decision-tree.md:工具决策树"
    "specs/006-web-90-1/contracts/api-verification-guide.md:API 验证指南"
)

for doc_entry in "${SPEC_DOCS[@]}"; do
    IFS=':' read -r doc_path doc_name <<< "$doc_entry"
    if [ -f "$doc_path" ]; then
        check_result "规范: $doc_name" 0
    else
        check_result "规范: $doc_name" 1
        DOCS_MISSING=$((DOCS_MISSING + 1))
    fi
done

# UI Inventory
if [ -f "docs/WEB_UI_ELEMENTS_INVENTORY.md" ]; then
    check_result "UI 元素清单" 0
else
    check_result "UI 元素清单" 1
    DOCS_MISSING=$((DOCS_MISSING + 1))
fi

echo ""

################################################################################
# Phase 3: Scripts and Helper Files
################################################################################

echo -e "${YELLOW}[Phase 3]${NC} 检查脚本和辅助文件..."
echo ""

# Check bash aliases
if [ -f "scripts/bash_aliases.sh" ]; then
    check_result "Bash 快捷命令 (bash_aliases.sh)" 0
else
    check_result "Bash 快捷命令 (bash_aliases.sh)" 1
fi

# Check API templates
if [ -f "scripts/api_templates.sh" ]; then
    check_result "API 测试模板 (api_templates.sh)" 0
else
    check_result "API 测试模板 (可选)" 0
fi

# Check SQL templates
if [ -f "scripts/sql_templates.sql" ]; then
    check_result "SQL 查询模板 (sql_templates.sql)" 0
else
    check_result "SQL 查询模板 (可选)" 0
fi

echo ""

################################################################################
# Phase 4: Test Directory Structure
################################################################################

echo -e "${YELLOW}[Phase 4]${NC} 检查测试目录结构..."
echo ""

# Check test directories
TEST_DIRS=(
    "tests/unit:单元测试"
    "tests/integration:集成测试"
    "tests/smoke:冒烟测试"
)

for dir_entry in "${TEST_DIRS[@]}"; do
    IFS=':' read -r dir_path dir_name <<< "$dir_entry"
    if [ -d "$dir_path" ]; then
        check_result "目录: $dir_name ($dir_path)" 0
    else
        check_result "目录: $dir_name ($dir_path)" 1
    fi
done

# Check playwright config
if [ -f "tests/integration/conftest.py" ]; then
    check_result "Playwright 配置 (conftest.py)" 0
else
    check_result "Playwright 配置 (conftest.py)" 1
fi

echo ""

################################################################################
# Phase 5: Example Verification Run
################################################################################

echo -e "${YELLOW}[Phase 5]${NC} 运行示例验证..."
echo ""

# Check if services are running
BACKEND_RUNNING=0
if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    check_result "Backend 服务 (http://localhost:8000)" 0
    BACKEND_RUNNING=1
else
    check_result "Backend 服务 (http://localhost:8000) - 未运行" 1
    echo -e "  ${YELLOW}提示:${NC} 启动命令: cd web/backend && uvicorn app.main:app --reload"
fi

FRONTEND_RUNNING=0
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    check_result "Frontend 服务 (http://localhost:5173)" 0
    FRONTEND_RUNNING=1
else
    check_result "Frontend 服务 (http://localhost:5173) - 未运行" 1
    echo -e "  ${YELLOW}提示:${NC} 启动命令: cd web/frontend && npm run dev"
fi

# If backend is running, try a simple API test
if [ $BACKEND_RUNNING -eq 1 ]; then
    echo ""
    echo -e "${BLUE}测试 API 端点...${NC}"

    # Try to get a token
    if command -v http &> /dev/null; then
        TOKEN_RESPONSE=$(http --ignore-stdin POST http://localhost:8000/api/auth/login username=admin password=admin123 2>&1)
        if echo "$TOKEN_RESPONSE" | grep -q "access_token"; then
            check_result "API 认证测试 (登录成功)" 0

            # Extract token and test an API
            TOKEN=$(echo "$TOKEN_RESPONSE" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
            if [ -n "$TOKEN" ]; then
                API_RESPONSE=$(http --ignore-stdin GET "http://localhost:8000/api/market/v3/dragon-tiger?limit=1" Authorization:"Bearer $TOKEN" 2>&1)
                if echo "$API_RESPONSE" | grep -q "success"; then
                    check_result "API 数据测试 (龙虎榜数据)" 0
                else
                    check_result "API 数据测试 (龙虎榜数据)" 1
                fi
            fi
        else
            check_result "API 认证测试 (登录)" 1
        fi
    else
        echo -e "  ${YELLOW}跳过:${NC} httpie 未安装，无法测试 API"
    fi
fi

echo ""

################################################################################
# Summary Report
################################################################################

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  验证结果总结                                               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "总计检查项: ${BLUE}$TOTAL_CHECKS${NC}"
echo -e "通过: ${GREEN}$PASSED_CHECKS${NC}"
echo -e "失败: ${RED}$FAILED_CHECKS${NC}"
echo ""

if [ $FAILED_CHECKS -eq 0 ]; then
    echo -e "${GREEN}✓ 所有检查通过！开发环境已就绪。${NC}"
    echo ""
    echo -e "${YELLOW}下一步:${NC}"
    echo -e "  1. 阅读文档: ${BLUE}docs/development-process/README.md${NC}"
    echo -e "  2. 完成上手: ${BLUE}docs/development-process/onboarding-checklist.md${NC}"
    echo -e "  3. 开始开发: 使用 5 层验证模型确保质量"
    echo ""
    exit 0
else
    echo -e "${RED}✗ 存在 $FAILED_CHECKS 项失败检查${NC}"
    echo ""
    echo -e "${YELLOW}建议操作:${NC}"

    if [ $DOCS_MISSING -gt 0 ]; then
        echo -e "  • 文档缺失: 检查项目文件完整性"
    fi

    echo -e "  • 安装缺失工具: 参考上方提示安装命令"
    echo -e "  • 启动服务: 确保 backend 和 frontend 服务运行"
    echo -e "  • 查看详细指南: ${BLUE}docs/development-process/INDEX.md${NC}"
    echo ""
    exit 1
fi
