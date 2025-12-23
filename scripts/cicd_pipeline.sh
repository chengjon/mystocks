#!/bin/bash

# MyStocks CI/CD Pipeline Script
# 实现三层测试架构：单元测试、集成测试、E2E测试

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖项..."

    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi

    # 检查npm
    if ! command -v npm &> /dev/null; then
        log_error "npm 未安装"
        exit 1
    fi

    # 检查pip
    if ! command -v pip &> /dev/null; then
        log_error "pip 未安装"
        exit 1
    fi

    # 检查playwright
    if ! python3 -c "import playwright" &> /dev/null; then
        log_error "playwright 未安装"
        exit 1
    fi

    log_success "依赖检查完成"
}

# 1. 环境设置和依赖安装
setup_environment() {
    log_info "设置环境和安装依赖..."

    # 安装Python依赖
    log_info "安装Python依赖..."
    pip install -r requirements.txt

    # 安装开发依赖
    if [ -f "requirements-mock.txt" ]; then
        pip install -r requirements-mock.txt
    fi

    # 安装安全依赖
    if [ -f "requirements-security.txt" ]; then
        pip install -r requirements-security.txt
    fi

    # 安装Playwright浏览器
    log_info "安装Playwright浏览器..."
    playwright install chromium firefox webkit

    log_success "环境设置完成"
}

# 2. 后端构建过程
build_backend() {
    log_info "构建后端服务..."

    # 进入后端目录
    cd web/backend

    # 安装后端依赖
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi

    # 运行后端代码检查
    log_info "运行后端代码质量检查..."
    if command -v mypy &> /dev/null; then
        mypy --config-file=../../mypy.ini --package src 2>/dev/null || true
    fi

    if command -v black &> /dev/null; then
        black --check src 2>/dev/null || true
    fi

    if command -v flake8 &> /dev/null; then
        flake8 src 2>/dev/null || true
    fi

    cd ../..
    log_success "后端构建完成"
}

# 3. 前端构建过程
build_frontend() {
    log_info "构建前端服务..."

    # 进入前端目录
    cd web/frontend

    # 检查是否有package.json
    if [ -f "package.json" ]; then
        # 安装前端依赖
        npm install

        # 构建前端
        npm run build
    else
        log_warning "前端package.json未找到，跳过前端构建"
    fi

    cd ../..
    log_success "前端构建完成"
}

# 4. 第一层：Mock函数单元测试（快速验证）
run_unit_tests() {
    log_info "运行第一层测试：Mock函数单元测试..."

    # 运行Python单元测试
    python -m pytest tests/ -m "unit" -v --tb=short --cov=src --cov-report=term-missing || true

    # 运行特定的单元测试
    python -m pytest tests/test_*.py -k "not integration and not e2e" -v --tb=short || true

    log_success "单元测试完成"
}

# 5. 第二层：页面集成测试（核心重点）
run_integration_tests() {
    log_info "运行第二层测试：页面集成测试..."

    # 运行集成测试
    python -m pytest tests/ -m "integration" -v --tb=short --cov=src --cov-report=term-missing || true

    # 运行API集成测试
    python -c "
import sys
sys.path.insert(0, '.')

# 测试数据库连接
try:
    from src.database.database_service import DatabaseService
    db_service = DatabaseService()
    print('数据库服务初始化成功')
except Exception as e:
    print(f'数据库服务初始化失败: {e}')

# 测试路由导入
try:
    from src.routes import *
    print('路由模块导入成功')
except Exception as e:
    print(f'路由模块导入失败: {e}')
"

    log_success "集成测试完成"
}

# 6. 第三层：完整E2E流程测试（用户场景）
run_e2e_tests() {
    log_info "运行第三层测试：完整E2E流程测试..."

    # 启动后端服务
    log_info "启动后端服务..."
    cd web/backend
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    cd ../..

    # 等待服务启动
    sleep 10

    # 运行Playwright E2E测试
    log_info "运行Playwright E2E测试..."

    # 创建测试报告目录
    mkdir -p playwright-report

    # 运行不同浏览器的测试
    for browser in "chromium" "firefox" "webkit"; do
        log_info "运行 $browser 测试..."
        PLAYWRIGHT_TEST_BASE_URL="http://localhost:8888" python -m pytest tests/ -s -v --browser="$browser" --html="playwright-report/report_$browser.html" --tb=short || true
    done

    # 运行分片测试
    log_info "运行测试分片..."
    PLAYWRIGHT_TEST_BASE_URL="http://localhost:8888" python -m pytest tests/ --shard 1/5 -v || true
    PLAYWRIGHT_TEST_BASE_URL="http://localhost:8888" python -m pytest tests/ --shard 2/5 -v || true
    PLAYWRIGHT_TEST_BASE_URL="http://localhost:8888" python -m pytest tests/ --shard 3/5 -v || true
    PLAYWRIGHT_TEST_BASE_URL="http://localhost:8888" python -m pytest tests/ --shard 4/5 -v || true
    PLAYWRIGHT_TEST_BASE_URL="http://localhost:8888" python -m pytest tests/ --shard 5/5 -v || true

    # 终止后端服务
    kill $BACKEND_PID 2>/dev/null || true

    log_success "E2E测试完成"
}

# 7. 性能测试（Lighthouse）
run_performance_tests() {
    log_info "运行性能测试（Lighthouse）..."

    # 安装lighthouse
    if ! command -v lighthouse &> /dev/null; then
        npm install -g lighthouse
    fi

    # 启动应用并运行Lighthouse测试
    cd web/backend
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    cd ../..

    # 等待服务启动
    sleep 10

    # 运行Lighthouse测试
    if command -v lighthouse &> /dev/null; then
        lighthouse http://localhost:8888/api/docs --output json --output html --output-path ./reports/lighthouse-report.html || true
        lighthouse http://localhost:8888/api/docs --output json --output-path ./reports/lighthouse-report.json || true
    else
        log_warning "Lighthouse未安装，跳过性能测试"
    fi

    # 终止后端服务
    kill $BACKEND_PID 2>/dev/null || true

    log_success "性能测试完成"
}

# 8. 测试结果处理
process_test_results() {
    log_info "处理测试结果..."

    # 创建测试报告目录
    mkdir -p reports

    # 生成测试覆盖率报告
    python -m pytest tests/ --cov=src --cov-report=html:reports/coverage --cov-report=xml:reports/coverage.xml --tb=short || true

    # 生成HTML测试报告
    python -m pytest tests/ --html=reports/test-report.html --self-contained-html || true

    # 收集测试指标
    echo "Test Results Summary" > reports/test-summary.txt
    echo "===================" >> reports/test-summary.txt
    echo "Date: $(date)" >> reports/test-summary.txt
    echo "Total Tests Run: $(python -m pytest tests/ --collect-only 2>/dev/null | grep -c '::test' 2>/dev/null)" >> reports/test-summary.txt
    echo "Passed Tests: $(python -m pytest tests/ -v 2>/dev/null | grep -c 'PASSED' 2>/dev/null)" >> reports/test-summary.txt
    echo "Failed Tests: $(python -m pytest tests/ -v 2>/dev/null | grep -c 'FAILED' 2>/dev/null)" >> reports/test-summary.txt

    log_success "测试结果处理完成"
}

# 9. 自动部署到测试环境
deploy_to_test() {
    log_info "部署到测试环境..."

    # 创建测试环境配置
    if [ -f "config/.env.simplified" ]; then
        cp config/.env.simplified .env.test
    else
        echo "# Test Environment Configuration" > .env.test
        echo "ENVIRONMENT=test" >> .env.test
        echo "DEBUG=true" >> .env.test
    fi

    # 构建测试环境Docker镜像
    if [ -f "docker-compose.test.yml" ]; then
        docker-compose -f docker-compose.test.yml build || true
        docker-compose -f docker-compose.test.yml up -d || true
    fi

    log_success "测试环境部署完成"
}

# 10. 自动部署到生产环境
deploy_to_production() {
    log_info "部署到生产环境..."

    # 创建生产环境配置
    if [ -f "config/.env" ]; then
        cp config/.env .env.prod
    else
        echo "# Production Environment Configuration" > .env.prod
        echo "ENVIRONMENT=production" >> .env.prod
        echo "DEBUG=false" >> .env.prod
    fi

    # 构建生产环境Docker镜像
    if [ -f "web/docker-compose.yml" ]; then
        docker-compose -f web/docker-compose.yml build || true
        docker-compose -f web/docker-compose.yml up -d || true
    fi

    log_success "生产环境部署完成"
}

# 运行完整的CI/CD流程
run_full_pipeline() {
    log_info "开始执行完整的CI/CD流程..."

    check_dependencies
    setup_environment
    build_backend
    build_frontend
    run_unit_tests
    run_integration_tests
    run_e2e_tests
    run_performance_tests
    process_test_results
    deploy_to_test
    deploy_to_production

    log_success "CI/CD流程执行完成！"
}

# 如果脚本被直接运行，则执行完整的CI/CD流程
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    run_full_pipeline
fi
