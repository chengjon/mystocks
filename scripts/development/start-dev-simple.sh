#!/bin/bash
# =================================
# MyStocks 简化开发环境启动脚本
# =================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_colored() {
    local color=$1
    local message=$2
    echo -e "${color}[INFO]${NC} $message"
}

print_success() {
    print_colored "$GREEN" "✅ $1"
}

print_error() {
    print_colored "$RED" "❌ $1"
}

SESSION_NAME="mystocks-dev-v2"
PROJECT_ROOT="/opt/claude/mystocks_spec"

# 清理现有会话
print_colored "$YELLOW" "清理现有会话..."
tmux kill-session -t "$SESSION_NAME" 2>/dev/null || true

# 创建基础会话
print_colored "$YELLOW" "创建TMUX会话..."
tmux new-session -d -s "$SESSION_NAME" -x 200 -y 100

# 启用鼠标支持
tmux set-option -t "$SESSION_NAME" mouse on

print_success "基础会话创建完成"

# 分割窗格
print_colored "$YELLOW" "分割窗格..."

# 水平分割
tmux split-window -t "$SESSION_NAME" -h

# 在左侧垂直分割
tmux select-pane -t "$SESSION_NAME"
tmux split-window -t "$SESSION_NAME" -v

# 在右侧垂直分割
tmux select-pane -t "$SESSION_NAME" -t 1
tmux split-window -t "$SESSION_NAME" -v

# 在底部创建第五个窗格
tmux select-pane -t "$SESSION_NAME"
tmux split-window -t "$SESSION_NAME" -v

print_success "5窗格布局创建完成"

# 调整窗格大小
print_colored "$YELLOW" "调整窗格大小..."

# 设置标题和基本信息
tmux send-keys -t "$SESSION_NAME" "echo 'MyStocks Backend (PM2) - Pane 0'" C-m
tmux send-keys -t "$SESSION_NAME" -t 1 "echo 'MyStocks Frontend - Pane 1'" C-m
tmux send-keys -t "$SESSION_NAME" -t 2 "echo 'MyStocks Monitoring - Pane 2'" C-m
tmux send-keys -t "$SESSION_NAME" -t 3 "echo 'MyStocks Database - Pane 3'" C-m
tmux send-keys -t "$SESSION_NAME" -t 4 "echo 'MyStocks Logs - Pane 4'" C-m

print_success "窗格标题设置完成"

# 检查窗格状态
print_colored "$YELLOW" "检查窗格状态..."
tmux list-panes -t "$SESSION_NAME"

print_success "开发环境创建完成！"
print_colored "$BLUE" "连接命令: tmux attach-session -t $SESSION_NAME"
