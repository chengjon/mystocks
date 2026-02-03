#!/bin/bash
# MyStocks 目录清理脚本（保守版）
# 所有文件都归档而非删除
# 作者: Claude
# 日期: 2025-10-19

set -e  # 遇到错误立即停止

echo "=== MyStocks 目录清理开始 ==="
echo ""

# 1. 创建归档目录
echo "[1/6] 创建归档目录结构..."
mkdir -p archive/{docs_history,specifications,reports,unused_modules}
echo "✅ 归档目录创建完成"
echo ""

# 2. 归档临时文档目录
echo "[2/6] 归档临时文档目录..."
if [ -d "temp_docs" ]; then
    mv temp_docs/ archive/docs_history/
    echo "✅ temp_docs/ 已归档"
else
    echo "⚠️  temp_docs/ 不存在"
fi
echo ""

# 3. 归档规格文档目录
echo "[3/6] 归档规格文档目录..."
if [ -d "specs" ]; then
    mv specs/ archive/specifications/
    echo "✅ specs/ 已归档"
else
    echo "⚠️  specs/ 不存在"
fi
echo ""

# 4. 归档根目录临时MD文件
echo "[4/6] 归档根目录临时MD文件..."
count=0

# WEEK系列
for file in WEEK*.md; do
    if [ -f "$file" ]; then
        mv "$file" archive/reports/
        count=$((count + 1))
    fi
done

# SUMMARY系列
for file in *_SUMMARY.md; do
    if [ -f "$file" ] && [ "$file" != "ARCHITECTURE_SIMPLIFICATION_SUMMARY.md" ]; then
        mv "$file" archive/reports/
        count=$((count + 1))
    fi
done

# REPORT系列
for file in *_REPORT.md; do
    if [ -f "$file" ]; then
        mv "$file" archive/reports/
        count=$((count + 1))
    fi
done

# COMPLETION系列
for file in *_COMPLETION.md; do
    if [ -f "$file" ]; then
        mv "$file" archive/reports/
        count=$((count + 1))
    fi
done

# 其他临时分析文件
for file in ANALYSIS_SUMMARY.md COMPREHENSIVE_ANALYSIS_REPORT.md DEEP_ANALYSIS_COMPLETION.md; do
    if [ -f "$file" ]; then
        mv "$file" archive/reports/
        count=$((count + 1))
    fi
done

# 其他临时文件
for file in TEMP_*.md INTEGRATION_SUMMARY.md MARKET_DATA_FIX_SUMMARY.md DELIVERY_v2.1.md; do
    if [ -f "$file" ]; then
        mv "$file" archive/reports/
        count=$((count + 1))
    fi
done

echo "✅ 已归档 $count 个临时MD文件"
echo ""

# 5. 删除空目录和可重新生成的文件
echo "[5/6] 清理空目录和临时文件..."
rmdir temp/ 2>/dev/null && echo "✅ 删除 temp/" || echo "⚠️  temp/ 不存在或不为空"
rm -rf htmlcov/ 2>/dev/null && echo "✅ 删除 htmlcov/" || echo "⚠️  htmlcov/ 不存在"
echo ""

# 6. 归档历史数据目录
echo "[6/6] 归档历史数据目录..."
if [ -d "inside" ]; then
    mv inside/ archive/unused_modules/
    echo "✅ inside/ 已归档"
else
    echo "⚠️  inside/ 不存在"
fi
echo ""

# 7. 生成清理报告
echo "=== 清理完成，生成报告 ==="
report_file="archive/CLEANUP_REPORT_$(date +%Y%m%d_%H%M%S).md"
cat > "$report_file" << EOF
# 目录清理报告

**清理日期**: $(date)
**脚本版本**: 保守版 v1.0

## 已归档内容

### 文档
- temp_docs/ → archive/docs_history/
- specs/ → archive/specifications/
- ${count}个临时MD → archive/reports/

### 历史数据
- inside/ → archive/unused_modules/

## 已删除内容
- temp/ （空目录）
- htmlcov/ （测试覆盖率报告，可重新生成）

## 保留内容
- 所有核心代码文件
- 重要文档（README, CLAUDE, CHANGELOG等）
- 适配器和数据库代码
- 测试文件

## 回退方法
如需恢复归档文件：
\`\`\`bash
# 恢复specs/
mv archive/specifications/specs ./

# 恢复temp_docs/
mv archive/docs_history/temp_docs ./

# 恢复临时MD
mv archive/reports/*.md ./
\`\`\`

## 下一步建议
1. 验证系统功能正常
2. 运行测试套件
3. 如果一切正常，可以在2周后永久删除archive/
EOF

echo ""
echo "✅ 清理完成！"
echo ""
echo "📊 统计信息："
echo "   - 归档目录: $(du -sh archive/ 2>/dev/null | cut -f1)"
echo "   - 当前目录数: $(ls -d */ 2>/dev/null | wc -l)"
echo ""
echo "📝 清理报告已保存到: $report_file"
echo ""
echo "⚠️  建议："
echo "   1. 立即运行测试：pytest tests/"
echo "   2. 验证系统启动：python -c 'from unified_manager import MyStocksUnifiedManager; print(\"OK\")'"
echo "   3. 如一切正常，2周后可删除archive/"
echo ""
