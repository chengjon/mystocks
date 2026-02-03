#!/bin/bash
# E2E 测试运行脚本
# Phase 6 E2E Testing

set -e

echo "========================================="
echo "Phase 6 E2E Testing"
echo "========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. 检查服务状态
echo -e "${YELLOW}[1/6] 检查服务状态${NC}"
echo "-------------------------------------"

BACKEND_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:5173"

# 检查后端
if curl -s "${BACKEND_URL}/api/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 后端服务运行中: ${BACKEND_URL}${NC}"
else
    echo -e "${RED}✗ 后端服务未运行${NC}"
    echo "请启动后端: cd web/backend && uvicorn app.main:app --reload"
    exit 1
fi

# 检查前端
if curl -s "${FRONTEND_URL}" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 前端服务运行中: ${FRONTEND_URL}${NC}"
else
    echo -e "${RED}✗ 前端服务未运行${NC}"
    echo "请启动前端: cd web/frontend && npm run dev"
    exit 1
fi

echo ""

# 2. 验证新的 API 端点
echo -e "${YELLOW}[2/6] 验证架构优化 API 端点${NC}"
echo "-------------------------------------"

API_ENDPOINTS=(
    "/api/system/database/health"
    "/api/system/database/pool-stats"
    "/api/system/architecture/layers"
    "/api/system/architecture"
    "/api/system/performance/metrics"
    "/api/system/data-classifications"
    "/api/system/datasources"
    "/api/system/datasources/capabilities"
)

SUCCESS_COUNT=0
FAILED_COUNT=0

for endpoint in "${API_ENDPOINTS[@]}"; do
    echo -n "检查 ${endpoint}... "
    if curl -s "${BACKEND_URL}${endpoint}" | python -m json.tool > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 可访问${NC}"
        ((SUCCESS_COUNT++))
    else
        echo -e "${RED}✗ 无法访问 (可能需要重启服务器)${NC}"
        ((FAILED_COUNT++))
    fi
done

echo ""
echo "API 端点状态: ${SUCCESS_COUNT}/${#API_ENDPOINTS[@]} 成功, ${FAILED_COUNT} 失败"

if [ ${FAILED_COUNT} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  某些端点需要后端服务器重启才能生效${NC}"
    echo "重启命令: cd web/backend && uvicorn app.main:app --reload"
fi

echo ""

# 3. 运行架构优化 E2E 测试 (Python)
echo -e "${YELLOW}[3/6] 运行架构优化 E2E 测试${NC}"
echo "-------------------------------------"

cd /opt/claude/mystocks_phase6_e2e

if [ -f "tests/e2e/test_architecture_optimization_e2e.py" ]; then
    echo "运行测试..."
    pytest tests/e2e/test_architecture_optimization_e2e.py -v --tb=short \
        2>&1 | tee /tmp/arch_e2e_test_results.txt

    # 统计测试结果
    TOTAL=$(grep -E "test_.*PASSED|test_.*FAILED" /tmp/arch_e2e_test_results.txt | wc -l)
    PASSED=$(grep "PASSED" /tmp/arch_e2e_test_results.txt | wc -l)
    FAILED=$(grep "FAILED" /tmp/arch_e2e_test_results.txt | wc -l)

    echo ""
    echo "架构优化 E2E 测试结果:"
    echo "  通过: ${PASSED}"
    echo "  失败: ${FAILED}"
    echo "  总计: ${TOTAL}"
    echo "  通过率: $(echo "scale=2; ${PASSED}*100/${TOTAL}" | bc)%"
else
    echo -e "${RED}✗ 测试文件不存在: tests/e2e/test_architecture_optimization_e2e.py${NC}"
fi

echo ""

# 4. 运行前端 Playwright E2E 测试
echo -e "${YELLOW}[4/6] 运行前端 Playwright E2E 测试${NC}"
echo "-------------------------------------"

if [ -d "web/frontend" ]; then
    cd web/frontend

    echo "检查 Playwright 测试文件..."
    TEST_FILES=$(find tests/e2e -name "test_*.py" -type f | wc -l)
    echo "找到 ${TEST_FILES} 个测试文件"

    echo ""
    echo "运行 Playwright E2E 测试..."
    echo "注意: 这可能需要几分钟..."
    echo ""

    npx playwright test --reporter=list 2>&1 | tee /tmp/playwright_results.txt

    echo ""
    echo "Playwright E2E 测试完成"
else
    echo -e "${RED}✗ 前端目录不存在: web/frontend${NC}"
fi

echo ""

# 5. 生成测试覆盖率报告
echo -e "${YELLOW}[5/6] 生成测试覆盖率报告${NC}"
echo "-------------------------------------"

cd /opt/claude/mystocks_phase6_e2e

echo "生成后端测试覆盖率..."
if pytest --cov=src --cov-report=html --cov-report=json 2>&1 | tee /tmp/coverage_output.txt; then
    if [ -f "coverage.json" ]; then
        COVERAGE=$(python -c "import json; data=json.load(open('coverage.json')); print(f'{data[\"totals\"][\"percent_covered\"]:.2f}%')")
        echo -e "${GREEN}✓ 测试覆盖率: ${COVERAGE}${NC}"

        if [ -f "htmlcov/index.html" ]; then
            echo "覆盖率报告: file://$(pwd)/htmlcov/index.html"
        fi
    fi
else
    echo -e "${RED}✗ 生成覆盖率报告失败${NC}"
fi

echo ""

# 6. 生成综合报告
echo -e "${YELLOW}[6/6] 生成综合测试报告${NC}"
echo "-------------------------------------"

REPORT_FILE="/tmp/phase6_e2e_test_report.txt"

cat > ${REPORT_FILE} << EOF
========================================
Phase 6 E2E Testing Report
========================================
Date: $(date)
Branch: $(git branch --show-current)

========================================
1. 服务状态
========================================
Backend: ${BACKEND_URL} - Running
Frontend: ${FRONTEND_URL} - Running

========================================
2. API 端点验证
========================================
API Endpoint Status:
  Successful: ${SUCCESS_COUNT}/${#API_ENDPOINTS[@]}
  Failed: ${FAILED_COUNT}

Endpoints Tested:
$(for ep in "${API_ENDPOINTS[@]}"; do
    if curl -s "${BACKEND_URL}${ep}" > /dev/null 2>&1; then
        echo "  ✓ ${ep}"
    else
        echo "  ✗ ${ep}"
    fi
done)

========================================
3. 架构优化 E2E 测试
========================================
EOF

if [ -f "/tmp/arch_e2e_test_results.txt" ]; then
    cat >> ${REPORT_FILE} << EOF
  Total Tests: ${TOTAL}
  Passed: ${PASSED}
  Failed: ${FAILED}
  Pass Rate: $(echo "scale=2; ${PASSED}*100/${TOTAL}" | bc)%

Test Results:
$(grep -E "test_.*PASSED|test_.*FAILED" /tmp/arch_e2e_test_results.txt | sed 's/^/  /')

EOF
fi

cat >> ${REPORT_FILE} << EOF
========================================
4. Playwright E2E 测试
========================================
$(if [ -f "/tmp/playwright_results.txt" ]; then
    echo "See: /tmp/playwright_results.txt for detailed results"
else
    echo "  Tests not run"
fi)

========================================
5. 测试覆盖率
========================================
EOF

if [ -f "coverage.json" ]; then
    cat >> ${REPORT_FILE} << EOF
  Overall Coverage: ${COVERAGE}
  HTML Report: file://$(pwd)/htmlcov/index.html
  JSON Report: $(pwd)/coverage.json
EOF
else
    echo "  Coverage report not generated" >> ${REPORT_FILE}
fi

cat >> ${REPORT_FILE} << EOF

========================================
Summary
========================================

Recommendations:
EOF

if [ ${FAILED_COUNT} -gt 0 ]; then
    echo "  ⚠️  Restart backend server to enable new API endpoints" >> ${REPORT_FILE}
fi

if [ ${FAILED} -gt 0 ]; then
    echo "  ⚠️  Fix failing architecture E2E tests" >> ${REPORT_FILE}
fi

python -c "import json; data=json.load(open('coverage.json')); cov=data['totals']['percent_covered']; print(f'  {'✓ Coverage meets target' if cov >= 80 else '⚠️  Coverage below 80% target'}: {cov:.2f}%')" >> ${REPORT_FILE}

cat ${REPORT_FILE}
echo ""
echo -e "${GREEN}✓ 报告已生成: ${REPORT_FILE}${NC}"

echo ""
echo "========================================="
echo "Phase 6 E2E Testing Complete"
echo "========================================="
