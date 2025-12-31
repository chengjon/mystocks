#!/bin/bash
###############################################################################
# PM2服务管理脚本
#
# 用于管理MyStocks Backend的PM2进程
#
# 使用方法:
#   ./pm2_manager.sh start   - 启动服务
#   ./pm2_manager.sh stop    - 停止服务
#   ./pm2_manager.sh restart - 重启服务
#   ./pm2_manager.sh status  - 查看状态
#   ./pm2_manager.sh logs    - 查看日志
#   ./pm2_manager.sh health  - 健康检查
#
# Author: Backend CLI (Claude Code)
# Date: 2025-12-31
###############################################################################

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目路径
PROJECT_ROOT="/opt/claude/mystocks_phase7_backend"
BACKEND_DIR="$PROJECT_ROOT/web/backend"
PM2_CONFIG="$BACKEND_DIR/ecosystem.config.js"
LOG_DIR="$BACKEND_DIR/logs"

# 服务名称
APP_NAME="mystocks-backend"

# 健康检查URL
HEALTH_URL="http://localhost:8000/health"

###############################################################################
# 辅助函数
###############################################################################

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    print_info "检查环境依赖..."

    # 检查PM2是否安装
    if ! command -v pm2 &> /dev/null; then
        print_error "PM2未安装，请先安装PM2: npm install -g pm2"
        exit 1
    fi

    # 检查Python3
    if ! command -v python3 &> /dev/null; then
        print_error "Python3未安装"
        exit 1
    fi

    # 检查配置文件
    if [ ! -f "$PM2_CONFIG" ]; then
        print_error "PM2配置文件不存在: $PM2_CONFIG"
        exit 1
    fi

    # 创建日志目录
    mkdir -p "$LOG_DIR"

    print_success "环境检查通过"
}

###############################################################################
# 服务管理函数
###############################################################################

start_service() {
    print_info "启动$APP_NAME服务..."

    # 检查服务是否已在运行
    if pm2 describe $APP_NAME &> /dev/null; then
        print_warning "服务已在运行，先停止现有服务"
        stop_service
        sleep 2
    fi

    # 启动服务
    cd "$BACKEND_DIR"
    pm2 start $PM2_CONFIG

    # 等待服务启动
    sleep 3

    # 保存PM2进程列表
    pm2 save

    # 显示状态
    print_success "服务启动完成"
    show_status
}

stop_service() {
    print_info "停止$APP_NAME服务..."

    if ! pm2 describe $APP_NAME &> /dev/null; then
        print_warning "服务未运行"
        return 0
    fi

    # 停止服务
    pm2 stop $PM2_CONFIG

    # 删除服务
    pm2 delete $PM2_CONFIG

    # 保存PM2进程列表
    pm2 save

    print_success "服务已停止"
}

restart_service() {
    print_info "重启$APP_NAME服务..."

    if ! pm2 describe $APP_NAME &> /dev/null; then
        print_warning "服务未运行，将启动服务"
        start_service
        return 0
    fi

    # 重启服务
    pm2 restart $PM2_CONFIG

    # 等待服务重启
    sleep 3

    print_success "服务重启完成"
    show_status
}

reload_service() {
    print_info "零宕机重载$APP_NAME服务..."

    if ! pm2 describe $APP_NAME &> /dev/null; then
        print_warning "服务未运行，将启动服务"
        start_service
        return 0
    fi

    # 重载服务（零宕机）
    pm2 reload $PM2_CONFIG

    print_success "服务重载完成"
    show_status
}

show_status() {
    print_info "服务状态:"
    echo ""
    pm2 list
    echo ""

    # 显示详细状态
    if pm2 describe $APP_NAME &> /dev/null; then
        print_info "服务详情:"
        pm2 describe $APP_NAME
        echo ""
    fi
}

show_logs() {
    local lines=${1:-100}

    print_info "显示最近 $lines 行日志:"
    echo ""

    if pm2 describe $APP_NAME &> /dev/null; then
        pm2 logs $APP_NAME --lines $lines
    else
        print_error "服务未运行"
    fi
}

clear_logs() {
    print_info "清理日志..."

    if pm2 describe $APP_NAME &> /dev/null; then
        pm2 flush $APP_NAME
        print_success "日志已清理"
    else
        print_warning "服务未运行"
    fi
}

###############################################################################
# 健康检查函数
###############################################################################

health_check() {
    print_info "执行健康检查..."

    # 检查PM2进程状态
    if ! pm2 describe $APP_NAME &> /dev/null; then
        print_error "服务未运行"
        return 1
    fi

    # 获取进程状态
    local status=$(pm2 jlist | jq -r ".[] | select(.name==\"$APP_NAME\") | .pm2_env.status" 2>/dev/null)

    if [ "$status" != "online" ]; then
        print_error "服务状态异常: $status"
        return 1
    fi

    # 检查HTTP端点
    if command -v curl &> /dev/null; then
        local http_code=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL || echo "000")

        if [ "$http_code" = "200" ]; then
            print_success "健康检查通过"
            echo ""
            print_info "服务响应:"
            curl -s $HEALTH_URL | jq '.' 2>/dev/null || curl -s $HEALTH_URL
            return 0
        else
            print_error "HTTP健康检查失败 (HTTP $http_code)"
            return 1
        fi
    else
        print_warning "curl未安装，跳过HTTP检查"
        return 0
    fi
}

monitor_service() {
    print_info "启动实时监控 (按Ctrl+Q退出)..."
    pm2 monit
}

###############################################################################
# 主函数
###############################################################################

show_usage() {
    cat << EOF
MyStocks Backend PM2服务管理脚本

使用方法:
  $0 start          启动服务
  $0 stop           停止服务
  $0 restart        重启服务
  $0 reload         零宕机重载
  $0 status         查看状态
  $0 logs [行数]    查看日志 (默认100行)
  $0 clear-logs     清理日志
  $0 health         健康检查
  $0 monitor        实时监控
  $0 help           显示帮助信息

示例:
  $0 start
  $0 logs 50
  $0 health

EOF
}

###############################################################################
# 脚本入口
###############################################################################

main() {
    # 检查环境
    check_requirements

    # 根据参数执行操作
    case "${1:-}" in
        start)
            start_service
            ;;
        stop)
            stop_service
            ;;
        restart)
            restart_service
            ;;
        reload)
            reload_service
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs ${2:-100}
            ;;
        clear-logs)
            clear_logs
            ;;
        health)
            health_check
            ;;
        monitor)
            monitor_service
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            print_error "未知操作: ${1:-}"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
