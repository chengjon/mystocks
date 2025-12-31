#!/bin/bash
###############################################################################
# PM2日志轮转设置脚本
#
# 安装和配置pm2-logrotate模块
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
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo "=========================================="
echo "PM2日志轮转设置"
echo "=========================================="
echo ""

# 项目路径
BACKEND_DIR="/opt/claude/mystocks_phase7_backend/web/backend"

# 检查PM2是否安装
if ! command -v pm2 &> /dev/null; then
    print_error "PM2未安装，请先安装: npm install -g pm2"
    exit 1
fi

print_info "检查pm2-logrotate模块..."

# 检查pm2-logrotate是否已安装
if pm2 list | grep -q "pm2-logrotate"; then
    print_warning "pm2-logrotate已安装，将重新配置"
    pm2 uninstall pm2-logrotate
    sleep 2
fi

# 安装pm2-logrotate
print_info "安装pm2-logrotate模块..."
pm2 install pm2-logrotate

# 等待安装完成
sleep 3

# 配置pm2-logrotate
print_info "配置pm2-logrotate..."

# 设置日志文件最大大小
pm2 set pm2-logrotate:max_size 100M

# 设置保留的日志文件数量
pm2 set pm2-logrotate:retain 7

# 设置是否压缩
pm2 set pm2-logrotate:compress true

# 设置压缩级别
pm2 set pm2-logrotate:compressLevel 9

# 设置日期格式
pm2 set pm2-logrotate:dateFormat 'YYYY-MM-DD_HH-mm-ss'

# 设置轮转间隔
pm2 set pm2-logrotate:rotateInterval '0 0 * * *'

# 创建日志归档目录
ARCHIVE_DIR="$BACKEND_DIR/logs/archive"
mkdir -p "$ARCHIVE_DIR"

print_success "日志归档目录: $ARCHIVE_DIR"

echo ""
print_success "PM2日志轮转配置完成!"
echo ""

# 显示配置
print_info "当前配置:"
pm2 conf | grep logrotate || echo "pm2-logrotate配置已应用"

echo ""
print_info "日志轮转规则:"
echo "  - 最大文件大小: 100MB"
echo "  - 保留文件数量: 7个"
echo "  - 压缩: 启用"
echo "  - 轮转间隔: 每天午夜"
echo ""

print_info "手动轮转命令:"
echo "  pm2 flush             # 清空所有日志"
echo "  pm2 reloadLogs        # 重载所有日志"
echo ""
