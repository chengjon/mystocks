#!/bin/bash

# MyStocks Web端可用性测试执行脚本
# 用于快速启动和执行完整的可用性测试套件

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TEST_RESULTS_DIR="$PROJECT_ROOT/test-results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# 环境变量
export BASE_URL="${BASE_URL:-http://localhost:}"
export API_URL="${API_URL:-http://localhost:}"
export TEST_TIMEOUT="${TEST_TIMEOUT:-120000}"
export TEST_RETRIES="${TEST_RETRIES:-2}"

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示帮助信息
show_help() {
    cat << EOF
MyStocks Web端可用性测试执行脚本

用法: $0 [选项] [测试类型]

选项:
    -h, --help              显示帮助信息
    -e, --env ENV           指定测试环境 (dev|staging|prod)
    -o, --output DIR        指定输出目录 (默认: ./test-results)
    -f, --force             强制执行测试，即使环境检查失败
    -q, --quick             快速模式（跳过部分耗时测试）
    -v, --verbose           详细输出
    --skip-functional       跳过功能性测试
    --skip-performance      跳过性能测试
    --skip-security         跳过安全性测试
    --skip-usability        跳过用户体验测试
    --skip-data-quality     跳过数据质量测试
    --report-only           仅生成报告，不执行测试

测试类型:
    all                     执行所有测试（默认）
    functional              仅执行功能性测试
    performance             仅执行性能测试
    security                仅执行安全性测试
    usability               仅执行用户体验测试
    data-quality            仅执行数据质量测试

环境变量:
    BASE_URL                前端服务地址 (默认: http://localhost:)
    API_URL                 后端API地址 (默认: http://localhost:)
    TEST_TIMEOUT            测试超时时间（毫秒） (默认: 120000)
    TEST_RETRIES            测试重试次数 (默认: 2)

示例:
    $0                      # 执行所有测试
    $0 functional           # 仅执行功能性测试
    $0 -e staging all       # 在staging环境执行所有测试
    $0 -q --skip-security   # 快速模式，跳过安全测试

EOF
}

# 解析命令行参数
TEST_TYPE="all"
ENVIRONMENT="dev"
OUTPUT_DIR="$TEST_RESULTS_DIR"
FORCE=false
QUICK=false
VERBOSE=false
REPORT_ONLY=false

SKIP_FUNCTIONAL=false
SKIP_PERFORMANCE=false
SKIP_SECURITY=false
SKIP_USABILITY=false
SKIP_DATA_QUALITY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -e|--env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -q|--quick)
            QUICK=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --skip-functional)
            SKIP_FUNCTIONAL=true
            shift
            ;;
        --skip-performance)
            SKIP_PERFORMANCE=true
            shift
            ;;
        --skip-security)
            SKIP_SECURITY=true
            shift
            ;;
        --skip-usability)
            SKIP_USABILITY=true
            shift
            ;;
        --skip-data-quality)
            SKIP_DATA_QUALITY=true
            shift
            ;;
        --report-only)
            REPORT_ONLY=true
            shift
            ;;
        all|functional|performance|security|usability|data-quality)
            TEST_TYPE="$1"
            shift
            ;;
        *)
            log_error "未知参数: $1"
            show_help
            exit 1
            ;;
    esac
done

# 设置环境配置
setup_environment() {
    log_info "设置测试环境: $ENVIRONMENT"

    case "$ENVIRONMENT" in
        dev)
            export BASE_URL="${BASE_URL:-http://localhost:}"
            export API_URL="${API_URL:-http://localhost:}"
            ;;
        staging)
            export BASE_URL="${BASE_URL:-https://staging.mystocks.com}"
            export API_URL="${API_URL:-https://api-staging.mystocks.com}"
            ;;
        prod)
            export BASE_URL="${BASE_URL:-https://mystocks.com}"
            export API_URL="${API_URL:-https://api.mystocks.com}"
            ;;
        *)
            log_error "不支持的环境: $ENVIRONMENT"
            exit 1
            ;;
    esac

    log_info "前端地址: $BASE_URL"
    log_info "API地址: $API_URL"
}

# 创建输出目录
create_output_directory() {
    mkdir -p "$OUTPUT_DIR"
    log_info "输出目录: $OUTPUT_DIR"
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."

    local missing_deps=()

    # 检查Node.js
    if ! command -v node &> /dev/null; then
        missing_deps+=("node")
    fi

    # 检查npm
    if ! command -v npm &> /dev/null; then
        missing_deps+=("npm")
    fi

    # 检查Python
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi

    # 检查Playwright
    if ! command -v npx &> /dev/null || ! npx playwright --version &> /dev/null; then
        log_warning "Playwright未安装，将尝试安装"
        if ! npm list -g @playwright/test &> /dev/null; then
            missing_deps+=("playwright")
        fi
    fi

    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "缺少依赖: ${missing_deps[*]}"
        log_info "请安装缺少的依赖后重试"

        if [ "$FORCE" = false ]; then
            exit 1
        fi
    fi

    log_success "依赖检查完成"
}

# 安装依赖
install_dependencies() {
    log_info "安装测试依赖..."

    # 安装前端依赖
    if [ -f "$PROJECT_ROOT/web/frontend/package.json" ]; then
        log_info "安装前端依赖..."
        cd "$PROJECT_ROOT/web/frontend"
        npm install

        # 安装Playwright浏览器
        if ! npx playwright --version &> /dev/null; then
            log_info "安装Playwright..."
            npm install @playwright/test
            npx playwright install --with-deps
        fi
    fi

    # 安装后端依赖
    if [ -f "$PROJECT_ROOT/web/backend/requirements.txt" ]; then
        log_info "安装后端依赖..."
        cd "$PROJECT_ROOT/web/backend"
        pip install -r requirements.txt
    fi

    cd "$PROJECT_ROOT"
    log_success "依赖安装完成"
}

# 环境健康检查
check_environment_health() {
    log_info "检查环境健康状态..."

    local healthy=true

    # 检查前端服务
    if ! curl -s --max-time 10 "$BASE_URL" > /dev/null; then
        log_error "前端服务不可访问: $BASE_URL"
        healthy=false
    else
        log_success "前端服务正常"
    fi

    # 检查后端服务
    if ! curl -s --max-time 10 "$API_URL/health" > /dev/null; then
        log_error "后端服务不可访问: $API_URL"
        healthy=false
    else
        log_success "后端服务正常"
    fi

    if [ "$healthy" = false ] && [ "$FORCE" = false ]; then
        log_error "环境健康检查失败，使用 -f 参数强制执行"
        exit 1
    fi

    return $([ "$healthy" = true ] && echo 0 || echo 1)
}

# 执行功能性测试
run_functional_tests() {
    if [ "$SKIP_FUNCTIONAL" = true ]; then
        log_info "跳过功能性测试"
        return 0
    fi

    log_info "执行功能性测试..."

    cd "$PROJECT_ROOT"

    # 执行Playwright功能测试
    if [ -f "playwright.config.web.ts" ]; then
        log_info "执行端到端功能测试..."
        npx playwright test \
            --config=playwright.config.web.ts \
            --grep="functional" \
            --reporter=json,html \
            --output-dir="$OUTPUT_DIR/playwright-functional" \
            > "$OUTPUT_DIR/functional-tests.log" 2>&1 || true
    fi

    # 执行API功能测试
    if [ -d "$PROJECT_ROOT/web/backend/tests" ]; then
        log_info "执行API功能测试..."
        cd "$PROJECT_ROOT/web/backend"
        python -m pytest tests/api/ \
            -v \
            --junitxml="$OUTPUT_DIR/api-functional-results.xml" \
            --html="$OUTPUT_DIR/api-functional-report.html" \
            --self-contained-html \
            > "$OUTPUT_DIR/api-functional.log" 2>&1 || true
    fi

    cd "$PROJECT_ROOT"
    log_success "功能性测试完成"
}

# 执行性能测试
run_performance_tests() {
    if [ "$SKIP_PERFORMANCE" = true ]; then
        log_info "跳过性能测试"
        return 0
    fi

    if [ "$QUICK" = true ]; then
        log_info "快速模式：跳过性能测试"
        return 0
    fi

    log_info "执行性能测试..."

    cd "$PROJECT_ROOT"

    # Lighthouse性能审计
    log_info "执行Lighthouse性能审计..."
    npx lighthouse "$BASE_URL" \
        --output=json \
        --output-path="$OUTPUT_DIR/lighthouse-report.json" \
        --chrome-flags="--headless" \
        --quiet \
        > "$OUTPUT_DIR/lighthouse.log" 2>&1 || true

    # API性能测试
    log_info "执行API性能测试..."
    node -e "
        const WebUsabilityTestRunner = require('./scripts/tests/web-usability-runner.js');
        const runner = new WebUsabilityTestRunner();
        runner.runAPIPerformanceTest().then(results => {
            require('fs').writeFileSync('$OUTPUT_DIR/api-performance-results.json', JSON.stringify(results, null, 2));
        }).catch(console.error);
    " > "$OUTPUT_DIR/api-performance.log" 2>&1 || true

    log_success "性能测试完成"
}

# 执行安全性测试
run_security_tests() {
    if [ "$SKIP_SECURITY" = true ]; then
        log_info "跳过安全性测试"
        return 0
    fi

    log_info "执行安全性测试..."

    cd "$PROJECT_ROOT"

    # Python安全扫描
    if [ -d "web/backend" ]; then
        log_info "执行后端安全扫描..."
        cd web/backend

        # 安装bandit（如果未安装）
        if ! command -v bandit &> /dev/null; then
            pip install bandit
        fi

        bandit -r . \
            -f json \
            -o "$OUTPUT_DIR/security-scan-backend.json" \
            > "$OUTPUT_DIR/security-scan-backend.log" 2>&1 || true

        cd ../..
    fi

    # 前端安全检查
    if [ -d "web/frontend" ]; then
        log_info "执行前端安全检查..."
        cd web/frontend

        # npm audit
        npm audit --json > "$OUTPUT_DIR/npm-audit.json" 2>&1 || true

        cd ../..
    fi

    log_success "安全性测试完成"
}

# 执行用户体验测试
run_usability_tests() {
    if [ "$SKIP_USABILITY" = true ]; then
        log_info "跳过用户体验测试"
        return 0
    fi

    log_info "执行用户体验测试..."

    cd "$PROJECT_ROOT"

    # 执行Playwright可用性测试
    if [ -f "playwright.config.web.ts" ]; then
        log_info "执行用户体验测试..."
        npx playwright test \
            --config=playwright.config.web.ts \
            --grep="usability|accessibility|responsive" \
            --reporter=json,html \
            --output-dir="$OUTPUT_DIR/playwright-usability" \
            > "$OUTPUT_DIR/usability-tests.log" 2>&1 || true
    fi

    log_success "用户体验测试完成"
}

# 执行数据质量测试
run_data_quality_tests() {
    if [ "$SKIP_DATA_QUALITY" = true ]; then
        log_info "跳过数据质量测试"
        return 0
    fi

    log_info "执行数据质量测试..."

    cd "$PROJECT_ROOT"

    # 执行数据质量测试脚本
    if [ -d "tests/data_quality" ]; then
        log_info "执行数据质量测试..."
        python -m pytest tests/data_quality/ \
            -v \
            --junitxml="$OUTPUT_DIR/data-quality-results.xml" \
            --html="$OUTPUT_DIR/data-quality-report.html" \
            --self-contained-html \
            > "$OUTPUT_DIR/data-quality.log" 2>&1 || true
    fi

    log_success "数据质量测试完成"
}

# 生成综合报告
generate_comprehensive_report() {
    log_info "生成综合测试报告..."

    cd "$PROJECT_ROOT"

    # 使用Node.js生成报告
    node -e "
        const WebUsabilityTestRunner = require('./scripts/tests/web-usability-runner.js');
        const runner = new WebUsabilityTestRunner();

        // 收集现有测试结果
        const results = {
            timestamp: new Date().toISOString(),
            environment: '$ENVIRONMENT',
            baseUrl: '$BASE_URL',
            apiUrl: '$API_URL'
        };

        require('fs').writeFileSync('$OUTPUT_DIR/comprehensive-test-results.json', JSON.stringify(results, null, 2));
        console.log('✅ 综合测试结果已保存到: $OUTPUT_DIR/comprehensive-test-results.json');
    " > "$OUTPUT_DIR/report-generation.log" 2>&1 || true

    # 创建索引页面
    cat > "$OUTPUT_DIR/index.html" << EOF
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MyStocks Web端可用性测试报告 - $(date)</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; margin-bottom: 30px; }
        .report-section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
        .report-section h2 { color: #555; margin-top: 0; }
        .file-list { list-style: none; padding: 0; }
        .file-list li { margin: 10px 0; }
        .file-list a { color: #007bff; text-decoration: none; padding: 8px 12px; background: #f8f9fa; border-radius: 4px; display: inline-block; }
        .file-list a:hover { background: #e9ecef; }
        .summary { background: #e8f5e8; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .timestamp { color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 MyStocks Web端可用性测试报告</h1>
        <p class="timestamp">生成时间: $(date)</p>
        <p class="timestamp">测试环境: $ENVIRONMENT</p>
        <p class="timestamp">前端地址: $BASE_URL</p>
        <p class="timestamp">API地址: $API_URL</p>

        <div class="summary">
            <h2>📊 测试概览</h2>
            <p>本页面包含了所有测试的详细报告和结果文件。</p>
        </div>

        <div class="report-section">
            <h2>🧪 功能性测试报告</h2>
            <ul class="file-list">
EOF

    # 添加功能性测试报告链接
    if [ -f "$OUTPUT_DIR/playwright-functional/index.html" ]; then
        echo "                <li><a href=\"playwright-functional/index.html\" target=\"_blank\">端到端功能测试报告</a></li>" >> "$OUTPUT_DIR/index.html"
    fi

    if [ -f "$OUTPUT_DIR/api-functional-report.html" ]; then
        echo "                <li><a href=\"api-functional-report.html\" target=\"_blank\">API功能测试报告</a></li>" >> "$OUTPUT_DIR/index.html"
    fi

    # 添加性能测试报告链接
    cat >> "$OUTPUT_DIR/index.html" << EOF
            </ul>
        </div>

        <div class="report-section">
            <h2>⚡ 性能测试报告</h2>
            <ul class="file-list">
EOF

    if [ -f "$OUTPUT_DIR/lighthouse-report.json" ]; then
        echo "                <li><a href=\"lighthouse-report.json\" target=\"_blank\">Lighthouse性能审计报告 (JSON)</a></li>" >> "$OUTPUT_DIR/index.html"
    fi

    if [ -f "$OUTPUT_DIR/api-performance-results.json" ]; then
        echo "                <li><a href=\"api-performance-results.json\" target=\"_blank\">API性能测试报告</a></li>" >> "$OUTPUT_DIR/index.html"
    fi

    # 添加安全性测试报告链接
    cat >> "$OUTPUT_DIR/index.html" << EOF
            </ul>
        </div>

        <div class="report-section">
            <h2>🔒 安全性测试报告</h2>
            <ul class="file-list">
EOF

    if [ -f "$OUTPUT_DIR/security-scan-backend.json" ]; then
        echo "                <li><a href=\"security-scan-backend.json\" target=\"_blank\">后端安全扫描报告</a></li>" >> "$OUTPUT_DIR/index.html"
    fi

    if [ -f "$OUTPUT_DIR/npm-audit.json" ]; then
        echo "                <li><a href=\"npm-audit.json\" target=\"_blank\">前端依赖安全报告</a></li>" >> "$OUTPUT_DIR/index.html"
    fi

    # 添加其他测试报告链接
    cat >> "$OUTPUT_DIR/index.html" << EOF
            </ul>
        </div>

        <div class="report-section">
            <h2>📄 原始日志文件</h2>
            <ul class="file-list">
                <li><a href="functional-tests.log" target="_blank">功能性测试日志</a></li>
                <li><a href="performance-tests.log" target="_blank">性能测试日志</a></li>
                <li><a href="security-tests.log" target="_blank">安全性测试日志</a></li>
                <li><a href="usability-tests.log" target="_blank">用户体验测试日志</a></li>
                <li><a href="data-quality.log" target="_blank">数据质量测试日志</a></li>
            </ul>
        </div>
    </div>
</body>
</html>
EOF

    log_success "综合测试报告已生成: $OUTPUT_DIR/index.html"
}

# 显示测试结果摘要
show_test_summary() {
    log_info "测试执行摘要:"

    echo
    echo "📊 测试结果位置:"
    echo "   主报告: $OUTPUT_DIR/index.html"
    echo "   结果目录: $OUTPUT_DIR"
    echo

    if [ -f "$OUTPUT_DIR/web-usability-test-report.html" ]; then
        echo "📄 详细报告:"
        echo "   HTML报告: $OUTPUT_DIR/web-usability-test-report.html"
        echo "   JSON数据: $OUTPUT_DIR/web-usability-test-results.json"
        echo
    fi

    echo "🔍 查看报告:"
    echo "   在浏览器中打开: file://$OUTPUT_DIR/index.html"
    echo "   或使用命令: open $OUTPUT_DIR/index.html (macOS)"
    echo "           或: xdg-open $OUTPUT_DIR/index.html (Linux)"
    echo

    if [ "$VERBOSE" = true ]; then
        echo "📋 测试配置:"
        echo "   环境: $ENVIRONMENT"
        echo "   前端地址: $BASE_URL"
        echo "   API地址: $API_URL"
        echo "   输出目录: $OUTPUT_DIR"
        echo "   测试超时: ${TEST_TIMEOUT}ms"
        echo "   测试重试: $TEST_RETRIES"
        echo
    fi
}

# 清理临时文件
cleanup() {
    if [ "$VERBOSE" = true ]; then
        log_info "清理临时文件..."
    fi
    # 这里可以添加清理逻辑
}

# 主执行函数
main() {
    log_info "🚀 开始执行MyStocks Web端可用性测试"
    log_info "测试类型: $TEST_TYPE"
    log_info "测试环境: $ENVIRONMENT"

    # 设置trap确保清理
    trap cleanup EXIT

    # 初始化
    setup_environment
    create_output_directory

    # 检查依赖和环境
    check_dependencies

    if [ "$REPORT_ONLY" = false ]; then
        # 根据测试类型执行相应的测试
        case "$TEST_TYPE" in
            all)
                check_environment_health
                run_functional_tests
                run_performance_tests
                run_security_tests
                run_usability_tests
                run_data_quality_tests
                ;;
            functional)
                run_functional_tests
                ;;
            performance)
                run_performance_tests
                ;;
            security)
                run_security_tests
                ;;
            usability)
                run_usability_tests
                ;;
            data-quality)
                run_data_quality_tests
                ;;
            *)
                log_error "不支持的测试类型: $TEST_TYPE"
                exit 1
                ;;
        esac
    fi

    # 生成报告
    generate_comprehensive_report

    # 显示摘要
    show_test_summary

    log_success "🎉 测试执行完成！"
}

# 执行主函数
main "$@"
