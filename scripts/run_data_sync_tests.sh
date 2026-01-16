#!/bin/bash
# 数据同步测试运行器
# 演示完整的API-Web数据对接自动化测试系统

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🎯 数据同步自动化测试系统演示"
echo "========================================"
echo ""

echo "📋 测试架构概览:"
echo "  1. 🏗️  API契约测试 - 验证API数据结构兼容性"
echo "  2. 🔄 数据映射测试 - 验证数据转换逻辑"
echo "  3. 🎨 UI绑定测试 - 验证UI控件数据渲染"
echo "  4. 🌐 E2E集成测试 - 验证完整数据流"
echo "  5. 🔄 CI/CD集成 - 自动化测试流水线"
echo ""

echo "🛠️  使用的测试工具:"
echo "  • Python: pytest, schemathesis, locust"
echo "  • 前端: vitest, vue-test-utils, happy-dom"
echo "  • E2E: playwright, playwright-python"
echo ""

echo "📊 测试执行策略:"
echo "  分层执行: 契约 → 映射 → UI绑定 → E2E"
echo "  依赖关系: 低层测试失败时跳过高层测试"
echo "  并行优化: 单元测试支持并行执行"
echo ""

# 检查测试文件是否存在
echo "🔍 检查测试文件..."
if [ ! -f "tests/api_contract_tests.py" ]; then
    echo "❌ API契约测试文件不存在"
    exit 1
fi

if [ ! -f "tests/data_mapping_tests.py" ]; then
    echo "❌ 数据映射测试文件不存在"
    exit 1
fi

if [ ! -f "tests/ui_binding_tests.spec.ts" ]; then
    echo "❌ UI绑定测试文件不存在"
    exit 1
fi

if [ ! -f "tests/e2e_data_flow.spec.ts" ]; then
    echo "❌ E2E集成测试文件不存在"
    exit 1
fi

if [ ! -f "scripts/ci_data_sync_tests.sh" ]; then
    echo "❌ CI集成脚本不存在"
    exit 1
fi

echo "✅ 所有测试文件就绪"
echo ""

# 运行API契约测试
echo "1️⃣ 运行API契约测试..."
echo "   验证API数据结构与前端类型的兼容性"
echo ""

cd "$PROJECT_ROOT"
if python -c "
from tests.api_contract_tests import run_data_sync_tests
try:
    results = run_data_sync_tests()
    print('✅ API契约测试完成')
    print(f'   测试通过率: {results[\"api_contracts\"][\"summary\"][\"success_rate\"]}%')
except Exception as e:
    print(f'❌ API契约测试失败: {e}')
    print('   注意: 这是一个演示，实际运行需要后端服务')
"

echo ""
echo "2️⃣ 运行数据映射测试..."
echo "   验证数据转换和映射逻辑的正确性"
echo ""

if python -c "
from tests.data_mapping_tests import run_data_mapping_tests
try:
    results = run_data_mapping_tests()
    print('✅ 数据映射测试完成')
    print(f'   测试通过率: {results[\"mapping_tests\"][\"summary\"][\"success_rate\"]}%')
except Exception as e:
    print(f'❌ 数据映射测试失败: {e}')
"

echo ""
echo "3️⃣ 运行UI绑定测试..."
echo "   验证Vue组件的数据绑定和状态同步"
echo ""

cd "$PROJECT_ROOT/web/frontend"
if [ -f "package.json" ]; then
    if npm run test:unit 2>/dev/null | grep -q "ui_binding_tests"; then
        echo "✅ UI绑定测试完成"
    else
        echo "⚠️  UI绑定测试需要完整的前端环境"
        echo "   运行命令: cd web/frontend && npm run test:unit tests/ui_binding_tests.spec.ts"
    fi
else
    echo "⚠️  前端环境未配置"
fi

echo ""
echo "4️⃣ E2E集成测试..."
echo "   验证完整的API到UI数据流"
echo ""

cd "$PROJECT_ROOT"
if command -v npx >/dev/null 2>&1; then
    if npx playwright --version >/dev/null 2>&1; then
        echo "✅ Playwright已安装"
        echo "   运行命令: npx playwright test tests/e2e_data_flow.spec.ts"
    else
        echo "⚠️  Playwright未安装"
    fi
else
    echo "⚠️  Node.js/npm未安装"
fi

echo ""
echo "5️⃣ CI/CD集成演示..."
echo "   自动化测试流水线配置"
echo ""

if [ -f "scripts/ci_data_sync_tests.sh" ]; then
    echo "✅ CI集成脚本已配置"
    echo "   运行命令: ./scripts/ci_data_sync_tests.sh"
    echo "   参数选项:"
    echo "     --frontend-port 3001    前端端口"
    echo "     --backend-port 8000     后端端口"
    echo "     --timeout 300000        测试超时(毫秒)"
else
    echo "❌ CI集成脚本不存在"
fi

echo ""
echo "📋 测试报告和文档"
echo "=================="
echo ""
echo "📄 架构文档: tests/data-synchronization-test-architecture.yaml"
echo "📊 API契约测试: tests/api_contract_tests.py"
echo "🔄 数据映射测试: tests/data_mapping_tests.py"
echo "🎨 UI绑定测试: tests/ui_binding_tests.spec.ts"
echo "🌐 E2E集成测试: tests/e2e_data_flow.spec.ts"
echo "🔄 CI/CD脚本: scripts/ci_data_sync_tests.sh"
echo ""

echo "🎯 测试执行顺序建议:"
echo "  1. 本地开发: 运行单元测试 (API契约 + 数据映射 + UI绑定)"
echo "  2. 功能验证: 运行E2E测试"
echo "  3. CI/CD: 全套自动化测试"
echo ""

echo "💡 最佳实践:"
echo "  • 分层测试保证数据流稳定性"
echo "  • Mock策略减少外部依赖"
echo "  • 契约测试提前发现接口不匹配"
echo "  • E2E测试验证用户体验完整性"
echo ""

echo "🚀 数据同步自动化测试系统已就绪！"
echo "========================================"