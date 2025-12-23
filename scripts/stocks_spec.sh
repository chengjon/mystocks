#!/bin/bash

###############################################################################
# MyStocks Project Management Script
# 用途: 管理MyStocks项目的前端和后端服务
# 版本: v1.0
# 日期: 2025-12-10
###############################################################################

# 项目根目录
PROJECT_ROOT="/opt/claude/mystocks_spec"
FRONTEND_DIR="$PROJECT_ROOT/web/frontend"
BACKEND_DIR="$PROJECT_ROOT/web/backend"

# 默认端口配置
DEFAULT_BACKEND_PORT=8000
DEFAULT_FRONTEND_PORT=3000
BACKEND_PORT_RANGE_START=8000
BACKEND_PORT_RANGE_END=8009
FRONTEND_PORT_RANGE_START=3000
FRONTEND_PORT_RANGE_END=3009

# 日志文件
BACKEND_LOG="$BACKEND_DIR/backend.log"
FRONTEND_LOG="$FRONTEND_DIR/frontend.log"

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

###############################################################################
# 工具函数
###############################################################################

# 打印成功消息
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# 打印错误消息
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 打印警告消息
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 打印信息消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# 检查端口是否被占用
check_port() {
    local port=$1
    # 使用ss命令同时检测IPv4和IPv6
    ss -tlnp | grep -E ":$port\s" >/dev/null 2>&1
    return $?
}

# 查找可用端口
find_available_port() {
    local start=$1
    local end=$2

    for port in $(seq $start $end); do
        if ! check_port $port; then
            echo $port
            return 0
        fi
    done

    return 1
}

# 获取后端进程
get_backend_processes() {
    ps aux | grep -E "python.*simple_backend_fixed.py|python.*uvicorn.*app.main:app.*8000|python3.*uvicorn.*app.main:app.*8000" | grep -v grep | awk '{print $2}'
}

# 获取前端进程
get_frontend_processes() {
    # 查找在允许端口范围内的node进程
    local pids=""
    for port in $(seq $FRONTEND_PORT_RANGE_START $FRONTEND_PORT_RANGE_END); do
        local pid=$(ps aux | grep -E "node.*vite.*--port.*$port|node.*--port.*$port" | grep -v grep | awk '{print $2}')
        if [ ! -z "$pid" ]; then
            pids="$pids $pid"
        fi
    done
    echo $pids | xargs
}

# 等待端口启动
wait_for_port() {
    local port=$1
    local max_wait=30
    local waited=0

    while [ $waited -lt $max_wait ]; do
        if check_port $port; then
            return 0
        fi
        sleep 1
        waited=$((waited + 1))
    done

    return 1
}

###############################################################################
# 后端管理函数
###############################################################################

# 启动后端服务
start_backend() {
    local port=${1:-$DEFAULT_BACKEND_PORT}

    print_info "启动后端服务 (FastAPI)..."

    # 检查是否已经运行
    if check_port $port; then
        print_warning "后端服务已在端口 $port 运行"
        return 0
    fi

    # 如果指定端口被占用，尝试查找可用端口
    if [ $port -ne $DEFAULT_BACKEND_PORT ] && check_port $port; then
        print_warning "端口 $port 已被占用，查找可用端口..."
        port=$(find_available_port $BACKEND_PORT_RANGE_START $BACKEND_PORT_RANGE_END)
        if [ -z "$port" ]; then
            print_error "端口范围 $BACKEND_PORT_RANGE_START-$BACKEND_PORT_RANGE_END 无可用端口"
            return 1
        fi
        print_info "使用可用端口: $port"
    fi

    # 切换到后端目录
    cd "$BACKEND_DIR" || {
        print_error "无法进入后端目录: $BACKEND_DIR"
        return 1
    }

    # 检查后端环境
    if [ ! -f "$BACKEND_DIR/app/main.py" ]; then
        print_error "找不到后端主文件: $BACKEND_DIR/app/main.py"
        return 1
    fi

    # 启动后端服务
    nohup python -m uvicorn app.main:app --host 0.0.0.0 --port $port --reload > "$BACKEND_LOG" 2>&1 &
    local pid=$!

    # 等待服务启动
    print_info "等待后端服务启动..."
    if wait_for_port $port; then
        # 额外检查服务是否响应
        sleep 2
        if curl -sf http://localhost:$port/health >/dev/null 2>&1; then
            print_success "后端服务已启动并就绪"
        else
            print_warning "后端服务已启动但健康检查失败"
        fi
        print_info "  PID: $pid"
        print_info "  端口: $port"
        print_info "  Swagger文档: http://localhost:$port/docs"
        print_info "  ReDoc文档: http://localhost:$port/api/redoc"
        print_info "  日志文件: $BACKEND_LOG"
        return 0
    else
        print_error "后端服务启动超时"
        return 1
    fi
}

# 停止后端服务
stop_backend() {
    print_info "停止后端服务..."

    local pids=$(get_backend_processes)

    if [ -z "$pids" ]; then
        print_warning "没有运行中的后端服务"
        return 0
    fi

    # 停止所有后端进程
    for pid in $pids; do
        kill -9 $pid 2>/dev/null
        print_info "已终止进程: $pid"
    done

    # 验证是否停止成功
    sleep 1
    pids=$(get_backend_processes)
    if [ -z "$pids" ]; then
        print_success "后端服务已停止"
        return 0
    else
        print_error "部分后端进程未能停止"
        return 1
    fi
}

# 重启后端服务
restart_backend() {
    local port=${1:-$DEFAULT_BACKEND_PORT}

    print_info "重启后端服务..."
    stop_backend
    sleep 2
    start_backend $port
}

###############################################################################
# 前端管理函数
###############################################################################

# 启动前端服务
start_frontend() {
    local port=${1:-$DEFAULT_FRONTEND_PORT}

    print_info "启动前端服务 (Vue.js)..."

    # 检查是否已经运行
    if check_port $port; then
        print_warning "前端服务已在端口 $port 运行"
        return 0
    fi

    # 切换到前端目录
    cd "$FRONTEND_DIR" || {
        print_error "无法进入前端目录: $FRONTEND_DIR"
        return 1
    }

    # 设置端口环境变量
    export FRONTEND_PORT=$port

    # 启动前端服务
    nohup npm run dev -- --port $port > "$FRONTEND_LOG" 2>&1 &
    local pid=$!

    # 等待服务启动
    print_info "等待前端服务启动..."
    if wait_for_port $port; then
        print_success "前端服务已启动"
        print_info "  PID: $pid"
        print_info "  端口: $port"
        print_info "  访问地址: http://localhost:$port"
        print_info "  日志文件: $FRONTEND_LOG"
        return 0
    else
        print_error "前端服务启动超时"
        return 1
    fi
}

# 停止前端服务
stop_frontend() {
    print_info "停止前端服务..."

    local pids=$(get_frontend_processes)

    if [ -z "$pids" ]; then
        print_warning "没有运行中的前端服务"
        return 0
    fi

    # 停止所有前端进程
    for pid in $pids; do
        kill -9 $pid 2>/dev/null
        print_info "已终止进程: $pid"
    done

    # 验证是否停止成功
    sleep 1
    pids=$(get_frontend_processes)
    if [ -z "$pids" ]; then
        print_success "前端服务已停止"
        return 0
    else
        print_error "部分前端进程未能停止"
        return 1
    fi
}

# 重启前端服务
restart_frontend() {
    local port=${1:-$DEFAULT_FRONTEND_PORT}

    print_info "重启前端服务..."
    stop_frontend
    sleep 2
    start_frontend $port
}

###############################################################################
# 全栈管理函数
###############################################################################

# 启动所有服务
start_all() {
    print_info "启动MyStocks_spec完整服务..."
    echo ""

    start_backend
    local backend_status=$?

    echo ""

    start_frontend
    local frontend_status=$?

    echo ""
    if [ $backend_status -eq 0 ] && [ $frontend_status -eq 0 ]; then
        print_success "MyStocks_spec服务已全部启动"
        echo ""
        print_info "📊 服务状态:"
        print_info "  后端: http://localhost:$DEFAULT_BACKEND_PORT"
        print_info "  前端: http://localhost:$DEFAULT_FRONTEND_PORT"
        print_info "  Swagger文档: http://localhost:$DEFAULT_BACKEND_PORT/docs"
        print_info "  ReDoc文档: http://localhost:$DEFAULT_BACKEND_PORT/api/redoc"
        echo ""
        print_info "📊 监控服务:"
        print_info "  Grafana: http://localhost:3100 (admin/admin需要修改密码)"
        print_info "  Prometheus: http://localhost:9090"
        return 0
    else
        print_error "部分服务启动失败"
        return 1
    fi
}

# 停止所有服务
stop_all() {
    print_info "停止MyStocks_spec所有服务..."
    echo ""

    stop_frontend
    echo ""
    stop_backend

    echo ""
    print_success "MyStocks_spec服务已全部停止"
}

# 重启所有服务
restart_all() {
    print_info "重启MyStocks_spec所有服务..."
    echo ""

    stop_all
    sleep 2
    echo ""
    start_all
}

# 查看服务状态
show_status() {
    print_info "MyStocks_spec服务状态:"
    echo ""

    # 后端状态
    echo "🔧 后端服务 (FastAPI):"
    local backend_pids=$(get_backend_processes)
    if [ -z "$backend_pids" ]; then
        echo "  状态: ❌ 未运行"
    else
        echo "  状态: ✅ 运行中"
        for pid in $backend_pids; do
            local port=$(lsof -i -P -n | grep "^python.*$pid" | grep LISTEN | awk '{print $9}' | cut -d: -f2 | head -1)
            echo "  PID: $pid | 端口: ${port:-未知}"
        done
    fi

    echo ""

    # 前端状态
    echo "🎨 前端服务 (Vue.js):"
    local frontend_pids=$(get_frontend_processes)
    if [ -z "$frontend_pids" ]; then
        echo "  状态: ❌ 未运行"
    else
        echo "  状态: ✅ 运行中"
        for pid in $frontend_pids; do
            local port=$(lsof -i -P -n | grep "^node.*$pid" | grep LISTEN | awk '{print $9}' | cut -d: -f2 | head -1)
            echo "  PID: $pid | 端口: ${port:-未知}"
        done
    fi
}

###############################################################################
# 帮助信息
###############################################################################

show_help() {
    cat << EOF
${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}
${GREEN}MyStocks_spec 项目管理工具 v1.0${NC}
${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}

${YELLOW}用法:${NC}
  stocks_spec [选项] [服务] [端口]

${YELLOW}全栈服务管理:${NC}
  stocks_spec -start              启动前端+后端服务
  stocks_spec -stop               停止前端+后端服务
  stocks_spec -restart            重启前端+后端服务
  stocks_spec -status             查看服务状态

${YELLOW}前端服务管理:${NC}
  stocks_spec -start front        启动前端服务 (默认端口: 3000)
  stocks_spec -start front 3001   启动前端服务 (指定端口: 3001)
  stocks_spec -stop front         停止所有前端服务
  stocks_spec -restart front      重启前端服务
  stocks_spec -restart front 3001 重启前端服务 (指定端口)

${YELLOW}后端服务管理:${NC}
  stocks_spec -start back         启动后端服务 (默认端口: 8000)
  stocks_spec -start back 8010    启动后端服务 (指定端口: 8010)
  stocks_spec -stop back          停止所有后端服务
  stocks_spec -restart back       重启后端服务
  stocks_spec -restart back 8010  重启后端服务 (指定端口)

${YELLOW}其他选项:${NC}
  -h, --help                      显示此帮助信息

${YELLOW}端口配置:${NC}
  前端端口范围: ${FRONTEND_PORT_RANGE_START}-${FRONTEND_PORT_RANGE_END}
  后端端口范围: ${BACKEND_PORT_RANGE_START}-${BACKEND_PORT_RANGE_END}

${YELLOW}示例:${NC}
  stocks_spec -start              # 启动完整服务
  stocks_spec -start front 3005   # 在端口3005启动前端
  stocks_spec -restart back       # 重启后端服务
  stocks_spec -status             # 查看服务状态

${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}
EOF
}

###############################################################################
# 主程序
###############################################################################

main() {
    # 检查参数
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi

    # 解析命令
    local action=$1
    local service=${2:-"all"}
    local port=$3

    case $action in
        -start)
            case $service in
                front|frontend)
                    start_frontend $port
                    ;;
                back|backend)
                    start_backend $port
                    ;;
                all|*)
                    start_all
                    ;;
            esac
            ;;
        -stop)
            case $service in
                front|frontend)
                    stop_frontend
                    ;;
                back|backend)
                    stop_backend
                    ;;
                all|*)
                    stop_all
                    ;;
            esac
            ;;
        -restart)
            case $service in
                front|frontend)
                    restart_frontend $port
                    ;;
                back|backend)
                    restart_backend $port
                    ;;
                all|*)
                    restart_all
                    ;;
            esac
            ;;
        -status)
            show_status
            ;;
        -h|--help)
            show_help
            ;;
        *)
            print_error "未知命令: $action"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 执行主程序
main "$@"
