#!/bin/bash

# 简化的TMUX测试脚本
SESSION_NAME="tmux-test"

echo "创建TMUX会话..."
tmux new-session -d -s "$SESSION_NAME" -x 100 -y 50

echo "检查会话状态..."
tmux list-sessions

echo "检查窗格..."
tmux list-panes -t "$SESSION_NAME"

echo "尝试发送命令..."
# 尝试不同的格式
tmux send-keys -t "$SESSION_NAME" "echo 'Test message'" C-m

echo "清理..."
tmux kill-session -t "$SESSION_NAME"