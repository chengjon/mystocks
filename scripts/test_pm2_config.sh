#!/bin/bash
###############################################################################
# PM2配置验证脚本
#
# 验证PM2配置文件的正确性和完整性
#
# Author: Backend CLI (Claude Code)
# Date: 2025-12-31
###############################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

echo "=========================================="
echo "PM2配置验证脚本"
echo "=========================================="
echo ""

PROJECT_ROOT="/opt/claude/mystocks_phase7_backend"
BACKEND_DIR="$PROJECT_ROOT/web/backend"
PM2_CONFIG="$BACKEND_DIR/ecosystem.config.js"
LOG_DIR="$BACKEND_DIR/logs"
RUN_SCRIPT="$BACKEND_DIR/run_server.py"

# 检查计数
checks_passed=0
checks_failed=0

###############################################################################
# 验证函数
###############################################################################

check_pm2_installed() {
    print_info "检查PM2是否安装..."
    if command -v pm2 &> /dev/null; then
        local version=$(pm2 --version)
        print_success "PM2已安装 (版本: $version)"
        ((checks_passed++))
    else
        print_error "PM2未安装"
        ((checks_failed++))
    fi
}

check_config_file() {
    print_info "检查PM2配置文件..."
    if [ -f "$PM2_CONFIG" ]; then
        print_success "配置文件存在: $PM2_CONFIG"
        ((checks_passed++))

        # 检查配置文件语法
        print_info "验证配置文件语法..."
        if node -c "$PM2_CONFIG" 2>/dev/null; then
            print_success "配置文件语法正确"
            ((checks_passed++))
        else
            print_error "配置文件语法错误"
            ((checks_failed++))
        fi
    else
        print_error "配置文件不存在: $PM2_CONFIG"
        ((checks_failed++))
    fi
}

check_run_script() {
    print_info "检查运行脚本..."
    if [ -f "$RUN_SCRIPT" ]; then
        print_success "运行脚本存在: $RUN_SCRIPT"
        ((checks_passed++))
    else
        print_error "运行脚本不存在: $RUN_SCRIPT"
        ((checks_failed++))
    fi
}

check_log_directory() {
    print_info "检查日志目录..."
    if [ -d "$LOG_DIR" ]; then
        print_success "日志目录存在: $LOG_DIR"
        ((checks_passed++))
    else
        print_warning "日志目录不存在，将创建: $LOG_DIR"
        mkdir -p "$LOG_DIR"
        if [ -d "$LOG_DIR" ]; then
            print_success "日志目录已创建"
            ((checks_passed++))
        else
            print_error "无法创建日志目录"
            ((checks_failed++))
        fi
    fi
}

check_python() {
    print_info "检查Python环境..."
    if command -v python3 &> /dev/null; then
        local version=$(python3 --version)
        print_success "Python已安装: $version"
        ((checks_passed++))
    else
        print_error "Python3未安装"
        ((checks_failed++))
    fi
}

check_dependencies() {
    print_info "检查Python依赖..."
    cd "$BACKEND_DIR"

    # 检查关键依赖
    local dependencies=("fastapi" "uvicorn" "pydantic")
    local missing=0

    for dep in "${dependencies[@]}"; do
        if python3 -c "import $dep" 2>/dev/null; then
            ((checks_passed++))
        else
            print_warning "缺少依赖: $dep"
            ((missing++))
        fi
    done

    if [ $missing -eq 0 ]; then
        print_success "所有关键依赖已安装"
    else
        print_warning "缺少 $missing 个依赖，请运行: pip install -r requirements.txt"
    fi
}

check_config_content() {
    print_info "检查配置文件内容..."

    # 检查关键配置项
    local required_keys=("name" "script" "cwd" "instances" "env")
    local config_content=$(cat "$PM2_CONFIG")

    for key in "${required_keys[@]}"; do
        if echo "$config_content" | grep -q "$key"; then
            ((checks_passed++))
        else
            print_error "缺少配置项: $key"
            ((checks_failed++))
        fi
    done

    print_success "配置内容检查完成"
}

check_environment_variables() {
    print_info "检查环境变量..."

    # 检查.env文件
    if [ -f "$BACKEND_DIR/.env" ]; then
        print_success "环境变量文件存在: .env"
        ((checks_passed++))
    else
        print_warning "环境变量文件不存在: .env（可选）"
    fi
}

###############################################################################
# 执行检查
###############################################################################

echo "开始验证PM2配置..."
echo ""

check_pm2_installed
check_config_file
check_run_script
check_log_directory
check_python
check_dependencies
check_config_content
check_environment_variables

echo ""
echo "=========================================="
echo "验证结果汇总"
echo "=========================================="
echo ""
echo -e "通过: ${GREEN}$checks_passed${NC}"
echo -e "失败: ${RED}$checks_failed${NC}"
echo ""

if [ $checks_failed -eq 0 ]; then
    echo -e "${GREEN}所有检查通过！PM2配置正确。${NC}"
    echo ""
    echo "下一步操作:"
    echo "  启动服务: ./scripts/pm2_manager.sh start"
    echo "  查看状态: ./scripts/pm2_manager.sh status"
    echo "  健康检查: ./scripts/pm2_manager.sh health"
    exit 0
else
    echo -e "${RED}部分检查失败，请修复后重试。${NC}"
    exit 1
fi
