#!/bin/bash
# E2E测试环境管理脚本
# 提供完整的测试环境启动、管理和清理功能
#
# 使用方法:
#   ./scripts/tests/manage-test-env.sh [命令] [选项]
#
# 命令:
#   start     - 启动完整的测试环境
#   stop      - 停止测试环境
#   restart   - 重启测试环境
#   clean     - 清理测试环境和数据
#   status    - 查看测试环境状态
#   logs      - 查看测试环境日志
#   setup     - 仅启动数据库服务
#   frontend  - 仅启动前端服务
#   backend   - 仅启动后端服务
#
# 选项:
#   --with-monitoring  - 包含监控服务 (pgadmin, redis-commander)
#   --with-data-setup  - 包含测试数据生成
#   --headless         - 无头模式运行 (CI环境)
#   --verbose          - 详细输出
#
# 作者: Claude Code
# 创建时间: 2025-11-14

set -e

# 脚本配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.test.yml"
PROJECT_NAME="mystocks-test"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# 帮助信息
show_help() {
    cat << EOF
E2E测试环境管理脚本

使用方法:
    $0 [命令] [选项]

命令:
    start       启动完整的测试环境
    stop        停止测试环境
    restart     重启测试环境
    clean       清理测试环境和数据
    status      查看测试环境状态
    logs        查看测试环境日志
    setup       仅启动数据库服务
    frontend    仅启动前端服务
    backend     仅启动后端服务

选项:
    --with-monitoring    包含监控服务
    --with-data-setup    包含测试数据生成
    --headless          无头模式运行
    --verbose           详细输出
    --help              显示此帮助信息

示例:
    $0 start --with-monitoring
    $0 logs --backend
    $0 clean --force

EOF
}

# 检查依赖
check_dependencies() {
    local missing_deps=()

    if ! command -v docker &> /dev/null; then
        missing_deps+=("docker")
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        missing_deps+=("docker-compose")
    fi

    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_error "缺少必要的依赖: ${missing_deps[*]}"
        log_info "请安装缺少的依赖后重试"
        exit 1
    fi

    # 检查Docker服务
    if ! docker info &> /dev/null; then
        log_error "Docker服务未运行，请启动Docker后重试"
        exit 1
    fi

    log_success "依赖检查通过"
}

# 检查项目结构
check_project_structure() {
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "找不到Docker Compose文件: $COMPOSE_FILE"
        exit 1
    fi

    if [ ! -d "$PROJECT_ROOT/web/frontend" ]; then
        log_error "找不到前端目录: $PROJECT_ROOT/web/frontend"
        exit 1
    fi

    if [ ! -d "$PROJECT_ROOT/web/backend" ]; then
        log_error "找不到后端目录: $PROJECT_ROOT/web/backend"
        exit 1
    fi

    log_success "项目结构检查通过"
}

# 构建Docker镜像
build_images() {
    log_info "构建Docker镜像..."

    local compose_cmd="docker-compose"
    if docker compose version &> /dev/null; then
        compose_cmd="docker compose"
    fi

    if [ "$VERBOSE" = "true" ]; then
        $compose_cmd -f "$COMPOSE_FILE" -p "$PROJECT_NAME" build --no-cache
    else
        $compose_cmd -f "$COMPOSE_FILE" -p "$PROJECT_NAME" build --no-cache > /dev/null 2>&1
    fi

    log_success "Docker镜像构建完成"
}

# 启动服务
start_services() {
    local services="$1"
    local profiles=""

    if [ "$WITH_MONITORING" = "true" ]; then
        profiles="$profiles monitoring"
    fi

    if [ "$WITH_DATA_SETUP" = "true" ]; then
        profiles="$profiles data-setup"
    fi

    log_info "启动服务: ${services:-all}"

    local compose_cmd="docker-compose"
    if docker compose version &> /dev/null; then
        compose_cmd="docker compose"
    fi

    # 设置环境变量
    export COMPOSE_PROJECT_NAME="$PROJECT_NAME"
    export USE_MOCK_DATA=true
    export NODE_ENV=test

    local compose_args="-f $COMPOSE_FILE"
    if [ -n "$profiles" ]; then
        compose_args="$compose_args --profile $profiles"
    fi

    if [ "$VERBOSE" = "true" ]; then
        $compose_cmd $compose_args up -d $services
    else
        $compose_cmd $compose_args up -d $services > /dev/null 2>&1
    fi

    log_success "服务启动完成"
}

# 停止服务
stop_services() {
    local services="$1"

    log_info "停止服务: ${services:-all}"

    local compose_cmd="docker-compose"
    if docker compose version &> /dev/null; then
        compose_cmd="docker compose"
    fi

    export COMPOSE_PROJECT_NAME="$PROJECT_NAME"

    if [ "$VERBOSE" = "true" ]; then
        $compose_cmd -f "$COMPOSE_FILE" -p "$PROJECT_NAME" stop $services
    else
        $compose_cmd -f "$COMPOSE_FILE" -p "$PROJECT_NAME" stop $services > /dev/null 2>&1
    fi

    log_success "服务停止完成"
}

# 清理环境
clean_environment() {
    if [ "$FORCE_CLEAN" != "true" ]; then
        read -p "确定要清理所有测试环境数据吗？这将删除所有容器和卷。[y/N]: " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "取消清理操作"
            return 0
        fi
    fi

    log_info "清理测试环境..."

    local compose_cmd="docker-compose"
    if docker compose version &> /dev/null; then
        compose_cmd="docker compose"
    fi

    export COMPOSE_PROJECT_NAME="$PROJECT_NAME"

    # 停止并删除容器
    if [ "$VERBOSE" = "true" ]; then
        $compose_cmd -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down -v --remove-orphans
    else
        $compose_cmd -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down -v --remove-orphans > /dev/null 2>&1
    fi

    # 清理未使用的镜像
    if [ "$VERBOSE" = "true" ]; then
        docker image prune -f
    else
        docker image prune -f > /dev/null 2>&1
    fi

    log_success "测试环境清理完成"
}

# 检查服务状态
check_status() {
    log_info "检查测试环境状态..."

    local compose_cmd="docker-compose"
    if docker compose version &> /dev/null; then
        compose_cmd="docker compose"
    fi

    export COMPOSE_PROJECT_NAME="$PROJECT_NAME"

    if [ "$VERBOSE" = "true" ]; then
        $compose_cmd -f "$COMPOSE_FILE" -p "$PROJECT_NAME" ps
    else
        $compose_cmd -f "$COMPOSE_FILE" -p "$PROJECT_NAME" ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
    fi

    echo
    log_info "服务访问地址:"
    log_info "  前端: http://localhost:5173"
    log_info "  后端API: http://localhost:8000"
    log_info "  PostgreSQL: localhost:5432"
    log_info "  Redis: localhost:6379"

    if [ "$WITH_MONITORING" = "true" ]; then
        log_info "  pgAdmin: http://localhost:8080 (test@mystocks.com/admin123)"
        log_info "  Redis Commander: http://localhost:8081 (admin/admin123)"
    fi
}

# 查看日志
show_logs() {
    local service="$1"

    log_info "查看服务日志: ${service:-all}"

    local compose_cmd="docker-compose"
    if docker compose version &> /dev/null; then
        compose_cmd="docker compose"
    fi

    export COMPOSE_PROJECT_NAME="$PROJECT_NAME"

    if [ "$HEADLESS" = "true" ]; then
        $compose_cmd -f "$COMPOSE_FILE" -p "$PROJECT_NAME" logs --tail=50 $service
    else
        $compose_cmd -f "$COMPOSE_FILE" -p "$PROJECT_NAME" logs -f $service
    fi
}

# 等待服务就绪
wait_for_services() {
    local timeout=60
    local interval=5
    local elapsed=0

    log_info "等待服务就绪..."

    # 等待PostgreSQL
    while [ $elapsed -lt $timeout ]; do
        if docker exec "$PROJECT_NAME-postgres-test-1" pg_isready -U postgres &> /dev/null; then
            log_success "PostgreSQL已就绪"
            break
        fi
        sleep $interval
        elapsed=$((elapsed + interval))
    done

    if [ $elapsed -ge $timeout ]; then
        log_error "PostgreSQL启动超时"
        return 1
    fi

    # 等待后端API
    elapsed=0
    while [ $elapsed -lt $timeout ]; do
        if curl -f http://localhost:8000/health &> /dev/null; then
            log_success "后端API已就绪"
            break
        fi
        sleep $interval
        elapsed=$((elapsed + interval))
    done

    if [ $elapsed -ge $timeout ]; then
        log_error "后端API启动超时"
        return 1
    fi

    # 等待前端
    elapsed=0
    while [ $elapsed -lt $timeout ]; do
        if curl -f http://localhost:5173 &> /dev/null; then
            log_success "前端已就绪"
            break
        fi
        sleep $interval
        elapsed=$((elapsed + interval))
    done

    if [ $elapsed -ge $timeout ]; then
        log_error "前端启动超时"
        return 1
    fi

    log_success "所有服务就绪"
}

# 解析命令行参数
parse_args() {
    COMMAND=""
    WITH_MONITORING=false
    WITH_DATA_SETUP=false
    HEADLESS=false
    VERBOSE=false
    FORCE_CLEAN=false
    SERVICES=""

    while [[ $# -gt 0 ]]; do
        case $1 in
            start|stop|restart|clean|status|logs|setup|frontend|backend)
                COMMAND="$1"
                shift
                ;;
            --with-monitoring)
                WITH_MONITORING=true
                shift
                ;;
            --with-data-setup)
                WITH_DATA_SETUP=true
                shift
                ;;
            --headless)
                HEADLESS=true
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --force)
                FORCE_CLEAN=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                if [ -z "$COMMAND" ]; then
                    log_error "未知命令: $1"
                    show_help
                    exit 1
                fi
                shift
                ;;
        esac
    done

    if [ -z "$COMMAND" ]; then
        log_error "请指定命令"
        show_help
        exit 1
    fi
}

# 主函数
main() {
    parse_args "$@"

    log_info "E2E测试环境管理 - 命令: $COMMAND"

    # 检查依赖和项目结构
    check_dependencies
    check_project_structure

    case $COMMAND in
        start)
            log_info "启动完整的测试环境..."
            build_images
            start_services ""
            wait_for_services
            check_status
            ;;
        stop)
            log_info "停止测试环境..."
            stop_services ""
            ;;
        restart)
            log_info "重启测试环境..."
            stop_services ""
            sleep 5
            start_services ""
            wait_for_services
            check_status
            ;;
        clean)
            log_info "清理测试环境..."
            stop_services ""
            sleep 5
            clean_environment
            ;;
        status)
            check_status
            ;;
        logs)
            show_logs "$SERVICES"
            ;;
        setup)
            log_info "启动数据库服务..."
            build_images
            start_services "postgres-test redis-test tdengine-test"
            ;;
        frontend)
            log_info "启动前端服务..."
            start_services "frontend-test"
            ;;
        backend)
            log_info "启动后端服务..."
            start_services "backend-test"
            ;;
        *)
            log_error "未知命令: $COMMAND"
            show_help
            exit 1
            ;;
    esac

    log_success "命令执行完成: $COMMAND"
}

# 执行主函数
main "$@"
