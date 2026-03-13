#!/usr/bin/bash
# 快速系统健康检查脚本
# Quick System Health Check Script

echo "🚀 快速系统健康检查"
echo "===================="

# 检查Python版本
echo ""
echo "🐍 检查Python版本..."
python3 --version

# 检查环境变量
echo ""
echo "🔧 检查环境变量..."
REQUIRED_VARS=("POSTGRESQL_HOST" "POSTGRESQL_USER" "POSTGRESQL_PASSWORD")
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ 缺少环境变量: $var"
    else
        echo "✅ $var 已配置"
    fi
done

# 检查关键文件存在
echo ""
echo "📁 检查关键文件..."
CRITICAL_FILES=(
    "src/adapters/sina_finance_adapter.py"
    "web/backend/app/api/stock_ratings_api.py"
    "config/compatibility/sina_finance/main.yaml"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file 存在"
    else
        echo "❌ $file 不存在"
    fi
done

# 快速语法检查
echo ""
echo "💻 快速语法检查..."
SYNTAX_ERRORS=$(find src web/backend -name "*.py" -exec python3 -m py_compile {} \; 2>&1 | wc -l)
if [ "$SYNTAX_ERRORS" -gt 0 ]; then
    echo "❌ 发现 $SYNTAX_ERRORS 个语法错误"
else
    echo "✅ 语法检查通过"
fi

# 检查FastAPI应用导入
echo ""
echo "🌐 检查FastAPI应用..."
cd web/backend
if python3 -c "from app.main import app; print('✅ FastAPI应用导入成功')" 2>/dev/null; then
    echo "✅ FastAPI应用可启动"
else
    echo "❌ FastAPI应用导入失败"
fi
cd ../..

# 检查Sina Finance适配器
echo ""
echo "📊 检查Sina Finance适配器..."
if python3 -c "
import os
os.environ['DEVELOPMENT_MODE'] = 'true'
from src.adapters.sina_finance_adapter import SinaFinanceAdapter
adapter = SinaFinanceAdapter()
print('✅ Sina Finance适配器工作正常')
" 2>/dev/null; then
    echo "✅ Sina Finance适配器可正常使用"
else
    echo "❌ Sina Finance适配器存在问题"
fi

echo ""
echo "===================="
echo "🏁 检查完成"
