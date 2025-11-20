#!/bin/bash

# MyStocks NiceGUI监控面板启动脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo -e "${BLUE}🚀 MyStocks NiceGUI监控面板启动脚本${NC}"
echo "=========================================="

# 设置默认值
HOST="127.0.0.1"
PORT="8889"
DEBUG="false"
LOG_LEVEL="info"

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--host)
            HOST="$2"
            shift 2
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -d|--debug)
            DEBUG="true"
            LOG_LEVEL="debug"
            shift
            ;;
        --help)
            echo "使用方法: $0 [选项]"
            echo "选项:"
            echo "  -h, --host HOST     监听地址 (默认: 127.0.0.1)"
            echo "  -p, --port PORT     监听端口 (默认: 8889)"
            echo "  -d, --debug         启用调试模式"
            echo "  --help              显示此帮助信息"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ 未知选项: $1${NC}"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}📋 配置信息:${NC}"
echo "  监听地址: $HOST"
echo "  监听端口: $PORT"
echo "  调试模式: $DEBUG"
echo "  日志级别: $LOG_LEVEL"
echo ""

# 检查Python环境
echo -e "${YELLOW}🔍 检查Python环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 未安装${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✅ Python版本: $PYTHON_VERSION${NC}"

# 检查必要的依赖
echo -e "${YELLOW}📦 检查依赖包...${NC}"

REQUIRED_PACKAGES=("nicegui" "uvicorn" "asyncio")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! python3 -c "import $package" &> /dev/null; then
        MISSING_PACKAGES+=("$package")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo -e "${RED}❌ 缺少依赖包: ${MISSING_PACKAGES[*]}${NC}"
    echo -e "${YELLOW}📥 安装依赖包...${NC}"
    
    cd "$PROJECT_ROOT"
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
    else
        pip3 install nicegui uvicorn
    fi
    
    # 重新检查
    for package in "${MISSING_PACKAGES[@]}"; do
        if ! python3 -c "import $package" &> /dev/null; then
            echo -e "${RED}❌ 依赖包安装失败: $package${NC}"
            exit 1
        fi
    done
fi

echo -e "${GREEN}✅ 所有依赖包已安装${NC}"

# 检查监控模块
echo -e "${YELLOW}🔧 检查监控模块...${NC}"

MONITORING_MODULES=(
    "src/monitoring/ai_alert_manager.py"
    "src/monitoring/ai_realtime_monitor.py"
    "web/frontend/nicegui_monitoring_dashboard.py"
)

for module in "${MONITORING_MODULES[@]}"; do
    if [ ! -f "$PROJECT_ROOT/$module" ]; then
        echo -e "${RED}❌ 监控模块不存在: $module${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✅ 所有监控模块已找到${NC}"

# 设置环境变量
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
export LOG_LEVEL="$LOG_LEVEL"

echo -e "${BLUE}🌐 启动NiceGUI监控面板...${NC}"
echo "=========================================="

# 显示启动信息
echo -e "${GREEN}📊 MyStocks AI监控面板${NC}"
echo -e "  访问地址: http://$HOST:$PORT"
echo -e "  API文档: http://$HOST:$PORT/docs"
echo -e "  健康检查: http://$HOST:$PORT/api/health"
echo -e "  告警API: http://$HOST:$PORT/api/alerts"
echo -e "  指标API: http://$HOST:$PORT/api/metrics"
echo ""

# 启动应用
cd "$PROJECT_ROOT"

if [ "$DEBUG" = "true" ]; then
    echo -e "${YELLOW}🐛 调试模式已启用${NC}"
    python3 -m uvicorn web.frontend.nicegui_monitoring_dashboard:app \
        --host "$HOST" \
        --port "$PORT" \
        --reload \
        --log-level "$LOG_LEVEL"
else
    python3 -m uvicorn web.frontend.nicegui_monitoring_dashboard:app \
        --host "$HOST" \
        --port "$PORT" \
        --log-level "$LOG_LEVEL"
fi