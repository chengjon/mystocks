#!/bin/bash
# API与Web前端数据使用分析工具 - 快速开始脚本

echo "============================================================"
echo "  MyStocks API与Web前端数据使用分析工具"
echo "============================================================"
echo ""

# 检查Python是否可用
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python 3"
    echo "   请先安装Python 3.7或更高版本"
    exit 1
fi

echo "✅ Python 3 已安装"
echo ""

# 检查脚本是否存在
if [ ! -f "scripts/analyze_api_data_usage.py" ]; then
    echo "❌ 错误: 分析脚本不存在"
    echo "   请确认 scripts/analyze_api_data_usage.py 文件存在"
    exit 1
fi

echo "✅ 分析脚本已找到"
echo ""

# 检查后端和前端目录
if [ ! -d "web/backend/app/api" ]; then
    echo "❌ 错误: 后端API目录不存在"
    echo "   请确认 web/backend/app/api 目录存在"
    exit 1
fi

if [ ! -d "web/frontend/src" ]; then
    echo "❌ 错误: 前端目录不存在"
    echo "   请确认 web/frontend/src 目录存在"
    exit 1
fi

echo "✅ 后端和前端目录都已找到"
echo ""

# 创建输出目录
mkdir -p docs/reports

echo "🚀 开始分析..."
echo ""

# 运行分析工具
python3 scripts/analyze_api_data_usage.py "$@"

# 检查是否成功
if [ $? -eq 0 ]; then
    echo ""
    echo "============================================================"
    echo "✅ 分析完成！"
    echo "============================================================"
    echo ""
    echo "📄 生成的文件:"
    echo "   - docs/reports/API_WEB_DATA_USAGE_REPORT.md (详细报告)"
    echo "   - docs/reports/api_data_inventory.json (API清单)"
    echo "   - docs/reports/web_api_calls.json (API调用清单)"
    echo ""
    echo "💡 提示:"
    echo "   - 查看详细报告: cat docs/reports/API_WEB_DATA_USAGE_REPORT.md"
    echo "   - 使用增量分析: ./analyze_api_data_usage_quick.sh --incremental"
    echo "   - 查看使用文档: cat docs/reports/ANALYSIS_TOOL_README.md"
    echo ""
else
    echo ""
    echo "❌ 分析失败"
    echo "   请检查错误信息并重试"
    exit 1
fi
