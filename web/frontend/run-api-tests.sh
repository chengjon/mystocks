#!/bin/bash
# Backend API Automation Test Runner
# 自动化测试后端 API 接口

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
if [ -f "${PROJECT_ROOT}/.env" ]; then
  set -a
  # shellcheck disable=SC1090
  source "${PROJECT_ROOT}/.env"
  set +a
fi

: "${BACKEND_PORT:?Missing BACKEND_PORT in .env}"
BACKEND_BASE_URL="http://localhost:${BACKEND_PORT}"

echo "🚀 Starting Backend API Automation Tests..."
echo "=========================================="

# 进入前端目录
cd "$(dirname "$0")"

# 检查后端服务是否运行
echo "📡 Checking backend service..."
if ! curl -s "${BACKEND_BASE_URL}/health" > /dev/null; then
  echo "❌ Backend service is not running!"
  echo "Please start the backend service first:"
  echo "  pm2 start ecosystem.config.js --only mystocks-backend"
  exit 1
fi

echo "✅ Backend service is running"
echo ""

# 检查 OpenAPI JSON 是否可访问
echo "📋 Checking OpenAPI specification..."
if ! curl -s "${BACKEND_BASE_URL}/openapi.json" > /dev/null; then
  echo "❌ OpenAPI JSON is not accessible!"
  exit 1
fi

echo "✅ OpenAPI specification is accessible"
echo ""

# 运行 Playwright 测试
echo "🧪 Running API automation tests..."
echo ""

# 运行测试（显示详细输出）
# 使用项目根目录的 playwright 配置
cd /opt/claude/mystocks_spec
npx playwright test web/frontend/tests/e2e/backend-api-automation.spec.ts \
  --config=playwright.e2e.config.ts \
  --reporter=list \
  --reporter=html \
  "$@"

# 测试结果
TEST_EXIT_CODE=$?

echo ""
echo "=========================================="
if [ $TEST_EXIT_CODE -eq 0 ]; then
  echo "✅ All API tests passed!"
  echo ""
  echo "📊 Test report: test-results/backend-api-automation-report.html"
  echo "📄 Test results: test-results/api-test-results.json"
else
  echo "❌ Some API tests failed!"
  echo ""
  echo "Please check the test report for details."
fi

exit $TEST_EXIT_CODE
