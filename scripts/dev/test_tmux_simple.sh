#!/bin/bash
# 简化的TMUX测试脚本

SESSION_NAME="mystocks-dev-test"
PROJECT_ROOT="/opt/claude/mystocks_spec"

echo "清理现有会话..."
tmux kill-session -t "$SESSION_NAME" 2>/dev/null || true
sleep 1

echo "创建基础会话..."
tmux new-session -d -s "$SESSION_NAME" -x 300 -y 100
echo "基础会话创建完成"

echo "开始分割窗格..."
# 水平分割
tmux split-window -t "$SESSION_NAME" -h
echo "第一次分割完成"

# 垂直分割 (左侧)
tmux select-pane -t "$SESSION_NAME" 
tmux split-window -t "$SESSION_NAME" -v
echo "第二次分割完成"

# 垂直分割 (右侧)
tmux select-pane -t "$SESSION_NAME" -t 1
tmux split-window -t "$SESSION_NAME" -v
echo "第三次分割完成"

# 底部分割
tmux select-pane -t "$SESSION_NAME" -t 0
tmux split-window -t "$SESSION_NAME" -v
echo "第四次分割完成"

echo "调整窗格大小..."
tmux resize-pane -t "$SESSION_NAME" -t 0 -x 120 -y 15
tmux resize-pane -t "$SESSION_NAME" -t 1 -x 120 -y 15  
tmux resize-pane -t "$SESSION_NAME" -t 2 -x 120 -y 15
tmux resize-pane -t "$SESSION_NAME" -t 3 -x 120 -y 15
tmux resize-pane -t "$SESSION_NAME" -t 4 -x 240 -y 30

echo "发送测试命令..."
tmux send-keys -t "$SESSION_NAME" -t 0 "echo 'Pane 0: Backend'"
tmux send-keys -t "$SESSION_NAME" -t 1 "echo 'Pane 1: Frontend'" 
tmux send-keys -t "$SESSION_NAME" -t 2 "echo 'Pane 2: Monitoring'"
tmux send-keys -t "$SESSION_NAME" -t 3 "echo 'Pane 3: Database'"
tmux send-keys -t "$SESSION_NAME" -t 4 "echo 'Pane 4: Logs'"

echo "测试完成！窗格数量: $(tmux list-panes -t $SESSION_NAME | wc -l)"
tmux kill-session -t "$SESSION_NAME"
echo "测试会话已清理"