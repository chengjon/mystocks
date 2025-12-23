#!/bin/bash
# MyStocks开发环境tmux会话配置脚本
# 作者: MyStocks开发团队
# 版本: 1.0

# 会话配置
SESSION_NAME="mystocks_dev"
PROJECT_ROOT="/opt/claude/mystocks_spec"
LOG_DIR="$PROJECT_ROOT/logs"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查tmux是否安装
check_tmux() {
    if ! command -v tmux &> /dev/null; then
        log_error "tmux未安装，请先安装tmux"
        exit 1
    fi
    log_info "tmux版本: $(tmux -V)"
}

# 检查项目目录
check_project_dir() {
    if [ ! -d "$PROJECT_ROOT" ]; then
        log_error "项目目录不存在: $PROJECT_ROOT"
        exit 1
    fi
    log_info "项目目录: $PROJECT_ROOT"
}

# 创建开发会话
create_dev_session() {
    log_info "创建MyStocks开发会话..."

    # 检查会话是否已存在
    if tmux has-session -t $SESSION_NAME 2>/dev/null; then
        log_warn "会话 $SESSION_NAME 已存在"
        return 1
    fi

    # 创建新会话 - 数据库监控窗口
    tmux new-session -d -s $SESSION_NAME -n databases -c $PROJECT_ROOT

    # 面板1: TDengine监控
    tmux send-keys -t $SESSION_NAME:databases.0 "echo 'TDengine监控面板'; echo '执行: docker stats mystocks-tdengine'" C-m

    # 分割面板 - PostgreSQL监控
    tmux split-window -h -t $SESSION_NAME:databases -c $PROJECT_ROOT
    tmux send-keys -t $SESSION_NAME:databases.1 "echo 'PostgreSQL监控面板'; echo '执行: docker stats mystocks-postgresql'" C-m

    # 创建服务窗口
    tmux new-window -t $SESSION_NAME -n services -c $PROJECT_ROOT

    # 面板1: 后端服务
    tmux send-keys -t $SESSION_NAME:services.0 "echo 'MyStocks后端服务'; echo '执行: cd web/backend && python -m uvicorn app.main:app --reload'" C-m

    # 分割面板 - 前端服务
    tmux split-window -v -t $SESSION_NAME:services -c $PROJECT_ROOT
    tmux send-keys -t $SESSION_NAME:services.1 "echo 'MyStocks前端服务'; echo '执行: cd web/frontend && npm run dev'" C-m

    # 分割面板 - GPU服务（如果存在）
    tmux split-window -h -t $SESSION_NAME:services.1 -c $PROJECT_ROOT
    tmux send-keys -t $SESSION_NAME:services.2 "echo 'GPU加速服务'; echo '执行: cd src/gpu/api_system && python main_server.py'" C-m

    # 创建日志监控窗口
    tmux new-window -t $SESSION_NAME -n logs -c $PROJECT_ROOT
    tmux send-keys -t $SESSION_NAME:logs.0 "echo '日志监控面板'; echo '执行: lnav $LOG_DIR'" C-m

    # 创建开发窗口
    tmux new-window -t $SESSION_NAME -n dev -c $PROJECT_ROOT
    tmux send-keys -t $SESSION_NAME:dev.0 "echo '开发面板'; echo '当前目录: $(pwd)'" C-m

    # 选择第一个窗口
    tmux select-window -t $SESSION_NAME:databases

    log_info "MyStocks开发会话创建完成"
    return 0
}

# 连接到会话
attach_session() {
    if [ -z "$TMUX" ]; then
        log_info "连接到会话 $SESSION_NAME"
        tmux attach-session -t $SESSION_NAME
    else
        log_warn "已经在tmux会话中，无法附加到其他会话"
    fi
}

# 列出所有会话
list_sessions() {
    log_info "当前tmux会话:"
    tmux list-sessions 2>/dev/null || log_warn "没有活动的tmux会话"
}

# 关闭会话
kill_session() {
    if tmux has-session -t $SESSION_NAME 2>/dev/null; then
        log_info "关闭会话 $SESSION_NAME"
        tmux kill-session -t $SESSION_NAME
    else
        log_warn "会话 $SESSION_NAME 不存在"
    fi
}

# 显示帮助信息
show_help() {
    echo "MyStocks tmux会话管理脚本"
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  start     创建并启动MyStocks开发会话"
    echo "  attach    连接到现有会话"
    echo "  list      列出所有会话"
    echo "  kill      关闭MyStocks会话"
    echo "  help      显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 start   # 创建开发环境会话"
    echo "  $0 attach  # 连接到会话"
}

# 主函数
main() {
    check_tmux
    check_project_dir

    case "$1" in
        start)
            create_dev_session
            if [ $? -eq 0 ]; then
                attach_session
            fi
            ;;
        attach)
            attach_session
            ;;
        list)
            list_sessions
            ;;
        kill)
            kill_session
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
