#!/bin/bash
# 文件分析系统演示脚本

echo "========================================="
echo "文件分析系统演示"
echo "========================================="
echo ""

# 设置环境变量
export POSTGRES_HOST=192.168.123.104
export POSTGRES_PORT=5438
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=c790414J
export ANALYSIS_DB=file_analysis_db

echo "1. 查看统计信息"
echo "-----------------------------------------"
python scripts/file_analysis/query_tool.py stats
echo ""

echo "2. 查看最新分析记录"
echo "-----------------------------------------"
python scripts/file_analysis/query_tool.py latest
echo ""

echo "3. 查询 unified_manager.py 文件"
echo "-----------------------------------------"
python scripts/file_analysis/query_tool.py name unified_manager
echo ""

echo "4. 查询 Python后端 分类文件"
echo "-----------------------------------------"
python scripts/file_analysis/query_tool.py category py_backend
echo ""

echo "5. 查看复杂度最高的文件（JSON格式）"
echo "-----------------------------------------"
# 这里我们查看所有文件，然后找出复杂度最高的
echo "已生成分析报告，请查看 analysis_report_*.md 文件"
echo ""

echo "========================================="
echo "演示完成"
echo "========================================="
echo ""
echo "更多查询示例："
echo "  python scripts/file_analysis/query_tool.py path /path/to/file.py"
echo "  python scripts/file_analysis/query_tool.py top --limit 20"
echo "  python scripts/file_analysis/query_tool.py --json name unified_manager"
echo ""
echo "重新扫描文件："
echo "  python scripts/file_analysis/main.py /path/to/directory"
echo ""