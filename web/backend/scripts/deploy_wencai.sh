#!/bin/bash
##############################################################################
# 问财功能部署脚本
#
# 自动化部署问财股票筛选功能到MyStocks Web后端
#
# 作者: MyStocks Backend Team
# 创建日期: 2025-10-17
# 使用方法: bash scripts/deploy_wencai.sh
##############################################################################

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MIGRATION_FILE="$PROJECT_ROOT/migrations/wencai_init.sql"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  问财功能部署脚本${NC}"
echo -e "${BLUE}========================================${NC}"
echo

# 1. 检查前置条件
echo -e "${YELLOW}[1/6] 检查前置条件...${NC}"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 未安装${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python3: $(python3 --version)${NC}"

# 检查pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip3 未安装${NC}"
    exit 1
fi
echo -e "${GREEN}✅ pip3: $(pip3 --version)${NC}"

# 检查MySQL客户端
if ! command -v mysql &> /dev/null; then
    echo -e "${YELLOW}⚠️  MySQL客户端未安装，将跳过自动数据库初始化${NC}"
    SKIP_DB_INIT=true
else
    echo -e "${GREEN}✅ MySQL客户端: $(mysql --version)${NC}"
    SKIP_DB_INIT=false
fi

echo

# 2. 检查必需文件
echo -e "${YELLOW}[2/6] 检查必需文件...${NC}"

REQUIRED_FILES=(
    "$PROJECT_ROOT/app/adapters/wencai_adapter.py"
    "$PROJECT_ROOT/app/models/wencai_data.py"
    "$PROJECT_ROOT/app/schemas/wencai_schemas.py"
    "$PROJECT_ROOT/app/services/wencai_service.py"
    "$PROJECT_ROOT/app/api/wencai.py"
    "$PROJECT_ROOT/app/tasks/wencai_tasks.py"
    "$MIGRATION_FILE"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ 文件不存在: $file${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ $(basename $file)${NC}"
done

echo

# 3. 安装Python依赖
echo -e "${YELLOW}[3/6] 检查Python依赖...${NC}"

cd "$PROJECT_ROOT"

REQUIRED_PACKAGES=("requests" "pandas" "sqlalchemy" "pymysql" "celery")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if python3 -c "import $package" 2>/dev/null; then
        echo -e "${GREEN}✅ $package${NC}"
    else
        echo -e "${RED}❌ $package (缺失)${NC}"
        MISSING_PACKAGES+=("$package")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -ne 0 ]; then
    echo -e "${YELLOW}正在安装缺失的包...${NC}"
    pip3 install "${MISSING_PACKAGES[@]}"
fi

echo

# 4. 执行数据库迁移
echo -e "${YELLOW}[4/6] 执行数据库迁移...${NC}"

if [ "$SKIP_DB_INIT" = false ]; then
    echo "请输入MySQL连接信息："
    read -p "主机 (默认: localhost): " MYSQL_HOST
    MYSQL_HOST=${MYSQL_HOST:-localhost}

    read -p "端口 (默认: 3306): " MYSQL_PORT
    MYSQL_PORT=${MYSQL_PORT:-3306}

    read -p "用户名 (默认: root): " MYSQL_USER
    MYSQL_USER=${MYSQL_USER:-root}

    read -sp "密码: " MYSQL_PASSWORD
    echo

    read -p "数据库名 (默认: wencai): " MYSQL_DB
    MYSQL_DB=${MYSQL_DB:-wencai}

    echo -e "${YELLOW}执行SQL脚本...${NC}"
    mysql -h "$MYSQL_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DB" < "$MIGRATION_FILE"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 数据库迁移成功${NC}"

        # 验证数据
        QUERY_COUNT=$(mysql -h "$MYSQL_HOST" -P "$MYSQL_PORT" -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DB" -se "SELECT COUNT(*) FROM wencai_queries")
        echo -e "${GREEN}✅ 已插入 $QUERY_COUNT 个查询定义${NC}"
    else
        echo -e "${RED}❌ 数据库迁移失败${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  跳过自动数据库初始化${NC}"
    echo -e "${YELLOW}请手动执行: mysql -u root -p < $MIGRATION_FILE${NC}"
fi

echo

# 5. 配置提示
echo -e "${YELLOW}[5/6] 配置检查...${NC}"

echo -e "${BLUE}请确保以下配置已更新:${NC}"
echo
echo -e "1. ${YELLOW}app/main.py${NC} - 添加问财路由"
echo -e "   ${GREEN}from app.api import wencai${NC}"
echo -e "   ${GREEN}app.include_router(wencai.router)${NC}"
echo
echo -e "2. ${YELLOW}app/core/config.py${NC} - 添加问财配置"
echo -e "   ${GREEN}WENCAI_TIMEOUT: int = 30${NC}"
echo -e "   ${GREEN}WENCAI_RETRY_COUNT: int = 3${NC}"
echo
echo -e "3. ${YELLOW}celeryconfig.py${NC} - 添加定时任务"
echo -e "   ${GREEN}参考: celeryconfig_wencai.py${NC}"
echo
echo -e "4. ${YELLOW}.env${NC} - 添加环境变量（可选）"
echo -e "   ${GREEN}WENCAI_TIMEOUT=30${NC}"
echo

read -p "是否已完成上述配置？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}请先完成配置，然后重新运行此脚本${NC}"
    exit 0
fi

echo

# 6. 测试验证
echo -e "${YELLOW}[6/6] 运行测试...${NC}"

# Python导入测试
echo -e "${BLUE}测试Python导入...${NC}"
python3 << EOF
try:
    from app.api import wencai
    from app.services.wencai_service import WencaiService
    from app.adapters.wencai_adapter import WencaiDataSource
    from app.models.wencai_data import WencaiQuery
    from app.tasks import wencai_tasks
    print("${GREEN}✅ 所有模块导入成功${NC}")
except ImportError as e:
    print(f"${RED}❌ 导入失败: {e}${NC}")
    exit(1)
EOF

echo

# 完成
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  ✅ 部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo
echo -e "${BLUE}下一步操作:${NC}"
echo
echo -e "1. 重启FastAPI服务:"
echo -e "   ${GREEN}systemctl restart mystocks-backend${NC}"
echo -e "   ${GREEN}# 或${NC}"
echo -e "   ${GREEN}uvicorn app.main:app --reload${NC}"
echo
echo -e "2. 重启Celery服务:"
echo -e "   ${GREEN}systemctl restart celery-worker${NC}"
echo -e "   ${GREEN}systemctl restart celery-beat${NC}"
echo
echo -e "3. 测试API端点:"
echo -e "   ${GREEN}curl http://localhost:8000/api/market/wencai/health${NC}"
echo -e "   ${GREEN}curl http://localhost:8000/api/market/wencai/queries${NC}"
echo
echo -e "4. 查看API文档:"
echo -e "   ${GREEN}http://localhost:8000/api/docs${NC}"
echo
echo -e "${BLUE}详细文档:${NC}"
echo -e "  - WENCAI_CONFIG_UPDATE_GUIDE.md"
echo -e "  - WENCAI_PHASE1_COMPLETED.md"
echo
