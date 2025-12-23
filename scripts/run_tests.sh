#!/bin/bash
# 测试运行脚本

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 进入项目目录
cd "$PROJECT_DIR"

echo "=================================="
echo "MyStocks 测试运行脚本"
echo "=================================="
echo "项目目录: $PROJECT_DIR"
echo ""

# 检查Python环境
if ! command -v python &> /dev/null; then
    echo "错误: 未找到Python命令"
    exit 1
fi

echo "Python版本: $(python --version)"
echo ""

# 检查pytest是否已安装
if ! python -m pytest --version &> /dev/null; then
    echo "错误: pytest未安装，请先运行 'pip install pytest'"
    exit 1
fi

echo "pytest版本: $(python -m pytest --version)"
echo ""

# 运行单元测试
echo "运行单元测试..."
echo "=================================="
python -m pytest tests/unit/ -v --tb=short

# 检查测试结果
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 所有测试通过"
else
    echo ""
    echo "❌ 部分测试失败"
    exit 1
fi

echo ""
echo "测试运行完成"
