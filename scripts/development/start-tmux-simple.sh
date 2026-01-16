#!/bin/bash
# MyStocks 简化版TMUX启动脚本
set -e

SESSION_NAME="mystocks-dev"
PROJECT_ROOT="/opt/claude/mystocks_spec"

echo "启动MyStocks 5窗格开发环境..."

# 清理现有会话
if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    tmux kill-session -t "$SESSION_NAME"
fi

# 创建基础会话
tmux new-session -d -s "$SESSION_NAME" -x 300 -y 100

# 水平分割创建左右两个区域
tmux split-window -h

# 左侧区域垂直分割
tmux select-pane -t 0
tmux split-window -v

# 右侧区域垂直分割
tmux select-pane -t 1
tmux split-window -v

# 底部创建第五个窗格
tmux select-pane -t 0
tmux split-window -v

# 调整窗格大小
tmux resize-pane -t "$SESSION_NAME" -x 120 -y 15
tmux resize-pane -t "$SESSION_NAME" -t 1 -x 120 -y 15
tmux resize-pane -t "$SESSION_NAME" -t 2 -x 120 -y 15
tmux resize-pane -t "$SESSION_NAME" -t 3 -x 120 -y 15
tmux resize-pane -t "$SESSION_NAME" -t 4 -x 240 -y 30

# 启动各窗格内容
echo "配置窗格内容..."

# 窗格0 - 后端服务
tmux select-pane -t 0
tmux send-keys "cd $PROJECT_ROOT" C-m
tmux send-keys "echo '=== MyStocks Backend Service ==='" C-m
tmux send-keys "echo 'PM2 management and backend APIs'" C-m
tmux send-keys "ls -la" C-m

# 窗格1 - 前端服务
tmux select-pane -t 1
tmux send-keys "cd $PROJECT_ROOT/web/frontend" C-m
tmux send-keys "echo '=== MyStocks Frontend Service ==='" C-m
tmux send-keys "echo 'Vue.js development server'" C-m
tmux send-keys "ls -la" C-m

# 窗格2 - 监控系统
tmux select-pane -t 2
tmux send-keys "echo '=== MyStocks Monitoring Panel ==='" C-m
tmux send-keys "echo 'System status and metrics'" C-m
tmux send-keys "htop" C-m

# 窗格3 - 数据库客户端
tmux select-pane -t 3
tmux send-keys "echo '=== MyStocks Database Client ==='" C-m
tmux send-keys "echo 'PostgreSQL and TDengine access'" C-m
tmux send-keys "psql --version" C-m

# 窗格4 - 日志中心
tmux select-pane -t 4
tmux send-keys "cd $PROJECT_ROOT" C-m
tmux send-keys "echo '=== MyStocks Log Center ==='" C-m
tmux send-keys "tail -f logs/backend.log" C-m

# 重置选择到第一个窗格
tmux select-pane -t 0

echo "5窗格环境创建完成！"
echo "使用 'tmux attach -t mystocks-dev' 连接会话"
echo "按 Ctrl+B 然后按 D 分离会话"

tmux attach-session -t "$SESSION_NAME"
