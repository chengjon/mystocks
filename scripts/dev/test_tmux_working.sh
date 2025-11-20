#!/bin/bash
# TMUX窗格创建的最佳实践版本

SESSION_NAME="mystocks-dev-working"
PROJECT_ROOT="/opt/claude/mystocks_spec"

echo "清理现有会话..."
tmux kill-session -t "$SESSION_NAME" 2>/dev/null || true
sleep 1

echo "创建基础会话..."
tmux new-session -d -s "$SESSION_NAME"

echo "创建窗格布局..."

# 方法1: 使用目标窗格的索引选择
tmux split-window -h
echo "第一个分割完成"

tmux select-pane -t 0
tmux split-window -v  
echo "第二个分割完成"

tmux select-pane -t 1
tmux split-window -v
echo "第三个分割完成"

tmux select-pane -t 0
tmux split-window -v
echo "第四个分割完成"

echo "发送命令到每个窗格..."
# 直接使用索引选择
tmux select-pane -t 0
tmux send-keys "echo 'Pane 0: Backend' && pwd && ls -la"
tmux select-pane -t 1  
tmux send-keys "echo 'Pane 1: Frontend' && pwd && ls -la"
tmux select-pane -t 2
tmux send-keys "echo 'Pane 2: Monitoring' && pwd && ls -la"
tmux select-pane -t 3
tmux send-keys "echo 'Pane 3: Database' && pwd && ls -la"
tmux select-pane -t 4
tmux send-keys "echo 'Pane 4: Logs' && pwd && ls -la"

echo "等待命令执行..."
sleep 2

echo "查看结果..."
tmux capture-pane -p

echo "窗格测试完成，数量: $(tmux list-panes | wc -l)"
tmux kill-session -t "$SESSION_NAME"
echo "会话已清理"