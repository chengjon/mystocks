#!/bin/bash

################################################################################
# MyStocks 部署前检查脚本
#
# 目的: 在部署到生产环境前运行所有烟雾测试，确保系统正常
# 使用: ./scripts/pre_deploy_check.sh
#
# 退出码:
#   0 - 所有检查通过，可以部署
#   1 - 有检查失败，阻止部署
################################################################################

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 结果变量
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# 日志函数
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
}

log_error() {
    echo -e "${RED}✗${NC} $1"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# 检查函数
check_result() {
    local name="$1"
    local result="$2"
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    if [ "$result" = "0" ]; then
        log_success "$name"
        return 0
    else
        log_error "$name"
        return 1
    fi
}

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  MyStocks 部署前检查                                      ║${NC}"
echo -e "${BLUE}║  Pre-Deployment Check Script                              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

################################################################################
# Phase 1: 环境检查
################################################################################

echo -e "${YELLOW}[Phase 1]${NC} 环境检查..."
echo ""

# 检查必要的工具
log_info "检查必要工具..."

command -v python3 >/dev/null 2>&1
check_result "Python3 已安装" $?

command -v pytest >/dev/null 2>&1
check_result "pytest 已安装" $?

command -v http >/dev/null 2>&1 || command -v curl >/dev/null 2>&1
check_result "HTTP 客户端已安装 (httpie/curl)" $?

echo ""

################################################################################
# Phase 2: 服务状态检查
################################################################################

echo -e "${YELLOW}[Phase 2]${NC} 服务状态检查..."
echo ""

# 后端服务
log_info "检查后端服务..."
if curl -sf http://localhost:8000/health >/dev/null 2>&1; then
    log_success "后端服务运行正常 (http://localhost:8000)"
else
    log_error "后端服务未运行或无响应"
    log_warning "请启动后端: cd web/backend && uvicorn app.main:app --reload"
fi

# 前端服务
log_info "检查前端服务..."
if curl -sf http://localhost:5173 >/dev/null 2>&1; then
    log_success "前端服务运行正常 (http://localhost:5173)"
else
    log_error "前端服务未运行或无响应"
    log_warning "请启动前端: cd web/frontend && npm run dev"
fi

# 数据库服务
log_info "检查数据库服务..."
if command -v psql >/dev/null 2>&1; then
    if PGPASSWORD=${POSTGRESQL_PASSWORD:-mystocks2025} psql \
        -h ${POSTGRESQL_HOST:-localhost} \
        -U ${POSTGRESQL_USER:-mystocks_user} \
        -d ${POSTGRESQL_DATABASE:-mystocks} \
        -c "SELECT 1;" >/dev/null 2>&1; then
        log_success "PostgreSQL 数据库连接正常"
    else
        log_error "PostgreSQL 数据库连接失败"
        log_warning "请检查数据库服务和配置"
    fi
else
    log_warning "psql 未安装，跳过数据库检查"
fi

echo ""

################################################################################
# Phase 3: 运行烟雾测试
################################################################################

echo -e "${YELLOW}[Phase 3]${NC} 运行烟雾测试套件..."
echo ""

if [ -f "tests/smoke/test_smoke.py" ]; then
    log_info "执行 pytest 烟雾测试..."

    # 运行 pytest 烟雾测试
    if pytest tests/smoke/test_smoke.py -v -x --tb=short; then
        log_success "烟雾测试套件全部通过"
    else
        log_error "烟雾测试失败"
        echo ""
        echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${RED}║  部署检查失败                                              ║${NC}"
        echo -e "${RED}║  Deployment Check FAILED                                  ║${NC}"
        echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        echo "❌ 烟雾测试未通过，阻止部署"
        echo ""
        echo "请执行以下步骤:"
        echo "1. 查看上面的测试失败信息"
        echo "2. 修复失败的测试"
        echo "3. 重新运行此脚本"
        echo ""
        exit 1
    fi
else
    log_warning "烟雾测试文件不存在: tests/smoke/test_smoke.py"
    log_info "运行快速手动检查..."

    # 如果没有烟雾测试文件，运行快速手动检查
    source scripts/bash_aliases.sh 2>/dev/null || true

    # 快速 API 检查
    log_info "测试登录 API..."
    if command -v http >/dev/null 2>&1; then
        TOKEN=$(http --ignore-stdin POST http://localhost:8000/api/auth/login \
            username=admin password=admin123 2>/dev/null | \
            python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

        if [ -n "$TOKEN" ]; then
            log_success "登录 API 正常"

            # 测试仪表盘 API
            log_info "测试仪表盘 API..."
            if http --check-status GET http://localhost:8000/api/data/dashboard/summary \
                Authorization:"Bearer $TOKEN" >/dev/null 2>&1; then
                log_success "仪表盘 API 正常"
            else
                log_error "仪表盘 API 失败"
            fi
        else
            log_error "登录 API 失败"
        fi
    else
        log_warning "httpie 未安装，跳过 API 检查"
    fi
fi

echo ""

################################################################################
# Phase 4: 代码质量检查
################################################################################

echo -e "${YELLOW}[Phase 4]${NC} 代码质量检查..."
echo ""

# 检查是否有未提交的更改
log_info "检查 Git 状态..."
if [ -d ".git" ]; then
    if [ -n "$(git status --porcelain)" ]; then
        log_warning "有未提交的更改"
        echo "  提示: 建议提交或暂存所有更改后再部署"
    else
        log_success "Git 工作区干净"
    fi
else
    log_warning "不是 Git 仓库"
fi

# 运行单元测试（可选）
if [ "${RUN_UNIT_TESTS:-false}" = "true" ]; then
    log_info "运行单元测试..."
    if pytest tests/unit/ -q; then
        log_success "单元测试通过"
    else
        log_warning "单元测试有失败项"
    fi
fi

echo ""

################################################################################
# 最终报告
################################################################################

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  部署前检查完成                                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo "完成时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "检查结果:"
echo -e "  总计检查项: ${BLUE}$TOTAL_CHECKS${NC}"
echo -e "  通过: ${GREEN}$PASSED_CHECKS${NC}"
echo -e "  失败: ${RED}$FAILED_CHECKS${NC}"
echo ""

if [ $FAILED_CHECKS -eq 0 ]; then
    echo -e "${GREEN}✅ 所有检查通过，准备部署！${NC}"
    echo ""
    echo "下一步:"
    echo "  1. 确认部署配置"
    echo "  2. 备份当前生产环境"
    echo "  3. 执行部署脚本"
    echo "  4. 部署后再次运行烟雾测试"
    echo ""
    exit 0
else
    echo -e "${RED}❌ 有 $FAILED_CHECKS 项检查失败，阻止部署！${NC}"
    echo ""
    echo "必须修复所有失败项后才能部署。"
    echo ""
    echo "故障排查:"
    echo "  1. 查看上面的失败信息"
    echo "  2. 参考文档: docs/development-process/troubleshooting.md"
    echo "  3. 修复问题后重新运行此脚本"
    echo ""
    exit 1
fi
