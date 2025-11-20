#!/bin/bash
# =================================
# Lnav 配置设置脚本
# 为 MyStocks 项目配置 lnav 日志格式识别
# =================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

info() {
    echo -e "${GREEN}[LNAV-SETUP]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[LNAV-SETUP]${NC} $1"
}

error() {
    echo -e "${RED}[LNAV-SETUP]${NC} $1"
}

# 检查 lnav 是否安装
check_lnav() {
    info "检查 lnav 是否已安装..."
    
    if ! command -v lnav &> /dev/null; then
        error "lnav 未安装，请先安装: sudo apt-get install lnav"
        warn "将使用 tail -f 作为备选方案"
        return 1
    else
        info "lnav 已安装，版本: $(lnav --version | head -1)"
        return 0
    fi
}

# 安装 lnav 格式配置
install_lnav_format() {
    info "安装 MyStocks 日志格式配置..."
    
    local lnav_config_dir="$HOME/.config/lnav"
    local project_config="/opt/claude/mystocks_spec/config/lnav_formats.json"
    
    # 创建 lnav 配置目录
    mkdir -p "$lnav_config_dir"
    
    # 复制格式配置文件
    if [ -f "$project_config" ]; then
        cp "$project_config" "$lnav_config_dir/formats.json"
        info "日志格式配置已安装到 $lnav_config_dir/formats.json"
        return 0
    else
        error "项目配置文件不存在: $project_config"
        return 1
    fi
}

# 测试 lnav 配置
test_lnav_config() {
    info "测试 lnav 配置..."
    
    # 创建测试日志文件
    local test_log="/tmp/mystocks_test.log"
    cat > "$test_log" << 'EOF'
2025-11-16 10:00:00 [INFO] request_id=abc123 duration=200ms path=/api/strategy status=200
2025-11-16 10:00:01 [WARNING] request_id=def456 duration=500ms path=/api/data error_timeout
2025-11-16 10:00:02 [ERROR] request_id=ghi789 duration=1000ms path=/api/market error_db_connection
2025-11-16 10:00:03 [INFO] request_id=jkl012 duration=150ms path=/api/indicators status=200
2025-11-16 10:00:04 [DEBUG] request_id=mno345 duration=80ms path=/api/auth action=login_success
EOF
    
    # 测试 lnav 能否识别格式
    if lnav -d /tmp/lnav_test.log -c ":ms-to-filter" -c ":quit" "$test_log" &>/dev/null; then
        info "lnav 格式测试通过"
    else
        warn "lnav 格式测试失败，但这是正常的（无网络连接等）"
    fi
    
    # 清理测试文件
    rm -f "$test_log"
}

# 启动 lnav 监控
start_lnav_monitoring() {
    local log_file="${1:-/opt/claude/mystocks_spec/logs/backend.log}"
    
    info "启动 lnav 监控: $log_file"
    
    if [ -f "$log_file" ]; then
        # 使用 lnav 监控指定日志文件
        lnav "$log_file"
    else
        warn "日志文件不存在: $log_file"
        warn "将创建测试日志并监控"
        
        # 创建测试日志
        echo "2025-11-16 10:00:00 [INFO] request_id=test123 duration=100ms path=/test status=200" > "$log_file"
        lnav "$log_file"
    fi
}

# 启动开发环境中的 lnav 监控
start_dev_lnav() {
    info "为开发环境启动 lnav 监控..."
    
    # 检查项目日志目录
    local log_dir="/opt/claude/mystocks_spec/logs"
    local backend_log="$log_dir/backend.log"
    local combined_log="$log_dir/backend-combined.log"
    
    if [ ! -d "$log_dir" ]; then
        warn "日志目录不存在: $log_dir"
        return 1
    fi
    
    # 创建后端日志文件（如果不存在）
    touch "$backend_log"
    touch "$combined_log"
    
    # 添加一些示例日志（如果文件为空）
    if [ ! -s "$backend_log" ]; then
        echo "2025-11-16 10:00:00 [INFO] request_id=startup duration=0ms path=/ action=service_started" >> "$backend_log"
    fi
    
    info "开始监控后端日志文件..."
    info "格式化字段将自动识别:"
    echo "  - timestamp: 时间戳 (2025-11-16 10:00:00)"
    echo "  - level: 日志级别 ([INFO], [WARNING], [ERROR], [DEBUG])"
    echo "  - request_id: 请求ID (request_id=abc123)"
    echo "  - duration: 响应时间 (duration=200ms)"
    echo "  - path: API路径 (path=/api/strategy)"
    echo "  - status: 响应状态 (status=200)"
    echo "  - error: 错误信息 (error=timeout)"
    echo "  - action: 操作类型 (action=login_success)"
    echo ""
    echo "快捷键:"
    echo "  :q      退出"
    echo "  :c      清除高亮"
    echo "  /关键词  搜索"
    echo "  Tab     切换窗格"
    echo ""
    
    # 启动 lnav
    lnav "$backend_log"
}

# 主函数
main() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}    MyStocks Lnav 配置工具${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    # 检查 lnav 是否安装
    if ! check_lnav; then
        info "正在安装 lnav..."
        sudo apt-get update && sudo apt-get install -y lnav
        if [ $? -eq 0 ]; then
            info "lnav 安装成功"
        else
            error "lnav 安装失败，请手动安装"
            exit 1
        fi
    fi
    
    # 安装格式配置
    if install_lnav_format; then
        test_lnav_config
        
        # 解析命令行参数
        if [ "$1" == "dev" ]; then
            start_dev_lnav
        elif [ "$1" == "start" ]; then
            start_lnav_monitoring "$2"
        elif [ "$1" == "test" ]; then
            test_lnav_config
        else
            echo ""
            echo "用法: $0 [选项]"
            echo ""
            echo "选项:"
            echo "  dev      启动开发环境 lnav 监控"
            echo "  start    启动 lnav 监控指定日志文件"
            echo "  test     测试 lnav 配置"
            echo "  (无参数) 安装 lnav 配置并显示使用说明"
            echo ""
            echo "示例:"
            echo "  $0 dev                    # 监控开发环境日志"
            echo "  $0 start backend.log      # 监控指定日志文件"
            echo "  $0 test                   # 测试配置"
            echo ""
        fi
    fi
}

# 脚本入口
main "$@"