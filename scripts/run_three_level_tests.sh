#!/bin/bash

# MyStocks三层测试架构执行脚本
# 实现：单元测试 -> 集成测试 -> E2E测试

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

# 第一层：Mock函数单元测试（快速验证）
run_unit_tests() {
    log_info "开始执行第一层测试：Mock函数单元测试"
    
    # 创建测试结果目录
    mkdir -p reports/unit
    
    # 运行单元测试
    python -m pytest tests/unit/ -v --tb=short --cov=src --cov-report=term-missing --junitxml=reports/unit/test-results.xml
    
    if [ $? -eq 0 ]; then
        log_success "单元测试执行成功"
    else
        log_error "单元测试执行失败"
        return 1
    fi
}

# 第二层：页面集成测试（核心重点）
run_integration_tests() {
    log_info "开始执行第二层测试：页面集成测试"
    
    # 创建测试结果目录
    mkdir -p reports/integration
    
    # 设置环境变量以使用Mock数据
    export USE_MOCK_DATA=true
    
    # 运行集成测试
    python -m pytest tests/integration/ -v --tb=short --cov=src --cov-report=term-missing --junitxml=reports/integration/test-results.xml
    
    if [ $? -eq 0 ]; then
        log_success "集成测试执行成功"
    else
        log_error "集成测试执行失败"
        return 1
    fi
}

# 第三层：完整E2E流程测试（用户场景）
run_e2e_tests() {
    log_info "开始执行第三层测试：完整E2E流程测试"
    
    # 创建测试结果目录
    mkdir -p reports/e2e
    
    # 设置Playwright测试环境
    export PLAYWRIGHT_TEST_BASE_URL=${PLAYWRIGHT_TEST_BASE_URL:-"http://localhost:8000"}
    
    # 检查后端服务是否运行
    if ! curl -s --connect-timeout 5 $PLAYWRIGHT_TEST_BASE_URL/api/stocks/health > /dev/null; then
        log_warning "后端服务未运行，尝试启动..."
        # 启动后端服务
        cd web/backend
        python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
        BACKEND_PID=$!
        cd ../..
        
        # 等待服务启动
        sleep 10
        
        # 检查服务是否成功启动
        if ! curl -s --connect-timeout 5 $PLAYWRIGHT_TEST_BASE_URL/api/stocks/health > /dev/null; then
            log_error "无法启动后端服务，跳过E2E测试"
            return 1
        fi
    fi
    
    # 运行Playwright E2E测试 - 并行5个浏览器
    log_info "运行E2E测试 - 并行5个浏览器"
    
    # 并行运行不同浏览器的测试
    (
        log_info "启动Chromium测试..."
        PLAYWRIGHT_TEST_BASE_URL=$PLAYWRIGHT_TEST_BASE_URL python -m pytest tests/e2e/ -v --browser="chromium" --tb=short --junitxml=reports/e2e/test-results-chromium.xml &
        
        log_info "启动Firefox测试..."
        PLAYWRIGHT_TEST_BASE_URL=$PLAYWRIGHT_TEST_BASE_URL python -m pytest tests/e2e/ -v --browser="firefox" --tb=short --junitxml=reports/e2e/test-results-firefox.xml &
        
        log_info "启动WebKit测试..."
        PLAYWRIGHT_TEST_BASE_URL=$PLAYWRIGHT_TEST_BASE_URL python -m pytest tests/e2e/ -v --browser="webkit" --tb=short --junitxml=reports/e2e/test-results-webkit.xml &
        
        # 等待所有测试完成
        wait
    )
    
    # 运行测试分片
    log_info "运行测试分片..."
    for shard in {1..5}; do
        PLAYWRIGHT_TEST_BASE_URL=$PLAYWRIGHT_TEST_BASE_URL python -m pytest tests/e2e/ --shard $shard/5 -v --tb=short &
    done
    wait
    
    if [ $? -eq 0 ]; then
        log_success "E2E测试执行成功"
    else
        log_error "E2E测试执行失败"
        return 1
    fi
    
    # 终止后端服务
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
}

# 生成测试报告
generate_test_report() {
    log_info "生成测试报告..."
    
    # 合并测试结果
    mkdir -p reports
    echo "# MyStocks 测试报告" > reports/test-report.md
    echo "" >> reports/test-report.md
    echo "## 测试执行摘要" >> reports/test-report.md
    echo "- 单元测试: $(if [ -f reports/unit/test-results.xml ]; then echo "✅"; else echo "❌"; fi)" >> reports/test-report.md
    echo "- 集成测试: $(if [ -f reports/integration/test-results.xml ]; then echo "✅"; else echo "❌"; fi)" >> reports/test-report.md
    echo "- E2E测试: $(if [ -f reports/e2e/test-results-chromium.xml ]; then echo "✅"; else echo "❌"; fi)" >> reports/test-report.md
    echo "" >> reports/test-report.md
    
    echo "## 测试覆盖率" >> reports/test-report.md
    if [ -f reports/coverage/index.html ]; then
        echo "- 详细覆盖率报告: [coverage/index.html](./reports/coverage/index.html)" >> reports/test-report.md
    fi
    echo "" >> reports/test-report.md
    
    echo "## 执行时间" >> reports/test-report.md
    echo "- 开始时间: $(date -d @"$(stat -c %Y reports/unit/test-results.xml 2>/dev/null || date +%s)" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "$(date "+%Y-%m-%d %H:%M:%S")")" >> reports/test-report.md
    echo "- 完成时间: $(date "+%Y-%m-%d %H:%M:%S")" >> reports/test-report.md
    echo "" >> reports/test-report.md
    
    log_success "测试报告生成完成"
}

# 性能测试
run_performance_tests() {
    log_info "运行性能测试..."
    
    # 创建性能测试目录
    mkdir -p reports/performance
    
    # 基准测试
    log_info "运行基准测试..."
    python -c "
import time
import sys
sys.path.insert(0, '.')
from src.database.database_service import DatabaseService

# 简单性能测试
start_time = time.time()
db_service = DatabaseService()
init_time = time.time() - start_time

print(f'数据库服务初始化时间: {init_time:.4f}秒')

# 简单查询性能测试
start_time = time.time()
result = db_service.get_monitoring_summary()
query_time = time.time() - start_time

print(f'监控摘要查询时间: {query_time:.4f}秒')
" > reports/performance/baseline.txt 2>&1 || true

    log_success "性能测试完成"
}

# 主函数
main() {
    log_info "开始执行MyStocks三层测试架构"
    
    # 创建必要的目录
    mkdir -p reports/unit reports/integration reports/e2e reports/performance
    
    # 执行三层测试
    run_unit_tests
    unit_tests_result=$?
    
    run_integration_tests
    integration_tests_result=$?
    
    run_e2e_tests
    e2e_tests_result=$?
    
    # 运行性能测试
    run_performance_tests
    
    # 生成报告
    generate_test_report
    
    # 汇总结果
    log_info "测试执行完成汇总:"
    log_info "  单元测试: $([ $unit_tests_result -eq 0 ] && echo 'PASSED' || echo 'FAILED')"
    log_info "  集成测试: $([ $integration_tests_result -eq 0 ] && echo 'PASSED' || echo 'FAILED')"
    log_info "  E2E测试: $([ $e2e_tests_result -eq 0 ] && echo 'PASSED' || echo 'FAILED')"
    
    if [ $unit_tests_result -eq 0 ] && [ $integration_tests_result -eq 0 ] && [ $e2e_tests_result -eq 0 ]; then
        log_success "所有测试执行成功！"
        exit 0
    else
        log_error "部分测试执行失败！"
        exit 1
    fi
}

# 如果脚本被直接运行
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi