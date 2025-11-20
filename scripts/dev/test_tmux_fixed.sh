#!/bin/bash
# 修复TMUX窗格引用的简化脚本

SESSION_NAME="mystocks-dev-fixed"
PROJECT_ROOT="/opt/claude/mystocks_spec"

echo "清理现有会话..."
tmux kill-session -t "$SESSION_NAME" 2>/dev/null || true
sleep 1

echo "创建基础会话..."
tmux new-session -d -s "$SESSION_NAME" -x 300 -y 100
echo "基础会话创建完成"

echo "开始分割窗格..."
# 水平分割创建左右两个区域
tmux split-window -t "$SESSION_NAME" -h
echo "第一次分割完成"

# 左侧区域垂直分割
tmux select-pane -t "$SESSION_NAME" 
tmux split-window -t "$SESSION_NAME" -v
echo "第二次分割完成"

# 右侧区域垂直分割  
tmux select-pane -t "$SESSION_NAME" -t right
tmux split-window -t "$SESSION_NAME" -v
echo "第三次分割完成"

# 底部分割
tmux select-pane -t "$SESSION_NAME" -t top
tmux split-window -t "$SESSION_NAME" -v
echo "第四次分割完成"

echo "发送测试命令到各个窗格..."
# 使用位置而不是数字索引
tmux send-keys -t "$SESSION_NAME" -t left-top "echo 'Backend - Top Left' && pwd"
tmux send-keys -t "$SESSION_NAME" -t left-bottom "echo 'Database - Bottom Left' && pwd" 
tmux send-keys -t "$SESSION_NAME" -t right-top "echo 'Frontend - Top Right' && pwd"
tmux send-keys -t "$SESSION_NAME" -t right-bottom "echo 'Monitoring - Bottom Right' && pwd"
tmux send-keys -t "$SESSION_NAME" -t bottom "echo 'Logs - Bottom Full Width' && pwd"

echo "等待命令执行..."
sleep 2

echo "检查窗格数量: $(tmux list-panes -t $SESSION_NAME | wc -l)"
echo "当前窗格内容:"
tmux capture-pane -t "$SESSION_NAME" -p

echo "清理测试会话..."
tmux kill-session -t "$SESSION_NAME"
echo "测试完成！"