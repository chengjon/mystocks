#!/bin/bash

# lnav 日志分析启动脚本
# 用于实时日志监控和分析

set -e

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    print_info "检查依赖..."

    if ! command -v lnav &> /dev/null; then
        print_error "lnav 未安装"
        exit 1
    fi

    print_info "依赖检查通过"
}

# 创建日志目录
setup_log_dirs() {
    print_info "创建日志目录..."

    mkdir -p logs/{api,e2e,frontend,backend,database}

    print_info "日志目录创建完成"
}

# 显示帮助信息
show_help() {
    cat << EOF
lnav 日志分析启动脚本

用法: ./lnav-monitor.sh [选项]

选项:
  all                 监控所有日志
  api                 监控API测试日志
  e2e                 监控E2E测试日志
  backend             监控后端日志
  frontend            监控前端日志
  database            监控数据库日志
  errors              仅显示错误日志
  performance         显示性能日志
  export [format]     导出日志 (json, csv, html)
  filter [pattern]   筛选日志
  help                显示此帮助信息

示例:
  ./lnav-monitor.sh all
  ./lnav-monitor.sh errors
  ./lnav-monitor.sh filter "/api/auth/"
  ./lnav-monitor.sh export json

lnav 快捷键:
  q                   退出
  /                   搜索
  n                   下一个匹配
  N                   上一个匹配
  :filter-in <expr>   筛选包含表达式的行
  :filter-out <expr>  排除包含表达式的行
  :stats              显示统计信息
  :db <sql>           执行SQL查询
EOF
}

# 启动 lnav 监控
start_monitoring() {
    local log_pattern=$1
    local description=$2

    print_info "启动 lnav 监控: ${description}"
    print_info "日志模式: ${log_pattern}"
    print_info ""
    print_info "快捷键提示:"
    print_info "  q - 退出"
    print_info "  :filter-in <expr> - 筛选日志"
    print_info "  :stats - 显示统计"
    print_info ""

    sleep 1

    lnav -d -I -c ":goto first" -c ":stats" ${log_pattern}
}

# 导出日志
export_logs() {
    local format=${1:-json}
    local output_file="logs/export_$(date +%Y%m%d_%H%M%S).${format}"

    print_info "导出日志到: ${output_file}"

    case "$format" in
        json)
            lnav -d -c ":export-to-json ${output_file}" logs/*/*
            ;;
        csv)
            lnav -d -c ":export-to-csv ${output_file}" logs/*/*
            ;;
        html)
            lnav -d -c ":export-to-html ${output_file}" logs/*/*
            ;;
        *)
            print_error "不支持的导出格式: ${format}"
            exit 1
            ;;
    esac

    print_info "导出完成: ${output_file}"
}

# 筛选日志
filter_logs() {
    local pattern=$1

    if [ -z "$pattern" ]; then
        print_error "请提供筛选模式"
        exit 1
    fi

    print_info "筛选日志: ${pattern}"
    print_info "使用 :filter-out 退出筛选模式"

    lnav -d -c ":filter-in ${pattern}" logs/*/*
}

# 主逻辑
case "$1" in
    all)
        check_dependencies
        setup_log_dirs
        start_monitoring "logs/*/*" "所有日志"
        ;;
    api)
        check_dependencies
        setup_log_dirs
        start_monitoring "logs/api/*" "API测试日志"
        ;;
    e2e)
        check_dependencies
        setup_log_dirs
        start_monitoring "logs/e2e/*" "E2E测试日志"
        ;;
    backend)
        check_dependencies
        setup_log_dirs
        start_monitoring "logs/backend/*" "后端日志"
        ;;
    frontend)
        check_dependencies
        setup_log_dirs
        start_monitoring "logs/frontend/*" "前端日志"
        ;;
    database)
        check_dependencies
        setup_log_dirs
        start_monitoring "logs/database/*" "数据库日志"
        ;;
    errors)
        check_dependencies
        print_info "显示错误日志"
        lnav -d -c ":filter-in log_level IN (ERROR, CRITICAL)" logs/*/*
        ;;
    performance)
        check_dependencies
        print_info "显示性能日志 (响应时间 > 1s)"
        lnav -d -c ":filter-in response_time > 1000" logs/api/*
        ;;
    export)
        check_dependencies
        if [ -z "$2" ]; then
            export_logs "json"
        else
            export_logs "$2"
        fi
        ;;
    filter)
        check_dependencies
        if [ -z "$2" ]; then
            print_error "请提供筛选模式"
            exit 1
        fi
        filter_logs "$2"
        ;;
    help|--help|-h)
        show_help
        ;;
    "")
        show_help
        ;;
    *)
        print_error "未知选项: $1"
        show_help
        exit 1
        ;;
esac
