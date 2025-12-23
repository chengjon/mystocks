#!/bin/bash
# =================================
# MyStocks 开发环境启动脚本
# 启动tmux会话，包含4个窗格：后端、前端、数据库、日志
# =================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的信息
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    info "检查依赖..."

    if ! command -v tmux &> /dev/null; then
        error "tmux 未安装，请先安装: sudo apt-get install tmux"
        exit 1
    fi

    if ! command -v python3 &> /dev/null; then
        error "Python3 未安装"
        exit 1
    fi

    if ! command -v node &> /dev/null; then
        error "Node.js 未安装"
        exit 1
    fi

    if ! command -v npm &> /dev/null; then
        error "npm 未安装"
        exit 1
    fi

    info "所有依赖检查通过"
}

# 创建目录
create_directories() {
    info "创建必要的目录..."
    mkdir -p logs
    mkdir -p data
    info "目录创建完成"
}

# 创建tmux会话
create_tmux_session() {
    local session_name="mystocks-dev"

    info "创建 tmux 会话: $session_name"

    # 如果会话已存在，删除它
    tmux kill-session -t "$session_name" 2>/dev/null || true

    # 创建新会话并设置基础设置
    tmux new-session -d -s "$session_name" -x 300 -y 50

    # 启用鼠标支持
    tmux set-option -t "$session_name" mouse on

    # 设置默认终端
    tmux set-environment -t "$session_name" TERM xterm-256color

    info "创建窗格布局..."

    # 创建4个窗格的布局（2x2）
    tmux split-window -t "$session_name" -h  # 水平分割，创建右侧窗格
    tmux split-window -t "$session_name" -v  # 垂直分割，创建下方窗格
    tmux select-pane -t "$session_name":0.3  # 选择第三个窗格
    tmux split-window -t "$session_name" -v  # 垂直分割，创建第四个窗格

    # 调整窗格大小（2x2网格）
    tmux resize-pane -t "$session_name":0.0 -x 120 -y 25  # 后端窗格 (左上)
    tmux resize-pane -t "$session_name":0.1 -x 180 -y 25  # 前端窗格 (右上)
    tmux resize-pane -t "$session_name":0.2 -x 120 -y 25  # 数据库窗格 (左下)
    tmux resize-pane -t "$session_name":0.3 -x 180 -y 25  # 日志窗格 (右下)

    # 设置窗格标题
    tmux select-pane -t "$session_name":0.0
    tmux send-keys "printf '\033]0;MyStocks Backend\033\\'" C-m

    tmux select-pane -t "$session_name":0.1
    tmux send-keys "printf '\033]0;MyStocks Frontend\033\\'" C-m

    tmux select-pane -t "$session_name":0.2
    tmux send-keys "printf '\033]0;MyStocks Database\033\\'" C-m

    tmux select-pane -t "$session_name":0.3
    tmux send-keys "printf '\033]0;MyStocks Logs\033\\'" C-m

    # 重新选择第一个窗格
    tmux select-pane -t "$session_name":0.0

    info "tmux 会话创建完成"
}

# 启动服务
start_services() {
    local session_name="mystocks-dev"

    info "启动服务..."

    # 启动后端服务 (窗格 0)
    tmux send-keys -t "$session_name" "cd /opt/claude/mystocks_spec" C-m
    tmux send-keys -t "$session_name" "source .env 2>/dev/null || echo '警告: .env 文件不存在，使用默认配置'" C-m
    tmux send-keys -t "$session_name" "echo '启动 FastAPI 后端服务...'" C-m
    tmux send-keys -t "$session_name" "cd web/backend" C-m
    tmux send-keys -t "$session_name" "uvicorn app.main:app --host 0.0.0.0 --port \$(python -c 'from app.core.config import settings; print(settings.port)') --reload --log-level info" C-m

    # 等待后端启动
    sleep 3

    # 启动前端服务 (窗格 1)
    tmux send-keys -t "$session_name:0.1" "cd /opt/claude/mystocks_spec" C-m
    tmux send-keys -t "$session_name:0.1" "echo '启动 Vue.js 前端服务...'" C-m
    tmux send-keys -t "$session_name:0.1" "cd web/frontend" C-m
    tmux send-keys -t "$session_name:0.1" "if [ -f package-lock.json ]; then npm install; fi" C-m
    tmux send-keys -t "$session_name:0.1" "npm run dev -- --host 0.0.0.0 --port 5173" C-m

    # 等待前端启动
    sleep 5

    # 连接数据库 (窗格 2)
    tmux send-keys -t "$session_name:0.2" "echo '数据库连接信息:'" C-m
    tmux send-keys -t "$session_name:0.2" "echo 'PostgreSQL: postgres://postgres:***@localhost:5432/mystocks'" C-m
    tmux send-keys -t "$session_name:0.2" "echo 'TDengine: taos://root:***@localhost:6030/market_data'" C-m
    tmux send-keys -t "$session_name:0.2" "echo '等待连接...' && sleep 2" C-m
    tmux send-keys -t "$session_name:0.2" "psql -h localhost -U postgres -d mystocks" C-m

    # 显示日志 (窗格 3)
    tmux send-keys -t "$session_name:0.3" "cd /opt/claude/mystocks_spec" C-m
    tmux send-keys -t "$session_name:0.3" "echo 'MyStocks 开发日志监控'" C-m
    tmux send-keys -t "$session_name:0.3" "echo '配置 lnav 格式化显示...'" C-m
    tmux send-keys -t "$session_name:0.3" "if command -v lnav &> /dev/null; then" C-m
    tmux send-keys -t "$session_name:0.3" "  ./scripts/setup_lnav.sh dev" C-m
    tmux send-keys -t "$session_name:0.3" "else" C-m
    tmux send-keys -t "$session_name:0.3" "  echo 'lnav 未安装，使用 tail -f 监控...' && tail -f logs/backend.log" C-m
    tmux send-keys -t "$session_name:0.3" "fi" C-m

    info "服务启动完成"
}

# 显示帮助信息
show_help() {
    echo -e "${BLUE}MyStocks 开发环境启动脚本${NC}"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示帮助信息"
    echo "  -c, --check    仅检查依赖，不启动服务"
    echo "  -d, --debug    启用调试模式"
    echo ""
    echo "窗格说明:"
    echo "  窗格 0 (左上): FastAPI 后端服务 (端口 8000)"
    echo "  窗格 1 (右上): Vue.js 前端服务 (端口 5173)"
    echo "  窗格 2 (左下): PostgreSQL 数据库客户端"
    echo "  窗格 3 (右下): 日志监控 (lnav 或 tail)"
    echo ""
    echo "快捷键 (在tmux中):"
    echo "  Ctrl+b d     分离会话"
    echo "  Ctrl+b ↑↓←→ 切换窗格"
    echo "  Ctrl+b z     切换全屏"
    echo "  Ctrl+b [     进入复制模式"
    echo ""
    echo "  后端 API:  http://localhost:8000/api/docs"
  echo "  前端界面: http://localhost:5173"
  echo "  监控面板: http://localhost:8000/monitoring"
    echo ""
}

# 调试模式
debug_mode() {
    info "启用调试模式..."
    set -x
    export DEBUG=1
}

# 主函数
main() {
    local check_only=false
    local debug=false

    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -c|--check)
                check_only=true
                shift
                ;;
            -d|--debug)
                debug=true
                shift
                ;;
            *)
                error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # 显示标题
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}    MyStocks 开发环境启动器${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""

    # 检查依赖
    check_dependencies

    if [ "$check_only" = true ]; then
        info "依赖检查完成，退出"
        exit 0
    fi

    # 启用调试模式
    if [ "$debug" = true ]; then
        debug_mode
    fi

    # 创建目录
    create_directories

    # 创建tmux会话
    create_tmux_session

    # 启动服务
    start_services

    # 显示完成信息
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}    MyStocks 开发环境已启动!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${YELLOW}访问地址:${NC}"
    echo -e "  后端 API: ${BLUE}http://localhost:8000/api/docs${NC}"
    echo -e "  前端界面: ${BLUE}http://localhost:5173${NC}"
    echo -e "  监控面板: ${BLUE}http://localhost:8000/monitoring${NC}"
    echo ""
    echo -e "${YELLOW}窗格说明:${NC}"
    echo -e "  窗格 0: ${GREEN}FastAPI 后端服务${NC}"
    echo -e "  窗格 1: ${GREEN}Vue.js 前端服务${NC}"
    echo -e "  窗格 2: ${GREEN}PostgreSQL 数据库客户端${NC}"
    echo -e "  窗格 3: ${GREEN}日志监控${NC}"
    echo ""
    echo -e "${YELLOW}tmux 快捷键:${NC}"
    echo -e "  Ctrl+b d     分离会话"
    echo -e "  Ctrl+b ↑↓←→ 切换窗格"
    echo -e "  Ctrl+b z     切换全屏"
    echo ""

    # 连接到tmux会话
    info "连接 tmux 会话..."
    tmux attach-session -t "mystocks-dev"
}

# 脚本入口
main "$@"
