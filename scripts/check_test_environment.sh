#!/bin/bash
# check_test_environment.sh
# MyStocks 测试环境检查脚本

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "  MyStocks 测试环境检查"
echo "=========================================="
echo ""

# 检查环境变量
echo -e "\n[1/5] 检查环境变量..."
required_vars=(
    "TDENGINE_HOST"
    "TDENGINE_PORT"
    "TDENGINE_USER"
    "TDENGINE_PASSWORD"
    "TDENGINE_DATABASE"
    "POSTGRESQL_HOST"
    "POSTGRESQL_PORT"
    "POSTGRESQL_USER"
    "POSTGRESQL_PASSWORD"
    "POSTGRESQL_DATABASE"
)

missing_vars=0
all_set=true

for var in "${required_vars[@]}"; do
    if [ -z "${!var+x}" ]; then
        if [ "$all_set" = true ]; then
            echo -e "${RED}❌ 环境变量未设置${NC}"
            all_set=false
        fi
        echo -e "   ${RED}❌ 缺失${NC}: $var"
        missing_vars=$((missing_vars + 1))
    else
        if [ "$all_set" = true ]; then
            echo -e "${GREEN}✅ 环境变量已设置${NC}"
            all_set=false
        fi
        echo -e "   ${GREEN}✅ 存在${NC}: $var"
    fi
done

if [ $missing_vars -eq 0 ]; then
    echo -e "\n   ${GREEN}✅ 所有环境变量已配置${NC}"
else
    echo -e "\n   ${RED}❌ 缺失 $missing_vars 个环境变量${NC}"
    echo -e "   ${YELLOW}提示: 运行 'source .env.test' 加载环境变量${NC}"
fi

# 检查Docker
echo -e "\n[2/5] 检查Docker..."
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✅ Docker 已安装${NC}: $(docker --version | awk '{print $3}')"
else
    echo -e "${RED}❌ Docker 未安装${NC}"
fi

if command -v docker-compose &> /dev/null || command -v docker compose &> /dev/null; then
    echo -e "${GREEN}✅ Docker Compose 已安装${NC}"
else
    echo -e "${RED}❌ Docker Compose 未安装${NC}"
fi

# 检查Python包
echo -e "\n[3/5] 检查Python包..."
packages=("psycopg2-binary" "taosws" "pytest" "pytest-cov")

for pkg in "${packages[@]}"; do
    if pip show "$pkg" > /dev/null 2>&1; then
        version=$(pip show "$pkg" | grep Version | awk '{print $2}')
        echo -e "${GREEN}✅ 已安装${NC}: $pkg ($version)"
    else
        echo -e "${RED}❌ 未安装${NC}: $pkg"
    fi
done

# 检查数据库连接
echo -e "\n[4/5] 检查数据库连接..."

# TDengine连接检查
if [ -n "${TDENGINE_HOST+x}" ]; then
    if command -v taos &> /dev/null; then
        if echo "SELECT 1;" | taos -h "$TDENGINE_HOST" -P "$TDENGINE_PORT" -u "$TDENGINE_USER" -p "$TDENGINE_PASSWORD" 2>/dev/null | grep -q "1"; then
            echo -e "${GREEN}✅ TDengine 连接成功${NC} ($TDENGINE_HOST:$TDENGINE_PORT)"
        else
            echo -e "${RED}❌ TDengine 连接失败${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  TDengine客户端未安装，无法测试连接${NC}"
        echo -e "   ${YELLOW}安装命令: pip install taosws${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  TDENGINE_HOST 环境变量未设置，跳过连接检查${NC}"
fi

# PostgreSQL连接检查
if [ -n "${POSTGRESQL_HOST+x}" ]; then
    if command -v psql &> /dev/null; then
        if PGPASSWORD="$POSTGRESQL_PASSWORD" psql -h "$POSTGRESQL_HOST" -p "$POSTGRESQL_PORT" -U "$POSTGRESQL_USER" -d "$POSTGRESQL_DATABASE" -c "SELECT 1;" 2>/dev/null | grep -q "1"; then
            echo -e "${GREEN}✅ PostgreSQL 连接成功${NC} ($POSTGRESQL_HOST:$POSTGRESQL_PORT)"
        else
            echo -e "${RED}❌ PostgreSQL 连接失败${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  PostgreSQL客户端未安装，无法测试连接${NC}"
        echo -e "   ${YELLOW}安装命令: apt install postgresql-client (Ubuntu)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  POSTGRESQL_HOST 环境变量未设置，跳过连接检查${NC}"
fi

# 检查Docker容器状态
echo -e "\n[5/5] 检查Docker容器状态..."
if command -v docker &> /dev/null; then
    tdengine_running=$(docker ps -q -f name=mystocks_tdengine_test)
    postgresql_running=$(docker ps -q -f name=mystocks_postgresql_test)

    if [ -n "$tdengine_running" ]; then
        echo -e "${GREEN}✅ TDengine 容器运行中${NC}"
    else
        echo -e "${RED}❌ TDengine 容器未运行${NC}"
        echo -e "   ${YELLOW}启动命令: docker-compose -f docker-compose.test.yml up -d${NC}"
    fi

    if [ -n "$postgresql_running" ]; then
        echo -e "${GREEN}✅ PostgreSQL 容器运行中${NC}"
    else
        echo -e "${RED}❌ PostgreSQL 容器未运行${NC}"
        echo -e "   ${YELLOW}启动命令: docker-compose -f docker-compose.test.yml up -d${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Docker 未安装，跳过容器检查${NC}"
fi

# 总结
echo -e "\n=========================================="
echo "  检查完成"
echo "=========================================="

if [ $missing_vars -eq 0 ]; then
    echo -e "\n${GREEN}✅ 环境就绪，可以开始测试${NC}"
    echo -e "\n运行测试命令："
    echo -e "  pytest tests/unit/ -v --cov=src"
else
    echo -e "\n${RED}❌ 需要配置 $missing_vars 个环境变量${NC}"
    echo -e "\n请执行以下步骤："
    echo -e "  1. 创建环境配置文件："
    echo -e "     cp .env.example .env.test"
    echo -e "  2. 编辑 .env.test 配置数据库连接"
    echo -e "  3. 加载环境变量："
    echo -e "     source .env.test"
    echo -e "  4. 重新运行此脚本验证"
fi
echo ""
