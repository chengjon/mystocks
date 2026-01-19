#!/bin/bash
# 测试新功能脚本
# 测试：1. 引用分析Bug修复 2. CSS和JSON文件支持 3. 增量扫描功能

set -e

# 设置数据库连接信息
export POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
export POSTGRES_PORT="${POSTGRES_PORT:-5432}"
export POSTGRES_USER="${POSTGRES_USER:-postgres}"
export POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-postgres}"
export ANALYSIS_DB="${ANALYSIS_DB:-file_analysis_db}"

echo "======================================"
echo "文件分析系统 - 新功能测试"
echo "======================================"
echo ""

# 1. 运行数据库迁移
echo "步骤 1: 运行数据库迁移（添加CSS和JSON列）"
echo "----------------------------------------"
psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $ANALYSIS_DB -f migration_add_css_json.sql
echo "✓ 数据库迁移完成"
echo ""

# 2. 测试全量扫描（包含CSS和JSON文件）
echo "步骤 2: 测试全量扫描（包含CSS和JSON文件）"
echo "----------------------------------------"
cd /opt/claude/mystocks_spec
python3 scripts/file_analysis/main.py
echo "✓ 全量扫描完成"
echo ""

# 3. 查询统计信息，验证CSS和JSON文件是否被正确统计
echo "步骤 3: 查询统计信息"
echo "----------------------------------------"
python3 scripts/file_analysis/query_tool.py --stats
echo ""

# 4. 测试增量扫描
echo "步骤 4: 测试增量扫描"
echo "----------------------------------------"
# 等待1秒以确保时间戳不同
sleep 1

# 创建一个测试文件以触发增量扫描
echo "/* 测试CSS文件 */" > /tmp/test_incremental.css
echo '{"test": "data"}' > /tmp/test_incremental.json

python3 scripts/file_analysis/main.py --incremental
echo "✓ 增量扫描完成"
echo ""

# 5. 测试指定时间的增量扫描
echo "步骤 5: 测试指定时间的增量扫描"
echo "----------------------------------------"
python3 scripts/file_analysis/main.py --incremental --since "2026-01-01 00:00:00"
echo "✓ 指定时间增量扫描完成"
echo ""

# 6. 查询最近的CSS和JSON文件
echo "步骤 6: 查询最近的CSS和JSON文件"
echo "----------------------------------------"
python3 scripts/file_analysis/query_tool.py --type css --limit 5
echo ""
python3 scripts/file_analysis/query_tool.py --type json --limit 5
echo ""

# 7. 验证引用分析是否正常工作（无Bug）
echo "步骤 7: 验证引用分析"
echo "----------------------------------------"
python3 scripts/file_analysis/query_tool.py --references --limit 10
echo ""

# 清理测试文件
rm -f /tmp/test_incremental.css /tmp/test_incremental.json

echo "======================================"
echo "所有测试完成！"
echo "======================================"