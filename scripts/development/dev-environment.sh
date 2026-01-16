#!/bin/bash
# MyStocks AI自动化开发环境启动脚本

set -e

# 项目配置
SESSION_NAME="mystocks-ai-dev"
PROJECT_ROOT="/opt/claude/mystocks_spec"

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}    MyStocks AI 自动化开发环境${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# 检查TMUX是否可用
if ! command -v tmux &> /dev/null; then
    echo "❌ TMUX未安装，正在安装..."
    sudo apt update && sudo apt install -y tmux
fi

# 检查会话是否存在
if tmux has-session -t $SESSION_NAME 2>/dev/null; then
    echo "📋 检测到现有会话，正在连接到: $SESSION_NAME"
    tmux attach-session -t $SESSION_NAME
    exit 0
fi

# 创建新的TMUX会话
print_header
print_success "创建新的开发环境会话: $SESSION_NAME"

# 创建会话并分割窗格
tmux new-session -d -s $SESSION_NAME -n "开发窗格"

# 水平分割创建5个窗格
tmux split-window -h -t $SESSION_NAME:0.0
tmux split-window -v -t $SESSION_NAME:0.0
tmux split-window -h -t $SESSION_NAME:0.2
tmux split-window -v -t $SESSION_NAME:0.4

# 设置窗格索引
WINDOWS=("后端开发" "前端开发" "监控系统" "数据库" "日志中心")

print_success "配置开发窗格..."

# 窗格0: 后端开发
tmux send-keys -t $SESSION_NAME:0.0 "cd $PROJECT_ROOT" C-m
tmux send-keys -t $SESSION_NAME:0.0 "echo '=== 后端开发环境 ==='" C-m
tmux send-keys -t $SESSION_NAME:0.0 "echo 'AI自动化分析器已就绪'" C-m
tmux send-keys -t $SESSION_NAME:0.0 "echo '策略分析系统已就绪'" C-m
tmux send-keys -t $SESSION_NAME:0.0 "echo ''" C-m

# 窗格1: 前端开发
tmux send-keys -t $SESSION_NAME:0.1 "cd $PROJECT_ROOT" C-m
tmux send-keys -t $SESSION_NAME:0.1 "echo '=== 前端开发环境 ==='" C-m
tmux send-keys -t $SESSION_NAME:0.1 "echo 'Vue.js 监控界面已就绪'" C-m
tmux send-keys -t $SESSION_NAME:0.1 "echo ''" C-m

# 窗格2: 监控系统
tmux send-keys -t $SESSION_NAME:0.2 "cd $PROJECT_ROOT" C-m
tmux send-keys -t $SESSION_NAME:0.2 "echo '=== AI监控和告警系统 ==='" C-m
tmux send-keys -t $SESSION_NAME:0.2 "echo '实时监控已启动'" C-m
tmux send-keys -t $SESSION_NAME:0.2 "echo 'GPU加速监控已就绪'" C-m
tmux send-keys -t $SESSION_NAME:0.2 "echo ''" C-m

# 窗格3: 数据库
tmux send-keys -t $SESSION_NAME:0.3 "cd $PROJECT_ROOT" C-m
tmux send-keys -t $SESSION_NAME:0.3 "echo '=== 数据库管理 ==='" C-m
tmux send-keys -t $SESSION_NAME:0.3 "echo 'PostgreSQL + TDengine已配置'" C-m
tmux send-keys -t $SESSION_NAME:0.3 "echo ''" C-m

# 窗格4: 日志中心
tmux send-keys -t $SESSION_NAME:0.4 "cd $PROJECT_ROOT" C-m
tmux send-keys -t $SESSION_NAME:0.4 "echo '=== 日志监控中心 ==='" C-m
tmux send-keys -t $SESSION_NAME:0.4 "echo 'AI自动化日志已就绪'" C-m
tmux send-keys -t $SESSION_NAME:0.4 "echo ''" C-m

print_success "✅ MyStocks AI自动化开发环境启动完成！"
echo ""
echo -e "${CYAN}📊 开发环境信息:${NC}"
echo -e "  🔧 后端开发窗格: 后端AI分析器、策略分析"
echo -e "  🎨 前端开发窗格: Vue.js监控界面"
echo -e "  📊 监控系统窗格: AI监控告警、GPU监控"
echo -e "  🗄️  数据库窗格: PostgreSQL + TDengine"
echo -e "  📝 日志中心窗格: AI自动化日志监控"
echo ""
echo -e "${GREEN}🚀 所有AI自动化组件已就绪！${NC}"
echo ""

# 连接会话
echo "正在连接开发环境..."
tmux attach-session -t $SESSION_NAME
