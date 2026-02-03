#!/bin/bash
# =================================
# MyStocks 启动脚本 (使用Mock数据)
# =================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的信息
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查端口占用情况
check_ports() {
    info "检查端口占用情况..."

    # 检查后端端口 (8000)
    if lsof -i :8000 &> /dev/null; then
        warn "端口 8000 (后端) 已被占用"
        info "将尝试停止现有服务..."
        pkill -f "uvicorn app.main:app --host 0.0.0.0 --port 8000"
        sleep 2
    else
        info "端口 8000 (后端) 可用"
    fi

    # 检查前端端口 (5173)
    if lsof -i :5173 &> /dev/null; then
        warn "端口 5173 (前端) 已被占用"
        info "将尝试停止现有服务..."
        pkill -f "vite.*--port 5173"
        sleep 2
    else
        info "端口 5173 (前端) 可用"
    fi
}

# 启动后端服务
start_backend() {
    info "启动后端服务..."

    cd /opt/claude/mystocks_spec

    # 确保环境变量设置正确
    export USE_MOCK_DATA=true
    export PORT=8000

    # 检查.env文件是否存在，如果存在则加载
    if [ -f .env ]; then
        info "加载 .env 文件..."
        # 手动加载环境变量，忽略注释行和空行
        set -a  # 自动导出变量
        source <(grep -v '^#' .env | grep -v '^$')
        set +a  # 停止自动导出
    fi

    # 检查是否需要安装依赖
    if [ ! -d "web/backend/__pycache__" ]; then
        warn "后端依赖可能未安装，正在安装..."
        cd web/backend
        pip install -r requirements.txt
        cd /opt/claude/mystocks_spec
    fi

    # 启动服务
    info "在后台启动后端服务..."
    cd web/backend
    nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > /opt/claude/mystocks_spec/logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > /opt/claude/mystocks_spec/backend.pid

    cd /opt/claude/mystocks_spec

    # 等待服务启动
    for i in {1..30}; do
        if curl -s http://localhost:8000/ > /dev/null; then
            info "后端服务已启动 (PID: $BACKEND_PID)"
            return 0
        fi
        sleep 1
    done

    error "后端服务启动超时"
    return 1
}

# 启动前端服务
start_frontend() {
    info "启动前端服务..."

    cd /opt/claude/mystocks_spec/web/frontend

    # 确保环境变量设置正确
    export VITE_APP_MODE=mock
    export VITE_API_BASE_URL=http://localhost:8000

    # 检查是否需要安装依赖
    if [ ! -d "node_modules" ]; then
        warn "前端依赖可能未安装，正在安装..."
        npm install
    fi

    # 启动服务
    info "在后台启动前端服务..."
    nohup npm run dev -- --host 0.0.0.0 --port 5173 > /opt/claude/mystocks_spec/logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > /opt/claude/mystocks_spec/frontend.pid

    # 等待服务启动
    for i in {1..30}; do
        if curl -s http://localhost:5173/ > /dev/null; then
            info "前端服务已启动 (PID: $FRONTEND_PID)"
            return 0
        fi
        sleep 1
    done

    error "前端服务启动超时"
    return 1
}

# 检查服务状态
check_services() {
    info "检查服务状态..."

    # 后端检查
    if curl -s http://localhost:8000/ > /dev/null; then
        info "✅ 后端服务 (API) 正常运行"

        # 检查缓存状态
        if curl -s http://localhost:8000/api/cache/status > /dev/null; then
            info "✅ 后端缓存系统正常工作"
        else
            warn "⚠️ 后端缓存系统无法访问"
        fi
    else
        error "❌ 后端服务 (API) 未正常运行"
        return 1
    fi

    # 前端检查
    if curl -s http://localhost:5173/ > /dev/null; then
        info "✅ 前端服务正常运行"
    else
        error "❌ 前端服务未正常运行"
        return 1
    fi

    return 0
}

# 显示启动信息
show_startup_info() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}    MyStocks 服务已成功启动!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${YELLOW}访问地址:${NC}"
    echo -e "  API文档: ${BLUE}http://localhost:8000/api/docs${NC}"
    echo -e "  前端界面: ${BLUE}http://localhost:5173${NC}"
    echo -e "  系统监控: ${BLUE}http://localhost:8000/api/cache/status${NC}"
    echo ""
    echo -e "${YELLOW}Mock数据状态:${NC}"
    echo -e "  USE_MOCK_DATA: ${GREEN}已启用${NC}"
    echo ""
    echo -e "${YELLOW}日志文件:${NC}"
    echo -e "  后端日志: ${BLUE}/opt/claude/mystocks_spec/logs/backend.log${NC}"
    echo -e "  前端日志: ${BLUE}/opt/claude/mystocks_spec/logs/frontend.log${NC}"
    echo ""
    echo -e "${YELLOW}进程ID文件:${NC}"
    if [ -f /opt/claude/mystocks_spec/backend.pid ]; then
        echo -e "  后端PID: ${BLUE}$(cat /opt/claude/mystocks_spec/backend.pid)${NC}"
    fi
    if [ -f /opt/claude/mystocks_spec/frontend.pid ]; then
        echo -e "  前端PID: ${BLUE}$(cat /opt/claude/mystocks_spec/frontend.pid)${NC}"
    fi
    echo ""
}

# 停止服务
stop_services() {
    info "正在停止所有服务..."

    # 停止后端服务
    if [ -f /opt/claude/mystocks_spec/backend.pid ]; then
        BACKEND_PID=$(cat /opt/claude/mystocks_spec/backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID
            info "已停止后端服务 (PID: $BACKEND_PID)"
        else
            warn "后端服务进程不存在"
        fi
        rm -f /opt/claude/mystocks_spec/backend.pid
    fi

    # 停止前端服务
    if [ -f /opt/claude/mystocks_spec/frontend.pid ]; then
        FRONTEND_PID=$(cat /opt/claude/mystocks_spec/frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID
            info "已停止前端服务 (PID: $FRONTEND_PID)"
        else
            warn "前端服务进程不存在"
        fi
        rm -f /opt/claude/mystocks_spec/frontend.pid
    fi

    # 确保所有相关进程已停止
    pkill -f "uvicorn app.main:app --host 0.0.0.0 --port 8000" || true
    pkill -f "vite.*--port 5173" || true

    info "所有服务已停止"
}

# 显示帮助信息
show_help() {
    echo -e "${BLUE}MyStocks 启动脚本 (使用Mock数据)${NC}"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示帮助信息"
    echo "  -s, --start    启动服务 (默认)"
    echo "  -k, --stop     停止服务"
    echo "  -r, --restart  重启服务"
    echo "  -c, --check    检查服务状态"
    echo ""
    echo "示例:"
    echo "  $0             # 启动服务"
    echo "  $0 --start     # 启动服务"
    echo "  $0 --stop      # 停止服务"
    echo "  $0 --restart   # 重启服务"
    echo "  $0 --check     # 检查服务状态"
    echo ""
}

# 主函数
main() {
    local action="start"

    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -s|--start)
                action="start"
                shift
                ;;
            -k|--stop)
                action="stop"
                shift
                ;;
            -r|--restart)
                action="restart"
                shift
                ;;
            -c|--check)
                action="check"
                shift
                ;;
            *)
                error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # 显示标题
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}    MyStocks 服务启动器${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""

    # 根据操作执行相应函数
    case $action in
        start)
            check_ports
            start_backend
            start_frontend
            if check_services; then
                show_startup_info
            else
                error "服务启动失败，请检查日志"
                exit 1
            fi
            ;;
        stop)
            stop_services
            ;;
        restart)
            stop_services
            sleep 2
            check_ports
            start_backend
            start_frontend
            if check_services; then
                show_startup_info
            else
                error "服务启动失败，请检查日志"
                exit 1
            fi
            ;;
        check)
            check_services
            ;;
    esac
}

# 脚本入口
main "$@"
