#!/bin/bash

# MyStocks Docker 服务停止脚本
# 停止所有监控基础设施服务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DOCKER_DIR="$(dirname "${BASH_SOURCE[0]}")/.."

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

# 检查 Docker
check_dependencies() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装或未在 PATH 中"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose 未安装或未在 PATH 中"
        exit 1
    fi
}

# 停止服务
stop_services() {
    log_info "停止 MyStocks 监控服务..."

    cd "$DOCKER_DIR"

    if docker-compose -f monitoring-stack.yml ps --services --filter "status=running" | grep -q .; then
        log_info "正在停止运行中的服务..."
        docker-compose -f monitoring-stack.yml down
        log_success "服务已停止"
    else
        log_info "没有运行中的服务"
    fi

    # 可选：清理未使用的容器和网络
    read -p "是否要清理未使用的容器和网络？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "清理未使用的资源..."
        docker system prune -f
        log_success "清理完成"
    fi
}

# 显示状态
show_status() {
    log_info "当前 Docker 容器状态："
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep mystocks || echo "没有 MyStocks 相关容器运行"
    echo
    log_info "数据卷状态："
    docker volume ls | grep mystocks || echo "没有 MyStocks 相关数据卷"
}

# 主函数
main() {
    echo "=================================="
    echo "MyStocks Docker 服务停止脚本"
    echo "=================================="
    echo

    cd "$PROJECT_ROOT"
    check_dependencies
    stop_services
    show_status

    echo
    log_success "MyStocks 监控服务已停止"
    log_info "数据已保留在 Docker 数据卷中，下次启动时会自动恢复"
}

# 运行主函数
main "$@"