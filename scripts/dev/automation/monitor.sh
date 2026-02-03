#!/bin/bash

# ===================================
# MyStocks 监控定时脚本
# 版本: v1.0
# 描述: 定期检查系统健康状态
# ===================================

# 配置
PROJECT_ROOT="/opt/claude/mystocks_spec"
HEALTH_SCRIPT="${PROJECT_ROOT}/scripts/automation/health_check_simple.sh"
LOG_DIR="/opt/mystocks/logs"
MONITOR_LOG="${LOG_DIR}/monitor.log"
CHECK_INTERVAL=300  # 默认5分钟检查一次（300秒）

# 函数：记录日志
log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$MONITOR_LOG"
}

# 显示使用信息
show_usage() {
    echo "MyStocks 监控定时脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help         显示此帮助信息"
    echo "  -i, --interval     设置检查间隔（秒），默认：$CHECK_INTERVAL"
    echo "  -t, --times        设置检查次数，-1表示无限次数"
    echo "  -n, --no-daemon    不在后台运行，直接执行一次"
    echo ""
    echo "示例:"
    echo "  $0                 # 在后台每5分钟检查一次，无限次"
    echo "  $0 -i 300 -t 10    # 每5分钟检查一次，共10次"
    echo "  $0 -i 60           # 每分钟检查一次，无限次"
    echo "  $0 -n              # 不后台运行，直接执行一次"
}

# 函数：执行健康检查
run_health_check() {
    log "开始执行健康检查..."

    # 确保健康检查脚本存在且可执行
    if [[ ! -x "$HEALTH_SCRIPT" ]]; then
        log "健康检查脚本不存在或不可执行: $HEALTH_SCRIPT"
        return 1
    fi

    # 执行健康检查脚本
    if bash "$HEALTH_SCRIPT" > /dev/null 2>&1; then
        log "健康检查完成: 正常"
        return 0
    else
        log "健康检查完成: 发现异常"
        return 1
    fi
}

# 函数：循环监控
monitor_loop() {
    local interval=$1
    local times=$2

    log "开始监控模式: 间隔=${interval}秒, 次数=${times}"

    local count=0
    while [[ $times -eq -1 || $count -lt $times ]]; do
        # 执行健康检查
        if run_health_check; then
            log "系统状态: 正常"
        else
            log "系统状态: 异常"
            # 在这里可以添加告警通知逻辑
        fi

        # 计算下次执行时间
        count=$((count + 1))
        if [[ $times -eq -1 || $count -lt $times ]]; then
            log "下次检查时间: $(date -d +${interval} seconds '+%Y-%m-%d %H:%M:%S')"
            sleep "$interval"
        fi
    done

    log "监控任务完成"
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            show_usage
            exit 0
            ;;
        -i|--interval)
            CHECK_INTERVAL=$2
            shift 2
            ;;
        -t|--times)
            CHECK_TIMES=$2
            shift 2
            ;;
        -n|--no-daemon)
            NO_DAEMON=true
            shift
            ;;
        *)
            echo "未知选项: $1"
            show_usage
            exit 1
            ;;
    esac
done

# 设置默认检查次数（如果未设置）
if [[ -z "${CHECK_TIMES}" ]]; then
    CHECK_TIMES=-1  # 无限次
fi

# 创建日志目录
mkdir -p "$LOG_DIR"

# 执行监控任务
if [[ "$NO_DAEMON" == true ]]; then
    # 不后台运行，直接执行一次
    log "执行单次健康检查..."
    run_health_check
else
    # 后台运行监控任务
    log "启动后台监控任务..."
    nohup bash "$0" -n -i "$CHECK_INTERVAL" -t "$CHECK_TIMES" > "$MONITOR_LOG" 2>&1 &
    MONITOR_PID=$!
    log "监控任务已启动，PID: $MONITOR_PID"

    # 记录PID到文件，便于管理
    echo "$MONITOR_PID" > "${LOG_DIR}/monitor.pid"
    log "PID已保存到: ${LOG_DIR}/monitor.pid"
fi
