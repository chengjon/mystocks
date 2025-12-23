#!/bin/bash

# MyStocks API模式GPU加速系统 - Docker入口点脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $1"
}

# 检查GPU环境
check_gpu() {
    log_info "检查GPU环境..."

    if ! command -v nvidia-smi &> /dev/null; then
        log_warn "nvidia-smi未找到，可能是在CPU环境运行"
    else
        log_info "GPU设备信息:"
        nvidia-smi --query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits | while read -r gpu_info; do
            IFS=', ' read -r name mem_total mem_used mem_free util <<< "$gpu_info"
            log_info "  - $name: 内存 ${mem_used}/${mem_total}MB, 利用率 ${util}%"
        done
    fi
}

# 检查Python环境
check_python() {
    log_info "检查Python环境..."

    if [[ ! -d "/opt/conda/envs/mystocks" ]]; then
        log_error "Conda环境未找到"
        exit 1
    fi

    source /opt/conda/bin/activate mystocks
    log_info "Python版本: $(python --version)"
    log_info "Python路径: $(which python)"

    # 检查关键库
    log_info "检查关键Python库:"
    libraries=("numpy" "pandas" "torch" "cudf" "cuml" "grpcio" "redis" "psutil")
    for lib in "${libraries[@]}"; do
        if python -c "import $lib" 2>/dev/null; then
            version=$(python -c "import $lib; print($lib.__version__ 2>/dev/null or 'N/A')")
            log_info "  - $lib: ✅ $version"
        else
            log_warn "  - $lib: ❌ 未安装"
        fi
    done
}

# 检查配置文件
check_config() {
    log_info "检查配置文件..."

    if [[ ! -f "/opt/mystocks_gpu_api/config/gpu_config.yaml" ]]; then
        log_warn "配置文件未找到，使用默认配置"
        # 可以在这里创建默认配置文件
    else
        log_info "配置文件: ✅ /opt/mystocks_gpu_api/config/gpu_config.yaml"

        # 检查关键配置
        if grep -q "gpu_enabled: true" /opt/mystocks_gpu_api/config/gpu_config.yaml; then
            log_info "GPU加速: ✅ 已启用"
        else
            log_info "GPU加速: ⚠️  已禁用"
        fi
    fi
}

# 检查依赖服务
check_dependencies() {
    log_info "检查依赖服务..."

    # 检查Redis
    if python -c "import redis; r = redis.Redis(host='redis', port=6379); r.ping()" 2>/dev/null; then
        log_info "Redis: ✅ 连接成功"
    else
        log_warn "Redis: ❌ 连接失败"
    fi

    # 检查PostgreSQL
    if python -c "import psycopg2; conn = psycopg2.connect(host='postgresql', database='mystocks', user='postgres', password='postgres')" 2>/dev/null; then
        log_info "PostgreSQL: ✅ 连接成功"
    else
        log_warn "PostgreSQL: ❌ 连接失败"
    fi

    # 检查TDengine
    if python -c "import taos; conn = taos.connect(host='tdengine', user='root', password='taosdata')" 2>/dev/null; then
        log_info "TDengine: ✅ 连接成功"
    else
        log_warn "TDengine: ❌ 连接失败"
    fi
}

# 创建必要目录
create_directories() {
    log_info "创建必要目录..."

    mkdir -p /opt/mystocks_gpu_api/{logs,backups,cache}
    mkdir -p /opt/mystocks_gpu_api/logs/{api,monitoring,services,errors}

    # 设置权限
    chown -R mystocks:mystocks /opt/mystocks_gpu_api

    log_info "目录创建完成"
}

# 初始化数据库
init_database() {
    log_info "初始化数据库..."

    source /opt/conda/bin/activate mystocks

    # 运行数据库初始化脚本
    if [[ -f "/opt/mystocks_gpu_api/deployment/init_database.py" ]]; then
        python /opt/mystocks_gpu_api/deployment/init_database.py
        log_info "数据库初始化完成"
    else
        log_warn "数据库初始化脚本未找到"
    fi
}

# 启动监控
start_monitoring() {
    log_info "启动监控服务..."

    # 启动Prometheus
    if [[ -f "/opt/mystocks_gpu_api/deployment/start_monitoring.sh" ]]; then
        chmod +x /opt/mystocks_gpu_api/deployment/start_monitoring.sh
        /opt/mystocks_gpu_api/deployment/start_monitoring.sh &
        log_info "监控服务启动中..."
    fi
}

# 启动服务
start_services() {
    log_info "启动MyStocks GPU API服务..."

    source /opt/conda/bin/activate mystocks

    # 启动主服务
    if [[ -f "/opt/mystocks_gpu_api/services/gpu_api_server.py" ]]; then
        log_info "启动GPU API主服务..."
        python /opt/mystocks_gpu_api/services/gpu_api_server.py &

        # 等待服务启动
        sleep 10

        # 检查服务状态
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            log_info "GPU API服务: ✅ 运行正常"
        else
            log_warn "GPU API服务: ⚠️  可能启动失败"
        fi
    else
        log_error "GPU API主服务未找到"
        exit 1
    fi

    # 启动Celery工作进程
    if [[ -f "/opt/mystocks_gpu_api/services/celery_worker.py" ]]; then
        log_info "启动Celery工作进程..."
        celery -A services.celery_app worker --loglevel=info --concurrency=4 &
    fi

    # 启动任务调度器
    if [[ -f "/opt/mystocks_gpu_api/services/scheduler.py" ]]; then
        log_info "启动任务调度器..."
        python /opt/mystocks_gpu_api/services/scheduler.py &
    fi
}

# 信号处理
cleanup() {
    log_info "收到终止信号，正在清理..."
    kill $(jobs -p)
    log_info "清理完成"
}

# 设置信号处理
trap cleanup SIGTERM SIGINT

# 主函数
main() {
    log_info "========================================="
    log_info "MyStocks GPU API系统启动中..."
    log_info "========================================="

    # 执行检查和初始化
    check_gpu
    check_python
    check_config
    check_dependencies
    create_directories
    init_database
    start_monitoring

    # 启动服务
    start_services

    log_info "========================================="
    log_info "MyStocks GPU API系统启动完成！"
    log_info "========================================="

    # 保持容器运行
    while true; do
        sleep 60
        # 检查服务状态
        if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
            log_warn "服务状态检查失败"
        fi
    done
}

# 执行主函数
main "$@"
