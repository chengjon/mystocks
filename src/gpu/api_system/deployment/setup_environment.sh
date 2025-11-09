#!/bin/bash

# MyStocks API模式GPU加速系统环境设置脚本
# 用于Phase 1: 基础设施搭建

set -e  # 遇到错误立即退出

echo "🚀 MyStocks GPU API系统环境设置开始..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# 检查是否为root用户
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "此脚本需要root权限执行"
        exit 1
    fi
}

# 检查GPU硬件
check_gpu() {
    log_info "检查GPU硬件状态..."
    if ! command -v nvidia-smi &> /dev/null; then
        log_error "nvidia-smi未找到，请确保NVIDIA驱动已安装"
        exit 1
    fi

    GPU_COUNT=$(nvidia-smi --query-gpu=count --format=csv,noheader,nounits | head -1)
    if [[ $GPU_COUNT -eq 0 ]]; then
        log_error "未检测到GPU设备"
        exit 1
    fi

    log_info "✅ 检测到 $GPU_COUNT 个GPU设备"

    # 显示GPU详细信息
    nvidia-smi --query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits | while read -r gpu_info; do
        IFS=', ' read -r name mem_total mem_used mem_free util <<< "$gpu_info"
        log_info "GPU: $name, 总内存: ${mem_total}MB, 已用: ${mem_used}MB, 空闲: ${mem_free}MB, 利用率: ${util}%"
    done
}

# 检查CUDA环境
check_cuda() {
    log_info "检查CUDA环境..."
    if ! command -v nvcc &> /dev/null; then
        log_warn "nvcc未找到，但CUDA运行时可能已安装"
    fi

    # 检查Python的CUDA支持
    python3 -c "import torch; print(f'PyTorch CUDA可用: {torch.cuda.is_available()}')" || {
        log_warn "PyTorch CUDA测试失败"
    }

    python3 -c "import cupy; print(f'CuPy版本: {cupy.__version__}')" || {
        log_error "CuPy未安装，请先安装RAPIDS"
        exit 1
    }

    log_info "✅ CUDA环境检查完成"
}

# 安装系统依赖
install_system_dependencies() {
    log_info "安装系统依赖包..."

    # 更新包管理器
    apt-get update

    # 安装基础工具
    apt-get install -y \
        wget \
        curl \
        git \
        htop \
        tmux \
        vim \
        net-tools \
        dnsutils \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release

    # 安装Python依赖
    apt-get install -y \
        python3 \
        python3-pip \
        python3-dev \
        python3-venv \
        python3-tk

    # 安装其他GPU相关工具
    apt-get install -y \
        libssl-dev \
        libffi-dev \
        build-essential

    log_info "✅ 系统依赖安装完成"
}

# 安装Docker和Docker Compose
install_docker() {
    log_info "安装Docker..."

    # 卸载旧版本
    apt-get remove -y docker docker-engine docker.io containerd runc

    # 安装Docker官方仓库
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io

    # 安装Docker Compose
    curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose

    # 添加用户到docker组
    usermod -aG docker $USER

    log_info "✅ Docker安装完成"
}

# 安装Redis
install_redis() {
    log_info "安装Redis..."

    apt-get install -y redis-server

    # 配置Redis
    cp /etc/redis/redis.conf /etc/redis/redis.conf.backup

    # 优化Redis配置
    cat > /etc/redis/redis.conf << EOF
bind 127.0.0.1 ::1
port 6379
tcp-backlog 511
timeout 0
tcp-keepalive 300
daemonize yes
supervised no
protected-mode no
pidfile /var/run/redis/redis-server.pid
loglevel notice
logfile ""
databases 16
always-show-logo yes
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir /var/lib/redis
replica-serve-stale-data yes
replica-read-only yes
repl-diskless-sync no
repl-diskless-sync-delay 5
repl-ping-replica-period 10
repl-timeout 60
repl-disable-tcp-nodelay no
repl-backlog-size 1mb
repl-backlog-ttl 3600
replica-priority 100
maxmemory 4gb
maxmemory-policy allkeys-lru
lazyfree-lazy-eviction no
lazyfree-lazy-expire no
lazyfree-lazy-server-del no
replica-lazy-flush no
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
aof-load-truncated yes
aof-use-rdb-preamble yes
lua-time-limit 5000
slowlog-log-slower-than 10000
slowlog-max-len 128
latency-monitor-threshold 0
notify-keyspace-events ""
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-size -2
list-compress-depth 0
set-max-intset-entries 512
zset-max-ziplist-entries 128
zset-max-ziplist-value 64
hll-sparse-max-bytes 3000
stream-node-max-bytes 4096
stream-node-max-entries 100
activerehashing yes
client-output-buffer-limit normal 0 0 0
client-output-buffer-limit replica 256mb 64mb 60
client-output-buffer-limit pubsub 32mb 8mb 60
hz 10
dynamic-hz yes
aof-rewrite-incremental-fsync yes
rdb-save-incremental-fsync yes
EOF

    # 创建redis用户和目录
    useradd -r -s /bin/false redis || true
    mkdir -p /var/lib/redis
    chown -R redis:redis /var/lib/redis
    chown -R redis:redis /var/log/redis

    # 启动Redis
    systemctl enable redis-server
    systemctl start redis-server

    log_info "✅ Redis安装完成"
}

# 安装NVIDIA Docker
install_nvidia_docker() {
    log_info "安装NVIDIA Docker..."

    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -
    curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | tee /etc/apt/sources.list.d/nvidia-docker.list

    apt-get update
    apt-get install -y nvidia-container-toolkit

    systemctl restart docker

    log_info "✅ NVIDIA Docker安装完成"
}

# 创建项目目录结构
create_directories() {
    log_info "创建项目目录结构..."

    # 创建主要目录
    mkdir -p /opt/mystocks_gpu_api/{services,config,monitoring,utils,api_proto,deployment,logs,backups,cache}

    # 创建服务目录
    mkdir -p /opt/mystocks_gpu_api/services/{backtest,realtime,ml,risk,order_execution,multi_factor}

    # 设置权限
    chown -R $USER:$USER /opt/mystocks_gpu_api

    log_info "✅ 目录结构创建完成"
}

# 创建系统服务文件
create_system_services() {
    log_info "创建系统服务文件..."

    # 创建GPU API服务文件
    cat > /etc/systemd/system/mystocks-gpu-api.service << EOF
[Unit]
Description=MyStocks GPU Acceleration API
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/mystocks_gpu_api
ExecStart=/usr/bin/docker-compose -f deployment/docker-compose.yml up
Restart=always
RestartSec=10
Environment=PYTHONPATH=/opt/mystocks_gpu_api
Environment=CONFIG_PATH=/opt/mystocks_gpu_api/config/gpu_config.yaml

[Install]
WantedBy=multi-user.target
EOF

    # 创建监控服务文件
    cat > /etc/systemd/system/mystocks-gpu-monitor.service << EOF
[Unit]
Description=MyStocks GPU Monitor
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/mystocks_gpu_api
ExecStart=/usr/bin/python3 monitoring/monitor_service.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # 重新加载systemd
    systemctl daemon-reload

    log_info "✅ 系统服务文件创建完成"
}

# 配置防火墙
configure_firewall() {
    log_info "配置防火墙..."

    # 安装ufw
    apt-get install -y ufw

    # 配置防火墙规则
    ufw default deny incoming
    ufw default allow outgoing

    # 允许必要的端口
    ufw allow ssh
    ufw allow 50051  # gRPC
    ufw allow 50052  # WebSocket
    ufw allow 50053  # REST
    ufw allow 6379  # Redis
    ufw allow 6030  # TDengine
    ufw allow 5432  # PostgreSQL

    # 启用防火墙
    ufw --force enable

    log_info "✅ 防火墙配置完成"
}

# 显示安装结果
show_results() {
    log_info "环境设置完成！"
    echo ""
    echo "🎉 MyStocks GPU API系统环境设置完成！"
    echo ""
    echo "📋 系统信息:"
    echo "   GPU数量: $(nvidia-smi --query-gpu=count --format=csv,noheader,nounits | head -1)"
    echo "   Docker版本: $(docker --version | cut -d' ' -f3 | tr -d ',')"
    echo "   Redis状态: $(systemctl is-active redis-server)"
    echo "   系统服务: mystocks-gpu-api, mystocks-gpu-monitor"
    echo ""
    echo "🚀 启动命令:"
    echo "   systemctl start mystocks-gpu-api"
    echo "   systemctl start mystocks-gpu-monitor"
    echo "   systemctl enable mystocks-gpu-api"
    echo "   systemctl enable mystocks-gpu-monitor"
    echo ""
    echo "📁 项目目录: /opt/mystocks_gpu_api"
    echo "📄 配置文件: /opt/mystocks_gpu_api/config/gpu_config.yaml"
    echo ""
    echo "🔧 重要提示:"
    echo "   1. 请重新登录以获得docker组权限"
    echo "   2. 请根据实际情况修改config/gpu_config.yaml"
    echo "   3. 请确保数据库服务正常运行"
}

# 主函数
main() {
    log_info "开始MyStocks GPU API系统环境设置..."

    check_root
    check_gpu
    check_cuda
    install_system_dependencies
    install_docker
    install_nvidia_docker
    install_redis
    create_directories
    create_system_services
    configure_firewall
    show_results
}

# 执行主函数
main "$@"