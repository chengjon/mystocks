#!/bin/bash
echo "=== 架构优化环境依赖检查 ==="
echo ""

# 检查Python版本
echo "1. Python版本:"
python --version
if python -c 'import sys; exit(0 if sys.version_info >= (3,12) else 1)' 2>/dev/null; then
    echo "   ✅ Python 3.12+"
else
    echo "   ❌ Python版本不足（需要3.12+）"
    exit 1
fi
echo ""

# 检查关键依赖
echo "2. 关键依赖包:"
packages=("pandas" "psycopg2-binary" "taospy" "akshare" "loguru")

for pkg in "${packages[@]}"; do
    # Try psycopg2 if psycopg2-binary is not found
    if [ "$pkg" = "psycopg2-binary" ]; then
        if pip show psycopg2-binary > /dev/null 2>&1; then
            version=$(pip show psycopg2-binary | grep Version | cut -d' ' -f2)
            echo "   ✅ psycopg2-binary ($version)"
        elif pip show psycopg2 > /dev/null 2>&1; then
            version=$(pip show psycopg2 | grep Version | cut -d' ' -f2)
            echo "   ✅ psycopg2 ($version)"
        else
            echo "   ❌ psycopg2-binary/psycopg2 未安装"
            exit 1
        fi
    else
        if pip show $pkg > /dev/null 2>&1; then
            version=$(pip show $pkg | grep Version | cut -d' ' -f2)
            echo "   ✅ $pkg ($version)"
        else
            echo "   ⚠️  $pkg 未安装（将在需要时安装）"
        fi
    fi
done
echo ""

# 检查数据库连接
echo "3. 数据库连接:"

# PostgreSQL
if PGPASSWORD="${POSTGRESQL_PASSWORD:-c790414J}" psql -h "${POSTGRESQL_HOST:-localhost}" -U "${POSTGRESQL_USER:-mystocks_user}" -d "${POSTGRESQL_DATABASE:-mystocks}" -c "SELECT 1;" > /dev/null 2>&1; then
    echo "   ✅ PostgreSQL 可连接"
else
    echo "   ⚠️  PostgreSQL 连接失败（检查.env配置）"
fi

# TDengine
if command -v taos > /dev/null 2>&1; then
    if taos -h localhost -s "SELECT 1;" > /dev/null 2>&1; then
        echo "   ✅ TDengine 可连接"
    else
        echo "   ⚠️  TDengine 连接失败（将在T005配置）"
    fi
else
    echo "   ⚠️  TDengine CLI未安装（将在Phase 2配置）"
fi
echo ""

echo "=== 环境检查完成 ==="
