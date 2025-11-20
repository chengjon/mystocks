#!/bin/bash
# MyStocks系统启动和监控一体化脚本
# 集成tmux会话管理和lnav日志监控
# 作者: MyStocks开发团队

# 配置变量
PROJECT_ROOT="/opt/claude/mystocks_spec"
LOG_DIR="$PROJECT_ROOT/logs"
CONFIG_DIR="$PROJECT_ROOT/config"
SCRIPTS_DIR="$PROJECT_ROOT/scripts"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

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

log_success() {
    echo -e "${CYAN}[SUCCESS]${NC} $1"
}

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    # 检查tmux
    if ! command -v tmux &> /dev/null; then
        log_error "tmux未安装"
        exit 1
    fi
    log_info "✓ tmux可用: $(tmux -V)"
    
    # 检查lnav
    if ! command -v lnav &> /dev/null; then
        log_error "lnav未安装"
        exit 1
    fi
    log_info "✓ lnav可用: $(lnav -V)"
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_error "python3未安装"
        exit 1
    fi
    log_info "✓ Python可用: $(python3 --version)"
    
    # 检查项目目录
    if [ ! -d "$PROJECT_ROOT" ]; then
        log_error "项目目录不存在: $PROJECT_ROOT"
        exit 1
    fi
    log_info "✓ 项目目录存在"
    
    # 检查日志目录
    if [ ! -d "$LOG_DIR" ]; then
        mkdir -p "$LOG_DIR"
        log_info "✓ 创建日志目录: $LOG_DIR"
    fi
}

# 检查数据库服务
check_database_services() {
    log_info "检查数据库服务..."
    
    # 检查Docker是否运行
    if command -v docker &> /dev/null; then
        if docker ps | grep -q "tdengine|postgresql"; then
            log_info "✓ 数据库服务正在运行"
        else
            log_warn "数据库服务未运行，启动它们?"
            read -p "是否启动数据库服务? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                cd $PROJECT_ROOT
                docker-compose -f config/docker-compose.tdengine.yml up -d
                docker-compose -f config/docker-compose.postgresql.yml up -d
                log_info "数据库服务启动中..."
                sleep 10
            fi
        fi
    else
        log_warn "Docker未安装，跳过数据库检查"
    fi
}

# 创建tmux会话
create_tmux_session() {
    local session_name="${1:-mystocks_dev}"
    
    log_info "创建tmux会话: $session_name"
    
    # 检查会话是否已存在
    if tmux has-session -t $session_name 2>/dev/null; then
        log_warn "会话 $session_name 已存在"
        return 1
    fi
    
    # 创建主会话 - 数据库监控
    tmux new-session -d -s $session_name -n db -c $PROJECT_ROOT
    
    # 面板1: TDengine状态
    tmux send-keys -t $session_name:db.0 "echo 'TDengine数据库监控'; echo '等待数据库启动...'; while true; do if command -v docker &> /dev/null && docker ps | grep -q tdengine; then docker logs --tail 10 mystocks-tdengine 2>/dev/null || echo 'TDengine未运行'; else echo 'Docker或TDengine未启动'; fi; sleep 5; done" C-m
    
    # 分割面板 - PostgreSQL状态
    tmux split-window -h -t $session_name:db -c $PROJECT_ROOT
    tmux send-keys -t $session_name:db.1 "echo 'PostgreSQL数据库监控'; echo '等待数据库启动...'; while true; do if command -v docker &> /dev/null && docker ps | grep -q postgresql; then docker logs --tail 10 mystocks-postgresql 2>/dev/null || echo 'PostgreSQL未运行'; else echo 'Docker或PostgreSQL未启动'; fi; sleep 5; done" C-m
    
    # 创建服务窗口
    tmux new-window -t $session_name -n services -c $PROJECT_ROOT
    
    # 面板1: 统一管理器
    tmux send-keys -t $session_name:services.0 "echo 'MyStocks统一管理器'; echo '等待服务启动...'; cd $PROJECT_ROOT && python3 -c 'from unified_manager import MyStocksUnifiedManager; manager = MyStocksUnifiedManager(); print(\"统一管理器初始化完成\")' && tail -f $LOG_DIR/mystocks_*.log" C-m
    
    # 分割面板 - 数据访问监控
    tmux split-window -v -t $session_name:services -c $PROJECT_ROOT
    tmux send-keys -t $session_name:services.1 "echo '数据访问模块监控'; echo '实时日志...'; cd $PROJECT_ROOT && tail -f $LOG_DIR/mystocks_*.log | grep -i 'data_access\\|save\\|load'" C-m
    
    # 创建监控窗口
    tmux new-window -t $session_name -n monitoring -c $PROJECT_ROOT
    
    # 面板1: lnav日志监控
    tmux send-keys -t $session_name:monitoring.0 "echo '使用lnav监控日志'; echo '等待日志文件...'; sleep 2; if [ -d \"$LOG_DIR\" ] && [ -n \"$(ls -A $LOG_DIR)\" ]; then lnav $LOG_DIR; else echo '日志目录为空，启动示例程序生成日志...'; python3 -c 'from src.core.logging import logger; logger.info(\"示例日志\"); logger.warning(\"警告日志\"); logger.error(\"错误日志\")'; fi" C-m
    
    # 创建开发窗口
    tmux new-window -t $session_name -n dev -c $PROJECT_ROOT
    tmux send-keys -t $session_name:dev.0 "echo 'MyStocks开发环境'; echo '项目路径: $PROJECT_ROOT'; echo '日志路径: $LOG_DIR'; echo '按Ctrl+C开始开发'" C-m
    
    # 选择数据库窗口
    tmux select-window -t $session_name:db
    
    log_success "tmux会话 $session_name 创建完成"
    return 0
}

# 启动监控脚本
start_monitoring() {
    local session_name="${1:-mystocks_dev}"
    
    check_database_services
    create_tmux_session "$session_name"
    
    log_info "启动监控会话: $session_name"
    log_info "使用以下面板布局:"
    log_info "  - db窗口: 数据库状态监控"
    log_info "  - services窗口: 服务状态监控"
    log_info "  - monitoring窗口: lnav日志分析"
    log_info "  - dev窗口: 开发环境"
    
    # 连接到会话
    if [ -z "$TMUX" ]; then
        tmux attach-session -t $session_name
    else
        log_warn "已经在tmux会话中，无法附加到其他会话"
        log_info "会话列表:"
        tmux list-sessions
    fi
}

# 停止监控
stop_monitoring() {
    local session_name="${1:-mystocks_dev}"
    
    if tmux has-session -t $session_name 2>/dev/null; then
        log_info "停止监控会话: $session_name"
        tmux kill-session -t $session_name
        log_success "会话 $session_name 已关闭"
    else
        log_warn "会话 $session_name 不存在"
    fi
}

# 显示日志统计
show_log_stats() {
    if [ -d "$LOG_DIR" ]; then
        log_info "日志统计信息:"
        echo "------------------------"
        echo "日志文件数量: $(ls -1 $LOG_DIR/*.log 2>/dev/null | wc -l)"
        echo "错误日志数量: $(grep -r 'ERROR' $LOG_DIR/*.log 2>/dev/null | wc -l)"
        echo "警告日志数量: $(grep -r 'WARNING' $LOG_DIR/*.log 2>/dev/null | wc -l)"
        echo "最近的日志文件:"
        ls -laht $LOG_DIR/*.log 2>/dev/null | head -5
        echo "------------------------"
    else
        log_warn "日志目录不存在: $LOG_DIR"
    fi
}

# 使用lnav分析日志
analyze_logs() {
    if [ -d "$LOG_DIR" ] && [ -n "$(ls -A $LOG_DIR)" ]; then
        log_info "启动lnav分析日志: $LOG_DIR"
        lnav "$LOG_DIR"
    else
        log_warn "日志目录为空或不存在: $LOG_DIR"
        log_info "尝试生成示例日志..."
        python3 -c "
from src.core.logging import logger
logger.info('示例信息日志')
logger.warning('示例警告日志')
logger.error('示例错误日志')
logger.debug('示例调试日志')
"
        log_info "示例日志已生成，再次尝试启动lnav..."
        sleep 1
        if [ -d "$LOG_DIR" ] && [ -n "$(ls -A $LOG_DIR/*.log 2>/dev/null)" ]; then
            lnav "$LOG_DIR"
        else
            log_error "无法启动lnav，日志文件仍未生成"
        fi
    fi
}

# 显示帮助信息
show_help() {
    echo "MyStocks系统监控一体化脚本"
    echo "集成tmux会话管理和lnav日志监控"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  start [session_name]     创建并启动监控会话 (默认: mystocks_dev)"
    echo "  attach [session_name]    连接到现有会话 (默认: mystocks_dev)"
    echo "  stop [session_name]      停止监控会话 (默认: mystocks_dev)"
    echo "  logs                     使用lnav分析日志"
    echo "  stats                    显示日志统计信息"
    echo "  check                    检查系统依赖和状态"
    echo "  help                     显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 start                # 启动默认监控会话"
    echo "  $0 start my_session     # 启动自定义会话"
    echo "  $0 logs                 # 分析日志文件"
    echo "  $0 stats                # 查看日志统计"
}

# 主函数
main() {
    case "$1" in
        start)
            check_dependencies
            start_monitoring "${2:-mystocks_dev}"
            ;;
        attach)
            if [ -z "$TMUX" ]; then
                tmux attach-session -t "${2:-mystocks_dev}"
            else
                log_warn "已经在tmux会话中"
            fi
            ;;
        stop)
            stop_monitoring "${2:-mystocks_dev}"
            ;;
        logs)
            check_dependencies
            analyze_logs
            ;;
        stats)
            show_log_stats
            ;;
        check)
            check_dependencies
            check_database_services
            ;;
        help|--help|-h)
            show_help
            ;;
        "")
            show_help
            ;;
        *)
            log_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
