#!/bin/bash

# MyStocks Docker 服务启动脚本
# 启动所有监控基础设施服务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DOCKER_DIR="$(dirname "${BASH_SOURCE[0]}")/.."

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 Docker 和 Docker Compose
check_dependencies() {
    log_info "检查依赖..."

    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装或未在 PATH 中"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose 未安装或未在 PATH 中"
        exit 1
    fi

    log_success "依赖检查通过"
}

# 检查环境变量文件
check_env_file() {
    local env_file="$PROJECT_ROOT/.env"

    if [[ ! -f "$env_file" ]]; then
        log_warning ".env 文件不存在，正在从 .env.example 复制..."
        cp "$PROJECT_ROOT/.env.example" "$env_file"
        log_info "请编辑 $env_file 文件配置您的环境变量"
        return 1
    fi

    # 加载环境变量
    source "$env_file"

    # 验证必需的安全配置
    if [[ -z "$GRAFANA_ADMIN_PASSWORD" ]]; then
        log_error "GRAFANA_ADMIN_PASSWORD 环境变量未设置"
        log_error "请在 $env_file 文件中设置安全的 Grafana 管理员密码"
        return 1
    fi

    if [[ "$GRAFANA_ADMIN_PASSWORD" == "mystocks2025" ]]; then
        log_error "请修改默认的 Grafana 管理员密码 'mystocks2025'"
        log_error "生产环境中使用默认密码存在安全风险"
        return 1
    fi

    if [[ -z "$MONGODB_ROOT_PASSWORD" ]]; then
        log_error "MONGODB_ROOT_PASSWORD 环境变量未设置"
        log_error "请在 $env_file 文件中设置安全的 MongoDB 密码"
        return 1
    fi

    if [[ "$MONGODB_ROOT_PASSWORD" == "mystocks2025" ]]; then
        log_error "请修改默认的 MongoDB 密码 'mystocks2025'"
        log_error "生产环境中使用默认密码存在安全风险"
        return 1
    fi

    log_success "环境变量文件和安全配置检查通过"
    return 0
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."

    local dirs=(
        "$PROJECT_ROOT/config/prometheus"
        "$PROJECT_ROOT/config/alerts"
        "$PROJECT_ROOT/config/alertmanager"
        "$PROJECT_ROOT/config/mongodb"
        "$PROJECT_ROOT/data/grafana/provisioning/datasources"
        "$PROJECT_ROOT/data/grafana/provisioning/dashboards"
        "$PROJECT_ROOT/data/grafana/dashboards"
    )

    for dir in "${dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            log_info "创建目录: $dir"
        fi
    done

    log_success "目录创建完成"
}

# 创建默认配置文件
create_default_configs() {
    log_info "检查配置文件..."

    # Prometheus 配置
    local prometheus_config="$PROJECT_ROOT/config/prometheus/prometheus.yml"
    if [[ ! -f "$prometheus_config" ]]; then
        log_info "创建默认 Prometheus 配置..."
        cat > "$prometheus_config" << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['localhost:9093']

rule_files:
  - "/etc/prometheus/alerts/*.yml"

scrape_configs:
  - job_name: 'mystocks-backend'
    static_configs:
      - targets: ['host.docker.internal:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s
    scrape_timeout: 20s
EOF
        log_success "Prometheus 配置文件已创建"
    fi

    # AlertManager 配置
    local alertmanager_config="$PROJECT_ROOT/config/alertmanager/alertmanager.yml"
    if [[ ! -f "$alertmanager_config" ]]; then
        log_info "创建默认 AlertManager 配置..."
        cat > "$alertmanager_config" << 'EOF'
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@mystocks.com'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
- name: 'web.hook'
  webhook_configs:
  - url: 'http://127.0.0.1:5001/'
EOF
        log_success "AlertManager 配置文件已创建"
    fi

    # MongoDB 配置
    local mongodb_config="$PROJECT_ROOT/config/mongodb/mongod.conf"
    if [[ ! -f "$mongodb_config" ]]; then
        log_info "创建默认 MongoDB 配置..."
        cat > "$mongodb_config" << 'EOF'
storage:
  dbPath: /data/db
  journal:
    enabled: true

systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongod.log

net:
  port: 27017
  bindIp: 0.0.0.0

processManagement:
  timeZoneInfo: /usr/share/zoneinfo

security:
  authorization: enabled
EOF
        log_success "MongoDB 配置文件已创建"
    fi
}

# 启动服务
start_services() {
    log_info "启动 MyStocks 监控服务..."

    cd "$DOCKER_DIR"

    # 检查是否已有服务运行
    if docker-compose -f monitoring-stack.yml ps --services --filter "status=running" | grep -q .; then
        log_warning "检测到已有服务运行，正在重新创建..."
        docker-compose -f monitoring-stack.yml down
    fi

    # 启动服务
    if docker-compose -f monitoring-stack.yml --env-file "$PROJECT_ROOT/.env" up -d; then
        log_success "服务启动成功！"
    else
        log_error "服务启动失败"
        exit 1
    fi
}

# 等待服务就绪
wait_for_services() {
    log_info "等待服务就绪..."

    local services=(
        "Prometheus:9090:-/healthy"
        "Grafana:3000:api/health"
        "AlertManager:9093:-/healthy"
    )

    for service in "${services[@]}"; do
        IFS=':' read -r name port path <<< "$service"
        log_info "等待 $name 就绪..."

        local max_attempts=30
        local attempt=1

        while [[ $attempt -le $max_attempts ]]; do
            if curl -sf "http://localhost:$port/$path" &> /dev/null; then
                log_success "$name 已就绪"
                break
            fi

            if [[ $attempt -eq $max_attempts ]]; then
                log_warning "$name 启动超时，但继续启动其他服务"
            fi

            sleep 2
            ((attempt++))
        done
    done
}

# 显示服务状态
show_status() {
    log_info "服务状态："
    cd "$DOCKER_DIR"
    docker-compose -f monitoring-stack.yml ps

    echo
    log_info "服务访问地址："
    echo -e "${GREEN}• Prometheus:${NC}  http://localhost:9090"
    echo -e "${GREEN}• Grafana:${NC}     http://localhost:3000 (admin/mystocks2025)"
    echo -e "${GREEN}• MongoDB:${NC}     localhost:27018 (admin/mystocks2025)"
    echo -e "${GREEN}• AlertManager:${NC} http://localhost:9093"
    echo
    log_info "查看日志命令: docker-compose -f docker/monitoring-stack.yml logs [service_name]"
}

# 主函数
main() {
    echo "=================================="
    echo "MyStocks Docker 服务启动脚本"
    echo "=================================="
    echo

    cd "$PROJECT_ROOT"

    check_dependencies

    if ! check_env_file; then
        log_error "请配置 .env 文件后重新运行此脚本"
        exit 1
    fi

    create_directories
    create_default_configs
    start_services
    wait_for_services
    show_status

    echo
    log_success "MyStocks 监控服务启动完成！"
}

# 运行主函数
main "$@"