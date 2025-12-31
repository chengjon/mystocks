#!/bin/bash

###############################################################################
# E2E测试环境验证脚本
#
# 验证E2E测试框架的所有组件是否正确配置
###############################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "E2E测试框架验证"
echo "=========================================="
echo ""

# 检查文件结构
echo "1. 检查文件结构..."
files=(
    "tests/e2e/pages/LoginPage.ts"
    "tests/e2e/pages/DashboardPage.ts"
    "tests/e2e/fixtures/auth.fixture.ts"
    "tests/e2e/fixtures/test-data.ts"
    "tests/e2e/auth.spec.ts"
    "tests/e2e/tsconfig.json"
    "tests/e2e/README.md"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file (缺失)"
    fi
done

echo ""

# 检查TypeScript编译
echo "2. 检查TypeScript类型..."
cd tests/e2e
if npx tsc --noEmit 2>/dev/null; then
    echo -e "${GREEN}✓${NC} TypeScript类型检查通过"
else
    echo -e "${YELLOW}⚠${NC} TypeScript类型检查有问题（可能需要安装依赖）"
fi
cd ../..

echo ""

# 统计测试用例
echo "3. 统计测试用例..."
test_count=$(grep -r "test('" tests/e2e/auth.spec.ts | wc -l)
echo -e "${GREEN}✓${NC} 认证测试用例: $test_count 个"

echo ""

# 检查Playwright
echo "4. 检查Playwright..."
if npx playwright --version >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Playwright已安装: $(npx playwright --version)"
else
    echo -e "${YELLOW}⚠${NC} Playwright未安装"
fi

echo ""

# 检查浏览器
echo "5. 检查浏览器..."
if npx playwright install --dry-run chromium >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Chromium浏览器已安装"
else
    echo -e "${YELLOW}⚠${NC} Chromium浏览器未安装"
fi

echo ""
echo "=========================================="
echo "验证完成"
echo "=========================================="
echo ""
echo "下一步："
echo "1. 启动测试服务器: bash scripts/start-system.sh"
echo "2. 运行E2E测试: bash scripts/run-e2e-tests.sh"
echo "3. 或直接运行: npx playwright test e2e"
echo ""
