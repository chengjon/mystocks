#!/bin/bash

# MyStocks 测试环境启动脚本
# 支持 tmux 多窗口测试环境

SESSION_NAME="mystocks_test"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/var/log"

# 显示帮助信息
show_help() {
    cat << EOF
MyStocks 测试环境启动脚本

用法: ./start-system.sh [选项]

选项:
  --tmux          启动 tmux 多窗口测试环境
  --help          显示此帮助信息

tmux 窗口配置:
  Window 0: API服务监控 (PM2)
  Window 1: Web服务 (Vite Dev Server)
  Window 2: 日志监控
  Window 3: 测试执行

快捷键:
  Ctrl+B, 0-3    切换窗口
  Ctrl+B, n      下一个窗口
  Ctrl+B, p      上一个窗口
  Ctrl+B, d      分离会话
EOF
}

# 检查依赖
check_dependencies() {
    local missing_deps=()

    if ! command -v pm2 &> /dev/null; then
        missing_deps+=("pm2")
    fi
    if ! command -v npm &> /dev/null; then
        missing_deps+=("npm")
    fi
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    if ! command -v lnav &> /dev/null; then
        missing_deps+=("lnav")
    fi

    if [ ${#missing_deps[@]} -ne 0 ]; then
        echo "❌ 缺少依赖: ${missing_deps[*]}"
        echo "请先安装缺少的依赖"
        exit 1
    fi
}

# 启动 tmux 测试环境
start_tmux() {
    check_dependencies

    # 检查会话是否已存在
    tmux has-session -t $SESSION_NAME 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "⚠️  会话 '$SESSION_NAME' 已存在"
        echo "连接到现有会话..."
        tmux attach-session -t $SESSION_NAME
        return
    fi

    echo "🚀 创建 tmux 测试环境: $SESSION_NAME"

    # 创建新会话
    tmux new-session -d -s $SESSION_NAME

    # Window 0: API服务监控（PM2）
    tmux rename-window -t $SESSION_NAME:0 'API-Monitor'
    tmux send-keys -t $SESSION_NAME:0 "cd $PROJECT_ROOT" Enter
    tmux send-keys -t $SESSION_NAME:0 "echo '📊 API服务监控窗口'" Enter
    tmux send-keys -t $SESSION_NAME:0 "echo '使用 pm2 管理 API 服务'" Enter
    tmux send-keys -t $SESSION_NAME:0 "echo ''" Enter
    tmux send-keys -t $SESSION_NAME:0 "pm2 list" Enter

    # Window 1: Web服务（Vite Dev Server）
    tmux new-window -t $SESSION_NAME -n 'Web-Service'
    tmux send-keys -t $SESSION_NAME:1 "cd $PROJECT_ROOT/web/frontend" Enter
    tmux send-keys -t $SESSION_NAME:1 "echo '🌐 Web服务窗口 - Vite Dev Server'" Enter
    tmux send-keys -t $SESSION_NAME:1 "echo ''" Enter
    tmux send-keys -t $SESSION_NAME:1 "npm run dev" Enter

    # Window 2: 日志监控
    tmux new-window -t $SESSION_NAME -n 'Log-Monitor'
    tmux send-keys -t $SESSION_NAME:2 "cd $PROJECT_ROOT" Enter
    tmux send-keys -t $SESSION_NAME:2 "echo '📝 日志监控窗口 - lnav'" Enter
    tmux send-keys -t $SESSION_NAME:2 "echo ''" Enter
    tmux send-keys -t $SESSION_NAME:2 "mkdir -p var/log" Enter
    tmux send-keys -t $SESSION_NAME:2 "# lnav var/log/mystocks_system.log" Enter
    tmux send-keys -t $SESSION_NAME:2 "echo '提示: 使用 :filter-in path=/api/market/ 筛选模块'" Enter

    # Window 3: 测试执行
    tmux new-window -t $SESSION_NAME -n 'Test-Execution'
    tmux send-keys -t $SESSION_NAME:3 "cd $PROJECT_ROOT" Enter
    tmux send-keys -t $SESSION_NAME:3 "echo '🧪 测试执行窗口'" Enter
    tmux send-keys -t $SESSION_NAME:3 "echo ''" Enter
    tmux send-keys -t $SESSION_NAME:3 "echo '可用命令:'" Enter
    tmux send-keys -t $SESSION_NAME:3 "echo '  playwright test tests/api/'" Enter
    tmux send-keys -t $SESSION_NAME:3 "echo '  playwright test tests/e2e/'" Enter
    tmux send-keys -t $SESSION_NAME:3 "echo '  python -m pytest tests/api/'" Enter
    tmux send-keys -t $SESSION_NAME:3 "echo '  python -m pytest tests/e2e/'" Enter

    # 设置窗口布局为 even-horizontal
    tmux select-layout -t $SESSION_NAME even-horizontal

    echo "✅ tmux 测试环境创建成功！"
    echo ""
    echo "📋 窗口列表:"
    echo "  0: API服务监控 (PM2)"
    echo "  1: Web服务 (Vite Dev Server)"
    echo "  2: 日志监控"
    echo "  3: 测试执行"
    echo ""
    echo "🎮 快捷键:"
    echo "  Ctrl+B, 0-3    切换窗口"
    echo "  Ctrl+B, n      下一个窗口"
    echo "  Ctrl+B, p      上一个窗口"
    echo "  Ctrl+B, d      分离会话"
    echo ""

    # 连接到会话
    tmux attach-session -t $SESSION_NAME
}

# 主逻辑
case "$1" in
    --tmux)
        start_tmux
        ;;
    --help|-h)
        show_help
        ;;
    "")
        show_help
        ;;
    *)
        echo "❌ 未知选项: $1"
        echo "使用 --help 查看帮助信息"
        exit 1
        ;;
esac
