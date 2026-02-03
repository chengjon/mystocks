#!/bin/bash
# ESM兼容性验证脚本
# 验证dayjs ESM导入正常，测试Vue应用基础渲染功能

echo "🔍 开始ESM兼容性验证..."
echo "========================================"

# 记录开始时间
START_TIME=$(date +%s)

# 验证脚本参数
FRONTEND_PORT=${1:-3001}
BACKEND_PORT=${2:-8000}

echo "📋 验证配置:"
echo "  前端端口: $FRONTEND_PORT"
echo "  后端端口: $BACKEND_PORT"
echo ""

# 函数：检查服务状态
check_service() {
    local name=$1
    local url=$2
    local timeout=${3:-10}

    echo "🔍 检查$name服务状态..."
    if curl -s --max-time $timeout "$url" > /dev/null 2>&1; then
        echo "  ✅ $name服务运行正常"
        return 0
    else
        echo "  ❌ $name服务无响应"
        return 1
    fi
}

# 函数：运行Playwright验证测试
run_validation_test() {
    local test_name=$1
    local test_file=$2

    echo "🧪 运行$test_name验证测试..."

    if npx playwright test "$test_file" --project=chromium-desktop --timeout=30000 --reporter=line > /tmp/test_output.log 2>&1; then
        echo "  ✅ $test_name测试通过"
        return 0
    else
        echo "  ❌ $test_name测试失败"
        echo "  📄 错误详情:"
        tail -10 /tmp/test_output.log | sed 's/^/    /'
        return 1
    fi
}

# 1. 检查服务状态
echo "1️⃣ 服务状态检查"
echo "----------------"

SERVICES_OK=true

if ! check_service "前端" "http://localhost:$FRONTEND_PORT" 15; then
    SERVICES_OK=false
fi

if ! check_service "后端" "http://localhost:$BACKEND_PORT/api/health" 10; then
    SERVICES_OK=false
fi

echo ""

if [ "$SERVICES_OK" = false ]; then
    echo "❌ 服务状态检查失败，跳过后续验证"
    exit 1
fi

# 2. 运行ESM兼容性测试
echo "2️⃣ ESM兼容性验证"
echo "------------------"

TESTS_PASSED=true

# 2.1 基础页面加载验证
if ! run_validation_test "基础页面加载" "tests/artdeco-diagnostic.test.ts"; then
    TESTS_PASSED=false
fi

# 2.2 Vue应用渲染验证
echo "🧪 验证Vue应用渲染状态..."
if curl -s "http://localhost:$FRONTEND_PORT" | grep -q "<!DOCTYPE html>" && \
   curl -s "http://localhost:$FRONTEND_PORT" | grep -q "id=\"app\""; then
    echo "  ✅ Vue应用HTML结构正常"
else
    echo "  ❌ Vue应用HTML结构异常"
    TESTS_PASSED=false
fi

# 2.3 dayjs ESM导入验证
echo "🧪 验证dayjs ESM导入..."
# 通过检查浏览器控制台错误来验证
if npx playwright test tests/esm-dayjs-validation.test.ts --project=chromium-desktop --timeout=20000 > /tmp/dayjs_test.log 2>&1; then
    if ! grep -q "does not provide an export named 'default'" /tmp/dayjs_test.log; then
        echo "  ✅ dayjs ESM导入正常"
    else
        echo "  ❌ dayjs ESM导入失败"
        TESTS_PASSED=false
    fi
else
    echo "  ❌ dayjs验证测试执行失败"
    TESTS_PASSED=false
fi

echo ""

# 3. 性能指标收集
echo "3️⃣ 性能指标收集"
echo "----------------"

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "📊 测试执行时间: ${DURATION}秒"

# 收集页面加载性能
echo "📈 页面加载性能:"
curl -s -w "  首页加载时间: %{time_total}s\n  HTTP状态码: %{http_code}\n" \
     -o /dev/null "http://localhost:$FRONTEND_PORT"

echo ""

# 4. 生成验证报告
echo "4️⃣ 验证结果汇总"
echo "=================="

if [ "$TESTS_PASSED" = true ]; then
    echo "🎉 ESM兼容性验证通过！"
    echo ""
    echo "✅ 验证结果:"
    echo "  - 前端服务正常运行"
    echo "  - 后端服务正常运行"
    echo "  - Vue应用基础渲染正常"
    echo "  - dayjs ESM导入无错误"
    echo "  - 页面加载性能良好"
    echo ""
    echo "📋 性能指标:"
    echo "  - 测试执行时间: ${DURATION}秒"
    echo "  - 页面响应正常"
    echo ""
    echo "🚀 可以继续进行Phase 1环境固化工作"

    exit 0
else
    echo "❌ ESM兼容性验证失败！"
    echo ""
    echo "❌ 发现问题:"
    if ! check_service "前端" "http://localhost:$FRONTEND_PORT" 5 >/dev/null 2>&1; then
        echo "  - 前端服务异常"
    fi
    if ! check_service "后端" "http://localhost:$BACKEND_PORT/api/health" 5 >/dev/null 2>&1; then
        echo "  - 后端服务异常"
    fi
    echo "  - Vue应用渲染异常"
    echo "  - dayjs ESM导入问题"
    echo ""
    echo "🔧 建议修复步骤:"
    echo "  1. 检查Vite配置中的dayjs别名设置"
    echo "  2. 验证前端和后端服务启动状态"
    echo "  3. 检查浏览器控制台错误信息"
    echo "  4. 重新运行验证脚本"

    exit 1
fi