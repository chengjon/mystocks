#!/bin/bash
##############################################################################
# 问财功能部署前检查脚本
#
# 检查所有必要的配置和文件是否就位
#
# 作者: MyStocks Backend Team
# 创建日期: 2025-10-17
# 使用方法: bash scripts/pre_deployment_check.sh
##############################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 脚本变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PASSED=0
FAILED=0
WARNINGS=0

# 测试函数
test_file() {
    local name="$1"
    local file="$2"

    if [ -f "$file" ]; then
        echo -e "${GREEN}✅${NC} $name: $file"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}❌${NC} $name 不存在: $file"
        FAILED=$((FAILED + 1))
    fi
}

test_config() {
    local name="$1"
    local file="$2"
    local keyword="$3"

    if grep -q "$keyword" "$file" 2>/dev/null; then
        echo -e "${GREEN}✅${NC} $name 已配置"
        PASSED=$((PASSED + 1))
    else
        echo -e "${YELLOW}⚠️${NC} $name 可能未配置 (未找到: $keyword)"
        WARNINGS=$((WARNINGS + 1))
    fi
}

# 开始检查
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  问财功能部署前检查${NC}"
echo -e "${BLUE}========================================${NC}"
echo

# 1. 文件检查
echo -e "${BLUE}[1] 检查必要文件...${NC}"
echo

test_file "适配器" "$PROJECT_ROOT/app/adapters/wencai_adapter.py"
test_file "模型" "$PROJECT_ROOT/app/models/wencai_data.py"
test_file "Schema" "$PROJECT_ROOT/app/schemas/wencai_schemas.py"
test_file "服务" "$PROJECT_ROOT/app/services/wencai_service.py"
test_file "API路由" "$PROJECT_ROOT/app/api/wencai.py"
test_file "Celery任务" "$PROJECT_ROOT/app/tasks/wencai_tasks.py"
test_file "数据库脚本" "$PROJECT_ROOT/migrations/wencai_init.sql"
test_file "部署脚本" "$PROJECT_ROOT/scripts/deploy_wencai.sh"
test_file "测试脚本" "$PROJECT_ROOT/scripts/test_wencai_api.sh"

echo

# 2. 配置检查
echo -e "${BLUE}[2] 检查配置文件...${NC}"
echo

if [ -f "$PROJECT_ROOT/app/main.py" ]; then
    test_config "main.py - wencai导入" "$PROJECT_ROOT/app/main.py" "from app.api import wencai"
    test_config "main.py - 路由注册" "$PROJECT_ROOT/app/main.py" "wencai.router"
else
    echo -e "${RED}❌${NC} app/main.py 不存在"
    FAILED=$((FAILED + 1))
fi

if [ -f "$PROJECT_ROOT/app/core/config.py" ]; then
    test_config "config.py - WENCAI配置" "$PROJECT_ROOT/app/core/config.py" "WENCAI_TIMEOUT"
else
    echo -e "${RED}❌${NC} app/core/config.py 不存在"
    FAILED=$((FAILED + 1))
fi

if [ -f "$PROJECT_ROOT/celeryconfig.py" ]; then
    test_config "celeryconfig.py - 问财任务" "$PROJECT_ROOT/celeryconfig.py" "wencai"
else
    echo -e "${YELLOW}⚠️${NC} celeryconfig.py 可能未配置"
    WARNINGS=$((WARNINGS + 1))
fi

echo

# 3. 依赖检查
echo -e "${BLUE}[3] 检查Python依赖...${NC}"
echo

check_package() {
    local package="$1"
    if python3 -c "import $package" 2>/dev/null; then
        echo -e "${GREEN}✅${NC} $package 已安装"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}❌${NC} $package 未安装"
        FAILED=$((FAILED + 1))
    fi
}

check_package "requests"
check_package "pandas"
check_package "sqlalchemy"
check_package "pymysql"
check_package "celery"

echo

# 4. 数据库检查
echo -e "${BLUE}[4] 检查数据库...${NC}"
echo

if command -v mysql &> /dev/null; then
    echo -e "${YELLOW}请输入MySQL连接信息用于验证:${NC}"
    read -p "主机 (默认: localhost): " MYSQL_HOST
    MYSQL_HOST=${MYSQL_HOST:-localhost}

    read -p "用户名 (默认: root): " MYSQL_USER
    MYSQL_USER=${MYSQL_USER:-root}

    read -sp "密码: " MYSQL_PASSWORD
    echo

    read -p "数据库名 (默认: wencai): " MYSQL_DB
    MYSQL_DB=${MYSQL_DB:-wencai}

    # 测试连接
    if mysql -h "$MYSQL_HOST" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DB" -e "SELECT 1;" &>/dev/null; then
        echo -e "${GREEN}✅${NC} MySQL连接成功"
        PASSED=$((PASSED + 1))

        # 检查表
        if mysql -h "$MYSQL_HOST" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DB" -e "SHOW TABLES LIKE 'wencai%';" 2>/dev/null | grep -q wencai; then
            echo -e "${GREEN}✅${NC} 问财表已存在"
            PASSED=$((PASSED + 1))
        else
            echo -e "${YELLOW}⚠️${NC} 问财表不存在（需要执行迁移）"
            WARNINGS=$((WARNINGS + 1))
        fi
    else
        echo -e "${RED}❌${NC} MySQL连接失败"
        FAILED=$((FAILED + 1))
    fi
else
    echo -e "${YELLOW}⚠️${NC} MySQL客户端未安装，跳过数据库检查"
fi

echo

# 5. 服务检查
echo -e "${BLUE}[5] 检查服务状态...${NC}"
echo

check_service() {
    local service="$1"
    if systemctl is-active --quiet "$service" 2>/dev/null; then
        echo -e "${GREEN}✅${NC} $service 运行中"
        PASSED=$((PASSED + 1))
    else
        echo -e "${YELLOW}⚠️${NC} $service 未运行（可能需要部署后启动）"
        WARNINGS=$((WARNINGS + 1))
    fi
}

check_service "mystocks-backend"
check_service "celery-worker"
check_service "celery-beat"

echo

# 6. 总结
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  检查结果${NC}"
echo -e "${BLUE}========================================${NC}"
echo

echo -e "通过: ${GREEN}$PASSED${NC}"
echo -e "失败: ${RED}$FAILED${NC}"
echo -e "警告: ${YELLOW}$WARNINGS${NC}"
echo

if [ $FAILED -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ 所有检查通过，可以部署！${NC}"
    echo
    echo -e "${BLUE}下一步:${NC}"
    echo "1. bash scripts/deploy_wencai.sh"
    echo "2. systemctl restart mystocks-backend"
    echo "3. bash scripts/test_wencai_api.sh"
    exit 0
elif [ $FAILED -eq 0 ]; then
    echo -e "${YELLOW}⚠️  有 $WARNINGS 个警告，可以继续部署${NC}"
    echo
    echo -e "${BLUE}建议:${NC}"
    echo "1. 根据配置指南更新配置文件"
    echo "2. 执行数据库迁移（如需要）"
    echo "3. 重启服务"
    exit 0
else
    echo -e "${RED}❌ 有 $FAILED 个错误，需要修复后再部署${NC}"
    echo
    echo -e "${BLUE}解决步骤:${NC}"
    echo "1. 查看上述错误信息"
    echo "2. 根据 CONFIG_PATCHES.md 更新配置"
    echo "3. 安装缺失的依赖"
    echo "4. 重新运行此脚本"
    exit 1
fi
