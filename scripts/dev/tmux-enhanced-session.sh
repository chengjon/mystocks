#!/bin/bash
# MyStocks增强版tmux会话配置脚本
# 版本: 2.0 Enhanced
# 作者: MyStocks开发团队
# 创建日期: 2026-01-27

# 会话配置
SESSION_NAME="mystocks_dev"
PROJECT_ROOT="/opt/claude/mystocks_spec"
LOG_DIR="$PROJECT_ROOT/logs"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=== MyStocks Enhanced Tmux Session ====${NC}"
    echo -e "${BLUE}会话名称: $SESSION_NAME${NC}"
    echo -e "${BLUE}项目根目录: $PROJECT_ROOT${NC}"
    echo ""
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    # 检查tmux是否安装
    if ! command -v tmux &> /dev/null; then
        log_error "tmux未安装，请先安装tmux"
        exit 1
    fi
    
    # 检查PM2是否安装
    if ! command -v pm2 &> /dev/null; then
        log_warn "PM2未安装，尝试使用基础pm2"
        PM2_CMD="pm2"
    else
        log_info "PM2已安装，使用增强版配置"
        PM2_CMD="pm2"
    fi
    
    # 检查lnav是否安装（用于日志分析）
    if ! command -v lnav &> /dev/null; then
        log_warn "lnav未安装，日志分析功能将受限"
        LNAV_AVAILABLE=false
    else
        log_info "lnav已安装，启用高级日志分析"
        LNAV_AVAILABLE=true
    fi
    
    # 检查基本工具
    for cmd in git docker; do
        if ! command -v $cmd &> /dev/null; then
            log_error "$cmd 未安装，请先安装"
            exit 1
        fi
    done
    
    log_info "依赖检查通过"
}

# 创建开发环境会话
create_dev_session() {
    log_info "创建MyStocks增强开发会话..."
    
    # 检查会话是否已存在
    if tmux has-session -t $SESSION_NAME 2>/dev/null; then
        log_warn "会话 $SESSION_NAME 已存在，将删除后重建"
        tmux kill-session -t $SESSION_NAME 2>/dev/null || true
    fi
    
    # 创建新会话 - 增强功能窗口
    tmux new-session -d -s $SESSION_NAME -c "$PROJECT_ROOT"
    
    # 窗口1: PM2应用管理和监控面板
    tmux new-window -t $SESSION_NAME -n pm2-manager -c "$PROJECT_ROOT"
    tmux send-keys -t $SESSION_NAME:pm2-manager.0 "echo 'PM2增强管理面板'; echo '执行: $PM2_CMD start ecosystem.enhanced.config.js'; echo '状态: 检查应用状态...'; echo '监控: 系统资源监控'" C-m
    
    # 分割面板 - 数据库监控
    tmux split-window -h -t $SESSION_NAME -n databases -c "$PROJECT_ROOT"
    # 子面板1: TDengine监控
    tmux send-keys -t $SESSION_NAME:databases.0 "echo 'TDengine数据库监控'; echo '执行: docker stats mystocks-tdengine'; echo '日志: tail -f logs/database/tdengine*.log'" C-m
    # 子面板2: PostgreSQL监控  
    tmux send-keys -t $SESSION_NAME:databases.1 "echo 'PostgreSQL数据库监控'; echo '执行: docker stats mystocks-postgresql'; echo '日志: tail -f logs/database/postgresql*.log'" C-m
    
    # 窗口2: 自动化监控面板
    tmux new-window -t $SESSION_NAME -n monitoring -c "$PROJECT_ROOT"
    tmux send-keys -t $SESSION_NAME:monitoring.0 "echo '自动化监控面板'; echo '执行: python scripts/automation/monitor_and_fix.py --daemon'; echo '日志: tail -f /tmp/monitoring.log'; echo 'Webhook: \$ALERT_WEBHOOK_URL'" C-m
    tmux send-keys -t $SESSION_NAME:monitoring.1 "echo '监控状态检查'; echo '执行: python scripts/automation/monitor_and_fix.py --check-once'" C-m
    tmux send-keys -t $SESSION_NAME:monitoring.2 "echo '告警管理'; echo 'Webhook通知: \$ALERT_WEBHOOK_URL'" C-m
    
    # 窗口3: 高级日志分析（如果lnav可用）
    if [ "$LNAV_AVAILABLE" = true ]; then
        tmux split-window -v -t $SESSION_NAME -n logs-analysis -c "$PROJECT_ROOT"
        tmux send-keys -t $SESSION_NAME:logs-analysis.0 "echo 'lnav增强日志分析'; echo '执行: lnav -c config/lnav_formats.json logs/api/*/*'" C-m
        tmux send-keys -t $SESSION_NAME:logs-analysis.1 "echo '实时错误日志'; echo '执行: lnav -c config/lnav_formats.json logs/api/*/* --filter-in log_level IN (ERROR, CRITICAL)'" C-m
        tmux send-keys -t $SESSION_NAME:logs-analysis.2 "echo '性能监控日志'; echo '执行: lnav -c config/lnav_formats.json logs/api/*/* --filter-in response_time > 1000'" C-m
        tmux send-keys -t $SESSION_NAME:logs-analysis.3 "echo '日志导出功能'; echo '执行: lnav -c config/lnav_formats.json logs/api/*/* :export-to-json'" C-m
        tmux send-keys -t $SESSION_NAME:logs-analysis.4 "echo '搜索和过滤'; echo '命令: :filter-in <pattern>, :stats, :db <sql>'" C-m
    fi
    
    # 窗口4: 系统资源监控
    tmux new-window -t $SESSION_NAME -n system-monitor -c "$PROJECT_ROOT"
    tmux send-keys -t $SESSION_NAME:system-monitor.0 "echo '系统资源监控'; echo '执行: watch -n 1 -d 60 -t \"(CPU|Memory|Disk):\"% \"echo '使用率超过阈值时告警'\"'" C-m
    tmux send-keys -t $SESSION_NAME:system-monitor.1 "echo '磁盘空间监控'; echo '执行: df -h | grep -E \"^/dev/\" | head -10'" C-m
    tmux send-keys -t $SESSION_NAME:system-monitor.2 "echo '进程监控'; echo '执行: ps aux | head -20'" C-m
    
    # 窗口5: 开发工具和交互式Python环境
    tmux new-window -t $SESSION_NAME -n dev-tools -c "$PROJECT_ROOT"
    tmux send-keys -t $SESSION_NAME:dev-tools.0 "echo '开发工具面板'; echo 'Python环境: \$PYTHONPATH'; echo '当前目录: \$(pwd)'" C-m
    tmux send-keys -t $SESSION_NAME:dev-tools.1 "echo 'Git操作'; echo '执行: git status; git add .; git commit -m \"\$(date +\"%Y-%m-%d %H:%M:%S\")\"'" C-m
    tmux send-keys -t $SESSION_NAME:dev-tools.2 "echo '包管理'; echo '执行: pip list; pip install <package>'" C-m
    tmux send-keys -t $SESSION_NAME:dev-tools.3 "echo '数据库连接测试'; echo '执行: python -c \"from unified_manager import MyStocksUnifiedManager; manager = MyStocksUnifiedManager(); print(manager.initialize_system())\"'" C-m
    
    # 选择第一个窗口
    tmux select-window -t $SESSION_NAME:pm2-manager
    
    log_info "MyStocks增强开发会话创建完成"
    log_info ""
    log_info "窗口说明："
    log_info "  Window 0: PM2管理面板 - 应用启动/停止/重启/状态查看"
    log_info "  Window 1: 数据库监控 - TDengine/PostgreSQL状态监控"
    log_info "  Window 2: 自动化监控 - 系统监控/告警/日志分析"
    if [ "$LNAV_AVAILABLE" = true ]; then
        log_info "  Window 3: 日志分析 - lnav高级日志分析"
    log_info "  Window 4: 系统监控 - 资源使用率监控"
    log_info "  Window 5: 开发工具 - Python环境和开发工具"
    log_info ""
    log_info "快捷键提示："
    log_info "  Ctrl+B 窗口列表"
    log_info "  Ctrl+O 在窗口间切换"
    log_info "  Ctrl+T 新建窗口"
    log_info "  Ctrl+& 分割面板"
    log_info "  Ctrl+X 关闭当前窗口"
    log_info "  :  进入命令模式"
    log_info "  q 退出日志分析模式"
    log_info ""
    log_info "使用 $PM2_CMD 管理应用进程"
}

# 连接到会话
attach_session() {
    if [ -z "$TMUX" ]; then
        log_info "连接到会话 $SESSION_NAME"
        tmux attach-session -t $SESSION_NAME
    else
        log_warn "已经在tmux会话中，无法附加到其他会话"
    fi
}

# 列出所有会话
list_sessions() {
    log_info "当前tmux会话:"
    tmux list-sessions 2>/dev/null || log_warn "没有活动的tmux会话"
}

# 关闭会话
kill_session() {
    if tmux has-session -t $SESSION_NAME 2>/dev/null; then
        log_info "关闭会话 $SESSION_NAME"
        tmux kill-session -t $SESSION_NAME
    else
        log_warn "会话 $SESSION_NAME 不存在"
    fi
}

# 显示帮助信息
show_help() {
    cat << EOF
MyStocks Enhanced Tmux Session Manager

用法: $0 [选项]

选项:
  start     创建并启动MyStocks增强开发会话
  attach    连接到现有会话
  list      列出所有会话
  kill      关闭MyStocks会话
  help      显示此帮助信息

示例:
  $0 start   # 创建开发环境会话
  $0 attach  # 连接到会话
  $0 list    # 列出所有会话

增强功能 (v2.0):
  • 6个功能窗口：PM2管理、数据库监控、自动化监控、日志分析、系统监控、开发工具
  • 智能健康检查和自动重启策略
  • 高级日志分析和错误处理
  • 系统资源监控和告警
  • lnav集成（如果可用）

快捷键：
  Ctrl+B  窗口列表
  Ctrl+O  在窗口间切换
  Ctrl+T  新建窗口
  Ctrl+&  分割面板
  Ctrl+X  关闭当前窗口
  :      进入命令模式
  q      退出日志分析模式

EOF
}

# 主函数
main() {
    case "$1" in
        start)
            check_dependencies
            create_dev_session
            if [ $? -eq 0 ]; then
                attach_session
            fi
            ;;
        attach)
            attach_session
            ;;
        list)
            list_sessions
            ;;
        kill)
            kill_session
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"