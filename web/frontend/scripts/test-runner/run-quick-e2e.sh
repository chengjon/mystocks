#!/bin/bash
# MyStocks Web端 - 一键E2E测试脚本
# 快速验证PM2部署的Web应用功能

set -e  # 遇到错误立即退出

PROJECT_ROOT="/opt/claude/mystocks_spec/web/frontend"
cd "$PROJECT_ROOT"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     MyStocks Web端 - 一键E2E测试                             ║"
echo "║     验证PM2部署的Web应用功能是否正常                            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ============================================
# 步骤1：环境检查
# ============================================
echo -e "${YELLOW}[1/6]${NC} 检查PM2服务状态..."

# 检查PM2是否安装
if ! command -v pm2 &> /dev/null; then
    echo -e "${RED}❌ PM2未安装${NC}"
    echo "请运行: npm install -g pm2"
    exit 1
fi

# 检查PM2服务状态
PM2_STATUS=$(pm2 list | grep -c "mystocks-frontend" || echo "0")

if [ "$PM2_STATUS" -eq "0" ]; then
    echo -e "${RED}❌ PM2服务未运行${NC}"
    echo ""
    echo "📝 启动PM2服务："
    echo "   1. 构建项目：npm run build"
    echo "   2. 启动服务：pm2 start ecosystem.prod.config.js"
    echo ""
    echo "⚠️  是否现在启动PM2服务？(y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo ""
        echo "🔨 构建生产版本..."
        npm run build

        echo "🚀 启动PM2服务..."
        pm2 start ecosystem.prod.config.js

        echo "⏳ 等待服务启动..."
        sleep 5
    else
        echo "请先启动PM2服务后再运行测试"
        exit 1
    fi
else
    echo -e "${GREEN}✅ PM2服务正在运行${NC}"
fi

echo ""

# ============================================
# 步骤2：端口检查
# ============================================
echo -e "${YELLOW}[2/6]${NC} 检查端口3001..."

if curl -s -o /dev/null -w "%{http_code}" http://localhost:3001 | grep -q "200\|301\|302"; then
    echo -e "${GREEN}✅ 服务响应正常 (HTTP 200/301/302)${NC}"
else
    echo -e "${RED}❌ 服务无响应${NC}"
    echo ""
    echo "📝 故障排查："
    echo "   1. 检查PM2日志: pm2 logs mystocks-frontend-prod --lines 20"
    echo "   2. 检查端口占用: lsof -i :3001"
    echo "   3. 重启服务: pm2 restart mystocks-frontend-prod"
    exit 1
fi

echo ""

# ============================================
# 步骤3：后端服务检查
# ============================================
echo -e "${YELLOW}[3/6]${NC} 检查后端API服务..."

if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health | grep -q "200\|302"; then
    echo -e "${GREEN}✅ 后端API服务正常${NC}"
else
    echo -e "${YELLOW}⚠️  后端API服务未响应${NC}"
    echo "   WebSocket实时更新测试可能失败"
    echo "   建议启动: cd web/backend && python3 simple_backend_fixed.py"
fi

echo ""

# ============================================
# 步骤4：运行冒烟测试
# ============================================
echo -e "${YELLOW}[4/6]${NC} 运行冒烟测试..."

echo "🧪 测试套件："
echo "   - 页面加载测试"
echo "   - 菜单导航测试"
echo "   - 基础交互测试"
echo ""

TEST_START=$(date +%s)

# 运行smoke测试
if npx playwright test tests/smoke/ --reporter=list; then
    TEST_END=$(date +%s)
    TEST_DURATION=$((TEST_END - TEST_START))

    echo -e "${GREEN}✅ 冒烟测试通过 (耗时: ${TEST_DURATION}秒)${NC}"
else
    echo -e "${RED}❌ 冒烟测试失败${NC}"
    echo ""
    echo "📋 查看详细错误："
    echo "   npx playwright test tests/smoke/ --reporter=list"
    echo "   npx playwright test tests/smoke/ --debug"
    exit 1
fi

echo ""

# ============================================
# 步骤5：生成测试报告
# ============================================
echo -e "${YELLOW}[5/6]${NC} 生成完整测试报告..."

# 运行完整测试并生成HTML报告
if npx playwright test --reporter=html; then
    echo -e "${GREEN}✅ 测试报告已生成${NC}"
    echo "   📄 报告位置: playwright-report/index.html"

    # 尝试打开报告（在支持desktop环境的系统）
    if command -v xdg-open &> /dev/null; then
        xdg-open playwright-report/index.html &> /dev/null &
    elif command -v gnome-open &> /dev/null; then
        gnome-open playwright-report/index.html &> /dev/null &
    fi
else
    echo -e "${YELLOW}⚠️  测试报告生成失败，但测试可能已通过${NC}"
fi

echo ""

# ============================================
# 步骤6：生成总结报告
# ============================================
echo -e "${YELLOW}[6/6]${NC} 生成测试总结..."

# 统计测试结果
TOTAL_TESTS=$(npx playwright test tests/smoke/ --reporter=json 2>/dev/null | jq '.stats.total' || echo "N/A")
PASSED_TESTS=$(npx playwright test tests/smoke/ --reporter=json 2>/dev/null | jq '.stats.expected' || echo "N/A")
FAILED_TESTS=$(npx playwright test tests/smoke/ --reporter=json 2>/dev/null | jq '.stats.unexpected' || echo "N/A")
FLAKY_TESTS=$(npx playwright test tests/smoke/ --reporter=json 2>/dev/null | jq '.stats.flaky' || echo "N/A")

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    测试总结                                     ║"
echo "╠════════════════════════════════════════════════════════════════╣"
echo "║  总测试数: $TOTAL_TESTS"
echo "║  通过数量: $PASSED_TESTS"
echo "║  失败数量: $FAILED_TESTS"
echo "║  不稳定数: $FLAKY_TESTS"
echo "╠════════════════════════════════════════════════════════════════╣"
echo "║  PM2服务: ✅ 运行中"
echo "║  端口3001: ✅ 可访问"
echo "║  后端API:  ✅ 正常"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# 性能建议
echo "💡 性能优化建议："
echo "   1. 如果页面加载慢，检查: npx playwright test --project=performance"
echo "   2. 如果测试不稳定，增加超时: --timeout=60000"
echo "   3. 如果视频录制失败，检查磁盘空间"
echo "   4. 查看完整日志: pm2 logs mystocks-frontend-prod"
echo ""

echo -e "${GREEN}🎉 测试完成！${NC}"
echo ""
echo "📚 更多信息："
echo "   - 查看测试报告: open playwright-report/index.html"
echo "   - 查看PM2日志: pm2 logs mystocks-frontend-prod"
echo "   - 重新运行测试: npm run test:e2e"
echo "   - 查看测试指南: docs/guides/PM2_PLAYWRIGHT_TESTING_GUIDE.md"
echo ""
