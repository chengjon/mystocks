#!/bin/bash

# Grafana 自动化配置脚本
# 用于自动添加数据源和创建 Dashboard

echo "=========================================="
echo "  Grafana 自动化配置脚本"
echo "=========================================="
echo ""

# 检查 Playwright 是否已安装
if ! command -v npx &> /dev/null; then
    echo "❌ npx 未安装"
    echo "请先安装 Node.js 和 npm"
    exit 1
fi

echo "✅ 检测到 npx"
echo ""

# 检查 Grafana 是否运行
if ! curl -s http://localhost:3000/api/health | grep -q '"ok"'; then
    echo "❌ Grafana 未运行"
    echo "请先启动 Grafana"
    echo "  docker ps | grep grafana"
    echo "  docker restart mystocks-grafana"
    exit 1
fi

echo "✅ Grafana 正在运行"
echo ""

# 选择运行模式
MODE=${1:-ui}
echo "运行模式: $MODE"
echo ""

case "$MODE" in
    ui)
        echo "🚀 启动 UI 模式 (浏览器模式)..."
        npx playwright test --config=playwright-grafana.config.ts --project=grafana --headed
        ;;
    headless)
        echo "🚀 启动无头模式..."
        npx playwright test --config=playwright-grafana.config.ts --project=grafana
        ;;
    setup)
        echo "🔧 安装 Playwright 浏览器..."
        npx playwright install chromium
        ;;
    report)
        echo "📊 生成测试报告..."
        npx playwright show-report
        ;;
    clean)
        echo "🧹 清理测试结果..."
        rm -rf playwright-tests/grafana/*
        ;;
    *)
        echo "用法: $0 [ui|headless|setup|report|clean]"
        echo ""
        echo "  ui       - 启动 UI 模式 (浏览器自动化)"
        echo "  headless - 启动无头模式"
        echo "  setup    - 安装 Playwright 浏览器"
        echo "  report   - 生成测试报告"
        echo "  clean    - 清理测试结果"
        exit 1
        ;;
esac
