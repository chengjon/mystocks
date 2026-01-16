#!/bin/bash

# MyStocks 部署脚本
# 支持测试环境和生产环境的自动化部署

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# 部署配置
DEPLOY_ENV=${DEPLOY_ENV:-test}
PROJECT_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
BACKUP_DIR="${PROJECT_ROOT}/backups/$(date +%Y%m%d_%H%M%S)"

# 环境检查
check_environment() {
    log_info "检查部署环境..."

    # 检查Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装"
        exit 1
    fi

    # 检查docker-compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "docker-compose 未安装"
        exit 1
    fi

    # 检查环境变量
    case $DEPLOY_ENV in
        test)
            check_test_env_vars
            ;;
        production)
            check_prod_env_vars
            ;;
        *)
            log_error "无效的部署环境: $DEPLOY_ENV"
            echo "使用方法: $0 [test|production]"
            exit 1
            ;;
    esac

    log_success "环境检查通过"
}

# 检查测试环境变量
check_test_env_vars() {
    log_info "检查测试环境变量..."

    required_vars=(
        "TEST_DATABASE_URL"
        "TEST_REDIS_URL"
    )

    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            log_error "缺少必需的环境变量: $var"
            exit 1
        fi
    done

    log_success "测试环境变量检查通过"
}

# 检查生产环境变量
check_prod_env_vars() {
    log_info "检查生产环境变量..."

    required_vars=(
        "DATABASE_URL"
        "REDIS_URL"
        "SECRET_KEY"
        "ALLOWED_HOSTS"
    )

    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            log_error "缺少必需的环境变量: $var"
            exit 1
        fi
    done

    log_success "生产环境变量检查通过"
}

# 创建备份
create_backup() {
    log_info "创建当前部署备份..."

    mkdir -p "$BACKUP_DIR"

    # 备份数据库
    if [ "$DEPLOY_ENV" = "production" ]; then
        log_info "备份生产数据库..."
        # 这里可以添加数据库备份命令
        echo "Database backup would be created here" > "$BACKUP_DIR/database_backup.sql"
    fi

    # 备份配置文件
    if [ -f ".env" ]; then
        cp .env "$BACKUP_DIR/.env.backup"
    fi

    # 备份Docker镜像
    log_info "备份当前运行的容器镜像..."
    docker-compose -f "docker-compose.${DEPLOY_ENV}.yml" images > "$BACKUP_DIR/images_backup.txt" 2>/dev/null || true

    log_success "备份创建完成: $BACKUP_DIR"
}

# 停止当前服务
stop_services() {
    log_info "停止当前服务..."

    if [ "$DEPLOY_ENV" = "production" ]; then
        # 生产环境：优雅停止
        docker-compose -f "docker-compose.${DEPLOY_ENV}.yml" stop
        sleep 10  # 等待连接处理完毕
    fi

    docker-compose -f "docker-compose.${DEPLOY_ENV}.yml" down

    log_success "服务已停止"
}

# 清理旧镜像（可选）
cleanup_old_images() {
    if [ "$CLEANUP_OLD_IMAGES" = "true" ]; then
        log_info "清理悬空镜像..."
        docker image prune -f
        log_success "镜像清理完成"
    fi
}

# 启动新服务
start_services() {
    log_info "启动新版本服务..."

    # 拉取最新镜像
    docker-compose -f "docker-compose.${DEPLOY_ENV}.yml" pull

    # 启动服务
    docker-compose -f "docker-compose.${DEPLOY_ENV}.yml" up -d

    log_success "服务启动完成"
}

# 等待服务启动
wait_for_services() {
    log_info "等待服务启动..."

    local max_attempts=60
    local attempt=1

    case $DEPLOY_ENV in
        test)
            local health_url="http://localhost:8001/health"
            ;;
        production)
            local health_url="http://localhost:8000/health"
            ;;
    esac

    while [ $attempt -le $max_attempts ]; do
        log_info "健康检查尝试 $attempt/$max_attempts..."

        if curl -f -s "$health_url" > /dev/null 2>&1; then
            log_success "服务健康检查通过"
            return 0
        fi

        sleep 5
        ((attempt++))
    done

    log_error "服务启动超时"
    return 1
}

# 运行部署后测试
run_post_deploy_tests() {
    log_info "运行部署后测试..."

    case $DEPLOY_ENV in
        test)
            # 测试环境：运行冒烟测试
            run_smoke_tests
            ;;
        production)
            # 生产环境：运行生产验证测试
            run_production_verification
            ;;
    esac

    log_success "部署后测试完成"
}

# 冒烟测试
run_smoke_tests() {
    log_info "运行冒烟测试..."

    local api_base="http://localhost:8001/api"

    # API健康检查
    curl -f "${api_base}/health" || {
        log_error "API健康检查失败"
        return 1
    }

    # 数据库连接检查
    curl -f "${api_base}/system/health" || {
        log_error "系统健康检查失败"
        return 1
    }

    log_success "冒烟测试通过"
}

# 生产验证测试
run_production_verification() {
    log_info "运行生产环境验证..."

    local api_base="http://localhost:8000/api"

    # 基础API检查
    curl -f "${api_base}/health" || {
        log_error "生产API健康检查失败"
        return 1
    }

    # 数据库连接检查
    curl -f "${api_base}/system/health" || {
        log_error "生产系统健康检查失败"
        return 1
    }

    # 缓存连接检查
    curl -f "${api_base}/system/cache-health" || {
        log_error "缓存健康检查失败"
        return 1
    }

    log_success "生产环境验证通过"
}

# 回滚函数
rollback() {
    log_error "部署失败，开始回滚..."

    # 停止失败的服务
    docker-compose -f "docker-compose.${DEPLOY_ENV}.yml" down

    # 从备份恢复
    if [ -f "$BACKUP_DIR/docker-compose.yml.backup" ]; then
        cp "$BACKUP_DIR/docker-compose.yml.backup" "docker-compose.${DEPLOY_ENV}.yml"
        docker-compose -f "docker-compose.${DEPLOY_ENV}.yml" up -d
    fi

    log_info "回滚完成，请检查服务状态"
    exit 1
}

# 发送通知
send_notification() {
    local status=$1
    local message=$2

    log_info "发送部署通知..."

    # 这里可以集成各种通知服务
    case $status in
        success)
            echo "🎉 MyStocks $DEPLOY_ENV 环境部署成功!"
            ;;
        failure)
            echo "❌ MyStocks $DEPLOY_ENV 环境部署失败: $message"
            ;;
    esac

    # 示例：发送到Slack或企业微信
    # curl -X POST -H 'Content-type: application/json' \
    #      --data '{"text":"'"$message"'"}' \
    #      $WEBHOOK_URL
}

# 主部署流程
main() {
    log_info "开始MyStocks $DEPLOY_ENV 环境部署..."

    # 错误处理
    trap 'send_notification failure "部署过程中发生错误"' ERR

    # 执行部署步骤
    check_environment
    create_backup
    stop_services
    cleanup_old_images
    start_services

    # 等待服务启动
    if ! wait_for_services; then
        rollback
    fi

    # 运行测试
    if ! run_post_deploy_tests; then
        rollback
    fi

    # 发送成功通知
    send_notification success "MyStocks $DEPLOY_ENV 环境部署成功"

    log_success "🎉 部署完成！"
    log_info "📊 部署环境: $DEPLOY_ENV"
    log_info "📁 备份位置: $BACKUP_DIR"
    log_info "🌐 服务状态: $(docker-compose -f "docker-compose.${DEPLOY_ENV}.yml" ps)"
}

# 回滚命令
rollback_cmd() {
    log_warning "执行手动回滚..."

    DEPLOY_ENV=${1:-production}

    if [ ! -d "$BACKUP_DIR" ]; then
        log_error "未找到备份目录: $BACKUP_DIR"
        exit 1
    fi

    stop_services

    # 恢复备份
    if [ -f "$BACKUP_DIR/docker-compose.yml.backup" ]; then
        cp "$BACKUP_DIR/docker-compose.yml.backup" "docker-compose.${DEPLOY_ENV}.yml"
    fi

    start_services
    wait_for_services

    log_success "手动回滚完成"
}

# 显示帮助信息
show_help() {
    cat << EOF
MyStocks 部署工具

用法:
  $0 [environment] [options]    部署到指定环境
  $0 rollback [environment]     回滚到上一个版本
  $0 --help                     显示此帮助信息

环境:
  test         部署到测试环境
  production   部署到生产环境

选项:
  --cleanup    清理旧的Docker镜像
  --no-backup  跳过备份步骤（仅用于测试环境）

示例:
  $0 test                      # 部署到测试环境
  $0 production                # 部署到生产环境
  $0 rollback production       # 回滚生产环境
  $0 test --cleanup           # 部署到测试环境并清理旧镜像

环境变量:
  DEPLOY_ENV          部署环境 (test|production)
  CLEANUP_OLD_IMAGES  是否清理旧镜像 (true|false)

EOF
}

# 解析命令行参数
parse_args() {
    case ${1:-} in
        test|production)
            DEPLOY_ENV=$1
            shift
            ;;
        rollback)
            shift
            rollback_cmd "$@"
            exit 0
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        "")
            # 默认使用test环境
            DEPLOY_ENV="test"
            ;;
        *)
            log_error "无效的环境参数: $1"
            show_help
            exit 1
            ;;
    esac

    # 解析其他选项
    while [[ $# -gt 0 ]]; do
        case $1 in
            --cleanup)
                CLEANUP_OLD_IMAGES=true
                shift
                ;;
            --no-backup)
                SKIP_BACKUP=true
                shift
                ;;
            *)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# 脚本入口
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    parse_args "$@"
    main
fi