#!/bin/bash
# 数据同步自动化测试CI/CD脚本
# 集成API-Web数据对接测试到CI/CD流水线

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 配置
FRONTEND_PORT=${FRONTEND_PORT:-3001}
BACKEND_PORT=${BACKEND_PORT:-8000}
TEST_TIMEOUT=${TEST_TIMEOUT:-300000}  # 5分钟超时

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# 检查服务健康状态
check_service_health() {
    local service_name=$1
    local url=$2
    local max_attempts=${3:-30}
    local attempt=1

    log_info "检查 $service_name 服务健康状态: $url"

    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            log_success "$service_name 服务已就绪"
            return 0
        fi

        log_info "等待 $service_name 服务启动... (尝试 $attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done

    log_error "$service_name 服务启动失败"
    return 1
}

# 启动后端服务
start_backend() {
    log_info "启动后端服务..."

    cd "$PROJECT_ROOT"

    # 检查是否已有运行中的后端服务
    if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_warning "后端服务已在端口 $BACKEND_PORT 运行"
        return 0
    fi

    # 启动后端服务 (这里需要根据实际的启动方式调整)
    # 例如: python -m uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT --reload &
    # 或者使用现有的启动脚本

    if [ -f "scripts/start_backend.sh" ]; then
        bash scripts/start_backend.sh &
        BACKEND_PID=$!
        log_info "后端服务PID: $BACKEND_PID"
    else
        log_warning "未找到后端启动脚本，使用模拟启动"
        # 这里可以添加模拟的后端启动逻辑
    fi

    # 等待后端服务启动
    check_service_health "后端" "http://localhost:$BACKEND_PORT/health" 60
}

# 启动前端服务
start_frontend() {
    log_info "启动前端服务..."

    cd "$PROJECT_ROOT/web/frontend"

    # 检查是否已有运行中的前端服务
    if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_warning "前端服务已在端口 $FRONTEND_PORT 运行"
        return 0
    fi

    # 安装依赖 (如果需要)
    if [ ! -d "node_modules" ]; then
        log_info "安装前端依赖..."
        npm ci
    fi

    # 启动前端服务
    npm run dev -- --port $FRONTEND_PORT --host 0.0.0.0 &
    FRONTEND_PID=$!
    log_info "前端服务PID: $FRONTEND_PID"

    # 等待前端服务启动
    check_service_health "前端" "http://localhost:$FRONTEND_PORT" 60
}

# 停止服务
stop_services() {
    log_info "停止测试服务..."

    # 停止前端服务
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
        log_info "前端服务已停止"
    fi

    # 停止后端服务
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
        log_info "后端服务已停止"
    fi

    # 清理可能残留的进程
    pkill -f "vite" || true
    pkill -f "uvicorn" || true
    pkill -f "node.*dev" || true
}

# 运行API契约测试
run_api_contract_tests() {
    log_info "运行API契约测试..."

    cd "$PROJECT_ROOT"

    if python -m pytest tests/api_contract_tests.py -v --tb=short; then
        log_success "API契约测试通过"
        return 0
    else
        log_error "API契约测试失败"
        return 1
    fi
}

# 运行数据映射测试
run_data_mapping_tests() {
    log_info "运行数据映射测试..."

    cd "$PROJECT_ROOT"

    if python -m pytest tests/data_mapping_tests.py -v --tb=short; then
        log_success "数据映射测试通过"
        return 0
    else
        log_error "数据映射测试失败"
        return 1
    fi
}

# 运行UI绑定测试
run_ui_binding_tests() {
    log_info "运行UI绑定测试..."

    cd "$PROJECT_ROOT/web/frontend"

    if npm run test:unit -- --run tests/ui_binding_tests.spec.ts; then
        log_success "UI绑定测试通过"
        return 0
    else
        log_error "UI绑定测试失败"
        return 1
    fi
}

# 运行E2E集成测试
run_e2e_integration_tests() {
    log_info "运行E2E集成测试..."

    cd "$PROJECT_ROOT"

    if npx playwright test tests/e2e_data_flow.spec.ts --headed=false --timeout=$TEST_TIMEOUT; then
        log_success "E2E集成测试通过"
        return 0
    else
        log_error "E2E集成测试失败"

        # 保存测试截图和报告
        log_info "保存测试工件..."
        mkdir -p test-results
        cp -r playwright-report test-results/ 2>/dev/null || true
        cp -r test-results test-results/ 2>/dev/null || true

        return 1
    fi
}

# 生成测试报告
generate_test_report() {
    log_info "生成测试报告..."

    cd "$PROJECT_ROOT"

    # 创建报告目录
    mkdir -p reports/data-sync-tests

    # 收集测试结果
    cat > reports/data-sync-tests/test-summary.json << EOF
{
  "timestamp": "$(date -Iseconds)",
  "environment": {
    "frontend_url": "http://localhost:$FRONTEND_PORT",
    "backend_url": "http://localhost:$BACKEND_PORT"
  },
  "test_results": {
    "api_contract_tests": $API_CONTRACT_RESULT,
    "data_mapping_tests": $DATA_MAPPING_RESULT,
    "ui_binding_tests": $UI_BINDING_RESULT,
    "e2e_integration_tests": $E2E_INTEGRATION_RESULT
  },
  "overall_status": "$OVERALL_STATUS"
}
EOF

    log_success "测试报告已生成: reports/data-sync-tests/test-summary.json"
}

# 主函数
main() {
    local start_time=$(date +%s)
    local overall_success=true

    log_info "🚀 开始数据同步自动化测试"
    log_info "前端端口: $FRONTEND_PORT, 后端端口: $BACKEND_PORT"

    # 设置清理函数
    trap stop_services EXIT

    # 启动服务
    start_backend
    start_frontend

    # 运行测试套件
    log_info "🎯 执行测试套件..."

    # 1. API契约测试
    if run_api_contract_tests; then
        API_CONTRACT_RESULT=true
    else
        API_CONTRACT_RESULT=false
        overall_success=false
    fi

    # 2. 数据映射测试
    if run_data_mapping_tests; then
        DATA_MAPPING_RESULT=true
    else
        DATA_MAPPING_RESULT=false
        overall_success=false
    fi

    # 3. UI绑定测试
    if run_ui_binding_tests; then
        UI_BINDING_RESULT=true
    else
        UI_BINDING_RESULT=false
        overall_success=false
    fi

    # 4. E2E集成测试 (只有前面的测试都通过才运行)
    if [ "$overall_success" = true ]; then
        if run_e2e_integration_tests; then
            E2E_INTEGRATION_RESULT=true
        else
            E2E_INTEGRATION_RESULT=false
            overall_success=false
        fi
    else
        log_warning "跳过E2E测试，因为前面的测试失败"
        E2E_INTEGRATION_RESULT=false
    fi

    # 计算执行时间
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    # 生成测试报告
    if [ "$overall_success" = true ]; then
        OVERALL_STATUS="PASSED"
        log_success "✅ 所有测试通过!"
        log_success "⏱️  总执行时间: ${duration}秒"
        generate_test_report
        exit 0
    else
        OVERALL_STATUS="FAILED"
        log_error "❌ 部分测试失败"
        log_error "⏱️  总执行时间: ${duration}秒"
        generate_test_report
        exit 1
    fi
}

# 参数解析
while [[ $# -gt 0 ]]; do
    case $1 in
        --frontend-port)
            FRONTEND_PORT="$2"
            shift 2
            ;;
        --backend-port)
            BACKEND_PORT="$2"
            shift 2
            ;;
        --timeout)
            TEST_TIMEOUT="$2"
            shift 2
            ;;
        --help)
            echo "数据同步测试CI/CD脚本"
            echo ""
            echo "用法: $0 [选项]"
            echo ""
            echo "选项:"
            echo "  --frontend-port PORT    前端服务端口 (默认: 3001)"
            echo "  --backend-port PORT     后端服务端口 (默认: 8000)"
            echo "  --timeout MS           测试超时时间(毫秒) (默认: 300000)"
            echo "  --help                 显示帮助信息"
            exit 0
            ;;
        *)
            log_error "未知选项: $1"
            echo "使用 --help 查看帮助信息"
            exit 1
            ;;
    esac
done

# 执行主函数
main