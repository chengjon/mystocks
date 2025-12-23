#!/bin/bash

# 端口配置脚本 - 快速切换前后端端口
# 使用方法: ./set-ports.sh [frontend_port] [backend_port]

set -e

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 帮助信息
help() {
    echo -e "${YELLOW}端口配置脚本${NC}"
    echo "使用方法:"
    echo "  ./set-ports.sh [前端端口] [后端端口]"
    echo ""
    echo "示例:"
    echo "  ./set-ports.sh 3001 8001    # 前端3001，后端8001"
    echo "  ./set-ports.sh 3005        # 前端3005，后端默认8000"
    echo ""
    echo "端口范围:"
    echo "  - 前端: 3000-3009"
    echo "  - 后端: 8000-8009"
}

# 检查端口是否在允许范围内
check_port_range() {
    local port=$1
    local type=$2

    if [ "$type" = "frontend" ]; then
        if [ "$port" -lt 3000 ] || [ "$port" -gt 3009 ]; then
            echo -e "${RED}错误: 前端端口 $port 不在允许范围 (3000-3009)${NC}"
            exit 1
        fi
    elif [ "$type" = "backend" ]; then
        if [ "$port" -lt 8000 ] || [ "$port" -gt 8009 ]; then
            echo -e "${RED}错误: 后端端口 $port 不在允许范围 (8000-8009)${NC}"
            exit 1
        fi
    fi
}

# 更新.env文件
update_env() {
    local frontend_port=$1
    local backend_port=$2

    echo -e "${GREEN}更新端口配置...${NC}"

    # 备份.env文件
    cp "$PROJECT_ROOT/.env" "$PROJECT_ROOT/.env.backup"

    # 更新前端端口
    sed -i "s/^FRONTEND_PORT_RANGE_START=.*/FRONTEND_PORT_RANGE_START=$frontend_port/" "$PROJECT_ROOT/.env"
    sed -i "s/^FRONTEND_PORT_RANGE_END=.*/FRONTEND_PORT_RANGE_END=3009/" "$PROJECT_ROOT/.env"

    # 更新后端端口
    sed -i "s/^BACKEND_HOST=.*/BACKEND_HOST=0.0.0.0/" "$PROJECT_ROOT/.env"
    sed -i "s/^BACKEND_PORT=.*/BACKEND_PORT=$backend_port/" "$PROJECT_ROOT/.env"

    # 更新CORS配置
    local cors_origins=""
    for i in {3000..3009}; do
        if [ "$i" -eq "$frontend_port" ]; then
            cors_origins="$cors_originshttp://localhost:$i"
        else
            cors_origins="$cors_originshttp://localhost:$i,"
        fi
    done
    cors_origins="${cors_origins%,}"

    sed -i "s|^CORS_ORIGINS=.*|CORS_ORIGINS=$cors_origins|" "$PROJECT_ROOT/.env"

    # 更新API基础URL
    sed -i "s|^VITE_API_BASE_URL=.*|VITE_API_BASE_URL=http://localhost:$backend_port|" "$PROJECT_ROOT/.env"

    echo -e "${GREEN}✅ 端口配置已更新${NC}"
    echo "  - 前端端口: $frontend_port"
    echo "  - 后端端口: $backend_port"
    echo ""
    echo -e "${YELLOW}使用新端口启动服务:${NC}"
    echo "  前端: npm run dev -- --port $frontend_port"
    echo "  后端: python -m uvicorn app.main:app --host 0.0.0.0 --port $backend_port"
}

# 检查端口是否被占用
check_port_usage() {
    local port=$1
    local type=$2

    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}警告: 端口 $port 已被占用${NC}"
        read -p "是否继续? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "已取消"
            exit 1
        fi
    fi
}

# 主逻辑
main() {
    if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
        help
        exit 0
    fi

    # 获取端口参数
    local frontend_port=${1:-3000}
    local backend_port=${2:-8000}

    # 验证端口范围
    check_port_range "$frontend_port" "frontend"
    check_port_range "$backend_port" "backend"

    # 检查端口使用情况
    check_port_usage "$frontend_port" "frontend"
    check_port_usage "$backend_port" "backend"

    # 更新配置
    update_env "$frontend_port" "$backend_port"
}

# 运行主函数
main "$@"