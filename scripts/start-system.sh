#!/bin/bash
#===============================================================================
# MyStocks 系统快速启动脚本
#
# 功能：
#   - 启动后端 API 服务 (PM2)
#   - 启动前端 Web 服务
#   - 启动 lnav 日志监控
#   - 运行 API 契约测试
#
# 使用方法:
#   ./scripts/start-system.sh --all      # 启动所有服务
#   ./scripts/start-system.sh --api      # 只启动 API
#   ./scripts/start-system.sh --web      # 只启动 Web
#   ./scripts/start-system.sh --test     # 运行测试
#   ./scripts/start-system.sh --tmux     # 创建 tmux 会话
#===============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
PROJECT_DIR="/opt/claude/mystocks_spec"
BACKEND_DIR="$PROJECT_DIR/web/backend"
FRONTEND_DIR="$PROJECT_DIR/web/frontend"
API_PORT=8000
WEB_PORT=5173

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $(date '+%H:%M:%S') - $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $(date '+%H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%H:%M:%S') - $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $(date '+%H:%M:%S') - $1"
}

# 检查依赖
check_dependencies() {
    log_step "检查依赖..."

    local missing=()

    command -v pm2 &> /dev/null || missing+=("pm2")
    command -v tmux &> /dev/null || missing+=("tmux")
    command -v lnav &> /dev/null || missing+=("lnav")
    command -v pytest &> /dev/null || missing+=("pytest")

    if [ ${#missing[@]} -ne 0 ]; then
        log_warn "缺少依赖: ${missing[*]}"
        echo "请安装: npm install -g pm2 && apt install tmux lnav"
        exit 1
    fi

    log_info "所有依赖已安装"
}

# 启动 API 服务
start_api() {
    log_step "启动后端 API 服务..."

    cd "$BACKEND_DIR"

    # 检查是否已启动
    if pm2 status | grep -q "mystocks-api"; then
        log_warn "API 服务已在运行"
        pm2 restart mystocks-api
    else
        pm2 start ecosystem.config.js --only mystocks-api || {
            # 如果 ecosystem config 不存在，使用直接启动
            pm2 start uvicorn --name "mystocks-api" -- \
                app.main:app --host 0.0.0.0 --port $API_PORT || {
                log_error "启动 API 失败"
                return 1
            }
        }
    fi

    log_info "API 服务已启动 (端口: $API_PORT)"
}

# 启动 Web 服务
start_web() {
    log_step "启动前端 Web 服务..."

    cd "$FRONTEND_DIR"

    if pm2 status | grep -q "mystocks-web"; then
        log_warn "Web 服务已在运行"
        pm2 restart mystocks-web
    else
        npm run dev -- --host 0.0.0.0 --port $WEB_PORT &> /dev/null &
        pm2 start npm --name "mystocks-web" -- \
            run dev --prefix "$FRONTEND_DIR" || {
            log_error "启动 Web 失败"
            return 1
        }
    fi

    log_info "Web 服务已启动 (端口: $WEB_PORT)"
}

# 创建 tmux 会话
create_tmux_session() {
    log_step "创建 tmux 会话..."

    local session_name="mystocks-dev"

    # 检查会话是否存在
    if tmux has-session -t "$session_name" 2>/dev/null; then
        log_warn "会话 $session_name 已存在"
        tmux kill-session -t "$session_name" 2>/dev/null || true
    fi

    # 创建新会话
    tmux new-session -d -s "$session_name" -x 120 -y 40

    # 窗口0: API 服务
    tmux rename-window -t "$session_name:0" 'API'
    tmux send-keys -t "$session_name:0" "cd $BACKEND_DIR && pm2 monit" Enter

    # 窗口1: Web 服务
    tmux new-window -t "$session_name" -n 'Web'
    tmux send-keys -t "$session_name:1" "cd $FRONTEND_DIR && npm run dev" Enter

    # 窗口2: 日志监控
    tmux new-window -t "$session_name" -n 'Logs'
    tmux send-keys -t "$session_name:2" "cd $PROJECT_DIR && lnav -q logs/" Enter

    # 窗口3: 测试
    tmux new-window -t "$session_name" -n 'Test'
    tmux send-keys -t "$session_name:3" "cd $BACKEND_DIR" Enter

    # 设置布局
    tmux select-layout -t "$session_name" even-horizontal

    log_info "tmux 会话已创建: $session_name"
    echo ""
    echo "使用以下命令进入会话:"
    echo "  tmux attach-session -t $session_name"
    echo ""
    echo "窗口说明:"
    echo "  [0] API - API 服务监控"
    echo "  [1] Web - Web 开发服务器"
    echo "  [2] Logs - 日志监控 (lnav)"
    echo "  [3] Test - 测试终端"
}

# 运行 API 测试
run_tests() {
    log_step "运行 API 测试..."

    cd "$BACKEND_DIR"

    # 检查服务是否可用
    if ! curl -s http://localhost:$API_PORT/health > /dev/null; then
        log_error "API 服务不可用，请先启动服务"
        return 1
    fi

    # 运行契约测试
    log_info "运行契约测试..."
    pytest "$PROJECT_DIR/tests/api/test_contract_consistency.py" -v --tb=short || {
        log_warn "部分测试失败，请检查日志"
    }

    # 运行 API 端点测试
    log_info "运行 API 端点测试..."
    pytest "$PROJECT_DIR/tests/api/" -v --api-base-url="http://localhost:$API_PORT" -x || {
        log_error "测试失败"
        return 1
    }

    log_info "测试完成"
}

# 生成 API 目录
generate_catalog() {
    log_step "生成 API 目录..."

    cd "$BACKEND_DIR"
    python scripts/generate_api_catalog.py

    log_info "API 目录已生成: docs/api/catalog.md"
}

# 检查服务状态
check_status() {
    log_step "检查服务状态..."

    echo ""
    echo "=== PM2 服务状态 ==="
    pm2 status

    echo ""
    echo "=== API 健康检查 ==="
    if curl -s http://localhost:$API_PORT/health | grep -q "ok"; then
        echo -e "${GREEN}API 服务正常${NC}"
    else
        echo -e "${RED}API 服务异常${NC}"
    fi

    echo ""
    echo "=== tmux 会话 ==="
    tmux list-sessions 2>/dev/null || echo "无活动会话"
}

# 停止所有服务
stop_all() {
    log_step "停止所有服务..."

    pm2 stop mystocks-api mystocks-web 2>/dev/null || true
    pm2 delete mystocks-api mystocks-web 2>/dev/null || true

    # 停止 tmux 会话
    tmux kill-session -t mystocks-dev 2>/dev/null || true

    log_info "所有服务已停止"
}

# 显示帮助
show_help() {
    echo "MyStocks 系统启动脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --all      启动所有服务"
    echo "  --api      只启动 API 服务"
    echo "  --web      只启动 Web 服务"
    echo "  --tmux     创建 tmux 开发会话"
    echo "  --test     运行 API 测试"
    echo "  --catalog  生成 API 目录"
    echo "  --status   检查服务状态"
    echo "  --stop     停止所有服务"
    echo "  --help     显示此帮助信息"
    echo ""
}

# 主函数
main() {
    echo "========================================"
    echo "  MyStocks 系统启动脚本"
    echo "========================================"
    echo ""

    case "${1:-}" in
        --all)
            check_dependencies
            start_api
            start_web
            sleep 3
            check_status
            ;;
        --api)
            check_dependencies
            start_api
            ;;
        --web)
            check_dependencies
            start_web
            ;;
        --tmux)
            check_dependencies
            create_tmux_session
            ;;
        --test)
            check_dependencies
            run_tests
            ;;
        --catalog)
            generate_catalog
            ;;
        --status)
            check_status
            ;;
        --stop)
            stop_all
            ;;
        --help|*)
            show_help
            ;;
    esac
}

main "$@"
