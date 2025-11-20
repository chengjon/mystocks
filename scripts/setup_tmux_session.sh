#!/bin/bash

# Tmux会话配置脚本
# 用于MyStocks项目的CI/CD流程管理

SESSION_NAME="mystocks_cicd"

# 检查会话是否存在
tmux has-session -t $SESSION_NAME 2>/dev/null

if [ $? != 0 ]; then
    # 创建新会话
    tmux new-session -d -s $SESSION_NAME
    
    # 创建窗格布局
    # 窗格0: 主控制台
    tmux rename-window -t $SESSION_NAME:0 'Main-Control'
    
    # 窗格1: 后端服务
    tmux new-window -t $SESSION_NAME:1 -n 'Backend-Service'
    
    # 窗格2: 前端服务
    tmux new-window -t $SESSION_NAME:2 -n 'Frontend-Service'
    
    # 窗格3: 测试执行
    tmux new-window -t $SESSION_NAME:3 -n 'Test-Execution'
    
    # 窗格4: 日志监控
    tmux new-window -t $SESSION_NAME:4 -n 'Log-Monitor'
    
    # 窗格5: 性能监控
    tmux new-window -t $SESSION_NAME:5 -n 'Performance'
    
    # 在主控制台窗格中设置初始命令
    tmux send-keys -t $SESSION_NAME:0 "echo 'MyStocks CI/CD 控制台'" Enter
    tmux send-keys -t $SESSION_NAME:0 "echo '可用命令:'" Enter
    tmux send-keys -t $SESSION_NAME:0 "echo '  - ./scripts/cicd_pipeline.sh run_full_pipeline'" Enter
    tmux send-keys -t $SESSION_NAME:0 "echo '  - ./scripts/cicd_pipeline.sh run_unit_tests'" Enter
    tmux send-keys -t $SESSION_NAME:0 "echo '  - ./scripts/cicd_pipeline.sh run_integration_tests'" Enter
    tmux send-keys -t $SESSION_NAME:0 "echo '  - ./scripts/cicd_pipeline.sh run_e2e_tests'" Enter
    
    # 在后端服务窗格中设置命令
    tmux send-keys -t $SESSION_NAME:1 "cd web/backend" Enter
    tmux send-keys -t $SESSION_NAME:1 "echo '后端服务控制台 - 准备启动服务'" Enter
    
    # 在前端服务窗格中设置命令
    tmux send-keys -t $SESSION_NAME:2 "cd web/frontend" Enter
    tmux send-keys -t $SESSION_NAME:2 "echo '前端服务控制台 - 准备启动服务'" Enter
    
    # 在测试执行窗格中设置命令
    tmux send-keys -t $SESSION_NAME:3 "echo '测试执行控制台'" Enter
    tmux send-keys -t $SESSION_NAME:3 "echo '使用以下命令运行测试:'" Enter
    tmux send-keys -t $SESSION_NAME:3 "echo '  python -m pytest tests/unit/ -v'" Enter
    tmux send-keys -t $SESSION_NAME:3 "echo '  python -m pytest tests/integration/ -v'" Enter
    tmux send-keys -t $SESSION_NAME:3 "echo '  python -m pytest tests/e2e/ -v'" Enter
    
    # 在日志监控窗格中设置命令
    tmux send-keys -t $SESSION_NAME:4 "echo '日志监控控制台'" Enter
    tmux send-keys -t $SESSION_NAME:4 "mkdir -p logs" Enter
    tmux send-keys -t $SESSION_NAME:4 "touch logs/mystocks_system.log" Enter
    tmux send-keys -t $SESSION_NAME:4 "# lnav logs/mystocks_system.log" Enter
    
    # 在性能监控窗格中设置命令
    tmux send-keys -t $SESSION_NAME:5 "echo '性能监控控制台'" Enter
    tmux send-keys -t $SESSION_NAME:5 "echo '使用以下命令进行性能分析:'" Enter
    tmux send-keys -t $SESSION_NAME:5 "echo '  python -m cProfile -o profile_output.prof <script>'" Enter
    tmux send-keys -t $SESSION_NAME:5 "echo '  py-spy record -o profile.svg -- python <script>'" Enter
fi

# 连接到会话
tmux attach-session -t $SESSION_NAME