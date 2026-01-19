#!/bin/bash
# 数据库服务器状态监控脚本
# 持续监控localhost服务器状态，等待恢复

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# 配置
SERVER_IP="localhost"
CHECK_INTERVAL=30  # 30秒检查一次
NOTIFICATION_FILE="${PROJECT_ROOT}/logs/server_monitor.log"

log_info() {
    echo -e "${BLUE}[MONITOR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$NOTIFICATION_FILE"
}

log_success() {
    echo -e "${GREEN}[MONITOR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$NOTIFICATION_FILE"
}

log_warn() {
    echo -e "${YELLOW}[MONITOR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$NOTIFICATION_FILE"
}

log_error() {
    echo -e "${RED}[MONITOR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$NOTIFICATION_FILE"
}

log_critical() {
    echo -e "${PURPLE}[MONITOR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$NOTIFICATION_FILE"
}

# 创建日志目录
mkdir -p "${PROJECT_ROOT}/logs"

# 网络连通性检查
check_network() {
    local port=$1
    local service_name=$2

    if nc -z -w3 "$SERVER_IP" "$port" 2>/dev/null; then
        echo "✅"
        return 0
    else
        echo "❌"
        return 1
    fi
}

# 数据库连接检查
check_database_connection() {
    local db_type=$1
    local port=$2

    case $db_type in
        "postgresql")
            python3 -c "
import psycopg2, os, sys
os.chdir('$PROJECT_ROOT')
from dotenv import load_dotenv
load_dotenv()
try:
    conn = psycopg2.connect(
        host='$SERVER_IP',
        port='$port',
        database=os.getenv('POSTGRESQL_DATABASE'),
        user=os.getenv('POSTGRESQL_USER'),
        password=os.getenv('POSTGRESQL_PASSWORD'),
        connect_timeout=5
    )
    conn.close()
    sys.exit(0)
except:
    sys.exit(1)
" 2>/dev/null && echo "✅" || echo "❌"
            ;;
        "tdengine")
            python3 -c "
import taos, os, sys
os.chdir('$PROJECT_ROOT')
from dotenv import load_dotenv
load_dotenv()
try:
    conn = taos.connect(
        host='$SERVER_IP',
        port=$port,
        user=os.getenv('TDENGINE_USER', 'root'),
        password=os.getenv('TDENGINE_PASSWORD'),
        connect_timeout=5
    )
    conn.close()
    sys.exit(0)
except:
    sys.exit(1)
" 2>/dev/null && echo "✅" || echo "❌"
            ;;
        "mysql")
            python3 -c "
import pymysql, os, sys
os.chdir('$PROJECT_ROOT')
from dotenv import load_dotenv
load_dotenv()
try:
    conn = pymysql.connect(
        host='$SERVER_IP',
        port=$port,
        database=os.getenv('MYSQL_DATABASE'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        connect_timeout=5
    )
    conn.close()
    sys.exit(0)
except:
    sys.exit(1)
" 2>/dev/null && echo "✅" || echo "❌"
            ;;
    esac
}

# 显示状态表格
show_status_table() {
    echo ""
    echo "📊 数据库服务器状态监控 - $SERVER_IP"
    echo "=========================================="
    printf "%-12s %-8s %-10s %-10s %-10s %-10s\n" "时间" "网络" "PostgreSQL" "TDengine" "MySQL" "Redis"
    echo "--------------------------------------------------------------"

    # 网络状态
    local net_postgres=$(check_network 5438 "PostgreSQL")
    local net_tdengine=$(check_network 6030 "TDengine")
    local net_mysql=$(check_network 3306 "MySQL")
    local net_redis=$(check_network 6379 "Redis")

    # 数据库连接状态
    local db_postgres=$(check_database_connection "postgresql" 5438)
    local db_tdengine=$(check_database_connection "tdengine" 6030)
    local db_mysql=$(check_database_connection "mysql" 3306)

    printf "%-12s %-8s %-10s %-10s %-10s %-10s\n" \
           "$(date '+%H:%M:%S')" \
           "✅" \
           "$db_postgres" \
           "$db_tdengine" \
           "$db_mysql" \
           "$net_redis"
}

# 检查是否所有服务都正常
check_all_services() {
    # 检查网络
    check_network 5438 >/dev/null || return 1
    check_network 6030 >/dev/null || return 1
    check_network 3306 >/dev/null || return 1
    check_network 6379 >/dev/null || return 1

    # 检查数据库连接
    [ "$(check_database_connection "postgresql" 5438)" = "✅" ] || return 1
    [ "$(check_database_connection "tdengine" 6030)" = "✅" ] || return 1
    [ "$(check_database_connection "mysql" 3306)" = "✅" ] || return 1

    return 0
}

# 发送恢复通知
send_recovery_notification() {
    log_critical "🎉 数据库服务器已恢复！所有服务连接正常"
    log_critical "✅ 可以开始完整测试链路验证"
    log_critical "🔧 运行: ./scripts/tools/verify-database-connections.sh"

    # 创建恢复标记文件
    echo "$(date '+%Y-%m-%d %H:%M:%S')" > "${PROJECT_ROOT}/logs/server_recovered.flag"
    echo "服务器已恢复，所有数据库服务连接正常" >> "${PROJECT_ROOT}/logs/server_recovered.flag"
}

# 主监控循环
main() {
    local check_count=0
    local last_status="unknown"

    log_info "开始监控数据库服务器状态: $SERVER_IP"
    log_info "检查间隔: ${CHECK_INTERVAL}秒"
    log_info "日志文件: $NOTIFICATION_FILE"
    echo ""

    # 检查是否已经有恢复标记
    if [ -f "${PROJECT_ROOT}/logs/server_recovered.flag" ]; then
        log_warn "检测到服务器已恢复标记，退出监控"
        cat "${PROJECT_ROOT}/logs/server_recovered.flag"
        exit 0
    fi

    while true; do
        ((check_count++))

        # 显示状态表格
        show_status_table

        # 检查所有服务状态
        if check_all_services; then
            current_status="healthy"
        else
            current_status="unhealthy"
        fi

        # 状态变化检测
        if [ "$current_status" = "healthy" ] && [ "$last_status" != "healthy" ]; then
            send_recovery_notification
            break
        elif [ "$current_status" = "unhealthy" ] && [ "$last_status" != "unhealthy" ]; then
            log_error "❌ 服务器状态异常，等待恢复..."
        fi

        last_status="$current_status"

        # 显示检查计数和等待信息
        echo "检查次数: $check_count | 下次检查: $(date -d "+${CHECK_INTERVAL} seconds" '+%H:%M:%S')"
        echo "按 Ctrl+C 停止监控"
        echo ""

        sleep $CHECK_INTERVAL
    done
}

# 参数处理
case "${1:-}" in
    --once)
        log_info "执行单次状态检查"
        show_status_table
        if check_all_services; then
            log_success "所有服务正常！"
            exit 0
        else
            log_error "部分服务异常"
            exit 1
        fi
        ;;
    --help|-h)
        echo "数据库服务器状态监控工具"
        echo ""
        echo "监控 localhost 服务器的数据库服务状态"
        echo ""
        echo "用法: $0 [选项]"
        echo ""
        echo "选项:"
        echo "  --once     执行单次检查后退出"
        echo "  --help,-h  显示此帮助信息"
        echo ""
        echo "无参数运行持续监控模式"
        echo ""
        echo "监控的服务:"
        echo "  • PostgreSQL (5438)"
        echo "  • TDengine (6030)"
        echo "  • MySQL (3306)"
        echo "  • Redis (6379)"
        ;;
    *)
        main
        ;;
esac