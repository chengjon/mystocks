#!/bin/bash
# API测试运行脚本

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🧪 MyStocks API测试套件"
echo ""

# 检查依赖
echo "🔍 检查测试依赖..."
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}❌ pytest未安装${NC}"
    echo "安装命令: pip install pytest pytest-cov pytest-asyncio requests pyyaml"
    exit 1
fi

echo -e "${GREEN}✅ 依赖检查通过${NC}"
echo ""

# 启动后端服务 (如果未运行)
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  后端服务未运行，正在启动...${NC}"
    cd web/backend
    python -m app.main &
    BACKEND_PID=$!
    cd ../..

    # 等待服务启动
    echo "等待后端服务启动..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ 后端服务已启动${NC}"
            break
        fi
        sleep 1
    done
fi

# 设置环境变量
export API_TEST_BASE_URL="http://localhost:8000"

# 运行测试
echo ""
echo "🚀 开始运行测试..."
echo ""

# 测试类型选择
TEST_TYPE="${1:-all}"

case $TEST_TYPE in
  contract)
    echo "运行契约测试..."
    pytest tests/api/test_api_contracts.py::TestContractVersionAPI -v
    ;;

  market)
    echo "运行Market API测试..."
    pytest tests/api/test_api_contracts.py::TestMarketAPI -v
    ;;

  technical)
    echo "运行Technical API测试..."
    pytest tests/api/test_api_contracts.py::TestTechnicalAPI -v
    ;;

  trade)
    echo "运行Trade API测试..."
    pytest tests/api/test_api_contracts.py::TestTradeAPI -v
    ;;

  consistency)
    echo "运行契约一致性测试..."
    pytest tests/api/test_api_contracts.py::TestContractConsistency -v
    ;;

  performance)
    echo "运行性能测试..."
    pytest tests/api/test_api_contracts.py::TestAPIPerformance -v -m performance
    ;;

  all)
    echo "运行所有测试..."
    pytest tests/api/test_api_contracts.py -v
    ;;

  *)
    echo -e "${RED}❌ 未知的测试类型: $TEST_TYPE${NC}"
    echo ""
    echo "用法: $0 [test_type]"
    echo ""
    echo "可用的测试类型:"
    echo "  contract      - 契约版本管理测试"
    echo "  market        - Market API测试"
    echo "  technical     - Technical API测试"
    echo "  trade         - Trade API测试"
    echo "  consistency   - 契约一致性测试"
    echo "  performance   - 性能测试"
    echo "  all           - 运行所有测试 (默认)"
    exit 1
    ;;
esac

# 测试结果
TEST_RESULT=$?

echo ""
if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ 测试通过${NC}"
else
    echo -e "${RED}❌ 测试失败${NC}"
fi

# 清理
if [ ! -z "$BACKEND_PID" ]; then
    echo "停止后端服务..."
    kill $BACKEND_PID 2>/dev/null || true
fi

exit $TEST_RESULT
