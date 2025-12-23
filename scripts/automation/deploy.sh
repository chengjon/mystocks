#!/bin/bash

# ===================================
# MyStocks 一键部署脚本
# 版本: v1.0
# 描述: 生产环境自动化部署脚本，支持前置检查、错误回滚
# ===================================

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
PROJECT_ROOT="/opt/claude/mystocks_spec"
BACKUP_DIR="/opt/mystocks/backups"
LOG_DIR="/opt/mystocks/logs"
DATA_DIR="/opt/mystocks/data"
ENV_FILE="${PROJECT_ROOT}/.env.production"
CONFIG_FILE="${PROJECT_ROOT}/ecosystem.production.config.js"
DEPLOY_LOG="${LOG_DIR}/deploy.log"

# 函数定义
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$DEPLOY_LOG"
}

success() {
    echo -e "${GREEN}[成功]${NC} $1" | tee -a "$DEPLOY_LOG"
}

warning() {
    echo -e "${YELLOW}[警告]${NC} $1" | tee -a "$DEPLOY_LOG"
}

error() {
    echo -e "${RED}[错误]${NC} $1" | tee -a "$DEPLOY_LOG"
}

# 前置检查函数
pre_deployment_check() {
    log "开始前置检查..."

    # 检查是否为root用户或有sudo权限
    if [[ $EUID -eq 0 ]]; then
        error "不建议使用root用户运行部署脚本"
        exit 1
    fi

    # 检查系统资源
    log "检查系统资源..."
    MEMORY=$(free -m | awk 'NR==2{printf "%.0f", $7}')
    if [[ $MEMORY -lt 2048 ]]; then
        warning "可用内存不足2GB，当前可用: ${MEMORY}MB"
    fi

    DISK=$(df -h / | awk 'NR==2{print $4}' | sed 's/G//')
    if [[ ${DISK%.*} -lt 10 ]]; then
        error "可用磁盘空间不足10GB，当前可用: ${DISK}"
        exit 1
    fi

    # 检查依赖安装
    log "检查系统依赖..."
    command -v python3 >/dev/null 2>&1 || { error "Python3 未安装"; exit 1; }
    command -v pip >/dev/null 2>&1 || { error "pip 未安装"; exit 1; }
    command -v node >/dev/null 2>&1 || { error "Node.js 未安装"; exit 1; }
    command -v npm >/dev/null 2>&1 || { error "npm 未安装"; exit 1; }
    command -v pm2 >/dev/null 2>&1 || { error "PM2 未安装，请运行: npm install -g pm2"; exit 1; }
    command -v docker >/dev/null 2>&1 || { error "Docker 未安装"; exit 1; }
    command -v docker-compose >/dev/null 2>&1 || { error "Docker Compose 未安装"; exit 1; }

    # 检查端口占用
    log "检查端口占用情况..."
    PORTS=(3000 3001 3002 3003 3004 3005 3006 3007 3008 3009 3010 8000 8001 8002 8003 8004 8005 8006 8007 8008 8009 8010 8888 5432 6030)
    OCCUPIED_PORTS=()

    for port in "${PORTS[@]}"; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            OCCUPIED_PORTS+=($port)
        fi
    done

    if [[ ${#OCCUPIED_PORTS[@]} -gt 0 ]]; then
        warning "以下端口已被占用: ${OCCUPIED_PORTS[*]}"
        warning "尝试自动清理冲突进程..."

        # 尝试清理可能的冲突进程
        pkill -f "uvicorn.*8888" 2>/dev/null || true
        pkill -f "serve.*300" 2>/dev/null || true
        pkill -f "node.*300" 2>/dev/null || true

        sleep 2

        # 重新检查
        for port in "${OCCUPIED_PORTS[@]}"; do
            if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
                error "端口 $port 仍然被占用，请手动清理"
                exit 1
            fi
        done
    fi

    # 检查配置文件
    log "检查配置文件..."
    [[ ! -f "$ENV_FILE" ]] && { error "环境配置文件不存在: $ENV_FILE"; exit 1; }
    [[ ! -f "$CONFIG_FILE" ]] && { error "PM2配置文件不存在: $CONFIG_FILE"; exit 1; }
    [[ ! -f "${PROJECT_ROOT}/requirements.txt" ]] && { error "Python依赖文件不存在"; exit 1; }
    [[ ! -f "${PROJECT_ROOT}/web/frontend/package.json" ]] && { error "前端依赖文件不存在"; exit 1; }

    success "前置检查完成"
}

# 备份函数
backup_existing_deployment() {
    log "备份现有部署..."

    # 创建备份目录
    mkdir -p "$BACKUP_DIR"
    BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_PATH="${BACKUP_DIR}/backup_${BACKUP_TIMESTAMP}"

    # 备份现有配置
    if [[ -f "/etc/systemd/system/mystocks.service" ]]; then
        cp /etc/systemd/system/mystocks.service "$BACKUP_PATH/" 2>/dev/null || true
    fi

    # 备份现有日志
    if [[ -d "$LOG_DIR" ]]; then
        cp -r "$LOG_DIR" "$BACKUP_PATH/" 2>/dev/null || true
    fi

    # 备份数据库数据 (如果存在)
    if command -v pg_dump >/dev/null 2>&1; then
        pg_dumpall > "$BACKUP_PATH/database_backup.sql" 2>/dev/null || true
    fi

    success "备份完成: $BACKUP_PATH"
}

# 数据库准备函数
prepare_database() {
    log "准备数据库..."

    # 启动数据库服务
    log "启动数据库服务..."
    docker-compose up -d postgresql tdengine 2>/dev/null || {
        error "数据库服务启动失败"
        return 1
    }

    # 等待数据库就绪
    log "等待数据库就绪..."
    for i in {1..30}; do
        if docker exec $(docker-compose ps -q postgresql) pg_isready -U postgres >/dev/null 2>&1; then
            success "PostgreSQL 数据库就绪"
            break
        fi
        sleep 2
        if [[ $i -eq 30 ]]; then
            error "PostgreSQL 数据库启动超时"
            return 1
        fi
    done

    for i in {1..30}; do
        if docker exec $(docker-compose ps -q tdengine) taos -s "show databases;" >/dev/null 2>&1; then
            success "TDengine 数据库就绪"
            break
        fi
        sleep 2
        if [[ $i -eq 30 ]]; then
            error "TDengine 数据库启动超时"
            return 1
        fi
    done

    return 0
}

# 应用部署函数
deploy_application() {
    log "开始部署应用..."

    # 创建必要目录
    mkdir -p "$LOG_DIR" "$DATA_DIR" /opt/mystocks

    # 安装Python依赖
    log "安装Python依赖..."
    cd "$PROJECT_ROOT"
    pip install -r requirements.txt || {
        error "Python依赖安装失败"
        return 1
    }

    # 构建前端应用
    log "构建前端应用..."
    cd web/frontend
    npm install || {
        error "npm依赖安装失败"
        return 1
    }

    npm run build || {
        error "前端构建失败"
        return 1
    }

    # 返回项目根目录
    cd "$PROJECT_ROOT"

    # 停止现有服务
    log "停止现有服务..."
    pm2 delete all 2>/dev/null || true
    pm2 flush 2>/dev/null || true

    # 启动新服务
    log "启动生产服务..."
    pm2 start ecosystem.production.config.js --env production || {
        error "服务启动失败"
        return 1
    }

    # 保存PM2配置
    pm2 save

    return 0
}

# 健康检查函数
health_check() {
    log "执行健康检查..."

    # 检查服务状态
    log "检查PM2服务状态..."
    pm2 list | grep -q "online" || {
        error "PM2服务未正常运行"
        return 1
    }

    # 检查API服务
    log "检查API服务..."
    for i in {1..30}; do
        if curl -s -f http://localhost:8000/api/monitoring/health >/dev/null 2>&1; then
            success "API服务健康检查通过"
            break
        fi
        sleep 2
        if [[ $i -eq 30 ]]; then
            error "API服务健康检查失败"
            return 1
        fi
    done

    # 检查前端服务
    log "检查前端服务..."
    for i in {1..15}; do
        if curl -s -f http://localhost:3000 >/dev/null 2>&1; then
            success "前端服务健康检查通过"
            break
        fi
        sleep 2
        if [[ $i -eq 15 ]]; then
            error "前端服务健康检查失败"
            return 1
        fi
    done

    # 检查数据库连接
    log "检查数据库连接..."
    cd "$PROJECT_ROOT"
    python3 -c "
import os
os.environ['PYTHONPATH'] = '$PROJECT_ROOT'
from src.data_access.postgresql_access import PostgreSQLDataAccess
from src.data_access.tdengine_access import TDengineDataAccess
try:
    pg = PostgreSQLDataAccess()
    print('PostgreSQL连接正常')
    td = TDengineDataAccess()
    print('TDengine连接正常')
except Exception as e:
    print(f'数据库连接失败: {e}')
    exit(1)
" || {
        error "数据库连接检查失败"
        return 1
    }

    success "所有健康检查通过"
    return 0
}

# 错误回滚函数
rollback_deployment() {
    error "部署失败，开始回滚..."

    # 停止当前服务
    log "停止当前服务..."
    pm2 delete all 2>/dev/null || true

    # 恢复备份 (如果存在)
    LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/backup_* 2>/dev/null | head -1)
    if [[ -n "$LATEST_BACKUP" ]]; then
        log "恢复备份: $LATEST_BACKUP"
        cp -r "$LATEST_BACKUP"/* /opt/mystocks/ 2>/dev/null || true
    fi

    # 重启服务 (使用开发配置)
    log "尝试恢复开发配置..."
    if [[ -f "${PROJECT_ROOT}/ecosystem.config.js" ]]; then
        pm2 start ecosystem.config.js --env development 2>/dev/null || true
    fi

    error "回滚完成，请检查系统状态"
}

# 清理函数
cleanup() {
    log "清理临时文件..."

    # 清理npm缓存
    cd web/frontend 2>/dev/null && npm cache clean --force || true

    # 清理Python缓存
    find "$PROJECT_ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find "$PROJECT_ROOT" -name "*.pyc" -delete 2>/dev/null || true

    # 清理临时文件
    rm -rf /tmp/mystocks_* 2>/dev/null || true

    success "清理完成"
}

# 显示使用信息
show_usage() {
    echo "MyStocks 生产环境部署脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示此帮助信息"
    echo "  -c, --check    仅执行前置检查"
    echo "  -b, --backup   仅创建备份"
    echo "  -f, --force    跳过确认提示"
    echo "  --rollback     执行回滚操作"
    echo ""
    echo "示例:"
    echo "  $0              # 完整部署"
    echo "  $0 --check      # 仅检查环境"
    echo "  $0 --backup     # 仅创建备份"
    echo "  $0 --rollback   # 执行回滚"
}

# 主函数
main() {
    # 创建日志目录
    mkdir -p "$LOG_DIR"

    log "MyStocks 生产环境部署开始"

    # 解析命令行参数
    SKIP_CONFIRMATION=false
    ONLY_CHECK=false
    ONLY_BACKUP=false
    ROLLBACK=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -c|--check)
                ONLY_CHECK=true
                shift
                ;;
            -b|--backup)
                ONLY_BACKUP=true
                shift
                ;;
            -f|--force)
                SKIP_CONFIRMATION=true
                shift
                ;;
            --rollback)
                ROLLBACK=true
                shift
                ;;
            *)
                error "未知选项: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    # 处理回滚请求
    if [[ "$ROLLBACK" == true ]]; then
        rollback_deployment
        exit $?
    fi

    # 确认部署
    if [[ "$SKIP_CONFIRMATION" != true ]]; then
        echo -e "${YELLOW}警告: 此操作将在生产环境中部署MyStocks系统${NC}"
        echo -e "${YELLOW}这将会停止现有服务并重新启动${NC}"
        echo -e "${YELLOW}确保您已备份重要数据${NC}"
        echo ""
        read -p "是否继续? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log "部署已取消"
            exit 0
        fi
    fi

    # 执行部署流程
    if [[ "$ONLY_CHECK" == true ]]; then
        pre_deployment_check
        exit $?
    fi

    if [[ "$ONLY_BACKUP" == true ]]; then
        backup_existing_deployment
        exit $?
    fi

    # 设置错误处理
    trap 'rollback_deployment; cleanup; exit 1' ERR

    # 执行部署步骤
    pre_deployment_check || exit 1
    backup_existing_deployment || exit 1
    prepare_database || exit 1
    deploy_application || exit 1

    # 等待服务启动
    log "等待服务完全启动..."
    sleep 10

    # 执行健康检查
    health_check || exit 1

    # 清理
    cleanup

    # 显示部署结果
    echo ""
    success "=========================================="
    success "MyStocks 生产环境部署成功完成!"
    success "=========================================="
    log "前端访问地址: http://localhost:3000"
    log "API文档地址: http://localhost:8000/api/docs"
    log "API健康检查: http://localhost:8000/api/monitoring/health"
    log "PM2状态查看: pm2 list"
    log "日志查看: pm2 logs"
    success "=========================================="
}

# 执行主函数
main "$@"
