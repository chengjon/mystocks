#!/bin/bash
# MyStocks 清理回退脚本
# 用于恢复cleanup.sh归档的文件
# 作者: Claude
# 日期: 2025-10-19

set -e

echo "=== 开始回退目录清理 ==="
echo ""

restored=0

# 恢复temp_docs/
echo "[1/4] 检查 temp_docs/..."
if [ -d "archive/docs_history/temp_docs" ]; then
    mv archive/docs_history/temp_docs ./
    echo "✅ 恢复 temp_docs/"
    restored=$((restored + 1))
else
    echo "⚠️  temp_docs/ 未找到归档"
fi
echo ""

# 恢复specs/
echo "[2/4] 检查 specs/..."
if [ -d "archive/specifications/specs" ]; then
    mv archive/specifications/specs ./
    echo "✅ 恢复 specs/"
    restored=$((restored + 1))
else
    echo "⚠️  specs/ 未找到归档"
fi
echo ""

# 恢复inside/
echo "[3/4] 检查 inside/..."
if [ -d "archive/unused_modules/inside" ]; then
    mv archive/unused_modules/inside ./
    echo "✅ 恢复 inside/"
    restored=$((restored + 1))
else
    echo "⚠️  inside/ 未找到归档"
fi
echo ""

# 恢复临时MD文件
echo "[4/4] 检查临时MD文件..."
if [ -d "archive/reports" ]; then
    md_count=$(ls archive/reports/*.md 2>/dev/null | wc -l)
    if [ "$md_count" -gt 0 ]; then
        mv archive/reports/*.md ./ 2>/dev/null
        echo "✅ 恢复 $md_count 个临时MD文件"
        restored=$((restored + 1))
    else
        echo "⚠️  未找到临时MD文件"
    fi
else
    echo "⚠️  archive/reports/ 不存在"
fi
echo ""

# 清理空目录
echo "清理空的归档目录..."
rmdir archive/docs_history 2>/dev/null
rmdir archive/specifications 2>/dev/null
rmdir archive/unused_modules 2>/dev/null
rmdir archive/reports 2>/dev/null
rmdir archive 2>/dev/null

echo ""
echo "✅ 回退完成！"
echo "   - 恢复项目数: $restored"
echo ""

if [ "$restored" -eq 0 ]; then
    echo "⚠️  警告: 未找到任何归档文件，可能已被删除或清理脚本未运行"
else
    echo "系统已恢复到清理前状态"
fi
